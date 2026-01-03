import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class ProviderSpec:
    provider_display_name: str
    provider_name: str
    model_display_name: str
    model_name: str
    env_var: str


def get_provider_specs() -> List[ProviderSpec]:
    """Get the list of provider specifications."""
    return [
        ProviderSpec(
            "Anthropic",
            "anthropic",
            "Claude Opus 4.5",
            "claude-opus-4-5",
            "ANTHROPIC_API_KEY",
        ),
        ProviderSpec("Gemini", "gemini", "Gemini 3 Pro", "gemini-3-pro-preview", "GEMINI_API_KEY"),
        ProviderSpec("OpenAI", "openai", "GPT-5.2", "gpt-5.2", "OPENAI_API_KEY"),
        ProviderSpec("xAI", "xai", "Grok 4.1", "grok-4.1-thinking", "XAI_API_KEY"),
    ]


def extract_chunk_content(chunk: Any) -> str:
    """Extract content text from a streaming chunk in a tolerant way."""
    try:
        choices = getattr(chunk, "choices", None) or (chunk.get("choices") if isinstance(chunk, dict) else None)
        if not choices:
            return ""
        first = choices[0]
        delta = getattr(first, "delta", None) or (first.get("delta") if isinstance(first, dict) else None)
        if delta is None:
            return ""
        return getattr(delta, "content", None) or (delta.get("content") if isinstance(delta, dict) else "") or ""
    except Exception:
        return ""


async def run_text_mode(
    available_specs: List[ProviderSpec],
    missing_specs: List[ProviderSpec],
    build_messages_for,
) -> List[Tuple[str, str, float, str]]:
    """Run in plain text mode without UI panels."""
    from any_llm import acompletion

    # Show missing providers
    for spec in missing_specs:
        print(f"{spec.model_display_name}: {spec.env_var} missing")

    if not available_specs:
        return []

    async def process_provider(spec: ProviderSpec) -> Tuple[str, str, float, str]:
        start_time = time.perf_counter()

        params: Dict[str, Any] = {
            "model": spec.model_name,
            "provider": spec.provider_name,
            "messages": build_messages_for(spec),
            "stream": False,
        }
        if spec.provider_name == "anthropic":
            params["max_tokens"] = 8096

        try:
            response = await acompletion(**params)
            content = response.choices[0].message.content  # type: ignore[assignment]

            elapsed = time.perf_counter() - start_time
            print(f"--- {spec.model_display_name} ({elapsed:.2f}s) ---")
            print(content)
            print()

            return (spec.provider_display_name, spec.model_name, elapsed, content)

        except Exception as ex:
            elapsed = time.perf_counter() - start_time
            print(f"--- {spec.model_display_name} Error: {ex} ---\n")
            return (spec.provider_display_name, spec.model_name, elapsed, "")

    # Run all providers concurrently and collect results
    tasks = [asyncio.create_task(process_provider(spec)) for spec in available_specs]
    results = await asyncio.gather(*tasks)

    return results
