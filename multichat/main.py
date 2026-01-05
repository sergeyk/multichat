import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import click


# RGB color type for click.style() true color support
Color = Union[str, Tuple[int, int, int]]


@dataclass(frozen=True)
class ProviderSpec:
    display_name: str
    provider_name: str
    model_name: str
    env_var: str
    color: Color


def _get_cache_dir() -> Path:
    # Prefer XDG cache dir if set, otherwise default to ~/.cache
    xdg_cache = os.getenv("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "multichat"
    # Fallbacks for non-XDG systems
    if os.name == "nt":
        # Windows: use LOCALAPPDATA if available
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "multichat" / "Cache"
    return Path.home() / ".cache" / "multichat"


# Store session under user's cache directory, e.g. ~/.cache/multichat/session.json
SESSION_FILE = _get_cache_dir() / "session.json"


def _load_session() -> Dict[str, Any]:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text())
        except Exception:
            return {"turns": []}
    return {"turns": []}


def _save_session(data: Dict[str, Any]) -> None:
    # Ensure parent directory exists before writing
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _render_transcript(turns: List[Dict[str, str]]) -> str:
    lines: List[str] = []
    for t in turns:
        role = t.get("role")
        if role == "user":
            lines.append(f"[user] {t.get('content', '')}")
        elif role == "model":
            model = t.get("model", "model")
            lines.append(f"[{model}]\n{t.get('content', '')}")
        # ignore unknown roles
        lines.append("")  # blank line between entries
    # strip trailing blank line
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--continue",
    "continue_",
    is_flag=True,
    flag_value=True,
    default=False,
    help="Continue the last conversation",
)
@click.argument("message", nargs=-1, required=False)
def main(continue_: bool, message: Tuple[str, ...]) -> None:
    """Send a message to multiple LLMs. Use -c to continue last chat."""
    import asyncio
    import os
    import sys
    import time

    from any_llm import acompletion

    provider_specs = [
        ProviderSpec(
            "Anthropic", "anthropic", "claude-opus-4-5", "ANTHROPIC_API_KEY", (217, 119, 6)
        ),  # #d97706 amber/orange
        ProviderSpec("Gemini", "gemini", "gemini-3-pro-preview", "GEMINI_API_KEY", (59, 130, 246)),  # #3b82f6 blue
        ProviderSpec("OpenAI", "openai", "gpt-5.2", "OPENAI_API_KEY", (16, 163, 127)),  # #10a37f teal-green
        ProviderSpec("xAI", "xai", "grok-4-1-fast-reasoning", "XAI_API_KEY", (139, 92, 246)),  # #8b5cf6 violet
    ]

    status_parts = []
    for spec in provider_specs:
        available = os.getenv(spec.env_var)
        mark = "✓ " if available else "✗ "
        status_parts.append(
            click.style(mark + spec.display_name, fg=spec.color if available else (128, 128, 128), dim=not available)
        )
    click.echo(" · ".join(status_parts))

    message_text = " ".join(message or ())
    # Read piped content from stdin if available
    if not sys.stdin.isatty():
        piped_content = sys.stdin.read().strip()
        if piped_content:
            if message_text:
                # Combine piped content with message argument
                message_text = f"{piped_content}\n\n{message_text}"
            else:
                message_text = piped_content
    if not message_text:
        click.echo('Usage: multichat [-c] "your message"', err=True)
        raise SystemExit(1)

    available_specs = [spec for spec in provider_specs if os.getenv(spec.env_var)]
    if not available_specs:
        raise SystemExit(1)

    # Prepare session and messages
    session = _load_session()
    if continue_:
        # In continuation mode, include prior context and system message per model
        session.setdefault("turns", [])
        # Append the new user message to the session before collecting model replies
        session["turns"].append({"role": "user", "content": message_text})

        base_transcript = _render_transcript(session["turns"])  # includes the new user line at the end

        def build_messages_for(spec: ProviderSpec) -> List[Dict[str, str]]:
            system_prompt = (
                f"The user is chatting with you, {spec.model_name}, using an interface that also sends the same "
                "message to other LLMs. Reply with just what you would reply, your name will be automatically "
                "prepended to your response."
            )
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": base_transcript},
            ]
    else:
        # New session: reset and just use a single user message
        session = {"turns": [{"role": "user", "content": message_text}]}

        def build_messages_for(_: ProviderSpec) -> List[Dict[str, str]]:
            return [{"role": "user", "content": message_text}]

    async def call_provider_async(spec: ProviderSpec):
        params: Dict[str, Any] = {
            "model": spec.model_name,
            "provider": spec.provider_name,
            "messages": build_messages_for(spec),
        }
        if spec.provider_name == "anthropic":
            params["max_tokens"] = 8096
        start = time.perf_counter()
        response = await acompletion(**params)
        elapsed = time.perf_counter() - start
        content = response.choices[0].message.content
        return spec.display_name, spec.model_name, elapsed, content, spec.color

    async def run_all():
        async def safe_call(spec: ProviderSpec):
            try:
                display_name, model_name, elapsed, content, color = await call_provider_async(spec)
                return display_name, model_name, elapsed, content, color, None
            except Exception as ex:
                return spec.display_name, spec.model_name, None, None, spec.color, ex

        tasks = [asyncio.create_task(safe_call(spec)) for spec in available_specs]
        collected: List[Tuple[str, str, float, str]] = []
        for task in asyncio.as_completed(tasks):
            display_name, model_name, elapsed, content, color, error = await task
            if error is not None:
                click.secho(f"\n[{display_name}] Error: {error}", fg="red")
            else:
                click.secho(f"\n[{model_name} · {elapsed:.2f}s]", fg=color, bold=True)
                click.secho(content, fg=color)
                collected.append((display_name, model_name, elapsed, content))
        return collected

    # Run all provider calls concurrently via asyncio
    collected_results = asyncio.run(run_all())

    # Update and save the session with model replies
    for _, model_name, _, content in collected_results:
        session["turns"].append({"role": "model", "model": model_name, "content": content})
    _save_session(session)


if __name__ == "__main__":
    main()
