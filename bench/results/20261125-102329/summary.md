# Benchmark 2026-11-25T10:23:29+00:00

- Label: Phase 1: Olala q5e6, reasoning medium
- Model: `olala` at `http://127.0.0.1:8000/v1`, params `{"temperature": 0.8, "top_p": 0.9, "top_k": 40, "chat_template_kwargs": {"reasoning_effort": "medium"}}`
- Machine: MacBook Pro (Mac14,5), Apple M2 Max, CPU 12 (8 Performance and 4 Efficiency) cores, GPU 30 cores, 32 GB memory, macOS 27.0.1
- Model server: mlx-engine (OVHcloud fork) 58083ca
- Code: french-open-data-mcp 0.1.0, commit `fbc1474`
- Questions: `questions_dev.json`, 32 questions
- Runs: 2 per question, 64 in total

**Success: 61/64 (95%, 95% interval 87%-98%)** (expected tool calls succeeded and the answer contains the tool's figure; runs of the same question are not independent, so the real uncertainty is larger).

| Category | Success | Names the source |
|---|---|---|
| municipality_code | 8/8 (100%, 95% interval 68%-100%) | 6/8 |
| dvf_town | 18/18 (100%, 95% interval 82%-100%) | 15/18 |
| dvf_arrondissement | 12/12 (100%, 95% interval 76%-100%) | 10/12 |
| dvf_half_year | 2/2 (100%, 95% interval 34%-100%) | 2/2 |
| dvf_not_covered | 8/8 (100%, 95% interval 68%-100%) | 0/1 |
| count_naf | 6/6 (100%, 95% interval 61%-100%) | 4/6 |
| count_section | 0/2 (0%, 95% interval 0%-66%) | 0/2 |
| company_siren | 7/8 (88%, 95% interval 53%-98%) | 4/8 |

Answers naming the source of the data returned: 41/57 (runs where a tool returned data; keyword check, not part of the success criterion).

Model output: 115264 tokens in 1453 s of model requests, 79.3 tokens/s end to end (includes prompt processing).

| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |
|---|---|---|---|---|---|---|---|
| municipality-code-beaune | 2/2 | 8.5 | 1.0 | 0 | 0 | 0 | 2/2 |
| municipality-code-montpellier | 2/2 | 11.5 | 1.0 | 0 | 0 | 0 | 2/2 |
| municipality-code-rennes | 2/2 | 11.5 | 1.0 | 0 | 0 | 0 | 1/2 |
| municipality-code-grenoble | 2/2 | 15.3 | 2.5 | 0 | 0 | 3 | 1/2 |
| dvf-beaune-apartment-m2 | 2/2 | 19.1 | 1.0 | 0 | 0 | 0 | 1/2 |
| dvf-dijon-house-m2 | 2/2 | 12.0 | 1.0 | 0 | 0 | 0 | 1/2 |
| dvf-toulouse-apartment-m2 | 2/2 | 16.1 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-nantes-apartment-m2-2024 | 2/2 | 26.0 | 2.0 | 0 | 1 | 0 | 2/2 |
| dvf-bordeaux-house-m2 | 2/2 | 20.7 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-lille-apartment-m2 | 2/2 | 17.5 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-rennes-house-m2-2024 | 2/2 | 17.2 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-nice-apartment-m2 | 2/2 | 16.5 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-angers-house-m2 | 2/2 | 22.4 | 1.5 | 0 | 0 | 0 | 1/2 |
| dvf-paris-11-apartment-m2 | 2/2 | 48.0 | 2.5 | 1 | 2 | 0 | 2/2 |
| dvf-marseille-8-apartment-m2 | 2/2 | 18.9 | 1.5 | 0 | 0 | 0 | 2/2 |
| dvf-lyon-3-apartment-m2-2024 | 2/2 | 28.4 | 1.5 | 0 | 1 | 0 | 2/2 |
| dvf-paris-15-apartment-m2-2024 | 2/2 | 40.6 | 2.0 | 0 | 2 | 0 | 1/2 |
| dvf-lyon-7-apartment-m2 | 2/2 | 46.4 | 1.5 | 0 | 0 | 0 | 1/2 |
| dvf-marseille-13-house-m2 | 2/2 | 20.3 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-grenoble-apartment-m2-2026-s1 | 2/2 | 14.9 | 1.0 | 0 | 0 | 0 | 2/2 |
| dvf-strasbourg-not-covered | 2/2 | 21.6 | 1.5 | 0 | 2 | 0 | 0/1 |
| dvf-metz-not-covered | 2/2 | 19.3 | 1.0 | 0 | 2 | 0 | - |
| dvf-colmar-not-covered | 2/2 | 23.3 | 1.0 | 0 | 2 | 0 | - |
| dvf-mamoudzou-not-covered | 2/2 | 20.0 | 0.5 | 0 | 1 | 0 | - |
| companies-toulouse-naf-62-02a | 2/2 | 51.0 | 1.5 | 0 | 0 | 0 | 1/2 |
| companies-bordeaux-naf-56-10a | 2/2 | 46.3 | 1.5 | 0 | 0 | 0 | 1/2 |
| companies-nantes-naf-10-71c | 2/2 | 35.4 | 1.0 | 0 | 0 | 0 | 2/2 |
| companies-grenoble-section-j | 0/2 | 69.0 | 1.5 | 0 | 0 | 0 | 0/2 |
| company-profile-siren | 1/2 | 18.9 | 1.0 | 0 | 0 | 0 | 2/2 |
| company-name-siren | 2/2 | 13.1 | 1.0 | 0 | 0 | 0 | 0/2 |
| company-profile-naf-380129866 | 2/2 | 18.9 | 1.0 | 0 | 0 | 0 | 0/2 |
| company-name-441639465 | 2/2 | 17.2 | 1.0 | 0 | 0 | 0 | 2/2 |

Unneeded calls: calls to tools the question does not need (looking up a municipality code is needed when the question names a town). Failed calls include tool errors the model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF).

## Failures

| Question | Run | Reason | Calls made | Answer (start) |
|---|---|---|---|---|
| companies-grenoble-section-j | 1 | answer (expected 1989) | search_companies(municipality=Grenoble, activity_section=J) | La recherche indique qu’il n’y a aucune entreprise active en section J à Grenoble. En effet, la requête `search_companies` avec la municipalité Grenoble et la s… |
| companies-grenoble-section-j | 2 | answer (expected 0) | count_companies(municipality=Grenoble, activity_section=J) > search_companies(text=information et communication, municipality=Grenoble) | [answer truncated: token limit reached] |
| company-profile-siren | 1 | missing or wrong call: company_profile/search_companies; answer (no value at {'company_profile': 'company.naf_activity_code', 'search_companies': 'results.0.naf_activity_code'} in the ['company_profile', 'search_companies'] result) | search_companies(text=SIREN: 552032534) | Il n’existe pas d’entreprise dont le SIREN est 552032534. La recherche via l’API « search_companies » ne retourne aucun résultat, donc le code NAF ne peut être … |

Memory used by the model server: not measured by this script (read it in Activity Monitor).
