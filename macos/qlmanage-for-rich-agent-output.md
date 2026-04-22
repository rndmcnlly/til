# `qlmanage -p` for rich agent output

```bash
qlmanage -p /tmp/report.html >/dev/null 2>&1
```

[`qlmanage`](https://ss64.com/mac/qlmanage.html) is macOS's CLI entry to [Quick Look](https://developer.apple.com/documentation/quicklook). The `-p` flag ("debug preview") pops open the same panel you get from hitting space in Finder, and it blocks the calling process until the panel is dismissed (Esc, space, click X, click outside). Process exit is the acknowledgment signal.

> Context: sometimes I want an agent to give me richer output than fits in its own output stream, like the OpenCode TUI. Opening a full browser is heavyweight and clutters tabs. Quick Look is, well, a quick look: and because the call blocks, the agent knows when I'm done reading and can continue.

Write an HTML file, call `qlmanage -p` in the foreground, and the bash tool call returns only after dismissal. HTML, CSS, inline SVG, `<details>`, `@keyframes`, and `:hover` all render. JavaScript is disabled entirely, which is the one real gotcha: build static-but-rich, not interactive.
