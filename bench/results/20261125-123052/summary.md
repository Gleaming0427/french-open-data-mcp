# Benchmark 2026-11-25T12:30:52+00:00

- Label: Phase 2: Olala q5e6, reasoning low, test
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: mlx-engine (OVHcloud fork) 58083ca
- Code: french-open-data-mcp 0.1.0, commit `ace3195`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 113/120 (94%, 95% interval 88%-97%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 15/15 (100%, 95% interval 80%-100%) | 8/15 |
| dvf_town | 15/15 (100%, 95% interval 80%-100%) | 12/15 |
| dvf_arrondissement | 14/15 (93%, 95% interval 70%-99%) | 11/14 |
| dvf_half_year | 15/15 (100%, 95% interval 80%-100%) | 12/15 |
| dvf_not_covered | 15/15 (100%, 95% interval 80%-100%) | 0/5 |
| count_naf | 11/15 (73%, 95% interval 48%-89%) | 7/15 |
| count_section | 13/15 (87%, 95% interval 62%-96%) | 10/14 |
| company_siren | 15/15 (100%, 95% interval 80%-100%) | 8/15 |

Answers naming the source of the data returned: 68/108 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 171195 tokens in 2339 s of model requests, 73.2 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 5.6 | 1 | 0 | 0 | 0 | 2/3 |
| t-code-2 | 3/3 | 9.2 | 1 | 0 | 0 | 2 | 2/3 |
| t-code-3 | 3/3 | 4.7 | 1 | 0 | 0 | 0 | 2/3 |
| t-code-4 | 3/3 | 7.1 | 1 | 1 | 1 | 0 | 1/3 |
| t-code-5 | 3/3 | 5.3 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-town-1 | 3/3 | 9.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-2 | 3/3 | 10.4 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-town-3 | 3/3 | 13.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-4 | 3/3 | 15.2 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-town-5 | 3/3 | 13.3 | 2 | 0 | 0 | 0 | 2/3 |
| t-dvf-arrondissement-1 | 3/3 | 19.5 | 2 | 0 | 2 | 0 | 3/3 |
| t-dvf-arrondissement-2 | 3/3 | 34.3 | 3 | 0 | 2 | 0 | 1/3 |
| t-dvf-arrondissement-3 | 2/3 | 24.0 | 1 | 0 | 1 | 0 | 2/2 |
| t-dvf-arrondissement-4 | 3/3 | 15.2 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-5 | 3/3 | 22.8 | 2 | 0 | 1 | 0 | 2/3 |
| t-dvf-half-year-1 | 3/3 | 16.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-2 | 3/3 | 12.0 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-3 | 3/3 | 14.6 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-4 | 3/3 | 14.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-5 | 3/3 | 18.5 | 2 | 1 | 0 | 0 | 2/3 |
| t-not-covered-1 | 3/3 | 19.6 | 1 | 0 | 2 | 0 | 0/1 |
| t-not-covered-2 | 3/3 | 15.4 | 1 | 0 | 3 | 0 | 0/1 |
| t-not-covered-3 | 3/3 | 16.7 | 1 | 0 | 3 | 0 | - |
| t-not-covered-4 | 3/3 | 14.7 | 2 | 0 | 3 | 0 | 0/2 |
| t-not-covered-5 | 3/3 | 19.4 | 1 | 0 | 3 | 0 | 0/1 |
| t-count-naf-1 | 2/3 | 34.2 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-naf-2 | 3/3 | 32.1 | 2 | 0 | 0 | 0 | 0/3 |
| t-count-naf-3 | 3/3 | 23.6 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-naf-4 | 0/3 | 36.4 | 1 | 0 | 0 | 0 | 1/3 |
| t-count-naf-5 | 3/3 | 25.1 | 2 | 0 | 0 | 0 | 2/3 |
| t-count-section-1 | 3/3 | 19.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-2 | 2/3 | 63.2 | 2 | 0 | 4 | 0 | 1/2 |
| t-count-section-3 | 2/3 | 71.3 | 2 | 0 | 0 | 2 | 2/3 |
| t-count-section-4 | 3/3 | 71.7 | 2 | 0 | 0 | 2 | 2/3 |
| t-count-section-5 | 3/3 | 29.6 | 2 | 0 | 0 | 1 | 2/3 |
| t-siren-1 | 3/3 | 8.5 | 1 | 0 | 0 | 0 | 2/3 |
| t-siren-2 | 3/3 | 13.9 | 1 | 0 | 0 | 1 | 1/3 |
| t-siren-3 | 3/3 | 6.8 | 1 | 0 | 0 | 0 | 1/3 |
| t-siren-4 | 3/3 | 12.9 | 1 | 0 | 0 | 0 | 2/3 |
| t-siren-5 | 3/3 | 10.2 | 1 | 0 | 0 | 0 | 2/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| t-dvf-arrondissement-3 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Lyon, period=2025) ERROR | Je ne peux pas fournir ce chiffre car l’outil `property_prices` ne renvoie que les prix par commune, pas par arrondissement spécifique. Pour le 6e arrondissemen… |
| t-count-naf-1 | 2 | answer (expected 313) | count_companies(municipality=Reims, naf_code=96.02A) > search_companies(municipality=Reims, naf_code=96.02A) | Il y a 5 entreprises actives qui ont pour activité principale la coiffure (code NAF 96.02A) et qui disposent d’au moins un établissement à Reims. **Source** : `… |
| t-count-naf-4 | 1 | answer (expected 535) | search_companies(municipality=Perpignan, naf_code=68.31Z) | Il y a 5 entreprises actives qui correspondent aux critères (actives, activité NAF 68.31Z, au moins un établissement à Perpignan). Source : résultat du service … |
| t-count-naf-4 | 2 | answer (expected 0) | search_companies(municipality=Perpignan, naf_code=68.31Z) > count_companies(municipality=Perpignan, naf_code=68.31Z, activity_section=J) | Il y a 535 entreprises actives qui sont des agences immobilières (NAF 68.31Z) et qui possèdent au moins un établissement à Perpignan. Source : réponse de la rec… |
| t-count-naf-4 | 3 | answer (expected 535) | search_companies(naf_code=68.31Z, municipality=Perpignan) | Les résultats montrent 5 entreprises actives correspondant aux critères. Réponse : 5. Source du résultat : recherche_companies (filtrage municipalement « Perpig… |
| t-count-section-2 | 1 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(municipality=Brest, naf_code=41) ERROR > count_companies(municipality=Brest, naf_code=41) ERROR > search_companies(municipality=Brest, naf_code=41) ERROR > search_companies(municipality=Brest, naf_code=41) ERROR | Les outils disponibles ne permettent pas de déterminer le nombre d’entreprises de la section d’activité F (construction) à Brest avec un établissement. **Imposs… |
| t-count-section-3 | 2 | answer (expected 2824) | count_companies(municipality=Limoges, activity_section=Q) > search_companies(municipality=Limoges, activity_section=Q) > count_companies(municipality=Limoges, activity_section=Q) repeated > search_companies(municipality=Limoges, activity_section=Q) repeated | Je ne peux pas déterminer ce nombre avec les outils disponibles. La requête nécessite un filtrage sur le statut « actif » et la localisation à Limoges, ce que l… |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
