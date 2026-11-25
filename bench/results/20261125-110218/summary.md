# Benchmark 2026-11-25T11:02:18+00:00

- Label: Phase 1: Olala q5e6, reasoning high
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "high"}}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: mlx-engine (OVHcloud fork) 58083ca
- Code: french-open-data-mcp 0.1.0, commit `fbc1474`
- Questions: `questions_dev.json`, 32 questions
- Runs: 2 per question, 64 in total

**Success: 56/64 (88%, 95% interval 77%-94%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 8/8 (100%, 95% interval 68%-100%) | 4/8 |
| dvf_town | 18/18 (100%, 95% interval 82%-100%) | 9/18 |
| dvf_arrondissement | 7/12 (58%, 95% interval 32%-81%) | 6/9 |
| dvf_half_year | 2/2 (100%, 95% interval 34%-100%) | 2/2 |
| dvf_not_covered | 8/8 (100%, 95% interval 68%-100%) | 1/1 |
| count_naf | 4/6 (67%, 95% interval 30%-90%) | 3/6 |
| count_section | 1/2 (50%, 95% interval 9%-91%) | 1/2 |
| company_siren | 8/8 (100%, 95% interval 68%-100%) | 3/8 |

Answers naming the source of the data returned: 29/54 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 171394 tokens in 2459 s of model requests, 69.7 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| municipality-code-beaune | 2/2 | 9.1 | 1.0 | 0 | 0 | 0 | 2/2 |
| municipality-code-montpellier | 2/2 | 13.0 | 1.0 | 0 | 0 | 0 | 1/2 |
| municipality-code-rennes | 2/2 | 13.7 | 1.0 | 0 | 0 | 0 | 1/2 |
| municipality-code-grenoble | 2/2 | 9.3 | 1.0 | 0 | 0 | 0 | 0/2 |
| dvf-beaune-apartment-m2 | 2/2 | 26.4 | 1.5 | 0 | 0 | 0 | 2/2 |
| dvf-dijon-house-m2 | 2/2 | 23.2 | 1.0 | 0 | 0 | 0 | 0/2 |
| dvf-toulouse-apartment-m2 | 2/2 | 23.3 | 1.0 | 0 | 0 | 0 | 0/2 |
| dvf-nantes-apartment-m2-2024 | 2/2 | 22.0 | 1.0 | 0 | 0 | 0 | 1/2 |
| dvf-bordeaux-house-m2 | 2/2 | 24.4 | 1.5 | 0 | 0 | 0 | 1/2 |
| dvf-lille-apartment-m2 | 2/2 | 26.6 | 1.0 | 0 | 0 | 0 | 0/2 |
| dvf-rennes-house-m2-2024 | 2/2 | 27.3 | 1.0 | 0 | 0 | 0 | 1/2 |
| dvf-nice-apartment-m2 | 2/2 | 30.4 | 1.5 | 0 | 0 | 0 | 2/2 |
| dvf-angers-house-m2 | 2/2 | 29.5 | 1.5 | 0 | 0 | 0 | 2/2 |
| dvf-paris-11-apartment-m2 | 2/2 | 63.0 | 2.0 | 0 | 1 | 0 | 2/2 |
| dvf-marseille-8-apartment-m2 | 2/2 | 33.1 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-lyon-3-apartment-m2-2024 | 2/2 | 47.6 | 1.5 | 0 | 0 | 0 | 2/2 |
| dvf-paris-15-apartment-m2-2024 | 1/2 | 37.9 | 0.5 | 0 | 0 | 0 | 0/1 |
| dvf-lyon-7-apartment-m2 | 0/2 | 72.0 | 1.0 | 0 | 1 | 0 | 0/1 |
| dvf-marseille-13-house-m2 | 0/2 | 63.7 | 1.0 | 0 | 1 | 0 | 0/1 |
| dvf-grenoble-apartment-m2-2026-s1 | 2/2 | 23.2 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-strasbourg-not-covered | 2/2 | 49.9 | 1.0 | 0 | 1 | 0 | 1/1 |
| dvf-metz-not-covered | 2/2 | 34.3 | 1.0 | 0 | 2 | 0 | - |
| dvf-colmar-not-covered | 2/2 | 38.5 | 1.0 | 0 | 2 | 0 | - |
| dvf-mamoudzou-not-covered | 2/2 | 47.5 | 0.5 | 0 | 1 | 0 | - |
| companies-toulouse-naf-62-02a | 1/2 | 94.0 | 1.5 | 0 | 0 | 0 | 1/2 |
| companies-bordeaux-naf-56-10a | 2/2 | 128.6 | 3.0 | 0 | 0 | 3 | 1/2 |
| companies-nantes-naf-10-71c | 1/2 | 91.6 | 3.5 | 0 | 4 | 0 | 1/2 |
| companies-grenoble-section-j | 1/2 | 113.8 | 1.5 | 0 | 0 | 0 | 1/2 |
| company-profile-siren | 2/2 | 20.2 | 1.0 | 0 | 0 | 0 | 0/2 |
| company-name-siren | 2/2 | 23.2 | 1.5 | 0 | 0 | 0 | 1/2 |
| company-profile-naf-380129866 | 2/2 | 32.0 | 1.5 | 0 | 0 | 1 | 1/2 |
| company-name-441639465 | 2/2 | 32.8 | 1.5 | 0 | 0 | 1 | 1/2 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| dvf-paris-15-apartment-m2-2024 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | Je ne peux pas répondre car les données demandées ne sont pas disponibles via les outils fournis. Le prix médian au m² par arrondissement n'est pas fourni par l… |
| dvf-lyon-7-apartment-m2 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | [answer truncated: token limit reached] |
| dvf-lyon-7-apartment-m2 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | find_municipality(name=Lyon) > property_prices(municipality=Lyon, period=2025) ERROR | Les données DVF ne sont pas disponibles pour l'arrondissement sans code INSEE spécifique. Je ne peux donc pas fournir le prix médian pour le 7e arrondissement d… |
| dvf-marseille-13-house-m2 | 1 | missing or wrong call: property_prices; answer (no successful property_prices call) | find_municipality(name=Marseille) > property_prices(municipality=Marseille, period=2025) ERROR | Les données demandées ne sont pas disponibles car les prix médians par arrondissement ne sont pas fournis par le service. (Source : aucune donnée disponible) |
| dvf-marseille-13-house-m2 | 2 | missing or wrong call: property_prices; answer (no successful property_prices call) | none | L'outil property_prices ne permet pas de filtrer les prix par arrondissement de Marseille, il fournit les prix médians que pour la commune. Je ne peux donc pas … |
| companies-toulouse-naf-62-02a | 1 | answer (expected 1501) | search_companies(municipality=Toulouse, naf_code=62.02A) > count_companies(municipality=Toulouse, naf_code=62.02A) | Il y a 5 entreprises actives. |
| companies-nantes-naf-10-71c | 1 | missing or wrong call: count_companies/search_companies; answer (no successful count_companies/search_companies call) | find_municipality(name=Nantes) > search_companies(municipality=Nantes, naf_code=10.71) ERROR > count_companies(municipality=Nantes, naf_code=10.71) ERROR > search_companies(municipality=Nantes, naf_code=10.71) ERROR > count_companies(municipality=Nantes, naf_code=10.71) ERROR | 0 Les recherches dans la base de données ne permettent pas de déterminer le nombre d'entreprises correspondant aux critères demandés. Par conséquent, le nombre … |
| companies-grenoble-section-j | 2 | answer (expected 1989) | search_companies(municipality=Grenoble, activity_section=J) | [answer truncated: token limit reached] |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
