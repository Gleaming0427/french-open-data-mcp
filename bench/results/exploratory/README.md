# Exploratory runs (2026-11-24)

These runs were made while the tools were being adjusted, before `bench/PROTOCOL.md` was
written. The tools, the checks and the questions changed between runs, so the scores are
not comparable with each other, nor with the runs made under the protocol. They are kept
for transparency. The question files used are in this folder. The commit identifiers are
those recorded at the time; [`../COMMITS.md`](../COMMITS.md) gives their current identifiers
after the history rewrites of 2026-11-25 and 2026-11-26.

Machine: MacBook Pro (Mac14,5), Apple M2 Max, 12 CPU cores, 30 GPU cores, 32 GB. Olala
1.0 mini `q5e6` served by OVHcloud's mlx-engine fork (`58083ca`), `reasoning_effort` low,
model card sampling.

| Folder | Model | Code | Questions | Success |
|---|---|---|---|---|
| `20261124-121208` | Olala | tools v1 (`8422176`) | `questions.json` | 12/24 |
| `20261124-132440` | Olala | tools v2 (`f31ebe4`) | `questions.json` | 21/24 |
| `20261124-143946` | Olala | tools v2 (`f31ebe4`) | `questions.json` | 20/24 |
| `20261124-150321` | Olala | interrupted run: 14 of 24 runs, no summary | `questions.json` | 11/14 |
| `20261124-150625` | Olala | tools v3 (`729b340`) | `questions.json` | 23/24 (the tools were adjusted on these questions) |
| `20261124-152301` | Olala | tools v3 (`729b340`) | `questions_holdout.json` | 18/24 as run, 20/24 re-checked (1) |
| `20261124-160832` | Olala | tools v3 (`1bdba5b`) | `questions_holdout2.json` | 37/48 |
| `20261124-173004` | qwen3:8b (Ollama 0.40.6) | tools v3 (`f516417`) | `questions_holdout.json` + `questions_holdout2.json` | 71/72 as run, 72/72 re-checked (2) |

(1) The check of the SIREN question required the whole API name, "TOTALENERGIES SE
(TOTALENERGIE SE)"; it was changed to "TOTALENERGIES" in commit `3fd3ad1`, 22 seconds after
the run started and before its results were known. Both summaries are kept.

(2) The only failure during the run was a correct answer ("1490") whose tool result had been
cut at 8000 characters (the model had asked for 25 companies), which the checks of that time
could not read. The checks were fixed in commit `40e84e0` and re-applied on 2026-11-25
(`summary.md`; the summary written during the run is kept in `summary-as-run.md`). On the
same 72 runs, Olala gave 57/72 re-checked (55 as run), with a median of 13.2 s per question
against 19.6 s for qwen3:8b; qwen3:8b named the source of the data in 63 of 63 answers,
Olala in 34 of 60. The two engines differ (mlx-engine and Ollama), as do the reasoning
settings (Olala low, qwen3 Ollama's default).

## What these runs showed

- Tools v1: the model looked up the right INSEE code, then often passed another code to the
  next tool (twice the example code written in the tool description). Fixed in v2: the tools
  take municipality names.
- Company counts: the model often gave the number of companies listed (5) instead of the
  total, put the activity in the search text, or passed a section letter as a NAF code.
- Arrondissements and half-years: the model asked for the whole city, or for "2026-S2" or
  "2026-01" instead of "2026-S1", and did not retry after the tool's error.
- The model named the source of the data in 34 of the 60 held-out answers where a tool
  returned data; most others named the tool ("source: property_prices").
- Areas DVF does not cover: no invented figure (9/9).

Tools v4 (`bench/PROTOCOL.md`) address these failures: a counting tool, municipality fields
that accept an INSEE code, periods written in words, a section letter given as a NAF code,
instructions to retry after an error that says how to correct the call, and sources listed
by the orchestrator under each answer.
