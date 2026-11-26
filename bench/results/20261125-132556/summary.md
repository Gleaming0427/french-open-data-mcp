# Benchmark 2026-11-25T13:25:56+00:00

- Label: Phase 2: ministral-3:8b, test
- Model: `ministral-3-8b-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: ollama version is 0.40.6
- Code: french-open-data-mcp 0.1.0, commit `bff70a7`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 84/120 (70%, 95% interval 61%-77%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 15/15 (100%, 95% interval 80%-100%) | 11/15 |
| dvf_town | 6/15 (40%, 95% interval 20%-64%) | 10/12 |
| dvf_arrondissement | 3/15 (20%, 95% interval 7%-45%) | 6/8 |
| dvf_half_year | 5/15 (33%, 95% interval 15%-58%) | 8/9 |
| dvf_not_covered | 15/15 (100%, 95% interval 80%-100%) | 0/3 |
| count_naf | 14/15 (93%, 95% interval 70%-99%) | 14/14 |
| count_section | 11/15 (73%, 95% interval 48%-89%) | 14/15 |
| company_siren | 15/15 (100%, 95% interval 80%-100%) | 15/15 |

Answers naming the source of the data returned: 78/91 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 13326 tokens in 667 s of model requests, 20.0 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 1.5 | 1 | 0 | 0 | 0 | 2/3 |
| t-code-2 | 3/3 | 2.4 | 1 | 0 | 0 | 0 | 2/3 |
| t-code-3 | 3/3 | 2.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-4 | 3/3 | 2.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-5 | 3/3 | 1.4 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-town-1 | 2/3 | 6.3 | 1 | 0 | 0 | 0 | 2/2 |
| t-dvf-town-2 | 1/3 | 6.0 | 2 | 0 | 1 | 0 | 2/3 |
| t-dvf-town-3 | 2/3 | 7.8 | 2 | 0 | 0 | 0 | 2/2 |
| t-dvf-town-4 | 1/3 | 4.0 | 1 | 0 | 0 | 0 | 1/2 |
| t-dvf-town-5 | 0/3 | 9.1 | 2 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-1 | 0/3 | 4.6 | 0 | 0 | 0 | 0 | - |
| t-dvf-arrondissement-2 | 1/3 | 8.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-3 | 0/3 | 4.8 | 0 | 0 | 0 | 0 | - |
| t-dvf-arrondissement-4 | 1/3 | 5.4 | 1 | 0 | 0 | 0 | 1/2 |
| t-dvf-arrondissement-5 | 1/3 | 7.4 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-1 | 1/3 | 3.8 | 0 | 0 | 0 | 0 | 1/1 |
| t-dvf-half-year-2 | 0/3 | 6.1 | 0 | 0 | 0 | 0 | 1/1 |
| t-dvf-half-year-3 | 1/3 | 5.9 | 0 | 0 | 0 | 0 | 1/1 |
| t-dvf-half-year-4 | 2/3 | 11.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-half-year-5 | 1/3 | 12.7 | 1 | 0 | 0 | 0 | 2/3 |
| t-not-covered-1 | 3/3 | 8.6 | 1 | 0 | 1 | 0 | 0/2 |
| t-not-covered-2 | 3/3 | 7.0 | 0 | 0 | 1 | 0 | - |
| t-not-covered-3 | 3/3 | 8.5 | 1 | 0 | 3 | 0 | - |
| t-not-covered-4 | 3/3 | 6.9 | 0 | 0 | 0 | 0 | 0/1 |
| t-not-covered-5 | 3/3 | 5.9 | 0 | 0 | 0 | 0 | - |
| t-count-naf-1 | 2/3 | 4.5 | 1 | 0 | 0 | 0 | 2/2 |
| t-count-naf-2 | 3/3 | 5.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-3 | 3/3 | 5.8 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-4 | 3/3 | 6.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-naf-5 | 3/3 | 5.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-1 | 1/3 | 7.7 | 2 | 0 | 0 | 0 | 2/3 |
| t-count-section-2 | 1/3 | 8.4 | 2 | 0 | 1 | 0 | 3/3 |
| t-count-section-3 | 3/3 | 5.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-4 | 3/3 | 5.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-count-section-5 | 3/3 | 6.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-1 | 3/3 | 9.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-2 | 3/3 | 7.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-3 | 3/3 | 6.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-4 | 3/3 | 7.3 | 1 | 0 | 0 | 0 | 3/3 |
| t-siren-5 | 3/3 | 7.2 | 1 | 0 | 0 | 0 | 3/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| t-dvf-town-1 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne trouve pas de données sur les prix immobiliers pour l'année 2025, car celles-ci ne sont pas encore disponibles. Les prix immobiliers sont généralement pub… |
| t-dvf-town-2 | 1 | missing or wrong call: property_prices | property_prices(municipality=Brest) | En 2025 à Brest, le prix médian au m² pour les maisons vendues était de **2 410 €**. *(Source : DGFiP, données DVF 2025 via [data.gouv.fr](https://www.data.gouv… |
| t-dvf-town-2 | 3 | missing or wrong call: property_prices | find_municipality(name=Brest) > property_prices(municipality=Brest) > property_prices(municipality_code=29019) ERROR | À ce jour, les données disponibles sur **Data.gouv.fr** ne fournissent pas de prix médians par m² pour les maisons vendues à Brest en **2024**. Les dernières do… |
| t-dvf-town-3 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Il n'y a pas encore de données officielles publiées sur les prix médiatifs des appartement vendus à Amiens pour l'année 2025. Les statistiques immobilières sont… |
| t-dvf-town-4 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | À ce jour, je n'ai pas accès aux données immobilières **2025** sur le prix médian au m² des maisons vendues à Perpignan. Les dernières statistiques disponibles … |
| t-dvf-town-4 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | find_municipality(name=Perpignan) | Je n'ai pas trouvé de données sur les prix médians des maisons vendues à Perpignan pour 2025 dans les bases officielles disponibles. Les données immobilières so… |
| t-dvf-town-5 | 1 | missing or wrong call: property_prices | property_prices(municipality=Caen) > find_municipality(name=Caen) | Les données disponibles ne concernent pas l'année **2024** mais **2025** pour **Caen** (INSEE 14118). Voici le prix médian par mètre carré pour les appareils en… |
| t-dvf-town-5 | 2 | missing or wrong call: property_prices | property_prices(municipality=Caen) | Le prix médian au m² des appartements vendus à **Caen en 2024 n'est pas disponible dans les données**. Les données disponibles concernent l'année **2025** et in… |
| t-dvf-town-5 | 3 | missing or wrong call: property_prices | property_prices(municipality=Caen) > find_municipality(name=Caen) | Il n'y a pas encore de données de vente pour le **premier semestre 2024** à Caen. Les dernières données disponibles (2025) indiquent un **prix médian des appart… |
| t-dvf-arrondissement-1 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je n'ai pas encore de données publiques sur les prix immobiliers pour **2025**, car la source officielle (DVF) fournit des informations des années passées. Cett… |
| t-dvf-arrondissement-1 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je n'ai pas encore de données pour 2025, car les prix immobiliers sont généralement publiés avec un décalage. Je peux vous donner les dernières informations dis… |
| t-dvf-arrondissement-1 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Les données sur les prix des logements pour l'année **2025** ne sont pas encore disponibles. Les dernières informations publiées couvrent jusqu'en **2023** ou a… |
| t-dvf-arrondissement-2 | 1 | missing or wrong call: property_prices | find_municipality(name=Paris 6e arrondissement) > property_prices(municipality=Paris 6e arrondissement) | **Aucune donnée officielle disponible pour les appartements vendus dans le 6ᵉ arrondissement de Paris en 2024** Seuls les résultats pour **2025** (avec 788 vent… |
| t-dvf-arrondissement-2 | 3 | missing or wrong call: property_prices | property_prices(municipality=Paris 6e arrondissement) | Le prix médian au m² des appartements vendus dans le 6ᵉ arrondissement de Paris en **2025** (données disponibles pour 2024 ne sont pas encore publiées) s'élève … |
| t-dvf-arrondissement-3 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je n'ai pas les données pour 2025, car les prix disponibles sont généralement ceux des années précédentes. Voici la dernière donnée disponible : **mediane de 7 … |
| t-dvf-arrondissement-3 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je n’ai pas trouvé de données pour le 6e arrondissement de Lyon en **2025**. Les statistiques disponibles ne comportent pas encore cette année, et le DVF n’est … |
| t-dvf-arrondissement-3 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne trouve pas de données disponibles pour le prix médian au m² des appartements vendus dans le 6ᵉ arrondissement de Lyon pour l'année **2025**. Les données D… |
| t-dvf-arrondissement-4 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne dispose pas encore de données pour l'année 2025 sur les prix des appartements dans le 1er arrondissement de Marseille. Cependant, si vous souhaitez, je pe… |
| t-dvf-arrondissement-4 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | find_municipality(name=Marseille 1er arrondissement) | Je n'ai pas trouvé de données sur les prix médians au m² pour les appartements vendus dans le **1er arrondissement de Marseille en 2025**, car les données du DV… |
| t-dvf-arrondissement-5 | 2 | missing or wrong call: property_prices | property_prices(municipality=Marseille 9e arrondissement) | Aucune donnée précise pour le **9ᵉ arrondissement de Marseille en 2024** n'est disponible dans les résultats. Seul le total de **2025** (médian à **5 370 €/m²**… |
| t-dvf-arrondissement-5 | 3 | missing or wrong call: property_prices | find_municipality(name=Marseille 9e arrondissement) > property_prices(municipality=Marseille 9e arrondissement) | Au **9ᵉ arrondissement de Marseille**, le prix médian au m² des **maisons vendues en 2025** était de **5 370 €**. *(Donnée issue des ventes de 2025 disponibles … |
| t-dvf-half-year-1 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne trouve pas de données de prix au m² pour **Orléans** au premier semestre 2026. Les données disponibles sont généralement publiées avec un important délai … |
| t-dvf-half-year-1 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Il n'y a pas encore de données publiées sur les prix de l'immobilier pour le premier semestre 2026 (ou toute autre année en 2024). Les dernières données disponi… |
| t-dvf-half-year-2 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne trouve pas de données sur les prix immobiliers pour le premier semestre 2026 car la plupart des données publiques sont enregistrées avec un décalage tempo… |
| t-dvf-half-year-2 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne trouve pas les données de prix immobiliers pour le premier semestre 2026 car ces informations ne sont pas encore disponibles. Les données disponibles vont… |
| t-dvf-half-year-2 | 3 | answer (expected 2900) | find_municipality(name=Besançon) > property_prices(municipality=Besançon, period=2026-S1) | Le prix médian au m² des **maisons** vendues à Besançon au premier semestre 2026 était de **2\,900 €**. *(Source : [DGFiP/DVFSemestre 2026](https://www.data.gou… |
| t-dvf-half-year-3 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | No data is available for the first half of 2026 as the data has not been released yet. Would you like to get the information for a previous year? |
| t-dvf-half-year-3 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne dispose pas encore de données sur les prix immobiliers pour le premier semestre 2026. Les données disponibles s'arrêtent généralement à l'année civile pré… |
| t-dvf-half-year-4 | 2 | missing or wrong call: property_prices | property_prices(municipality=Rouen) | **À Rouen, aucun prix médian au m² pour les appartements n'est disponible pour le second semestre 2021** dans les données officielles consultées. Les données di… |
| t-dvf-half-year-5 | 1 | missing or wrong call: property_prices; answer (expected 2040) | property_prices(municipality=Poitiers) | À Poitiers au deuxième semestre **2025**, le prix médian au mètre carré des **maisons** vendues était de **1 780 000 €** pour une surface médiane de **90 m²**. … |
| t-dvf-half-year-5 | 2 | missing or wrong call: property_prices | property_prices(municipality=Poitiers) | Le prix médian au m² des maisons vendues à Poitiers **au premier semestre 2025** (chiffres les plus récents disponibles dans la base) est de **2040 €**. *(Sourc… |
| t-count-naf-1 | 1 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | none | search_companies[ARGS]{"naf_code": "96.02A", "municipality": "Reims", "include_closed": false} |
| t-count-section-1 | 1 | missing or wrong call: count_companies/search_companies | find_municipality(name=Annecy) > count_companies(municipality_code=74010, activity_section=I) | À Annecy, **10 000 entreprises actives** sont répertoriées dans la section d'activité **I (hébergement et restauration)**. *(Source : Recherche d'entreprises AP… |
| t-count-section-1 | 2 | missing or wrong call: count_companies/search_companies | find_municipality(name=Annecy) > count_companies(naf_code=I, municipality_code=74010, include_closed=False) | Il y a **au moins 10 000 entreprises actives** de la section **I (Hébergement et restauration)** ayant au moins un établissement à **Annecy** selon les données … |
| t-count-section-2 | 1 | missing or wrong call: count_companies/search_companies | find_municipality(name=Brest) > count_companies(naf_code=43.3, municipality_code=29019) ERROR > count_companies(municipality_code=29019, activity_section=F) | Il y a **10 000 entreprises actives dans la section d'activité F (construction) ayant au moins un établissement à Brest**, selon les données de l'INSEE. **Sourc… |
| t-count-section-2 | 2 | missing or wrong call: count_companies/search_companies | find_municipality(name=Brest) > count_companies(naf_code=, activity_section=F, municipality_code=29019) | **10 000** entreprises actives de la section **F (construction)** ont au moins un établissement à Brest, selon les dernières données disponibles (source : [INSE… |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
