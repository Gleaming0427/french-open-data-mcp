# Benchmark 2026-11-27T10:10:44+00:00

- Label: Phase 2: llama3.2:latest, test
- Model: `llama3.2-ctx8k` at `http://localhost:11434/v1`, params `{}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.2.1
- Model server: ollama version is 0.40.18
- Code: french-open-data-mcp 0.1.0, commit `ad58959`
- Questions: `questions_test.json`, 40 questions
- Runs: 3 per question, 120 in total

**Success: 68/120 (57%, 95% interval 48%-65%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 12/15 (80%, 95% interval 55%-93%) | 15/15 |
| dvf_town | 10/15 (67%, 95% interval 42%-85%) | 7/15 |
| dvf_arrondissement | 10/15 (67%, 95% interval 42%-85%) | 10/14 |
| dvf_half_year | 4/15 (27%, 95% interval 11%-52%) | 8/12 |
| dvf_not_covered | 15/15 (100%, 95% interval 80%-100%) | - |
| count_naf | 1/15 (7%, 95% interval 1%-30%) | 0/1 |
| count_section | 4/15 (27%, 95% interval 11%-52%) | 5/15 |
| company_siren | 12/15 (80%, 95% interval 55%-93%) | 3/13 |

Answers naming the source of the data returned: 48/85 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 10869 tokens in 194 s of model requests, 55.9 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| t-code-1 | 3/3 | 2.7 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-2 | 3/3 | 2.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-3 | 0/3 | 6.0 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-4 | 3/3 | 2.1 | 1 | 0 | 0 | 0 | 3/3 |
| t-code-5 | 3/3 | 2.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-town-1 | 3/3 | 1.7 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-town-2 | 1/3 | 1.6 | 1 | 0 | 0 | 0 | 0/3 |
| t-dvf-town-3 | 3/3 | 1.2 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-town-4 | 3/3 | 1.9 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-town-5 | 0/3 | 1.5 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-1 | 1/3 | 1.8 | 1 | 0 | 1 | 0 | 1/2 |
| t-dvf-arrondissement-2 | 3/3 | 1.6 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-3 | 3/3 | 1.4 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-arrondissement-4 | 3/3 | 1.4 | 1 | 0 | 0 | 0 | 3/3 |
| t-dvf-arrondissement-5 | 0/3 | 1.6 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-1 | 0/3 | 2.6 | 1 | 0 | 3 | 0 | - |
| t-dvf-half-year-2 | 1/3 | 4.0 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-3 | 2/3 | 4.3 | 1 | 0 | 0 | 0 | 1/3 |
| t-dvf-half-year-4 | 0/3 | 3.6 | 1 | 0 | 0 | 0 | 2/3 |
| t-dvf-half-year-5 | 1/3 | 3.9 | 1 | 0 | 0 | 0 | 3/3 |
| t-not-covered-1 | 3/3 | 2.4 | 1 | 0 | 3 | 0 | - |
| t-not-covered-2 | 3/3 | 2.1 | 1 | 0 | 3 | 0 | - |
| t-not-covered-3 | 3/3 | 2.5 | 1 | 0 | 3 | 0 | - |
| t-not-covered-4 | 3/3 | 1.6 | 1 | 0 | 3 | 0 | - |
| t-not-covered-5 | 3/3 | 2.3 | 1 | 0 | 3 | 0 | - |
| t-count-naf-1 | 0/3 | 1.7 | 1 | 0 | 3 | 0 | - |
| t-count-naf-2 | 1/3 | 2.7 | 1 | 0 | 2 | 0 | 0/1 |
| t-count-naf-3 | 0/3 | 2.9 | 1 | 0 | 3 | 0 | - |
| t-count-naf-4 | 0/3 | 1.4 | 1 | 0 | 3 | 0 | - |
| t-count-naf-5 | 0/3 | 1.4 | 1 | 0 | 3 | 0 | - |
| t-count-section-1 | 0/3 | 1.9 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-section-2 | 2/3 | 2.8 | 1 | 0 | 0 | 0 | 0/3 |
| t-count-section-3 | 0/3 | 3.1 | 1 | 0 | 0 | 0 | 2/3 |
| t-count-section-4 | 2/3 | 4.8 | 1 | 0 | 0 | 0 | 0/3 |
| t-count-section-5 | 0/3 | 2.8 | 1 | 0 | 0 | 0 | 1/3 |
| t-siren-1 | 3/3 | 1.6 | 1 | 0 | 0 | 0 | 0/3 |
| t-siren-2 | 3/3 | 0.8 | 1 | 0 | 0 | 0 | 0/3 |
| t-siren-3 | 3/3 | 1.0 | 1 | 0 | 0 | 0 | 1/3 |
| t-siren-4 | 0/3 | 1.9 | 1 | 0 | 2 | 0 | 1/1 |
| t-siren-5 | 3/3 | 1.8 | 1 | 0 | 0 | 0 | 1/3 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| t-code-3 | 1 | missing or wrong call: find_municipality; answer (expected ['42218']) | find_municipality(name=Saint-\u00c9tienne) | Le code INSEE de la commune de Saint-Étienne est 42115. Source : Découpage administratif API (geo.api.gouv.fr) |
| t-code-3 | 2 | missing or wrong call: find_municipality; answer (expected ['42218']) | find_municipality(name=Saint-\u00e9tienne) | Le code INSEE de la commune de Saint-Étienne est 42130. Source : Découpage administratif API (geo.api.gouv.fr) |
| t-code-3 | 3 | missing or wrong call: find_municipality; answer (expected ['42218']) | find_municipality(name=Saint-\u00eatienne) | Je suis désolé, mais je n'ai pas pu obtenir le code INSEE de la commune de Saint-Étienne à travers la fonction "find_municipality" de l'API geo.api.gouv.fr. Pou… |
| t-dvf-town-2 | 2 | missing or wrong call: property_prices | property_prices(municipality=Brest) | Le prix médian au m² des maisons vendues à Brest en 2024 est de 2 410 euros. |
| t-dvf-town-2 | 3 | missing or wrong call: property_prices | property_prices(municipality=Brest) | Le prix médian au m² des maisons vendues à Brest en 2025 est de 2 410 euros. |
| t-dvf-town-5 | 1 | missing or wrong call: property_prices | property_prices(municipality=Caen) | Le prix médian au m² des appartements vendus à Caen en 2024 est de 2 970 euros. Source : data.gouv.fr, DVF 2025 |
| t-dvf-town-5 | 2 | missing or wrong call: property_prices | property_prices(municipality=Caen) | Le prix médian au m² des appartements vendus à Caen en 2025 est de 2970 euros. Source : DVF géolocalisées (DGFiP, processed by data.gouv.fr) |
| t-dvf-town-5 | 3 | missing or wrong call: property_prices | property_prices(municipality=Caen) | Le prix médian au m² des appartements vendus à Caen en 2024 est de 2970 euros. Source : data.gouv.fr, DVF 2025 |
| t-dvf-arrondissement-1 | 1 | missing or wrong call: property_prices; answer (expected 4260) | property_prices(municipality=Marseille 8e arrondissement, period=2025) | Je suis désolé, mais je ne peux pas fournir les informations demandées sur le 18e arrondissement de Paris en 2025, car les données sont disponibles pour le 8e a… |
| t-dvf-arrondissement-1 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(period=2025-S1, municipality=Marseille 8e arrondissement) ERROR | Puisque la période 2025-S1 n'est pas disponible, je vais appeler à nouveau le tool property_prices avec la période 2025-S1. {"name": "property_prices", "paramet… |
| t-dvf-arrondissement-5 | 1 | missing or wrong call: property_prices | property_prices(municipality=Marseille 8e arrondissement, period=2024) | Le prix médian au m² des maisons vendues dans le 9e arrondissement de Marseille en 2024 est de 7250 euros. |
| t-dvf-arrondissement-5 | 2 | missing or wrong call: property_prices | property_prices(municipality=Marseille 8e arrondissement, period=2024) | Le prix médian au m² des maisons vendues dans le 9e arrondissement de Marseille en 2024 est de 7 250 euros. Source : DVF géolocalisées (DGFiP, processed by data… |
| t-dvf-arrondissement-5 | 3 | missing or wrong call: property_prices | property_prices(municipality=Marseille 8e arrondissement, period=2024) | Le prix médian au m² des maisons vendues dans le 9e arrondissement de Marseille en 2024 est de 7250 euros. Source : data.gouv.fr, DVF géolocalisées (DGFiP) |
| t-dvf-half-year-1 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Orlæans, period=2026-S1) ERROR | Pardon, je m'excuse pour la erreur. Il semble que j'ai commis une erreur en saisissant le nom de la commune. Je vais essayer à nouveau. Puisque les données ne s… |
| t-dvf-half-year-1 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Orlêns, period=2026-S1) ERROR | Il semblerait que j'ai rencontré une erreur en appelant le tool. Je vais essayer à nouveau avec le nom complet de la commune. Puisque je n'ai pas reçu de répons… |
| t-dvf-half-year-1 | 3 | missing or wrong call: property_prices; answer (no successful property_prices call) | property_prices(municipality=Orlêns) ERROR | Je suis désolé, je ne peux pas trouver d'informations sur le prix médian au m² des appartements vendus à Orléans pour le premier semestre 2026. Le service de pr… |
| t-dvf-half-year-2 | 1 | missing or wrong call: property_prices | property_prices(municipality=Besançon) | Je suis désolé, mais le tool n'a pas fourni d'information pour le premier semestre 2026. L'information disponible est pour le premier semestre 2025. Selon les d… |
| t-dvf-half-year-2 | 3 | missing or wrong call: property_prices | property_prices(municipality=Besançon) | Je suis désolé, mais je ne peux pas fournir des données pour 2026 car le tool me fournit des données pour 2025. Cependant, je peux vous fournir les informations… |
| t-dvf-half-year-3 | 1 | missing or wrong call: property_prices; answer (expected 2170) | property_prices(municipality=Nîmes) | Il n'y a pas d'informations disponibles sur les prix médians des appartements vendus à Nîmes au premier semestre 2026, car les données les plus récentes disponi… |
| t-dvf-half-year-4 | 1 | missing or wrong call: property_prices | property_prices(municipality=Rouen) | Je suis désolé, mais le tool m'a retourné un résultat qui n'est pas spécifique au second semestre 2021. Cependant, je peux vous indiquer que le prix médian au m… |
| t-dvf-half-year-4 | 2 | missing or wrong call: property_prices | property_prices(municipality=Rouen) | Le prix médian au m² des appartements vendus à Rouen au second semestre 2021 était de 2680 euros. Source : data.gouv.fr, DVF géolocalisées (DGFiP) |
| t-dvf-half-year-4 | 3 | missing or wrong call: property_prices | property_prices(municipality=Rouen) | Le prix médian au m² des appartements vendus à Rouen au second semestre 2021 est de 2 680 €. Source : data.gouv.fr |
| t-dvf-half-year-5 | 2 | missing or wrong call: property_prices | property_prices(municipality=Poitiers) | Le prix médian au m² des maisons vendues à Poitiers au second semestre 2021 est de 2040 euros. Source : data.gouv.fr, DVF géolocalisées (DGFiP) |
| t-dvf-half-year-5 | 3 | missing or wrong call: property_prices | property_prices(municipality=Poitiers) | Le prix médian au m² des maisons vendues à Poitiers au second semestre 2021 est de 2040 euros. Source : data.gouv.fr, DVF géolocalisées (DGFiP) |
| t-count-naf-1 | 1 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(limit=5, include_closed=false, municipality=Reims, text=coiffure, naf_code=96.02A, department=51100) ERROR | D'après les données de la Commission d'orientation et de la concurrence de la Chambre des comptes, il n'est pas possible de fournir la réponse attendue suite à … |
| t-count-naf-1 | 2 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=96.02A, municipality=Reims, include_closed=false, limit=5) ERROR | Désolé, je vais essayer à nouveau avec une activité principale correspondant à la coiffure. {"name": "search_companies", "parameters": {"activity_section": "96.… |
| t-count-naf-1 | 3 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=96.02A, municipality=Reims) ERROR | Désolé, je vais essayer à nouveau avec les codes NAF corrects. Il n'y a pas de résultats pour la recherche de entreprises actives avec activité principale la co… |
| t-count-naf-2 | 2 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=47.73Z, municipality=Tours) ERROR | Pardon, je vais essayer à nouveau avec le code NAF correct. Voici la réponse : Aucune entreprise n'a été trouvée qui a pour activité principale le commerce de d… |
| t-count-naf-2 | 3 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=47.73Z, municipality=Tours) ERROR | Je m'excuse pour la erreur. Voici la réponse à votre question : Pour trouver les entreprises actives avec activité principale le commerce de détail de produits … |
| t-count-naf-3 | 1 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=43.22A, municipality=Caen) ERROR | Désolé, je vais essayer à nouveau avec les arguments corrects. Voici la réponse : Je n'ai pas trouvé de réponse précise via le outil "search_companies" pour vot… |
| t-count-naf-3 | 2 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(department=14, municipality=Caen, include_closed=False, limit=25, naf_code=43.22A, activity_section=43.22A) ERROR | Je m'excuse pour la erreur. Voici la réponse avec la correction de l'activité section : Il n'est pas possible de trouver les entreprises correspondant à la requ… |
| t-count-naf-3 | 3 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=43.22A, municipality=Caen) ERROR | Désolé pour la erreur. Voici la mise à jour de la requête : {"name": "search_companies", "parameters": {"activity_code":"43.22A","municipality":"Caen"}} |
| t-count-naf-4 | 1 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=68.31Z, municipality=Perpignan, include_closed=false) ERROR | Poursuivons avec une autre recherche. Nous allons remplacer la lettre Z par la lettre I, car le code NAF 68.31I correspond aux agences immobilières. {"name": "s… |
| t-count-naf-4 | 2 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=68.31Z, municipality=Perpignan) ERROR | Désolé, je vais essayer à nouveau avec une activité différente. {"name": "search_companies", "parameters": {"activity_section": "68.31H", "municipality": "Perpi… |
| t-count-naf-4 | 3 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=68.31Z, municipality=Perpignan) ERROR | Désolé, je vais essayer à nouveau avec l'activité sous la forme d'un numéro SIC. {"name": "search_companies", "parameters": {"activity_code": "6813Z", "municipa… |
| t-count-naf-5 | 1 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=56.10C, department=81, municipality=Amiens, include_closed=false, limit=25, naf_code=56.10C) ERROR | Pardon, je vais essayer à nouveau. Voici la réponse après avoir correctement spécifié la section de l'activité : {"name": "search_companies", "parameters": {"na… |
| t-count-naf-5 | 2 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=56.10C, municipality=Amiens) ERROR | Pardon, je vais essayer à nouveau. {"name": "search_companies", "parameters": {"activity_section": "56", "municipality": "Amiens"}} |
| t-count-naf-5 | 3 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | search_companies(activity_section=56.10C, municipality=Amiens) ERROR | Désolé, je vais essayer à nouveau avec la bonne activité. {"name": "search_companies", "parameters": {"activity_section": "56.10C", "municipality": "Amiens"}} |
| t-count-section-1 | 1 | answer (expected 1993) | search_companies(activity_section=I, municipality=Annecy) | Il y a 7 entreprises actives de la section d'activité I (hébergement et restauration) avec au moins un établissement à Annecy. Source : Recherche d'entreprises … |
| t-count-section-1 | 2 | answer (expected 1993) | search_companies(activity_section=I, municipality=Annecy) | Il y a 5 entreprises actives de la section d'activité I (hébergement et restauration) qui ont au moins un établissement à Annecy, selon les données de la Recher… |
| t-count-section-1 | 3 | answer (expected 1993) | search_companies(activity_section=I, municipality=Annecy) | Il y a 5 entreprises actives de la section d'activité I (hébergement et restauration) qui ont au moins un établissement à Annecy. |
| t-count-section-2 | 3 | answer (expected 1555) | search_companies(municipality=Brest, activity_section=F) | Il y a 92 entreprises actives de la section d'activité F (construction) qui ont au moins un établissement à Brest. |
| t-count-section-3 | 1 | answer (expected 2825) | search_companies(activity_section=Q, municipality=Limoges, include_closed=False, limit=1) | Il n'y a pas de données disponibles pour répondre à la question. La recherche a returné moins d'une réponse. Votre question pourrait être reformulée en demandan… |
| t-count-section-3 | 2 | answer (expected 2825) | search_companies(activity_section=Q, municipality=Limoges, include_closed=false, limit=5) | Il y a 5 entreprises actives de la section d'activité Q (santé humaine et action sociale) qui ont au moins un établissement à Limoges. Source : Recherche d'entr… |
| t-count-section-3 | 3 | answer (expected 2825) | search_companies(activity_section=Q, municipality=Limoges) | Il y a 5 entreprises actives de la section d'activité Q (santé humaine et action sociale) qui ont au moins un établissement à Limoges. Source : Recherche d'entr… |
| t-count-section-4 | 1 | answer (expected 4672) | search_companies(activity_section=G, limit=25, municipality=Avignon) | Il y a 134 entreprises actives de la section d'activité G (commerce et réparation d'automobiles) qui ont au moins un établissement à Avignon. |
| t-count-section-5 | 1 | answer (expected 826) | search_companies(activity_section=K, municipality=Pau) | Il y a 4 entreprises actives de la section d'activité K (activités financières et d'assurance) qui ont au moins un établissement à Pau. Source : API Recherche d… |
| t-count-section-5 | 2 | answer (expected 826) | search_companies(text=, activity_section=K, municipality=Pau) | Il y a 4 entreprises actives de la section d'activité K (activités financières et d'assurance) qui ont au moins un établissement à Pau. |
| t-count-section-5 | 3 | answer (expected 826) | search_companies(activity_section=K, municipality=Pau, limit=25, include_closed=false) | Il y a 82 entreprises actives de la section d'activité K (activités financières et d'assurance) avec au moins un établissement à Pau. |
| t-siren-4 | 1 | answer (expected '64.19Z') | search_companies(text=552120222) | L'activité principale (code NAF) de l'entreprise dont le SIREN est 552120222 est la location de biens immobiliers. Source : API Recherche d'entreprises INSEE - … |
| t-siren-4 | 2 | missing or wrong call: company_profile/search_companies; answer (no successful company_profile/search_companies call) | search_companies(department=, municipality_code=, postcode=, activity_section=, include_closed=False, limit=1, municipality=, naf_code=, text=, siren=552120222) ERROR | Désolé, je n'ai pas pu obtenir la réponse avec le tool search_companies. Vous pouvez essayer d'utiliser un autre tool ou me donner plus d'informations sur l'ent… |
| t-siren-4 | 3 | missing or wrong call: company_profile/search_companies; answer (no successful company_profile/search_companies call) | search_companies(siren=552120222, activity_section=null) ERROR | Désolé, je n'ai pas pu obtenir la réponse avec le tool "search_companies". Pour trouver l'activité principale de l'entreprise dont le SIREN est 552120222, je pe… |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
