# Benchmark 2026-11-24T12:12:08+00:00

- Label: Olala q5e6, MacBook Pro M2 Max
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "low"}}`
- Machine: Apple M2 Max, 32 GB memory, macOS 27.0.1
- Code: french-open-data-mcp 0.1.0, commit `8422176`
- Runs: 3 per question, 24 in total

**Success: 12/24** (expected tool calls succeeded and the answer contains the tool's figure).

Model output: 32508 tokens in 403 s of model requests, 80.7 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls |
|---|---|---|---|---|---|---|
| municipality-code-beaune | 3/3 | 6.7 | 1 | 0 | 0 | 0 |
| dvf-beaune-apartment-m2 | 3/3 | 11.6 | 2 | 0 | 0 | 0 |
| dvf-dijon-house-m2 | 0/3 | 18.2 | 2 | 0 | 1 | 0 |
| dvf-toulouse-apartment-m2 | 0/3 | 15.5 | 2 | 0 | 0 | 0 |
| dvf-paris-11-apartment-m2 | 0/3 | 16.6 | 1 | 0 | 2 | 0 |
| dvf-strasbourg-not-covered | 2/3 | 19.0 | 2 | 0 | 2 | 0 |
| companies-toulouse-naf-62-02a | 1/3 | 31.7 | 2 | 0 | 0 | 0 |
| company-profile-siren | 3/3 | 12.9 | 1 | 0 | 0 | 0 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| dvf-dijon-house-m2 | 1 | missing or wrong call: property_prices | find_municipality(name=Dijon) > property_prices(insee_code=21054, period=2024) | Le prix médian des maisons vendues à Dijon en 2024 est de 2 660 € par mètre carré. (source : DVF géolocalisées, période 2024, insee 21231) |
| dvf-dijon-house-m2 | 2 | missing or wrong call: property_prices; answer (no value at statistics.house.median_price_per_m2_eur in a property_prices result) | find_municipality(name=Dijon) > property_prices(insee_code=15064, period=2024) ERROR | Les données demandées ne sont pas disponibles ; le service de prix immobiliers n’a pas trouvé de transactions pour Dijon en 2024. Source : API property_prices (… |
| dvf-dijon-house-m2 | 3 | missing or wrong call: property_prices; answer (expected 2660) | find_municipality(name=Dijon) > property_prices(insee_code=21054, period=2024) | Je ne peux pas fournir cette information, les données nécessaires ne sont pas disponibles. |
| dvf-toulouse-apartment-m2 | 1 | missing or wrong call: property_prices | find_municipality(name=Toulouse) > property_prices(insee_code=11054, period=2025) | Le prix médian des appartements à Toulouse en 2025 est de **1 710 € par m²** selon les données publiées par le DVF. Source : `property_prices` (insee_code 31555… |
| dvf-toulouse-apartment-m2 | 2 | missing or wrong call: property_prices; answer (no value at statistics.apartment.median_price_per_m2_eur in a property_prices result) | find_municipality(name=Toulouse) > property_prices(insee_code=31064, period=2025) | Le prix médian au m² des appartements vendus à Toulouse en 2025 n’est pas disponible dans les données fournies. Les outils ne donnent pas cette information. Sou… |
| dvf-toulouse-apartment-m2 | 3 | missing or wrong call: property_prices; answer (no value at statistics.apartment.median_price_per_m2_eur in a property_prices result) | find_municipality(name=Toulouse) > property_prices(insee_code=21101, period=2025) | Le prix médian au m² des appartements à Toulouse en 2025 est de 1500 €/m². Source : API DVF, recherche `property_prices` avec le code INSEE 31555 et la période … |
| dvf-paris-11-apartment-m2 | 1 | missing or wrong call: property_prices; answer (no value at statistics.apartment.median_price_per_m2_eur in a property_prices result) | none | Je ne dispose pas des données nécessaires pour le 11e arrondissement de Paris en 2025. Les outils disponibles ne permettent pas de préciser le prix médian au m²… |
| dvf-paris-11-apartment-m2 | 2 | missing or wrong call: property_prices; answer (no value at statistics.apartment.median_price_per_m2_eur in a property_prices result) | property_prices(insee_code=75011, period=2025) ERROR | Le prix médian au m² des appartements dans le 11e arrondissement de Paris en 2025 n’est pas disponible selon les données de la source. Réponse : aucun chiffre n… |
| dvf-paris-11-apartment-m2 | 3 | missing or wrong call: property_prices; answer (no value at statistics.apartment.median_price_per_m2_eur in a property_prices result) | property_prices(insee_code=75200, period=2025) ERROR | Je ne trouve pas d'information sur le prix médian des appartements dans le 11e arrondissement de Paris en 2025. Le calcul n’a pas été effectué avec les données … |
| dvf-strasbourg-not-covered | 3 | missing or wrong call: property_prices | none | Les données de prix médians par m² pour Strasbourg en 2025 ne sont pas disponibles, car la fonction `property_prices` ne fournit pas d’information pour les muni… |
| companies-toulouse-naf-62-02a | 1 | missing or wrong call: search_companies | find_municipality(name=Toulouse) > search_companies(text=62.02A, limit=25) | Il n'existe pas d'entreprises actives ayant pour activité principale le conseil en systèmes et logiciels informatiques (code NAF 62.02A) et un établissement à T… |
| companies-toulouse-naf-62-02a | 3 | missing or wrong call: search_companies | find_municipality(name=Toulouse) > search_companies(text=62.02A, municipality_code=31111, limit=1) | 0 entreprises actives correspondent à ce critère. Source : résultat du service de recherche d’entreprises qui indique un total de résultats égal à 0. 0 |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
