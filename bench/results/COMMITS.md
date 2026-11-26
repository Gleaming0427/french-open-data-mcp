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

GitHub kept serving the old commits by their identifier after these rewrites. On
2026-11-26, the GitHub repository was therefore deleted and created again with the same
name, from the rewritten history. The recorded identifiers below no longer exist on GitHub.

The files of every commit are otherwise unchanged: tools, scripts, questions, settings,
`summary.md` and `meta.json`. The files written before these dates keep the identifiers
recorded at the time. Those still referenced in the repository correspond to these commits:

| Recorded | Current | Date (UTC) | Commit | Referenced by |
|---|---|---|---|---|
| `fbc1474` | `4ff3fc5` | 2026-11-25 09:57 | Add exploratory qwen3:8b run | phase 1 results, in `bench/PROTOCOL.md` |
| `ace3195` | `16bb01d` | 2026-11-25 12:23 | Phase 1 results (dev set): q5e6 low/medium/high, q8 low | `20261125-123052` (Olala, phase 2) |
| `bff70a7` | `8364f17` | 2026-11-25 13:19 | Phase 2: Olala q5e6 low, test set | `20261125-132556`, `20261125-134016`, `20261125-134910` (Ollama models, phase 2) |

In a clone made before 2026-11-25, which still has the recorded commits,
`git diff <recorded> <current>` shows only the removed `runs.jsonl` files.

Runs made from now on record the current identifiers.
