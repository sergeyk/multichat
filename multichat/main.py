from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderSpec:
    display_name: str
    provider_name: str
    model_name: str
    env_var: str


def main() -> int:
    import asyncio
    import os
    import sys
    import time

    from any_llm import acompletion

    provider_specs = [
        ProviderSpec("Anthropic", "anthropic", "claude-opus-4-1", "ANTHROPIC_API_KEY"),
        ProviderSpec("Gemini", "google", "gemini-2.5-pro", "GEMINI_API_KEY"),
        ProviderSpec("OpenAI", "openai", "gpt-5", "OPENAI_API_KEY"),
        ProviderSpec("xAI", "xai", "grok-4", "XAI_API_KEY"),
    ]

    print(" · ".join(("✓ " if os.getenv(spec.env_var) else "✗ ") + spec.display_name for spec in provider_specs))
    if len(sys.argv) < 2:
        print('Usage: multichat "your message"')
        return 1

    message_text = " ".join(sys.argv[1:])
    available_specs = [spec for spec in provider_specs if os.getenv(spec.env_var)]
    if not available_specs:
        return 1

    async def call_provider_async(spec: ProviderSpec):
        params = {
            "model": spec.model_name,
            "provider": spec.provider_name,
            "messages": [{"role": "user", "content": message_text}],
        }
        if spec.provider_name == "anthropic":
            params["max_tokens"] = 8096
        start = time.perf_counter()
        response = await acompletion(**params)
        elapsed = time.perf_counter() - start
        return spec.display_name, spec.model_name, elapsed, response

    async def run_all():
        async def safe_call(spec: ProviderSpec):
            try:
                display_name, model_name, elapsed, response = await call_provider_async(spec)
                return display_name, model_name, elapsed, response, None
            except Exception as ex:
                return spec.display_name, spec.model_name, None, None, ex

        tasks = [asyncio.create_task(safe_call(spec)) for spec in available_specs]
        for task in asyncio.as_completed(tasks):
            display_name, model_name, elapsed, response, error = await task
            if error is not None:
                print(f"\n[{display_name}] Error: {error}")
            else:
                print(f"\n[{model_name} · {elapsed:.2f}s]\n{response.choices[0].message.content}")

    # Run all provider calls concurrently via asyncio
    asyncio.run(run_all())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
