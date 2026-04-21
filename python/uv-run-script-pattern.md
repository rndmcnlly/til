# The `uv run --script` pattern

`uv run --script` lets you run a Python script that declares its own dependencies inline using PEP 723 metadata. No virtualenv, no `pip install`, no `requirements.txt`.

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mistune>=3.0",
# ]
# ///

import mistune
print(mistune.create_markdown()("**bold**"))
```

Run it with `uv run script.py`. uv resolves and caches the deps automatically. The `# ///` markers are a TOML block that uv parses before execution.

This is ideal for single-file tools and build scripts where you want zero setup friction.
