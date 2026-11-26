# Commit identifiers recorded before the history rewrites

The Git history of this repository was rewritten twice to remove personal data:

- **2026-11-25**: the raw benchmark runs (`runs.jsonl`), which kept the full tool results
  (names of company directors, names and addresses of sole proprietors, from public
  registers), were removed from every commit. Commit signatures were removed at the same
  time, so every commit identifier changed.
- **2026-11-26**: the name and email of one commit's author ("Add benchmark results (M2 Max,
  Olala q5e6)") were replaced by the account's GitHub noreply identity, and an absolute path
  to a home folder was made relative in four `meta.json` files of 2026-11-24. The commit
  "Benchmark results: questions file path made relative in meta.json" now changes nothing.
  The identifiers of that commit and of every later commit changed again.

The files of every commit are otherwise unchanged: tools, scripts, questions, settings,
`summary.md` and `meta.json`. The `meta.json` and `summary.md` files of the runs, and the
documents written before these dates, keep the identifiers recorded at the time. They
correspond to these commits:

| Recorded | Current | Date (UTC) | Commit |
|---|---|---|---|
| `8422176` | `301cf64` | 2026-11-24 12:09 | Add a reproducible benchmark (bench/run.py) |
| `f31ebe4` | `1cc822c` | 2026-11-24 12:30 | Benchmark: check the company search on the filters applied; Strasbourg |
| `729b340` | `fe0aa8a` | 2026-11-24 15:00 | Benchmark: held-out questions; questions file in the summary |
| `3fd3ad1` | `c0ab15f` | 2026-11-24 15:23 | Held-out benchmark: check the company name on "TOTALENERGIES" |
| `1f310a9` | `a9633a3` | 2026-11-24 15:43 | Benchmark: re-apply checks to stored runs; held-out results in README |
| `1bdba5b` | `9df71c4` | 2026-11-24 16:06 | Benchmark results: questions file path made relative in meta.json |
| `f516417` | `9b78830` | 2026-11-24 17:20 | Prepare the comparison with models served by Ollama |
| `40e84e0` | `f2da8cb` | 2026-11-24 17:55 | Benchmark: read the leading fields of a truncated tool result; ignore Modelfiles |
| `fbc1474` | `4ff3fc5` | 2026-11-25 10:57 | Add exploratory qwen3:8b run |
| `ace3195` | `16bb01d` | 2026-11-25 13:23 | Phase 1 results (dev set): q5e6 low/medium/high, q8 low |

In a clone made before 2026-11-25, which still has the recorded commits,
`git diff <recorded> <current>` shows only the removed `runs.jsonl` files.

Runs made from now on record the current identifiers.
