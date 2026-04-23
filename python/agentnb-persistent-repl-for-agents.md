# `agentnb` gives coding agents a persistent Python REPL through bash

We were doing incremental analysis of some time-series data, and the agent kept writing fresh scripts that booted Python and re-loaded the CSV from disk on every step. Each follow-up question ("now group by week") paid the full setup cost again. The agent wasn't being careless: bash is a stateless medium, and `python -c` dies with its process. That's just what working through the bash tool looks like, unless you break the frame.

[`agentnb`](https://github.com/oegedijk/agentnb) breaks the frame. It's a CLI wrapping a long-lived [IPython kernel](https://ipython.readthedocs.io/en/stable/), so the namespace survives between bash invocations.

```bash
agentnb --session work "df = pd.read_csv('sales.csv'); df.shape"
agentnb --session work "df['rev'] = df.qty * df.price"
agentnb --session work inspect df          # structured dtypes, nulls, head
agentnb --session work history @last-error
```

`df` is still there on the second call. And the third. The agent stops writing defensive re-loads and starts making smaller moves.

State lives in `<project>/.agentnb/`. Multiple named sessions are supported, each a separate process with an isolated namespace. A per-session mutex refuses concurrent callers with a clear error and the blocking `execution_id`, which is the right failure mode when multiple agents might share a workspace.

Install with [`uv tool install agentnb`](https://docs.astral.sh/uv/guides/tools/). Needs [`ipykernel`](https://pypi.org/project/ipykernel/) in the target env (`uv add --dev ipykernel` for [uv](https://docs.astral.sh/uv/) projects).
