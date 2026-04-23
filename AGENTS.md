# AGENTS.md

Read [README.md](./README.md) for what the site is. This file is for authoring new posts.

## Style guide

- **Short posts** suitable for being linked from social media. One pedagogical payload per post.
- **Payload up front.** The thing you'd learn goes first. Context and backstory go below the fold, often in a blockquote.
- **Dense with real links.** Every tool, spec, library, or concept mentioned should link to its actual home on the web. Links are verified, not assumed.
- **Plain blockquotes** for callouts and meta-commentary. No `[!NOTE]` syntax (mistune v3 doesn't render it).
- **Topic as directory.** A short noun: `python`, `git`, `macos`, `llms`. Created implicitly by adding a file.
- **First person, not second.** Use `I` for my own judgment calls and opinions, `we` for work an agent and I did together (the transagentic author), and reserve `you` for direct instructions to the reader. Avoid the lecturing second-person default.
- **No frontmatter.** Title comes from the first `# heading`. Dates come from git history.

## Publishing flow: expect to rebase

The GitHub Actions build regenerates the README index on every push, so a freshly-pushed commit from the bot will almost always be sitting on `origin/main` by the time you try to push your TIL. Another machine (or another agent) may also have posted a TIL since you last pulled.

Expected flow:

1. Write your post, commit locally (including your local README regeneration if you ran `uv run build.py`).
2. `git push` will often fail fast-forward.
3. `git pull --rebase` will conflict on `README.md` because both sides touched the index.
4. Resolve by taking the remote's README and letting the bot regenerate after your push:
   ```bash
   git checkout --theirs README.md
   git add README.md
   GIT_EDITOR=true git rebase --continue
   git push
   ```

`GIT_EDITOR=true` skips the commit-message editor that would otherwise hang a non-interactive shell. Don't try to hand-merge README: the bot's version will be authoritative within seconds of your push anyway.
