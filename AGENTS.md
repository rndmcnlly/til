# AGENTS.md

Read [README.md](./README.md).

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
