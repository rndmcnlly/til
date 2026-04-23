# Today I Learned

Browse at <https://til.adamsmith.as/> · [Atom feed](https://til.adamsmith.as/feed.atom)

<!-- count starts -->6<!-- count ends --> TILs so far.

## How this works

Each TIL is a plain markdown file at `<topic>/<slug>.md`. The first line is a `# Title`. No frontmatter, no config: titles come from the heading, dates come from git history.

On push to main, a GitHub Actions workflow runs `build.py` (a single-file site generator using mistune and `uv run --script`), which renders all `*/*.md` files into static HTML and deploys to GitHub Pages. The README index you're reading now is also auto-updated by the build.

Inspired by [simonw/til](https://github.com/simonw/til).

## Style guide

- **Short posts** suitable for being linked from social media. One pedagogical payload per post.
- **Payload up front.** The thing you'd learn goes first. Context and backstory go below the fold, often in a blockquote.
- **Dense with real links.** Every tool, spec, library, or concept mentioned should link to its actual home on the web. Links are verified, not assumed.
- **Plain blockquotes** for callouts and meta-commentary. No `[!NOTE]` syntax.
- **Topic as directory.** A short noun: `python`, `git`, `macos`, `llms`. Created implicitly by adding a file.
- **First person, not second.** Use `I` for my own judgment calls and opinions, `we` for work an agent and I did together (the transagentic author), and reserve `you` for direct instructions to the reader. Avoid the lecturing second-person default.

<!-- index starts -->
## llms

- [Visual perception testing for VLMs](https://github.com/rndmcnlly/til/blob/main/llms/visual-perception-testing.md) - 2026-04-21
- [Local Parakeet beats hosted for interview-length ASR](https://github.com/rndmcnlly/til/blob/main/llms/local-parakeet-beats-hosted-asr.md) - 2026-04-21
- [A one-shot probe for thinking preservation across turns](https://github.com/rndmcnlly/til/blob/main/llms/testing-thinking-preservation.md) - 2026-04-21

## macos

- [`qlmanage -p` for rich agent output](https://github.com/rndmcnlly/til/blob/main/macos/qlmanage-for-rich-agent-output.md) - 2026-04-22

## python

- [The `uv run --script` pattern](https://github.com/rndmcnlly/til/blob/main/python/uv-run-script-pattern.md) - 2026-04-21
- [`agentnb` gives coding agents a persistent Python REPL through bash](https://github.com/rndmcnlly/til/blob/main/python/agentnb-persistent-repl-for-agents.md) - 2026-04-22

<!-- index ends -->
