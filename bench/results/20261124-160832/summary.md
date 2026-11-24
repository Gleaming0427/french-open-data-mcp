# Benchmark 2026-11-24T16:08:32+00:00

- Label: Olala q5e6, M2 Max, tools v3, held-out 2
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: mlx-engine (OVHcloud fork) 58083ca
- Code: french-open-data-mcp 0.1.0, commit `1bdba5b`
- Questions: `questions_holdout2.json`, 16 questions
- Runs: 3 per question, 48 in total

**Success: 37/48** (expected tool calls succeeded and the answer contains the tool's figure).

Model output: 62073 tokens in 778 s of model requests, 79.8 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls |
|---|---|---|---|---|---|---|
| municipality-code-rennes | 3/3 | 4.4 | 1 | 0 | 0 | 3 |
| municipality-code-grenoble | 3/3 | 5.3 | 1 | 0 | 0 | 0 |
| dvf-lille-apartment-m2 | 3/3 | 12.2 | 1 | 0 | 0 | 0 |
| dvf-rennes-house-m2-2024 | 3/3 | 8.8 | 1 | 0 | 0 | 0 |
| dvf-nice-apartment-m2 | 3/3 | 14.6 | 1 | 0 | 0 | 0 |
| dvf-angers-house-m2 | 3/3 | 11.6 | 1 | 0 | 0 | 0 |
| dvf-paris-15-apartment-m2-2024 | 2/3 | 20.1 | 1 | 0 | 2 | 0 |
| dvf-lyon-7-apartment-m2 | 1/3 | 33.8 | 2 | 0 | 2 | 0 |
| dvf-marseille-13-house-m2 | 2/3 | 16.9 | 1 | 1 | 1 | 0 |
| dvf-grenoble-apartment-m2-2026-s1 | 1/3 | 15.4 | 1 | 0 | 2 | 0 |
| dvf-colmar-not-covered | 3/3 | 13.0 | 1 | 0 | 3 | 0 |
| dvf-mamoudzou-not-covered | 3/3 | 12.0 | 1 | 0 | 4 | 1 |
| companies-nantes-naf-10-71c | 2/3 | 25.5 | 1 | 0 | 0 | 0 |
| companies-grenoble-section-j | 0/3 | 65.6 | 2 | 2 | 4 | 0 |
| company-profile-naf-380129866 | 3/3 | 9.2 | 1 | 0 | 0 | 1 |
| company-name-441639465 | 2/3 | 11.7 | 2 | 0 | 0 | 0 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| dvf-paris-15-apartment-m2-2024 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Paris, period=2024) ERROR > find_municipality(name=Paris 15e arrondissement) > property_prices(municipality=75115, period=2024) ERROR | Les données demandées ne sont pas disponibles dans les sources disponibles. Impossibilité de récupérer le prix médian exact pour ce segment en 2024. |
| dvf-lyon-7-apartment-m2 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | find_municipality(name=Lyon) > property_prices(municipality=Lyon, period=2025) ERROR | Je n’ai pas pu obtenir le prix médian au m² pour le 7e arrondissement de Lyon en 2025, car l’API `property_prices` ne fournit pas de données par arrondissement.… |
| dvf-lyon-7-apartment-m2 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | find_municipality(name=Lyon 7e arrondissement) > property_prices(municipality=Lyon_01_1105, period=2025) ERROR | Le prix médian au m² des appartements vendus dans le 7e arrondissement de Lyon pour 2025 n’est pas disponible via les outils fournis. Les données demandées ne s… |
| dvf-marseille-13-house-m2 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Marseille, period=2025) ERROR | Je ne peux pas déterminer le prix médian au m² des maisons dans le 13e arrondissement de Marseille en 2025 avec les données disponibles. La demande nécessite un… |
| dvf-grenoble-apartment-m2-2026-s1 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Grenoble, period=2026-S2) ERROR | Les données demandées pour le premier semestre 2026 ne sont pas disponibles dans le système. |
| dvf-grenoble-apartment-m2-2026-s1 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Grenoble, period=2026-01) ERROR | Le premier semestre 2026 n'est pas disponible dans les données de prix médians pour Grenoble. Aucun prix médian ne peut être fourni. Source: erreur du service d… |
| companies-nantes-naf-10-71c | 1 | answer (expected 185) | search_companies(naf_code=10.71C, municipality=Nantes) | Il y a 5 entreprises actives correspondant aux critères. Source : recherche_companies avec les filtres NAF 10.71C et Nantes. Source: search_companies tool (retu… |
| companies-grenoble-section-j | 1 | missing or wrong call: search_companies; answer (expected 373) | search_companies(text=information et communication, naf_code=J, municipality=Grenoble) ERROR > search_companies(naf_code=62.02A, municipality=Grenoble) | Il y a 1 entreprise active de la section d'activité J (information et communication) ayant au moins un établissement à Grenoble. Source : recherche d'entreprise… |
| companies-grenoble-section-j | 2 | answer (expected 1989) | find_municipality(name=Grenoble) > search_companies(municipality=Grenoble, naf_code=J, limit=10) ERROR > search_companies(municipality=Grenoble, naf_code=62, limit=10) ERROR > company_profile(siren=0244231230) ERROR > search_companies(municipality=Grenoble, activity_section=J, limit=10) | 0 La recherche des entreprises actives de la section J (information et communication) situées à Grenoble ne renvoie aucun résultat valide. En effet, les entrepr… |
| companies-grenoble-section-j | 3 | missing or wrong call: search_companies; answer (expected 10000) | search_companies(municipality=Grenoble) > company_profile(siren=123456789) | Je ne peux pas déterminer ce nombre avec les données disponibles. |
| company-name-441639465 | 1 | missing or wrong call: company_profile | search_companies(text=441639465) | RENAULT Source: search_companies |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
