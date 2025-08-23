# MultiChat

Python CLI tool that sends the same message to multiple LLMs and returns their responses.

## Usage

Make sure to have at least one of the following API keys in your environment:

```bash
OPENAI_API_KEY
ANTHROPIC_API_KEY
XAI_API_KEY
GEMINI_API_KEY
```

```bash
➜  multichat git:(main) ✗ uvx multichat "Tell me a joke"
✅ Anthropic · ✅ Gemini · ✅ OpenAI · ✅ xAI

[claude-opus-4-1 · 2.94s]
Why don't scientists trust atoms?

Because they make up everything! 😄

[grok-4 · 3.51s]
Why don't skeletons fight each other?

They don't have the guts! 😄

[gpt-5 · 4.98s]
Why don’t scientists trust atoms? Because they make up everything.

Want another—any preference (dad joke, tech, dark, pun)?

[gemini-2.5-pro · 10.33s]
Why don't scientists trust atoms?

Because they make up everything
```
