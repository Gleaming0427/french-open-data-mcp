# Benchmark 2026-11-24T13:24:40+00:00

- Label: Olala q5e6, MacBook Pro M2 Max, tools v2
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: Apple M2 Max, 32 GB memory, macOS 27.0.1
- Code: french-open-data-mcp 0.1.0, commit `f31ebe4`
- Runs: 3 per question, 24 in total

**Success: 21/24** (expected tool calls succeeded and the answer contains the tool's figure).

Model output: 22718 tokens in 262 s of model requests, 86.6 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls |
|---|---|---|---|---|---|---|
| municipality-code-beaune | 3/3 | 5.6 | 1 | 0 | 0 | 0 |
| dvf-beaune-apartment-m2 | 3/3 | 14.5 | 1 | 0 | 0 | 0 |
| dvf-dijon-house-m2 | 3/3 | 13.3 | 1 | 0 | 0 | 0 |
| dvf-toulouse-apartment-m2 | 3/3 | 11.7 | 1 | 0 | 0 | 0 |
| dvf-paris-11-apartment-m2 | 3/3 | 14.4 | 1 | 0 | 0 | 0 |
| dvf-strasbourg-not-covered | 3/3 | 11.1 | 1 | 0 | 3 | 0 |
| companies-toulouse-naf-62-02a | 0/3 | 15.8 | 0 | 0 | 0 | 0 |
| company-profile-siren | 3/3 | 14.4 | 2 | 0 | 0 | 0 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| companies-toulouse-naf-62-02a | 1 | answer (expected 1501) | search_companies(naf_code=62.02A, municipality=Toulouse) | Il y a 4 entreprises actives répondant à ces critères. Cette information provient de la recherche : les résultats renseignent 4 entreprises actives avec le NAF … |
| companies-toulouse-naf-62-02a | 2 | missing or wrong call: search_companies; answer (no successful search_companies call) | none | Je ne peux pas déterminer le nombre d’entreprises actives qui répondent à ces critères sans filtrer spécifiquement le code NAF 62.02A. Les outils disponibles ne… |
| companies-toulouse-naf-62-02a | 3 | missing or wrong call: search_companies; answer (no successful search_companies call) | none | Je ne peux pas déterminer le nombre d'entreprises avec le code NAF 62.02A et un établissement à Toulouse à partir des outils disponibles. L’outil de recherche n… |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
