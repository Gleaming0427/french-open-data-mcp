# Benchmark 2026-11-24T14:39:46+00:00

- Label: Olala q5e6, MacBook Pro M2 Max, tools v2
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: Apple M2 Max, 32 GB memory, macOS 27.0.1
- Code: french-open-data-mcp 0.1.0, commit `f31ebe4`
- Runs: 3 per question, 24 in total

**Success: 20/24** (expected tool calls succeeded and the answer contains the tool's figure).

Model output: 26514 tokens in 301 s of model requests, 88.0 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls |
|---|---|---|---|---|---|---|
| municipality-code-beaune | 3/3 | 12.7 | 1 | 0 | 0 | 0 |
| dvf-beaune-apartment-m2 | 3/3 | 12.1 | 1 | 0 | 0 | 0 |
| dvf-dijon-house-m2 | 3/3 | 21.3 | 1 | 0 | 0 | 0 |
| dvf-toulouse-apartment-m2 | 3/3 | 11.7 | 1 | 0 | 0 | 0 |
| dvf-paris-11-apartment-m2 | 2/3 | 36.5 | 2 | 0 | 2 | 0 |
| dvf-strasbourg-not-covered | 3/3 | 14.9 | 1 | 0 | 2 | 0 |
| companies-toulouse-naf-62-02a | 0/3 | 13.5 | 1 | 0 | 0 | 0 |
| company-profile-siren | 3/3 | 9.4 | 2 | 0 | 1 | 0 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| dvf-paris-11-apartment-m2 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | find_municipality(name=Paris) > property_prices(municipality=Paris, period=2025) ERROR | Je ne peux pas déterminer le prix médian pour le 11e arrondissement de Paris en 2025 avec les outils disponibles. |
| companies-toulouse-naf-62-02a | 1 | answer (expected 1501) | search_companies(naf_code=62.02A, municipality=Toulouse) | Il existe 5 entreprises actives ayant pour activité principale le conseil en systèmes et logiciels informatiques (code NAF 62.02A) et au moins un établissement … |
| companies-toulouse-naf-62-02a | 2 | answer (expected 1501) | search_companies(municipality=Toulouse, naf_code=62.02A, limit=5) | Je ne peux pas déterminer le nombre d'entreprises actives qui correspondent à ce critère avec les données disponibles. |
| companies-toulouse-naf-62-02a | 3 | answer (expected 1501) | search_companies(naf_code=62.02A, municipality=Toulouse) | Il y a 5 entreprises actives qui correspondent à ces critères. |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
