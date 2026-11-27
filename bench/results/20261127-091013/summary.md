# Benchmark 2026-11-27T09:10:13+00:00

- Label: Phase 2: qwen3.5:4b, test
- Model: `qwen3.5-4b-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.2.1
- Model server: ollama version is 0.40.18
- Code: french-open-data-mcp 0.1.0, commit `ad58959`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 114/120 (95%, 95% interval 90%-98%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 15/15 (100%, 95% interval 80%-100%) | 0/15 |
| dvf_town | 13/15 (87%, 95% interval 62%-96%) | 3/15 |
| dvf_arrondissement | 15/15 (100%, 95% interval 80%-100%) | 6/15 |
| dvf_half_year | 13/15 (87%, 95% interval 62%-96%) | 6/15 |
| dvf_not_covered | 14/15 (93%, 95% interval 70%-99%) | 0/6 |
| count_naf | 14/15 (93%, 95% interval 70%-99%) | 8/15 |
| count_section | 15/15 (100%, 95% interval 80%-100%) | 3/15 |
| company_siren | 15/15 (100%, 95% interval 80%-100%) | 2/15 |

Answers naming the source of the data returned: 28/111 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 44132 tokens in 898 s of model requests, 49.1 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 2.2 | 1 | 0 | 0 | 0 | 0/3 |
| t-code-2 | 3/3 | 5.2 | 1 | 0 | 0 | 0 | 0/3 |
| t-code-3 | 3/3 | 5.5 | 1 | 0 | 0 | 0 | 0/3 |
| t-code-4 | 3/3 | 3.0 | 1 | 0 | 0 | 0 | 0/3 |
| t-code-5 | 3/3 | 3.4 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-town-1 | 2/3 | 8.2 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-town-2 | 3/3 | 7.6 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-town-3 | 3/3 | 7.4 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-town-4 | 3/3 | 11.1 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-town-5 | 2/3 | 6.9 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-arrondissement-1 | 3/3 | 10.5 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-arrondissement-2 | 3/3 | 8.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-3 | 3/3 | 7.8 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-arrondissement-4 | 3/3 | 10.3 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-arrondissement-5 | 3/3 | 6.7 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-half-year-1 | 3/3 | 12.3 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-half-year-2 | 2/3 | 8.0 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-half-year-3 | 2/3 | 15.7 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-4 | 3/3 | 8.7 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-half-year-5 | 3/3 | 8.8 | 1 | 0 | 0 | 0 | 2/3 |
| t-not-covered-1 | 3/3 | 18.0 | 2 | 0 | 3 | 0 | 0/2 |
| t-not-covered-2 | 3/3 | 10.4 | 1 | 0 | 4 | 0 | - |
| t-not-covered-3 | 3/3 | 9.1 | 1 | 0 | 3 | 0 | 0/1 |
| t-not-covered-4 | 3/3 | 8.2 | 1 | 0 | 3 | 0 | - |
| t-not-covered-5 | 2/3 | 16.0 | 2 | 0 | 2 | 0 | 0/3 |
| t-count-naf-1 | 2/3 | 9.1 | 1 | 0 | 0 | 0 | 1/3 |
| t-count-naf-2 | 3/3 | 12.1 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-naf-3 | 3/3 | 9.1 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-naf-4 | 3/3 | 8.4 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-naf-5 | 3/3 | 11.4 | 1 | 0 | 0 | 0 | 1/3 |
| t-count-section-1 | 3/3 | 7.7 | 1 | 0 | 0 | 0 | 0/3 |
| t-count-section-2 | 3/3 | 7.0 | 1 | 0 | 0 | 0 | 1/3 |
| t-count-section-3 | 3/3 | 8.0 | 1 | 0 | 0 | 0 | 1/3 |
| t-count-section-4 | 3/3 | 10.1 | 1 | 0 | 0 | 0 | 1/3 |
| t-count-section-5 | 3/3 | 9.5 | 1 | 0 | 0 | 0 | 0/3 |
| t-siren-1 | 3/3 | 5.8 | 1 | 0 | 0 | 0 | 0/3 |
| t-siren-2 | 3/3 | 4.3 | 1 | 0 | 0 | 0 | 0/3 |
| t-siren-3 | 3/3 | 5.8 | 1 | 0 | 0 | 0 | 0/3 |
| t-siren-4 | 3/3 | 7.4 | 1 | 0 | 0 | 0 | 1/3 |
| t-siren-5 | 3/3 | 6.5 | 1 | 0 | 0 | 0 | 1/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| t-dvf-town-1 | 1 | answer (expected 2830) | property_prices(municipality=Tours, period=2025) |  |
| t-dvf-town-5 | 1 | answer (expected 2780) | property_prices(municipality=Caen, period=2024) |  |
| t-dvf-half-year-2 | 2 | answer (expected 2900) | property_prices(municipality=Besançon, period=2026-S1) |  |
| t-dvf-half-year-3 | 3 | answer (expected 2190) | property_prices(municipality=Nîmes, period=2026-S1) |  |
| t-not-covered-5 | 1 | model: HTTP 500: {"error":{"message":"XML syntax error on line 9: unexpected EOF","type":"api_error","param":null,"code":null}}
 | find_municipality(name=Dzaoudzi) | Model error: HTTP 500: {"error":{"message":"XML syntax error on line 9: unexpected EOF","type":"api_error","param":null,"code":null}} |
| t-count-naf-1 | 3 | missing or wrong call: count_companies/search_companies | count_companies(department=51, naf_code=96.02A, include_closed=False) | Il y a **875** entreprises actives dont l'activité principale est la coiffure (code NAF 96.02A) et qui possèdent au moins un établissement à Reims. |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
