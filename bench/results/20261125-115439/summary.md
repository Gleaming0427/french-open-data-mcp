# Benchmark 2026-11-25T11:54:39+00:00

- Label: Phase 1: Olala q8, reasoning low
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: mlx-engine (OVHcloud fork) 58083ca
- Code: french-open-data-mcp 0.1.0, commit `fbc1474`
- Questions: `questions_dev.json`, 32 questions
- Runs: 2 per question, 64 in total

**Success: 58/64 (91%, 95% interval 81%-96%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 7/8 (88%, 95% interval 53%-98%) | 3/8 |
| dvf_town | 18/18 (100%, 95% interval 82%-100%) | 7/18 |
| dvf_arrondissement | 8/12 (67%, 95% interval 39%-86%) | 5/8 |
| dvf_half_year | 2/2 (100%, 95% interval 34%-100%) | 0/2 |
| dvf_not_covered | 7/8 (88%, 95% interval 53%-98%) | 0/5 |
| count_naf | 6/6 (100%, 95% interval 61%-100%) | 2/6 |
| count_section | 2/2 (100%, 95% interval 34%-100%) | 1/2 |
| company_siren | 8/8 (100%, 95% interval 68%-100%) | 1/8 |

Answers naming the source of the data returned: 19/57 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 80104 tokens in 1319 s of model requests, 60.7 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| municipality-code-beaune | 2/2 | 4.7 | 1.0 | 0 | 0 | 0 | 0/2 |
| municipality-code-montpellier | 2/2 | 5.7 | 1.5 | 1 | 1 | 0 | 2/2 |
| municipality-code-rennes | 2/2 | 5.5 | 1.0 | 0 | 0 | 0 | 0/2 |
| municipality-code-grenoble | 1/2 | 17.9 | 8.0 | 8 | 4 | 7 | 1/2 |
| dvf-beaune-apartment-m2 | 2/2 | 18.8 | 5.0 | 3 | 1 | 5 | 2/2 |
| dvf-dijon-house-m2 | 2/2 | 13.2 | 1.0 | 0 | 0 | 0 | 0/2 |
| dvf-toulouse-apartment-m2 | 2/2 | 15.6 | 1.5 | 0 | 0 | 0 | 1/2 |
| dvf-nantes-apartment-m2-2024 | 2/2 | 19.8 | 3.0 | 1 | 1 | 1 | 1/2 |
| dvf-bordeaux-house-m2 | 2/2 | 9.8 | 1.0 | 0 | 0 | 0 | 1/2 |
| dvf-lille-apartment-m2 | 2/2 | 17.1 | 2.5 | 0 | 0 | 2 | 0/2 |
| dvf-rennes-house-m2-2024 | 2/2 | 10.4 | 1.0 | 0 | 0 | 0 | 0/2 |
| dvf-nice-apartment-m2 | 2/2 | 14.6 | 1.0 | 0 | 0 | 0 | 1/2 |
| dvf-angers-house-m2 | 2/2 | 13.1 | 1.5 | 0 | 0 | 0 | 1/2 |
| dvf-paris-11-apartment-m2 | 1/2 | 29.3 | 2.0 | 0 | 2 | 0 | 0/1 |
| dvf-marseille-8-apartment-m2 | 2/2 | 28.8 | 2.5 | 0 | 2 | 0 | 2/2 |
| dvf-lyon-3-apartment-m2-2024 | 1/2 | 35.3 | 3.0 | 1 | 2 | 0 | 1/1 |
| dvf-paris-15-apartment-m2-2024 | 0/2 | 24.6 | 0.5 | 0 | 1 | 0 | - |
| dvf-lyon-7-apartment-m2 | 2/2 | 22.2 | 2.0 | 0 | 1 | 0 | 1/2 |
| dvf-marseille-13-house-m2 | 2/2 | 32.1 | 3.0 | 0 | 2 | 0 | 1/2 |
| dvf-grenoble-apartment-m2-2026-s1 | 2/2 | 14.1 | 1.0 | 0 | 0 | 0 | 0/2 |
| dvf-strasbourg-not-covered | 2/2 | 53.3 | 2.5 | 1 | 3 | 1 | 0/1 |
| dvf-metz-not-covered | 1/2 | 29.4 | 5.0 | 0 | 3 | 4 | 0/2 |
| dvf-colmar-not-covered | 2/2 | 14.2 | 2.5 | 0 | 3 | 1 | 0/1 |
| dvf-mamoudzou-not-covered | 2/2 | 12.5 | 1.5 | 0 | 2 | 0 | 0/1 |
| companies-toulouse-naf-62-02a | 2/2 | 28.0 | 1.5 | 0 | 0 | 0 | 0/2 |
| companies-bordeaux-naf-56-10a | 2/2 | 31.3 | 1.5 | 0 | 0 | 0 | 1/2 |
| companies-nantes-naf-10-71c | 2/2 | 39.6 | 1.5 | 0 | 0 | 0 | 1/2 |
| companies-grenoble-section-j | 2/2 | 82.8 | 2.5 | 0 | 0 | 1 | 1/2 |
| company-profile-siren | 2/2 | 12.7 | 2.0 | 1 | 1 | 1 | 0/2 |
| company-name-siren | 2/2 | 12.4 | 1.0 | 0 | 0 | 0 | 0/2 |
| company-profile-naf-380129866 | 2/2 | 10.9 | 1.0 | 0 | 0 | 0 | 1/2 |
| company-name-441639465 | 2/2 | 9.8 | 1.0 | 0 | 0 | 0 | 0/2 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| municipality-code-grenoble | 1 | model: max_turns; answer (expected ['38185']) | find_municipality(name=Grenoble) > company_profile(siren=38185) ERROR > property_prices(municipality=Grenoble, period=2023) > search_companies(municipality=Grenoble, limit=5) > find_municipality(name=Lille) > company_profile(siren=38185) ERROR > property_prices(municipality=Grenoble, period=2023) re… | Maximum number of tool calls reached without a final answer. |
| dvf-paris-11-apartment-m2 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Paris, period=2025) ERROR | Les données demandées ne sont pas disponibles : l’outil de prix immobilier ne fournit que les prix par arrondissement dans les 20 arrondissements de Paris, mais… |
| dvf-lyon-3-apartment-m2-2024 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Lyon, period=2024) ERROR | Pour obtenir le prix médian au m² des appartements vendus dans le 3e arrondissement de Lyon en 2024, il faut préciser le nom complet du quartier : "Lyon 3e arro… |
| dvf-paris-15-apartment-m2-2024 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne peux pas répondre car les données demandées (prix médian par arrondissement) ne sont pas disponibles dans les outils fournis. Les informations sur les pri… |
| dvf-paris-15-apartment-m2-2024 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Paris, period=2024) ERROR | Je ne peux pas répondre à cette question car l'outil `property_prices` ne fournit les données que pour Paris en général, et non par arrondissement spécifique. V… |
| dvf-metz-not-covered | 2 | model: max_turns | property_prices(municipality=Metz, period=2025) ERROR > find_municipality(name=Metz) > find_municipality(name=Metz) repeated > find_municipality(name=Moselle) > find_municipality(name=Moselle) repeated > find_municipality(name=Metz) repeated | Maximum number of tool calls reached without a final answer. |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
