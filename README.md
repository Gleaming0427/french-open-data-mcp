# french-open-data-mcp

MCP server for French public data (companies, property prices, Légifrance) and an
orchestrator for a local LLM, such as Olala on a Mac.

Everything runs on your machine: the model, the orchestrator and the MCP server. The model
does not answer from memory. It calls tools, and each tool result carries a `source` field
that the answer cites.

## Architecture

```
 question ──▶ orchestrator (this repo) ──────▶ local LLM, OpenAI-compatible API with tool calling
                  │                             Olala via mlx-engine (http://127.0.0.1:8000/v1)
                  │                             or Ollama (http://localhost:11434/v1)
                  │
                  └──▶ MCP server "french-open-data" (this repo, subprocess over stdio)
                          ├─ Recherche d'entreprises API  (companies: Sirene + RNE)
                          ├─ geo.api.gouv.fr              (municipality codes)
                          ├─ data.gouv.fr Tabular API     (DVF property sales)
                          └─ Légifrance via PISTE         (optional, needs credentials)
```

Three separate parts, all on the same machine:

1. **The model** is served locally by an OpenAI-compatible `/chat/completions` endpoint
   that supports `tools`.
2. **The MCP server** holds the code that calls the public APIs. The orchestrator starts it
   as a subprocess and talks to it over stdio.
3. **The orchestrator** passes the tool list to the model, runs the tools the model asks
   for, and sends the results back. Neither Olala nor Ollama connects to an MCP server by
   itself.

**What leaves the machine.** The questions, the answers and the model stay on the
machine. The tools need the Internet to fetch the data: each tool call sends the arguments
chosen by the model (company name or SIREN, postcode, municipality name or INSEE code,
Légifrance search words) to the public APIs listed above; the DVF tool also reads the
data.gouv.fr catalogue to find the yearly files. This project's code makes no other
requests. Installing the model downloads it once from Hugging Face. If `llm.base_url` in
`config.json` points to another machine, the orchestrator and the benchmark print a warning
at startup: questions and tool results would then be sent there.

## Tools

| Tool | Data source | Key | Notes |
|---|---|---|---|
| `search_companies` | Recherche d'entreprises API (DINUM) | none | Name, address, director, SIREN/SIRET; filters: municipality name or INSEE code, postcode, department (any establishment), NAF codes and activity section (main activity). Returns the filters applied, the total count and up to 25 companies |
| `company_profile` | same | none | Directors (no birth date or nationality), published financials, labels, collective agreements |
| `find_municipality` | Découpage administratif API (geo.api.gouv.fr) | none | Name → INSEE code, ranked by population; arrondissements of Paris, Lyon and Marseille by name ("Paris 11e") |
| `property_prices` | DVF géolocalisées via the data.gouv.fr Tabular API | none | Median and quartile price per m², houses and apartments, per municipality (name or INSEE code) and year or half-year |
| `search_legifrance` | Légifrance API (DILA) via PISTE | PISTE OAuth | Only registered when `LEGIFRANCE_CLIENT_ID` and `LEGIFRANCE_CLIENT_SECRET` are set. **Not tested against the live API.** |
| `read_legifrance_article` | same | PISTE OAuth | Article text and dates of validity. **Not tested against the live API.** |

All tools are read-only. They return compact JSON to fit small context windows
(Olala mini has 32K tokens).

## What was checked, and what it changes

Each claim below was checked against the primary source on 2026-11-23/24. Findings that
shaped the code:

**Running Olala locally.** The model card states that "Ollama, LM Studio and the official
llama.cpp, vLLM and mlx-lm cannot load Olala 1.0 mini yet" and points to OVHcloud's forks
(vLLM, llama.cpp, MLX). On a Mac, this project uses the mlx-engine fork (Quick start,
step 3). With Ollama, use another tool-calling model (the Ollama tool-calling guide uses
`qwen3`). The model card gives 6.8B parameters in total, about 1B active per token, a 32K
context and the Apache 2.0 licence.

**The model card's own limits.** It recommends short, single-purpose requests, and lists as
out of scope "answering from memory where accuracy matters: facts, figures, legal, medical
or financial information" and decisions with legal effects without review by a qualified
person. The orchestrator therefore handles each question separately and instructs the model
to answer only from tool results.

**"SIRENE".** The free Recherche d'entreprises API is not full access to the Sirene
database: it searches companies by name or address, excludes companies that opted out of
public disclosure, and allows 7 requests per second per IP and 30 per second per ASN. For
full Sirene data, the API documentation points to
https://api.gouv.fr/guides/quelle-api-sirene. Results include the RNE flag
`opposition_diffusion_commerciale` (objection to the reuse of the company's data for
commercial prospecting, GDPR art. 21); it is returned as `objects_to_commercial_prospecting`
and must be honoured for any prospecting use.

**DVF.** The DGFiP states that the DVF file contains personal data, that its use must not
allow re-identification (article R112 A-3 of the Livre des procédures fiscales) and that
reuse must not allow indexing by search engines. The `property_prices` tool returns only
aggregated statistics per municipality. DVF does not cover Alsace, Moselle or Mayotte.
In October 2026, the per-municipality files were replaced by yearly files; the old files
are marked as archived and due for deletion. The tool uses the data.gouv.fr Tabular API on
the yearly files instead, which has been possible since 2026-11-18. Paris, Lyon and
Marseille are published per arrondissement.

**Légifrance** requires a PISTE account, acceptance of the API terms and OAuth
`client_credentials` credentials. The official records consulted only give the sandbox
URLs; the production URLs used by default come from consistent third-party sources and can
be overridden (`LEGIFRANCE_TOKEN_URL`, `LEGIFRANCE_API_URL`).

## Quick start

### 1. Install this project

Requires Python 3.11 or later.

```bash
git clone https://github.com/Gleaming0427/french-open-data-mcp.git && cd french-open-data-mcp
```

```bash
python3.11 -m venv .venv
```

```bash
source .venv/bin/activate && pip install -e .
```

### 2. Check without a model

```bash
python -m unittest discover -s tests -t .
```

The tests use a fake OpenAI-compatible server (`tools/fake_llm.py`) and in-memory MCP
servers. They make no network calls. Messages such as "Tool … failed" are expected: some
tests check error cases.

### 3. Run Olala on a Mac (mlx-engine)

Requirements stated by the MLX model card and the fork: a Mac with Apple Silicon,
macOS 14 or later, Python 3.11. The model card recommends 16 GB of memory. The `q5e6`
folder (routed experts in 5 bits, the rest in 6 bits) is 4.9 GB.

In a separate terminal and a folder outside this project:

```bash
git clone https://github.com/OVHai-LLM/mlx-engine.git && cd mlx-engine
```

```bash
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/hf download OVHaiLLM/Olala-v1.0-mini-7A1B-MLX --include "q5e6/*" --local-dir ./olala-mlx
```

```bash
export MLX_ENGINE_API_KEY=choose-a-value
```

```bash
.venv/bin/python -m mlx_engine.server --model ./olala-mlx/q5e6 --host 127.0.0.1 --port 8000 --context-length 8192 --parallel-sessions 1
```

On an M1, the MLX model card says to run `export OLALA_MOE_V3=0` before starting the
server. `--context-length` goes up to 32,768 (model card). Keep this terminal open while
you use the orchestrator. With `--host 127.0.0.1`, the server only accepts connections
from this Mac.

Server constraints, read in the fork's source code (commit `58083ca`, 2026-11-18): responses
are streamed only (`stream: true`); `temperature` and `top_k` are required; `tool_choice`
accepts `auto` or `none`; `reasoning_effort` goes in `chat_template_kwargs`; the request is
rejected (HTTP 400) when a past tool call has arguments that are not valid JSON, so the
orchestrator sends `{}` in that case. The default `llm` block of `config.example.json`
follows these constraints, with the sampling recommended by the model card
(`temperature 0.8, top_p 0.9, top_k 40`).

### 4. Ask questions

In this project's folder, with its virtual environment active:

```bash
cp config.example.json config.json
```

```bash
cp .env.example .env
```

Open `.env` in an editor and set `MLX_ENGINE_API_KEY=` to the value chosen in step 3. The
file is listed in `.gitignore`, so it is not committed. The orchestrator and the server read
`.env` from the current directory at startup (another file: `--env-file PATH`). A variable
already set in the terminal takes precedence over the file.

```bash
python -m fr_open_data.orchestrator --config config.json --check
```

```bash
python -m fr_open_data.orchestrator --config config.json --question "Prix médian des appartements à Beaune en 2025 ?"
```

Without `--question`, the orchestrator starts an interactive prompt.

Tested on 2026-11-24 with Olala through mlx-engine on a Mac: `--check` returned
`Model: 'OK'`, and for the question above the model called `find_municipality`, then
`property_prices` with the INSEE code of Beaune (21054) and the year 2025.

### 5. With another local model (Ollama)

Copy the `ollama_local` block from `_other_llms` into `llm` in `config.json`. Ollama serves
an OpenAI-compatible API at `http://localhost:11434/v1` that supports tools; the block turns
streaming off and omits `tool_choice`, and the context length must be raised with a
Modelfile (see section 8). The model must support tool calling.

### 6. In another MCP client on the same machine

Command: `python -m fr_open_data.server` (run from the virtual environment). The server
speaks MCP over stdio.

### 7. Measure (benchmark)

`bench/run.py` asks the fixed questions of `bench/questions.json` several times and checks
each answer: the expected tool calls must succeed with the expected arguments (for DVF: the
result must be for the right municipality and period), and the answer must contain the
figure returned by the tool in that run (or, for Strasbourg, which DVF does not cover, no
euro amount). With the model server running:

```bash
python -m bench.run --config config.json --runs 3 --label "Olala q5e6, MacBook Pro M2 Max"
```

Results go to `bench/results/<date>-<time>/`: `summary.md` (tables), `runs.jsonl` (one line
per run, with the full answer and the tools called) and `meta.json` (machine, model,
configuration, commit). Token counts come from the model server when it reports them
(mlx-engine does, at the end of each response); tokens/s are computed over the whole model
request, so they include prompt processing. Runs during which a public API failed
(network, HTTP 429 or 5xx) are counted and shown separately: they are not the model's
fault. The script does not measure memory: read the model server's memory use in Activity
Monitor during the run. The summary also counts the answers that name the source of the
data returned (keyword check, not part of the success criterion). `--only id1,id2` runs some
questions only. `--questions
bench/questions_holdout.json` runs the held-out questions (see Limits).

`bench/questions_holdout2.json` is a second held-out set of 16 questions, written after the
tools were frozen (commit `1f310a9`). Before running a model on it, check that the data each
question needs exists, without any model:

```bash
python -m bench.run --validate --questions bench/questions_holdout2.json
```

A question that fails validation is corrected or removed before the model run, never after.
On macOS, `meta.json` and `summary.md` record the Mac model, chip, CPU and GPU core counts
(`system_profiler`), memory and macOS version. `--server-version` records the model server,
e.g. `--server-version "mlx-engine (OVHcloud fork) $(git -C ../mlx-engine log -1 --format=%h)"`.

The failures table lists the calls made and the start of each wrong answer; `python -m bench.run --summarize latest`
rebuilds `summary.md` of the latest results with the current version of the script and
re-applies the checks of the questions file to the stored answers (the summary written
during the run is kept as `summary-as-run.md`).

### 8. Compare with another local model (Ollama)

The benchmark can measure any model served by Ollama on the same questions, with
`bench/config.ollama.json` (same MCP server and limits as `config.example.json`). From the
Ollama documentation (consulted 2026-11-24): its OpenAI-compatible endpoint supports tools
but lists `tool_choice` as unsupported, so the config omits it; streaming with tools is
documented only for the native API, so the config turns streaming off; the default context
is 4k tokens below 24 GiB of VRAM, and the OpenAI-compatible endpoint cannot change it per
request: a model with `PARAMETER num_ctx` must be created. The Olala server ran with a
context of 8192 tokens, so:

```bash
ollama pull qwen3:8b
```

```bash
printf 'FROM qwen3:8b\nPARAMETER num_ctx 8192\n' > Modelfile.qwen3-8k && ollama create qwen3-8b-ctx8k -f Modelfile.qwen3-8k
```

Then run the 24 held-out questions (both files in one run):

```bash
python -m bench.run --config bench/config.ollama.json --model qwen3-8b-ctx8k --runs 3 --questions bench/questions_holdout.json bench/questions_holdout2.json --label "qwen3:8b (Ollama), held-out 1+2" --server-version "$(ollama --version)"
```

What differs from the Olala runs, to state with any comparison: Ollama runs GGUF models on
its own engine and Olala ran on MLX, so speeds are not comparable; sampling and thinking use
each model's defaults in Ollama (Olala used the model card's sampling and
`reasoning_effort` low); the tool descriptions were adjusted while testing Olala.

### Raw results

`bench/results/` holds the raw results of the runs on the M2 Max (`meta.json`, `runs.jsonl`
with every answer and tool result, `summary.md`):

| Folder | Code | Questions | Success |
|---|---|---|---|
| `20261124-121208` | tools v1 (`8422176`) | `questions.json` | 12/24 |
| `20261124-132440` | tools v2 (`f31ebe4`) | `questions.json` | 21/24 |
| `20261124-143946` | tools v2 (`f31ebe4`) | `questions.json` | 20/24 |
| `20261124-150321` | interrupted run: 14 of 24 runs, no summary | `questions.json` | 11/14 |
| `20261124-150625` | tools v3 (`729b340`) | `questions.json` | 23/24 |
| `20261124-152301` | tools v3 (`729b340`) | `questions_holdout.json` | 18/24 as run, 20/24 re-checked |
| `20261124-160832` | tools v3 (`1bdba5b`) | `questions_holdout2.json` | 37/48 |


## Configuration (`config.json`)

| Key | Meaning |
|---|---|
| `llm.base_url`, `llm.model` | Local OpenAI-compatible endpoint and model id (mlx-engine serves one model and ignores the id) |
| `llm.api_key_env` | Name of the environment variable holding the key (never the key itself); it can be set in `.env`. `null` for Ollama |
| `llm.stream` | `true` (mlx-engine only accepts streaming) |
| `llm.max_tokens` | Maximum length of each model reply (default 4096) |
| `llm.params` | Added to every request (sampling, `chat_template_kwargs`) |
| `mcp_servers[].command` | Command that starts the MCP server as a subprocess (stdio) |
| `mcp_servers[].tools` | Keep only these tools (small models choose better among few tools) |
| `system_prompt` | Replaces the default instructions given to the model |
| `max_turns`, `max_result_chars` | Limits of the tool loop (model requests per question, characters of a tool result sent to the model) |
| `max_tool_calls` | Tools actually run per question (default 10); beyond it, the model is told to answer with the results it has. The benchmark runs never exceeded 5 |

An MCP server that cannot be started is skipped with a warning. Tool errors are passed to
the model as text, so it can report them instead of guessing.

## Limits

- **Légifrance is untested** against the live API. Request building follows the published
  specification and response parsing is defensive. Verify before relying on it.
- **DVF statistics are an approximation.** Only sales of a single dwelling are kept, and
  the price per m² of houses includes the land. It is not an official index.
  The rows of a municipality are read in one request to the Tabular API JSON export:
  Toulouse 2025, 24,586 rows, took 2.3 s on 2026-11-24. Beyond the export limit (50,000
  rows in api-tabular's default configuration), the tool reads at most 12,000 rows and
  says that the figures are partial.
- **The data.gouv.fr Tabular API can be briefly unavailable.** On 2026-11-24 it answered
  HTTP 503 (PostgREST error PGRST002) for the DVF 2025 file while the other DVF files
  answered; the same query worked again shortly after. Each request is retried once; if it
  still fails, the tool returns the error and the model reports it.
- **Small model.** Olala mini has about 1B active parameters per token (model card). Its
  tool-call reliability on these tools has not been measured beyond the runs described
  here. In a second run of the question above (2026-11-24), after `property_prices` it also
  called `search_companies`, `company_profile` with the INSEE code instead of a SIREN (which
  failed), and `property_prices` twice more with the same arguments; the answer gave the
  median sale price (130,000 €), which matches the tool result, without the price per m².
  Since then, an identical repeated call reuses the first result instead of querying the
  API again, and the instructions ask the model to stop once a result answers the question;
  the effect on Olala has not been measured yet. Restrict the tool list (`tools` in
  `mcp_servers`) if the model picks the wrong tool.
- **First benchmark (2026-11-24, M2 Max 32 GB, Olala q5e6, 24 runs): 12/24.** The main
  failure: the model called `find_municipality` correctly, then passed another INSEE code to
  the next tool (for Dijon, twice 21054, the example code then written in the tool
  description). Two answers gave a figure that was not the one asked: one from another
  municipality's data while citing Dijon's code, one with no figure in the tool result at
  all. For Paris 11th it passed the postcode (75011). Since then: `property_prices` and
  `search_companies` take the municipality name (arrondissements included) and resolve it
  themselves; example codes were removed from the tool descriptions; a NAF code written in
  the search text is used as a NAF filter; a Paris postcode is converted to the
  arrondissement code; an empty statistic says that there is no figure.
- **Second benchmark (same machine and questions, tools v2): 20/24** (a first run with the same
  code gave 21/24; its 3 failures were all on the company count: once "4", twice no call). All DVF questions
  succeeded except one Paris run, where the model asked for "Paris" without the
  arrondissement and gave up after the error. The company count failed 3/3: the search was
  right, but two answers gave the number of companies listed (5) instead of the total
  (1,501), and one said it could not answer. Since then, the Paris error asks for the
  arrondissement by name, and the search result states the total in a sentence. These
  changes were made on the same 8 questions, so a new run on them would be optimistic:
  `bench/questions_holdout.json` holds 8 other questions, written before any run on them and
  not used to adjust the tools.
- **Third benchmark (tools v3), same 8 questions: 23/24** (optimistic: the tools were
  adjusted on these questions). The remaining failure: a company count answered "5".
- **Held-out questions (tools v3, never used to adjust the tools): 18/24 as scored during
  the run, 20/24 with the corrected name check.** The check for the SIREN question required
  the whole API name, "TOTALENERGIES SE (TOTALENERGIE SE)"; it was changed to
  "TOTALENERGIES" in commit `3fd3ad1`, 22 seconds after the run started and before its
  results were known, and two answers reading "TOTALENERGIES SE" then pass. Both summaries
  are kept (`summary-as-run.md`, `summary.md`). Results by kind of question: municipality
  code 3/3; DVF prices (Nantes 2024, Bordeaux, Marseille 8th, Lyon 3rd 2024) 11/12, the
  failure being a run without any tool call; Metz (not covered) 3/3, no invented figure;
  company name from a SIREN 3/3 with the corrected check; **company count 0/3**: once the
  number listed (5) instead of the total (1,490), once the activity written in the search
  text (0 results), once "0" although the result gave 1,490. Counting from a search result
  is the weak point measured here.
- **Second held-out set (16 questions, written after the tools were frozen and checked with
  `--validate` before the run; tools v3, commit `1bdba5b`): 37/48.** Over both held-out sets:
  57/72 with the corrected name check, 79% (95% Wilson interval 68-87%); 55/72 as scored
  during the runs. The 3 runs of a question are not independent, so the real uncertainty is
  larger. By kind of question:

  | Kind | Success | What went wrong |
  |---|---|---|
  | Municipality code | 9/9 | |
  | DVF, town without arrondissements | 18/18 | |
  | DVF, arrondissement of Paris, Lyon or Marseille | 10/15 | asked for the whole city, put the INSEE code in the name field, or wrote an invalid name; no retry after the error |
  | DVF, half-year | 1/3 | asked for "2026-S2" or "2026-01" instead of "2026-S1" |
  | Area DVF does not cover | 9/9 | no invented figure |
  | Company count | 2/9 | number listed instead of the total; activity section passed as a NAF code; invented SIRENs; "0" although the result gave a total |
  | Company identity from a SIREN | 8/9 | the failure is a correct answer ("RENAULT") found with `search_companies` instead of `company_profile`, which the checks written before the run count as a failure |

  Among the failed held-out runs, every wrong figure given as an answer was a company count;
  for property prices, the failed runs said that the data was not available. Output: about
  1,300 tokens per question, 79.8 tokens/s end to end. Machine: MacBook Pro (Mac14,5),
  M2 Max with 12 CPU cores and 30 GPU cores, 32 GB, model server mlx-engine (OVHcloud fork)
  `58083ca`. An INSEE code in the `municipality` field is rejected by the tool; accepting it
  would be a tool change, to be measured on new questions.
- **Citing the source.** The instructions ask the model to cite the source given by the tool.
  A keyword check added after the runs (`cites_source` in `bench/run.py`: DVF, Sirene,
  Découpage administratif...), applied to the stored answers, finds the source of the data
  named in 34 of the 60 held-out answers where a tool returned data. Most of the others name
  the tool instead ("source: property_prices") or no source. This check is not part of the
  success criterion.
- **Not advice.** Answers are not legal, tax or financial advice. Check important
  answers against the cited source.

## Project layout

```
fr_open_data/
  server.py          MCP server (stdio)
  companies.py       Recherche d'entreprises API
  municipalities.py  geo.api.gouv.fr
  dvf.py             DVF via the data.gouv.fr Tabular API
  legifrance.py      Légifrance via PISTE (optional, untested live)
  orchestrator.py    tool loop between a local OpenAI-compatible LLM and MCP servers
  llm.py             streaming chat client (standard library)
  http.py            HTTP helper (User-Agent, one retry on 429/502/503/504 and network errors)
  envfile.py         .env reader (standard library)
bench/run.py         benchmark: fixed questions, checks, results to publish
bench/questions.json the questions and what each answer must contain
bench/questions_holdout*.json  held-out questions (not used to adjust the tools)
bench/config.ollama.json      configuration for measuring a model served by Ollama
tools/fake_llm.py    fake OpenAI-compatible server for tests
tests/               offline tests (unittest)
config.example.json
.env.example         template for .env (keys)
```

## Sources (consulted 2026-11-23/24)

- Olala model card: https://huggingface.co/OVHaiLLM/Olala-v1.0-mini-7A1B
- Olala MLX model card: https://huggingface.co/OVHaiLLM/Olala-v1.0-mini-7A1B-MLX
- OVHcloud's mlx-engine fork: https://github.com/OVHai-LLM/mlx-engine
- Recherche d'entreprises API: https://recherche-entreprises.api.gouv.fr/openapi.json and https://www.data.gouv.fr/dataservices/api-recherche-dentreprises
- DVF (DGFiP): https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/
- DVF géolocalisées: https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/
- Légifrance on data.gouv.fr: https://www.data.gouv.fr/dataservices/legifrance
- Légifrance API specification: https://github.com/betagouv/api_gouv_swaggers (`swaggers/api-legifrance-v2.json`)
- PostgREST error codes: https://github.com/PostgREST/postgrest/blob/main/docs/references/errors.rst
- data.gouv.fr Tabular API source code (JSON export, limits): https://github.com/datagouv/api-tabular
- Découpage administratif API specification (`boost` parameter): https://github.com/datagouv/api-geo (`definition.yml`)
- Ollama, tool calling and OpenAI compatibility: https://docs.ollama.com/capabilities/tool-calling and https://docs.ollama.com/api/openai-compatibility
- MCP Python SDK (v2): https://pypi.org/project/mcp/
