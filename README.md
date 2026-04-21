# Today I Learned

Browse at <https://til.adamsmith.as/> · [Atom feed](https://til.adamsmith.as/feed.atom)

<!-- count starts -->1<!-- count ends --> TILs so far.

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

<!-- index starts -->
## python

- [The `uv run --script` pattern](https://github.com/rndmcnlly/til/blob/main/python/uv-run-script-pattern.md) - 2026-04-21

<!-- index ends -->
