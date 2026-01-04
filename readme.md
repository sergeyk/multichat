# MultiChat

Python CLI tool that sends the same message to multiple LLMs and returns their responses.

Warning: mostly vibe-coded using Codex with GPT-5.

## Usage

### Basic

Make sure to have at least one of `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, or `GEMINI_API_KEY` set in your environment.

For example, you can stick them in your `~/.zshrc` or `~/.bashrc` like so:

```
export ANTHROPIC_API_KEY=
export GEMINI_API_KEY=
export OPENAI_API_KEY=
export XAI_API_KEY=
```

Then, simply run `uvx multichat <message>`!

```
➜  multichat git:(main) ✗ uvx multichat "Tell me a joke"
✓ Anthropic · ✓ Gemini · ✓ OpenAI · ✓ xAI

[claude-opus-4-1 · 2.70s]
Why don't scientists trust atoms?

Because they make up everything! 😄

[gpt-5 · 3.96s]
I started a band called 999 Megabytes—still waiting for a gig.

[grok-4 · 4.71s]
Sure, here's a classic one:

Why don't skeletons fight each other?
They don't have the guts!

Haha, got any favorites of your own? 😊

[gemini-2.5-pro · 9.37s]
Why don't scientists trust atoms?

Because they make up everything
```

### Continuing conversation

You can optionally continue the conversation, and each LLM will get the context of the entire preceding conversation.

```
➜  multichat git:(main) ✗ uvx multichat --continue "Which one is funniest?"
✓ Anthropic · ✓ Gemini · ✓ OpenAI · ✓ xAI

[claude-opus-4-1 · 5.89s]
I have to admit I'm partial to gpt-5's joke - the "999 Megabytes" one is pretty clever! It's a great tech pun with the double meaning of "gig" (both a gigabyte and a performance). Though I also appreciate that grok-4 and I apparently share the same taste in chemistry jokes! 😄

What did you think? Did any of them get a laugh from you?

[grok-4 · 7.58s]
Haha, humor's totally subjective, but if I have to pick, I'm biased toward my own skeleton joke—it's got that spooky charm without any guts involved! What do you think? 😄

[gpt-5 · 9.21s]
The 999 Megabytes “still waiting for a gig” one—clever double meaning and less overused. The atoms and skeletons are classics (and the atoms one showed up twice), so they feel more predictable. Which landed best for you?

[gemini-2.5-pro · 16.18s]
Humor is definitely subjective, but here's my breakdown:

*   **GPT-5's** joke is the most original and clever of the bunch. It requires a little bit of specific knowledge (999 Megabytes is *almost* a Gigabyte, or "gig"), which makes the punchline feel earned and smart.
*   **Claude's and my** atom joke is a certified classic pun. It's a top-tier "dad joke" that's clever because of the wordplay on "make up." The fact that two of us told it shows how popular it is.
*   **Grok-4's** skeleton joke is a timeless, simple classic. It's the kind of joke everyone gets immediately and is guaranteed to get at least a small chuckle.

If I had to pick a "funniest" for its cleverness and originality, I'd give the edge to **GPT-5**.

Which one made you laugh the most?
```

### Piping input

You can also pipe content from stdin instead of passing a positional message:

```
echo "hello" | uvx multichat
```

## Development

When working in this repo, you should run `uv run multichat/main.py` instead of `uvx multichat`.

Run formatting with `uvx ruff format`.
