# MultiChat

Python CLI tool that sends the same message to multiple LLMs and returns their responses.

## Usage

Make sure to have at least one of `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, or `GEMINI_API_KEY` set in your environment.

```
➜  multichat git:(main) ✗ uv run multichat "Tell me a joke"
✓ Anthropic · ✓ Gemini · ✓ OpenAI · ✓ xAI

[claude-opus-4-1 · 2.54s]
Why don't scientists trust atoms?

Because they make up everything! 😄

[grok-4 · 3.64s]
Sure, here's a classic one:

Why don't skeletons fight each other?
They don't have the guts!

Haha, got any favorites you'd like to share? 😊

[gpt-5 · 7.34s]
Parallel lines have so much in common. It’s a shame they’ll never meet.

[gemini-2.5-pro · 14.65s]
I'm reading a book on anti-gravity.

It’s impossible to put down.
```
