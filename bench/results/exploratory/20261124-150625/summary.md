# Benchmark 2026-11-24T15:06:25+00:00

- Label: Olala q5e6, M2 Max, tools v3
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: Apple M2 Max, 32 GB memory, macOS 27.0.1
- Code: french-open-data-mcp 0.1.0, commit `729b340`
- Questions: `questions.json`, 8 questions
- Runs: 3 per question, 24 in total

**Success: 23/24** (expected tool calls succeeded and the answer contains the tool's figure).

Model output: 25238 tokens in 300 s of model requests, 84.0 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls |
|---|---|---|---|---|---|---|
| municipality-code-beaune | 3/3 | 4.8 | 1 | 0 | 0 | 0 |
| dvf-beaune-apartment-m2 | 3/3 | 11.1 | 1 | 0 | 0 | 0 |
| dvf-dijon-house-m2 | 3/3 | 13.4 | 1 | 0 | 0 | 0 |
| dvf-toulouse-apartment-m2 | 3/3 | 11.7 | 1 | 0 | 0 | 0 |
| dvf-paris-11-apartment-m2 | 3/3 | 22.8 | 1 | 0 | 1 | 0 |
| dvf-strasbourg-not-covered | 3/3 | 11.8 | 1 | 0 | 3 | 0 |
| companies-toulouse-naf-62-02a | 2/3 | 21.6 | 1 | 1 | 0 | 0 |
| company-profile-siren | 3/3 | 14.8 | 1 | 0 | 0 | 0 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| companies-toulouse-naf-62-02a | 2 | answer (expected 1501) | search_companies(text=, municipality=Toulouse, naf_code=62.02A) | Le nombre d'entreprises actives dans la catégorie 62.02A qui possèdent au moins un établissement à Toulouse est de **5**. Source : recherche_companies avec les … |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
