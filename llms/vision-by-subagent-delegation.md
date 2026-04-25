# Giving a text-only agent eyes via a cheap vision subagent

A text-only model like [Z.ai GLM 5.1](https://z.ai/) can still "see" images if you give it a locked-down vision subagent to delegate to. In [OpenCode](https://opencode.ai), this is a ~10-line agent definition.

`~/.config/opencode/agents/vision.md`:

```markdown
---
mode: subagent
description: A read-only, vision-capable subagent available to answer
  questions about local image files without crowding the main agent's
  context or requiring the main agent to have multi-modal capabilities.
model: openrouter/google/gemma-4-26b-a4b-it
permission:
  "*": deny
  read: allow
  glob: allow
---
```

The main agent hands off a file path (or a directory, thanks to `glob`), the subagent describes the image in text, and that description lands back in the main context. No image bytes ever enter the main model's context window.

> We landed on `read` + `glob` as the full toolkit. `read` covers both file reads and directory listings. `glob` lets the subagent resolve a task like "describe the photos in this directory" without the main agent having to enumerate first. Everything else (bash, edit, write, webfetch, grep, task) is either unsafe or irrelevant for a pure perception role. `question` is structurally unsuitable for subagents: they shouldn't interrupt the user.

The broader move is worth naming: **specialized subagents with minimal permissions let you compose capabilities the main model lacks, without paying for them on every turn.** Vision is the obvious first case, but the same shape works for anything expensive or modality-specific.
