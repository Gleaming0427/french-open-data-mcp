# Benchmark 2026-11-27T07:05:06+00:00

- Label: Phase 2: qwen3:4b, test
- Model: `qwen3-4b-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.2.1
- Model server: ollama version is 0.40.18
- Code: french-open-data-mcp 0.1.0, commit `ad58959`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 118/120 (98%, 95% interval 94%-100%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 15/15 (100%, 95% interval 80%-100%) | 14/15 |
| dvf_town | 14/15 (93%, 95% interval 70%-99%) | 14/15 |
| dvf_arrondissement | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_half_year | 14/15 (93%, 95% interval 70%-99%) | 13/15 |
| dvf_not_covered | 15/15 (100%, 95% interval 80%-100%) | 4/4 |
| count_naf | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| count_section | 15/15 (100%, 95% interval 80%-100%) | 14/15 |
| company_siren | 15/15 (100%, 95% interval 80%-100%) | 15/15 |

Answers naming the source of the data returned: 104/109 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 268705 tokens in 6271 s of model requests, 42.8 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 10.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-2 | 3/3 | 14.3 | 1 | 0 | 0 | 0 | 2/3 |
| t-code-3 | 3/3 | 10.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-4 | 3/3 | 12.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-5 | 3/3 | 11.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-1 | 3/3 | 43.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-2 | 3/3 | 89.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-3 | 3/3 | 51.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-4 | 2/3 | 67.2 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-town-5 | 3/3 | 33.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-1 | 3/3 | 57.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-2 | 3/3 | 32.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-3 | 3/3 | 52.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-4 | 3/3 | 55.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-5 | 3/3 | 43.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-1 | 2/3 | 180.8 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-half-year-2 | 3/3 | 92.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-3 | 3/3 | 63.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-4 | 3/3 | 43.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-5 | 3/3 | 33.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-not-covered-1 | 3/3 | 101.5 | 1 | 0 | 3 | 0 | 1/1 |
| t-not-covered-2 | 3/3 | 88.0 | 1 | 0 | 2 | 0 | - |
| t-not-covered-3 | 3/3 | 104.9 | 1 | 0 | 3 | 0 | 1/1 |
| t-not-covered-4 | 3/3 | 93.2 | 1 | 0 | 3 | 0 | - |
| t-not-covered-5 | 3/3 | 96.6 | 2 | 0 | 3 | 0 | 2/2 |
| t-count-naf-1 | 3/3 | 45.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-2 | 3/3 | 42.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-3 | 3/3 | 44.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-4 | 3/3 | 57.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-5 | 3/3 | 56.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-1 | 3/3 | 67.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-2 | 3/3 | 58.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-3 | 3/3 | 45.7 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-section-4 | 3/3 | 47.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-5 | 3/3 | 48.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-1 | 3/3 | 25.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-2 | 3/3 | 18.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-3 | 3/3 | 19.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-4 | 3/3 | 28.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-5 | 3/3 | 21.8 | 1 | 0 | 0 | 0 | 3/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| t-dvf-town-4 | 3 | answer (expected 2220) | property_prices(municipality=Perpignan, period=2025) | [answer truncated: token limit reached] |
| t-dvf-half-year-1 | 1 | answer (expected 2520) | property_prices(municipality=Orléans, period=2026-S1) | [answer truncated: token limit reached] |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
