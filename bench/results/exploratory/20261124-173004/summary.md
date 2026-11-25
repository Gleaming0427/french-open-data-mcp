# Benchmark 2026-11-24T17:30:04+00:00

- Label: qwen3:8b (Ollama), M2 Max, held-out 1+2
- Model: `qwen3-8b-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: ollama version is 0.40.6
- Code: french-open-data-mcp 0.1.0, commit `f516417`
- Questions: `questions_holdout.json`, `questions_holdout2.json`, 24 questions
- Runs: 3 per question, 72 in total
- Checks re-applied on 2026-11-25T09:59:14+00:00 with `questions_holdout.json, questions_holdout2.json` (commit `fbc1474`) to 72 stored runs; the summary written during the run is kept in summary-as-run.md

**Success: 72/72 (100%, 95% interval 95%-100%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

Answers naming the source of the data returned: 63/63 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 38587 tokens in 1342 s of model requests, 28.7 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| municipality-code-montpellier | 3/3 | 9.4 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-nantes-apartment-m2-2024 | 3/3 | 17.9 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-bordeaux-house-m2 | 3/3 | 16.9 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-marseille-8-apartment-m2 | 3/3 | 19.9 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-lyon-3-apartment-m2-2024 | 3/3 | 21.0 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-metz-not-covered | 3/3 | 17.3 | 1 | 0 | 2 | 0 | - |
| companies-bordeaux-naf-56-10a | 3/3 | 28.4 | 1 | 0 | 0 | 0 | 3/3 |
| company-name-siren | 3/3 | 22.6 | 1 | 0 | 0 | 0 | 3/3 |
| municipality-code-rennes | 3/3 | 10.3 | 1 | 0 | 0 | 0 | 3/3 |
| municipality-code-grenoble | 3/3 | 12.2 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-lille-apartment-m2 | 3/3 | 17.8 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-rennes-house-m2-2024 | 3/3 | 17.0 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-nice-apartment-m2 | 3/3 | 25.5 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-angers-house-m2 | 3/3 | 22.7 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-paris-15-apartment-m2-2024 | 3/3 | 21.4 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-lyon-7-apartment-m2 | 3/3 | 25.7 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-marseille-13-house-m2 | 3/3 | 21.8 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-grenoble-apartment-m2-2026-s1 | 3/3 | 27.0 | 1 | 0 | 0 | 0 | 3/3 |
| dvf-colmar-not-covered | 3/3 | 22.0 | 1 | 0 | 2 | 0 | - |
| dvf-mamoudzou-not-covered | 3/3 | 9.4 | 0 | 0 | 0 | 0 | - |
| companies-nantes-naf-10-71c | 3/3 | 25.0 | 1 | 0 | 0 | 0 | 3/3 |
| companies-grenoble-section-j | 3/3 | 23.8 | 1 | 0 | 0 | 0 | 3/3 |
| company-profile-naf-380129866 | 3/3 | 17.2 | 1 | 0 | 0 | 0 | 3/3 |
| company-name-441639465 | 3/3 | 20.2 | 1 | 0 | 0 | 0 | 3/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

Memory used by the model server: not measured by this script (read it in Activity Monitor).
