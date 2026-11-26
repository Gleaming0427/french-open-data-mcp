# Benchmark 2026-11-25T13:49:10+00:00

- Label: Phase 2: qwen3:8b, test
- Model: `qwen3-8b-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: ollama version is 0.40.6
- Code: french-open-data-mcp 0.1.0, commit `bff70a7`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 120/120 (100%, 95% interval 97%-100%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_town | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_arrondissement | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_half_year | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_not_covered | 15/15 (100%, 95% interval 80%-100%) | - |
| count_naf | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| count_section | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| company_siren | 15/15 (100%, 95% interval 80%-100%) | 15/15 |

Answers naming the source of the data returned: 105/105 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 73105 tokens in 2955 s of model requests, 24.7 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 20.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-2 | 3/3 | 12.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-3 | 3/3 | 14.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-4 | 3/3 | 14.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-5 | 3/3 | 14.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-1 | 3/3 | 22.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-2 | 3/3 | 21.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-3 | 3/3 | 30.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-4 | 3/3 | 25.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-5 | 3/3 | 28.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-1 | 3/3 | 26.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-2 | 3/3 | 30.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-3 | 3/3 | 26.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-4 | 3/3 | 22.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-5 | 3/3 | 28.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-1 | 3/3 | 27.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-2 | 3/3 | 32.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-3 | 3/3 | 25.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-4 | 3/3 | 31.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-5 | 3/3 | 27.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-not-covered-1 | 3/3 | 27.8 | 1 | 0 | 3 | 0 | - |
| t-not-covered-2 | 3/3 | 28.3 | 1 | 0 | 3 | 0 | - |
| t-not-covered-3 | 3/3 | 23.8 | 1 | 0 | 3 | 0 | - |
| t-not-covered-4 | 3/3 | 21.9 | 1 | 0 | 3 | 0 | - |
| t-not-covered-5 | 3/3 | 14.7 | 0 | 0 | 1 | 0 | - |
| t-count-naf-1 | 3/3 | 28.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-2 | 3/3 | 27.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-3 | 3/3 | 37.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-4 | 3/3 | 28.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-5 | 3/3 | 24.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-1 | 3/3 | 28.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-2 | 3/3 | 22.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-3 | 3/3 | 21.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-4 | 3/3 | 34.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-5 | 3/3 | 24.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-1 | 3/3 | 22.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-2 | 3/3 | 23.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-3 | 3/3 | 24.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-4 | 3/3 | 22.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-5 | 3/3 | 26.4 | 1 | 0 | 0 | 0 | 3/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

Memory used by the model server: not measured by this script (read it in Activity Monitor).
