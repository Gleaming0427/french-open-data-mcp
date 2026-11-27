# Benchmark 2026-11-27T09:56:42+00:00

- Label: Phase 2: gpt-oss:latest, test
- Model: `gpt-oss-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.2.1
- Model server: ollama version is 0.40.18
- Code: french-open-data-mcp 0.1.0, commit `ad58959`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 120/120 (100%, 95% interval 97%-100%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 15/15 (100%, 95% interval 80%-100%) | 14/15 |
| dvf_town | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_arrondissement | 15/15 (100%, 95% interval 80%-100%) | 14/15 |
| dvf_half_year | 15/15 (100%, 95% interval 80%-100%) | 14/15 |
| dvf_not_covered | 15/15 (100%, 95% interval 80%-100%) | - |
| count_naf | 15/15 (100%, 95% interval 80%-100%) | 14/15 |
| count_section | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| company_siren | 15/15 (100%, 95% interval 80%-100%) | 11/15 |

Answers naming the source of the data returned: 97/105 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 25008 tokens in 735 s of model requests, 34.0 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 3.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-2 | 3/3 | 2.8 | 1 | 0 | 0 | 0 | 2/3 |
| t-code-3 | 3/3 | 3.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-4 | 3/3 | 3.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-5 | 3/3 | 2.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-1 | 3/3 | 7.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-2 | 3/3 | 8.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-3 | 3/3 | 7.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-4 | 3/3 | 8.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-5 | 3/3 | 7.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-1 | 3/3 | 7.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-2 | 3/3 | 10.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-3 | 3/3 | 7.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-4 | 3/3 | 7.7 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-arrondissement-5 | 3/3 | 7.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-1 | 3/3 | 6.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-2 | 3/3 | 6.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-3 | 3/3 | 8.0 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-4 | 3/3 | 7.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-5 | 3/3 | 7.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-not-covered-1 | 3/3 | 5.9 | 1 | 0 | 3 | 0 | - |
| t-not-covered-2 | 3/3 | 7.1 | 1 | 0 | 3 | 0 | - |
| t-not-covered-3 | 3/3 | 9.6 | 1 | 0 | 2 | 0 | - |
| t-not-covered-4 | 3/3 | 8.8 | 1 | 0 | 3 | 0 | - |
| t-not-covered-5 | 3/3 | 7.8 | 1 | 0 | 2 | 0 | - |
| t-count-naf-1 | 3/3 | 7.0 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-naf-2 | 3/3 | 8.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-3 | 3/3 | 7.5 | 1 | 0 | 1 | 0 | 3/3 |
| t-count-naf-4 | 3/3 | 7.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-5 | 3/3 | 4.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-1 | 3/3 | 5.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-2 | 3/3 | 5.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-3 | 3/3 | 4.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-4 | 3/3 | 4.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-5 | 3/3 | 6.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-1 | 3/3 | 8.3 | 1 | 0 | 0 | 0 | 2/3 |
| t-siren-2 | 3/3 | 6.6 | 1 | 0 | 0 | 0 | 1/3 |
| t-siren-3 | 3/3 | 4.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-4 | 3/3 | 5.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-5 | 3/3 | 6.8 | 1 | 0 | 0 | 0 | 2/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

Memory used by the model server: not measured by this script (read it in Activity Monitor).
