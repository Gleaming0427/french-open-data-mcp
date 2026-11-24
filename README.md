# french-open-data-mcp

MCP server for French public data (companies, property prices, Légifrance) and an
orchestrator for any OpenAI-compatible LLM, such as Olala.

The model does not answer from memory. It calls tools, and each tool result carries a
`source` field that the answer cites.

## Architecture

```
 question ──▶ MCP client ──────────────▶ LLM (OpenAI-compatible API, tool calling)
              (this repo's orchestrator,   e.g. Olala, Ollama, vLLM
               or Open WebUI, ...)
                  │
                  ├──▶ MCP server "french-open-data" (this repo)
                  │       ├─ Recherche d'entreprises API  (companies: Sirene + RNE)
                  │       ├─ geo.api.gouv.fr              (municipality codes)
                  │       ├─ data.gouv.fr Tabular API     (DVF property sales)
                  │       └─ Légifrance via PISTE         (optional, needs credentials)
                  │
                  └──▶ official data.gouv.fr MCP server (optional, https://mcp.data.gouv.fr/mcp)
```

Three separate parts:

1. **The model** only needs an OpenAI-compatible `/chat/completions` endpoint that supports `tools`.
2. **The MCP server** holds the code that calls the public APIs. It runs over stdio (same
   machine as the client) or Streamable HTTP (remote, with a bearer token).
3. **The MCP client** passes the tool list to the model, runs the tools the model asks for,
   and sends the results back. Neither Olala nor Ollama connects to an MCP server by itself.

## Tools

| Tool | Data source | Key | Notes |
|---|---|---|---|
| `search_companies` | Recherche d'entreprises API (DINUM) | none | Name, address, director, SIREN/SIRET; filters: postcode, department, NAF code |
| `company_profile` | same | none | Directors (no birth date or nationality), published financials, labels, collective agreements |
| `find_municipality` | Découpage administratif API (geo.api.gouv.fr) | none | Name → INSEE code |
| `property_prices` | DVF géolocalisées via the data.gouv.fr Tabular API | none | Median and quartile price per m², houses and apartments, per municipality and year |
| `search_legifrance` | Légifrance API (DILA) via PISTE | PISTE OAuth | Only registered when `LEGIFRANCE_CLIENT_ID` and `LEGIFRANCE_CLIENT_SECRET` are set. **Not tested against the live API.** |
| `read_legifrance_article` | same | PISTE OAuth | Article text and dates of validity. **Not tested against the live API.** |

All tools are read-only. They return compact JSON to fit small context windows
(Olala mini has 32K tokens).

## What was checked, and what it changes

The starting point was a proposal to pair a model hosted in France with an MCP server
calling State APIs (SIRENE, DVF, Légifrance). Each claim was checked against the
primary source on 2026-11-23/24. Findings that shaped the code:

**Olala on OVHcloud AI Endpoints.** The model card and the OVHcloud catalogue page both
list `Olala-v1.0-mini-7A1B` on AI Endpoints, base URL
`https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`, with function calling, reasoning and
streaming, a 32K context and the Apache 2.0 licence. Rate limits on the catalogue page:
2 requests per minute per IP and per model without a key, 400 per minute per Public Cloud
project and per model with a key. The catalogue page showed the price as "Free" on
2026-11-23. The model card states that "Ollama, LM Studio and the official llama.cpp,
vLLM and mlx-lm cannot load Olala 1.0 mini yet". So "Olala on Ollama" is not possible
today: with Ollama, use another tool-calling model (the Ollama tool-calling guide uses
`qwen3`). To run Olala yourself, use OVHcloud's forks (vLLM, llama.cpp, MLX) listed on
the model card (on a Mac: Quick start, section 3).

**The model card's own limits.** It recommends short, single-purpose requests, and lists as
out of scope "answering from memory where accuracy matters: facts, figures, legal, medical
or financial information" and decisions with legal effects without review by a qualified
person. The orchestrator therefore handles each question separately and instructs the model
to answer only from tool results.

**The official data.gouv.fr MCP server** (`https://mcp.data.gouv.fr/mcp`) is described as
experimental by data.gouv.fr. It is read-only and needs no key. Its 10 tools search the
data.gouv.fr catalogue, read tabular resources and describe third-party APIs (including
their OpenAPI specifications). It has no tool that queries Sirene, DVF or Légifrance
directly. This server fills that gap; both can be used together (see `config.example.json`).

**"SIRENE".** The free Recherche d'entreprises API is not full access to the Sirene
database: it searches companies by name or address, excludes companies that opted out of
public disclosure, and allows 7 requests per second per IP and 30 per second per ASN. Its
documentation notes that the ASN limit is likely to be hit from public clouds, which
matters when the server runs on a VPS. For full Sirene data, the API documentation points
to https://api.gouv.fr/guides/quelle-api-sirene. Results include the RNE flag `opposition_diffusion_commerciale`
(objection to the reuse of the company's data for commercial prospecting, GDPR art. 21);
it is returned as `objects_to_commercial_prospecting` and must be honoured for any
prospecting use.

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

**Open WebUI** has supported MCP natively since v0.6.31, over Streamable HTTP only.
Only administrators can add MCP servers, with optional bearer authentication. This
server's HTTP mode matches that setup.

**OVHcloud "VPS MCP".** This page markets the standard VPS range for hosting MCP servers.
On 2026-11-23 the lowest tier shown on that page was VPS-2 (4 vCores, 8 GB RAM) from
€7.21 excl. VAT per month.

**Data location.** Questions and tool results are sent to the model host. The model card
describes AI Endpoints as "hosted in Europe". Where the model, the MCP server and the
client run decides where this traffic goes; the public APIs themselves are operated by
French administrations. AI Endpoints is covered by the OVHcloud Public Cloud Special
Conditions (Appendix 10, "Specific Conditions – AI Endpoints"): read them for how request
data is handled.

## Quick start

Requires Python 3.11 or later (tested with 3.11).

```bash
python3.11 -m venv .venv
```

```bash
source .venv/bin/activate && pip install -e .
```

### 1. Check without a model (no API key)

```bash
python -m unittest discover -s tests -t .
```

The tests use a fake OpenAI-compatible server (`tools/fake_llm.py`) and in-memory MCP
servers. They make no network calls.

### 2. With the Olala API

Create an API key for the Olala API (see the "Getting started" guide linked from the model card),
then put it in a `.env` file at the root of the project:

```bash
cp .env.example .env
```

Open `.env` in an editor and fill in the line `OLALA_API_KEY=`. The file is listed in
`.gitignore`, so it is not committed. Both the orchestrator and the server read `.env` from
the current directory at startup (another file: `--env-file PATH`). A variable already set
in the terminal (`export OLALA_API_KEY=...`) takes precedence over the file. Then:

```bash
cp config.example.json config.json
```

```bash
python -m fr_open_data.orchestrator --config config.json --check
```

```bash
python -m fr_open_data.orchestrator --config config.json --question "Median apartment price per m2 in Beaune in 2025?"
```

Without `--question`, the orchestrator starts an interactive prompt. The `params` block is
added to every request. The model card recommends `temperature 0.8, top_p 0.9, top_k 40`.
`reasoning_effort` (`low`, `medium`, `high`) is the parameter shown in the Olala API
example.

### 3. Olala on a Mac (local, mlx-engine)

Ollama and LM Studio cannot load Olala yet (model card). On a Mac with Apple Silicon,
OVHcloud's fork of mlx-engine serves it with an OpenAI-compatible API. Requirements stated
by the MLX model card and the fork: Apple Silicon, macOS 14 or later, Python 3.11. The model
card recommends 16 GB of memory. The `q5e6` folder (routed experts in 5 bits, the rest in
6 bits) is 4.9 GB.

In a folder outside this project:

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
server. `--context-length` goes up to 32,768 (model card). The server must stay running
while the orchestrator is used.

Then, in this project: copy the `olala_mlx_local` block from `_other_llms` into `llm` in
`config.json`, and put the same `MLX_ENGINE_API_KEY` value in `.env`. Only `--check` has
been run with this setup so far (2026-11-24); it returned `Model: 'OK'`.

Server constraints, read in the fork's source code (commit `58083ca`, 2026-11-18): responses
are streamed only (`stream: true`); `temperature` and `top_k` are required; `tool_choice`
accepts `auto` or `none`; `reasoning_effort` goes in `chat_template_kwargs`; the request is
rejected (HTTP 400) when a past tool call has arguments that are not valid JSON, so the
orchestrator sends `{}` in that case. The `olala_mlx_local` block follows these constraints.

### 4. With another local model (Ollama)

Copy the `ollama_local` block from `_other_llms` into `llm`. Ollama serves an
OpenAI-compatible API at `http://localhost:11434/v1` and supports tools and streaming.

### 5. As a remote server (VPS, Open WebUI)

```bash
export MCP_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

(or set `MCP_TOKEN` in `.env`)

```bash
fr-open-data-server --http --host 127.0.0.1 --port 8765 --domain mcp.example.org
```

Put an HTTPS reverse proxy in front of `127.0.0.1:8765`. The server refuses to listen
beyond localhost without `MCP_TOKEN`. In Open WebUI (admin settings, Integrations), add a
connection of type "MCP (Streamable HTTP)" with URL `https://mcp.example.org/mcp` and
Bearer authentication using the token.

### 6. In any MCP client over stdio

Command: `python -m fr_open_data.server` (run from the virtual environment).

## Configuration (`config.json`)

| Key | Meaning |
|---|---|
| `llm.base_url`, `llm.model` | OpenAI-compatible endpoint and model id |
| `llm.api_key_env` | Name of the environment variable holding the key (never the key itself); it can be set in `.env` |
| `llm.stream` | `true` by default (the Olala MLX server only accepts streaming) |
| `llm.params` | Added to every request (sampling, reasoning effort) |
| `mcp_servers[].command` | Start the server as a subprocess (stdio) |
| `mcp_servers[].url`, `token_env` | Connect over Streamable HTTP, optional bearer token |
| `mcp_servers[].tools` | Keep only these tools (small models choose better among few tools) |
| `max_turns`, `max_result_chars` | Limits of the tool loop |

An MCP server that cannot be reached is skipped with a warning. Tool errors are passed to
the model as text, so it can report them instead of guessing.

## Limits

- **Légifrance is untested** against the live API. Request building follows the published
  specification and response parsing is defensive. Verify before relying on it.
- **DVF statistics are an approximation.** Only sales of a single dwelling are kept, and
  the price per m² of houses includes the land. It is not an official index.
  A large arrondissement takes about 30 s (Paris 11th, 2025: about 6,400 rows, measured
  during development).
- **Small models and tools.** Olala mini is a small mixture-of-experts model (6.8B
  parameters in total; about 1B active according to the model card, 1.5B according to the
  OVHcloud catalogue). Its tool-call reliability on these tools has not been measured here. Restrict the tool list per server
  if the model picks the wrong tool.
- **Not advice.** Answers are not legal, tax or financial advice. Check important
  answers against the cited source.

## Project layout

```
fr_open_data/
  server.py          MCP server (stdio or Streamable HTTP + bearer token)
  companies.py       Recherche d'entreprises API
  municipalities.py  geo.api.gouv.fr
  dvf.py             DVF via the data.gouv.fr Tabular API
  legifrance.py      Légifrance via PISTE (optional, untested live)
  orchestrator.py    tool loop between an OpenAI-compatible LLM and MCP servers
  llm.py             streaming chat client (standard library)
  http.py            HTTP helper (User-Agent, 429/Retry-After, one retry)
  envfile.py         .env reader (standard library)
tools/fake_llm.py    fake OpenAI-compatible server for tests
tests/               offline tests (unittest)
config.example.json
.env.example         template for .env (API keys, tokens)
```

## Sources (consulted 2026-11-23/24)

- Olala model card: https://huggingface.co/OVHaiLLM/Olala-v1.0-mini-7A1B
- Olala MLX model card: https://huggingface.co/OVHaiLLM/Olala-v1.0-mini-7A1B-MLX
- OVHcloud's mlx-engine fork: https://github.com/OVHai-LLM/mlx-engine
- OVHcloud catalogue, Olala: https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/olala-v1-0-mini-7a1b/
- AI Endpoints, function calling: https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-function-calling
- AI Endpoints, catalogue API: https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-catalog-api
- OVHcloud VPS MCP: https://www.ovhcloud.com/fr/vps/vps-mcp/
- data.gouv.fr MCP server: https://github.com/datagouv/datagouv-mcp and https://guides.data.gouv.fr/intelligence-artificielle/le-serveur-mcp-de-data.gouv.fr
- Recherche d'entreprises API: https://recherche-entreprises.api.gouv.fr/openapi.json and https://www.data.gouv.fr/dataservices/api-recherche-dentreprises
- DVF (DGFiP): https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/
- DVF géolocalisées: https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/
- Légifrance on data.gouv.fr: https://www.data.gouv.fr/dataservices/legifrance
- Légifrance API specification: https://github.com/betagouv/api_gouv_swaggers (`swaggers/api-legifrance-v2.json`)
- Ollama, tool calling and OpenAI compatibility: https://docs.ollama.com/capabilities/tool-calling and https://docs.ollama.com/api/openai-compatibility
- Open WebUI, MCP: https://docs.openwebui.com/features/extensibility/mcp
- MCP Python SDK (v2): https://pypi.org/project/mcp/
