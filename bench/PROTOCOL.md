# Benchmark protocol (version 1)

Written on 2026-11-24, before any run with the tools of this version. It fixes what is
measured, how, and what may not change once the test runs have started.

## Purpose

Measure how reliably a local model answers questions on French public data with the tools
of this project, and compare Olala 1.0 mini with other local models on the same machine.

## What is frozen

- **Code**: tools, instructions and orchestrator "v4", as of the commit that adds this file
  (default system prompt, tool descriptions, `max_turns` 6, `max_tool_calls` 10,
  `max_result_chars` 8000), and the checks of `bench/run.py` at that commit.
- **Development set**, `bench/questions_dev.json` (32 questions): the questions of the
  exploratory runs, with the checks of this version. It may be used to choose settings. A
  score on it is not a measure of reliability.
- **Test set**, `bench/questions_test.json` (40 questions, 8 categories of 5: municipality
  code, DVF for a town, DVF for an arrondissement, DVF for a half-year, area DVF does not
  cover, company count by NAF code, company count by activity section, company identity
  from a SIREN). Written before any run with this version. Every question must pass
  `python -m bench.run --validate --questions bench/questions_test.json` before the first
  model run; a question that fails is corrected or removed before that run, never after.
  It is never used to choose a setting or to change the tools.

Any change to the tools, instructions, checks or test questions after the first test run
starts a new protocol version with a new test set. Results of different versions are not
pooled.

## Success criterion (one run of one question)

- the expected tool call succeeded and returned the expected data (for DVF: the right
  municipality and period; for counts: the right filters; for companies: the right SIREN),
  whichever of the equally valid tools listed in the question was used;
- the answer contains the figure the tool returned in that run (or the expected text, or
  no euro amount where DVF has no data);
- the model did not fail (error, or no answer within `max_turns`).

## What is reported

- Success with a 95% Wilson interval, overall and by category. The runs of one question are
  not independent, so the real uncertainty is larger than the interval.
- Whether the answer names the source of the data (keyword check, not part of the
  criterion), unneeded, failed and repeated tool calls, median time per question, output
  tokens and tokens/s end to end (prompt processing included).
- Runs hit by a public API error (network, HTTP 429 or 5xx): shown separately, but kept in
  the totals.
- Memory used by the model server: read in Activity Monitor and reported by hand.
- Every run is published in `bench/results/`, including interrupted runs and the settings
  that were not chosen.
  Added on 2026-11-26: since 2026-11-25, the published files of a run are `summary.md`
  and `meta.json`. The raw runs (`runs.jsonl`) were removed from the repository and from
  the history of its branches, because they keep the full tool results, which include
  personal data from public registers (names of company directors, names and addresses of
  sole proprietors). This changes neither the measurements nor the checks.

## Phase 1: settings of Olala (development set only)

Fixed: Olala-v1.0-mini-7A1B served by OVHcloud's mlx-engine fork (`58083ca`) with
`--context-length 8192`, sampling of the model card (temperature 0.8, top_p 0.9, top_k 40).

Candidates, 2 runs per question (64 runs each):

1. `q5e6`, `reasoning_effort` low
2. `q5e6`, `reasoning_effort` medium (the default, according to the model card)
3. `q5e6`, `reasoning_effort` high (the level used for the model card's scores)
4. `q8`, with the `reasoning_effort` chosen among 1 to 3

Rule: the candidate with the highest success is chosen. If two candidates are within 2 runs
of each other, the one with the lower median time per question is chosen.

## Phase 2: test set

3 runs per question (120 runs) for each model:

- Olala with the settings chosen in phase 1;
- `qwen3:8b`, `qwen3:4b` and `qwen3:1.7b` served by Ollama;
- two Mistral AI models served by Ollama, as European points of comparison: Mistral 7B
  Instruct v0.3, and Ministral 3 8B in its instruct variant if Ollama offers one (Olala's
  model card scored the reasoning variant, 42.0 on BFCL V3, against 48.2 for Mistral 7B v0.3
  and 59.6 for Olala).

The Ollama models run with Ollama's default sampling and thinking and a context of 8192
tokens (a model created with `PARAMETER num_ctx 8192`). They are not tuned. Their exact
Ollama tags were not checked when this protocol was written (ollama.com could not be reached
from the session that wrote it): before phase 2 starts, each tag is confirmed with
`ollama pull`; a missing model is replaced by the closest available version, and the tags
used are recorded below.

### Recorded before phase 2 (2026-11-25, before any run on the test set)

**Phase 1 results** (development set, 64 runs each, commit `fbc1474`, folders in `bench/results/`):

| Setting | Folder | Success | Median time per run | Output tokens per question |
|---|---|---|---|---|
| `q5e6`, reasoning low | `20261125-100314` | 60/64 | 15.5 s | 1,248 |
| `q5e6`, reasoning medium | `20261125-102329` | 61/64 | 20.3 s | 1,801 |
| `q5e6`, reasoning high | `20261125-110218` | 56/64 | 29.0 s | 2,678 |
| `q8`, reasoning low | `20261125-115439` | 58/64 | 15.6 s | 1,252 |

Rule applied: medium has the highest success (61); low is within 2 runs (60) and faster
(15.5 s against 20.3 s); high and q8 are more than 2 runs behind. **Chosen for phase 2:
`q5e6`, reasoning low.** Not taken into account by the rule, and reported here: among their
failed runs, low gave two answers with an invented fact (a price per m² for Paris 15th with
no tool result; "Marseille has 7 arrondissements"), medium gave none.

**Ollama**: version 0.40.6. Models as installed (`ollama list`, `ollama show`):

| Tag | ID | Size | Notes |
|---|---|---|---|
| `qwen3:8b` | `500a1f067a9f` | 5.2 GB | |
| `qwen3:4b` | `359d7dd4bcda` | 2.5 GB | |
| `qwen3:1.7b` | `8f68893c685c` | 1.4 GB | |
| `mistral:7b` | `6577803aa9a0` | 4.4 GB | 7.2B parameters, Q4_K_M, capabilities completion and tools; Ollama does not display the version (v0.3 is likely: the first Mistral 7B version with tool calling) |
| `ministral-3:8b` | `1922accd5827` | 6.0 GB | 8.9B parameters, Q4_K_M, capabilities completion, vision and tools, no thinking capability listed (instruct variant); default temperature 0.15 |

Each runs through a model created with `PARAMETER num_ctx 8192` (`qwen3-8b-ctx8k`,
`qwen3-4b-ctx8k`, `qwen3-1.7b-ctx8k`, `mistral-7b-ctx8k`, `ministral-3-8b-ctx8k`). The Ollama
models are 4-bit quantizations (Q4_K_M where displayed), more compressed than Olala's `q5e6`
(5.76 bits per weight according to its MLX model card).

## Conditions

Same Mac (MacBook Pro Mac14,5, Apple M2 Max, 12 CPU cores, 30 GPU cores, 32 GB); one model
server at a time; the label and model server version of each run are recorded in its
`meta.json`.

The commit identifiers in this file and in the results are those recorded at the time. The
history was rewritten afterwards to remove personal data; `bench/results/COMMITS.md` gives
the current identifier of each.

## Not covered

The Légifrance tools (not tested against the live API). Speeds are not compared across
engines (mlx-engine and Ollama).
