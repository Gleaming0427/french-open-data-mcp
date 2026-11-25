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

### Recorded before phase 2

- Ollama version: (to fill in)
- Tags: (to fill in)

## Conditions

Same Mac (MacBook Pro Mac14,5, Apple M2 Max, 12 CPU cores, 30 GPU cores, 32 GB); one model
server at a time; the label and model server version of each run are recorded in its
`meta.json`.

## Not covered

The Légifrance tools (not tested against the live API). Speeds are not compared across
engines (mlx-engine and Ollama).
