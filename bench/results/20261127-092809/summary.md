# Benchmark 2026-11-27T09:28:09+00:00

- Label: Phase 2: gemma4:latest, test
- Model: `gemma4-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.2.1
- Model server: ollama version is 0.40.18
- Code: french-open-data-mcp 0.1.0, commit `ad58959`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 117/120 (98%, 95% interval 93%-99%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_town | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| dvf_arrondissement | 14/15 (93%, 95% interval 70%-99%) | 14/14 |
| dvf_half_year | 13/15 (87%, 95% interval 62%-96%) | 13/13 |
| dvf_not_covered | 15/15 (100%, 95% interval 80%-100%) | - |
| count_naf | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| count_section | 15/15 (100%, 95% interval 80%-100%) | 15/15 |
| company_siren | 15/15 (100%, 95% interval 80%-100%) | 15/15 |

Answers naming the source of the data returned: 102/102 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 51582 tokens in 1563 s of model requests, 33.0 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 8.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-2 | 3/3 | 3.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-3 | 3/3 | 3.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-4 | 3/3 | 5.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-5 | 3/3 | 8.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-1 | 3/3 | 14.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-2 | 3/3 | 9.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-3 | 3/3 | 16.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-4 | 3/3 | 14.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-5 | 3/3 | 12.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-1 | 3/3 | 17.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-2 | 3/3 | 14.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-3 | 2/3 | 14.8 | 1 | 0 | 0 | 0 | 2/2 |
| t-dvf-arrondissement-4 | 3/3 | 24.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-5 | 3/3 | 14.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-1 | 2/3 | 12.6 | 1 | 0 | 0 | 0 | 2/2 |
| t-dvf-half-year-2 | 2/3 | 17.9 | 1 | 0 | 0 | 0 | 2/2 |
| t-dvf-half-year-3 | 3/3 | 15.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-4 | 3/3 | 13.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-5 | 3/3 | 13.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-not-covered-1 | 3/3 | 12.2 | 1 | 0 | 3 | 0 | - |
| t-not-covered-2 | 3/3 | 15.9 | 1 | 0 | 3 | 0 | - |
| t-not-covered-3 | 3/3 | 12.4 | 1 | 0 | 3 | 0 | - |
| t-not-covered-4 | 3/3 | 20.1 | 1 | 0 | 2 | 0 | - |
| t-not-covered-5 | 3/3 | 19.4 | 1 | 0 | 3 | 0 | - |
| t-count-naf-1 | 3/3 | 14.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-2 | 3/3 | 15.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-3 | 3/3 | 14.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-4 | 3/3 | 16.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-5 | 3/3 | 19.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-1 | 3/3 | 12.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-2 | 3/3 | 14.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-3 | 3/3 | 15.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-4 | 3/3 | 12.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-5 | 3/3 | 15.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-1 | 3/3 | 11.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-2 | 3/3 | 9.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-3 | 3/3 | 9.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-4 | 3/3 | 10.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-5 | 3/3 | 10.0 | 1 | 0 | 0 | 0 | 3/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| t-dvf-arrondissement-3 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Les données sur les prix immobiliers ne sont pas disponibles pour l'année 2025. |
| t-dvf-half-year-1 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Les données de prix immobiliers sont basées sur des ventes passées et ne peuvent pas fournir d'estimation pour une date aussi éloignée que le premier semestre 2… |
| t-dvf-half-year-2 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne dispose pas de données officielles de prix immobiliers pour le premier semestre 2026, car il s'agit d'une date future. Je ne peux fournir que des données … |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
