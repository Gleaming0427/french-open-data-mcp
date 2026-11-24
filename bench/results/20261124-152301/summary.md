# Benchmark 2026-11-24T15:23:01+00:00

- Label: Olala q5e6, M2 Max, tools v3, held-out
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: Apple M2 Max, 32 GB memory, macOS 27.0.1
- Code: french-open-data-mcp 0.1.0, commit `729b340`
- Questions: `questions_holdout.json`, 8 questions
- Runs: 3 per question, 24 in total
- Checks re-applied on 2026-11-24T15:45:25+00:00 with `questions_holdout.json` (commit `1f310a9`) to 24 stored runs; the summary written during the run is kept in summary-as-run.md

**Success: 20/24** (expected tool calls succeeded and the answer contains the tool's figure).

Model output: 26597 tokens in 320 s of model requests, 83.0 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls |
|---|---|---|---|---|---|---|
| municipality-code-montpellier | 3/3 | 6.4 | 1 | 0 | 0 | 0 |
| dvf-nantes-apartment-m2-2024 | 3/3 | 9.1 | 1 | 0 | 0 | 0 |
| dvf-bordeaux-house-m2 | 3/3 | 13.1 | 1 | 0 | 0 | 0 |
| dvf-marseille-8-apartment-m2 | 2/3 | 14.8 | 1 | 0 | 0 | 0 |
| dvf-lyon-3-apartment-m2-2024 | 3/3 | 15.9 | 1 | 0 | 0 | 0 |
| dvf-metz-not-covered | 3/3 | 16.1 | 1 | 0 | 3 | 0 |
| companies-bordeaux-naf-56-10a | 0/3 | 26.1 | 1 | 0 | 0 | 1 |
| company-name-siren | 3/3 | 13.7 | 1 | 0 | 0 | 0 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| dvf-marseille-8-apartment-m2 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne dispose pas de données spécifiques pour le 8e arrondissement de Marseille en 2025. Les résultats fournis par l'outil `property_prices` sont disponibles po… |
| companies-bordeaux-naf-56-10a | 1 | answer (expected 1490) | search_companies(municipality=Bordeaux, naf_code=56.10A) | Les résultats de la recherche indiquent 5 entreprises actives avec le NAF 56.10A ayant au moins un établissement à Bordeaux. Source : recherche_companies (33063… |
| companies-bordeaux-naf-56-10a | 2 | missing or wrong call: search_companies | search_companies(text=NAF 56.10A Bordeaux, municipality=Bordeaux) | Les recherches indiquent qu’il n’existe aucune entreprise active correspondant à ce critère, donc le nombre est 0. Source : recherche_companies (résultat 0) 0. |
| companies-bordeaux-naf-56-10a | 3 | answer (expected 1490) | search_companies(naf_code=56.10A, municipality=Bordeaux) > search_companies(naf_code=56.10A, municipality=Bordeaux) repeated | 0. Aucune entreprise active ne correspond à ces critères. Source de la recherche : résultat de la recherche d’entreprises avec NAF 56.10A et municipalité Bordea… |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
