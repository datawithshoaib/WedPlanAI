# WedPlannerAI

A multi-agent wedding planning assistant. You fill in a wedding brief; a main planner agent sends two research workers out to search the web (venues and vendors, plus logistics and market pricing), then writes a client-ready plan with a budget, timeline, risks, and open questions. A second pass turns that plan into an "at a glance" dashboard. Every plan is saved to SQLite.

- **Backend**: FastAPI, LangChain agents, Groq (`openai/gpt-oss-120b`), Tavily search, SQLite. Managed with [uv](https://docs.astral.sh/uv/).
- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind v4, shadcn/ui on Base UI.

## Project structure

```text
.
├── backend/
│   ├── pyproject.toml          # uv project (deps, scripts, pytest + ruff config)
│   ├── uv.lock
│   ├── .env                    # API keys (not committed) – copy from .env.example
│   ├── data/planner.db         # SQLite database (created on first run)
│   ├── src/wedplanner/
│   │   ├── config.py           # Settings from env / backend/.env
│   │   ├── brief.py            # WeddingBrief model + validation + prompt text
│   │   ├── options.py          # Dropdown options + sample brief
│   │   ├── prompts.py          # All LLM prompts
│   │   ├── llm.py              # Groq chat model factory
│   │   ├── planner.py          # Orchestrator agent + progress events
│   │   ├── progress.py         # Progress event types
│   │   ├── research/           # Tavily search + research worker tools
│   │   ├── structure.py        # Structured "at a glance" extraction
│   │   ├── storage.py          # SQLite repository
│   │   ├── cli.py              # `uv run wedplanner` command-line planner
│   │   └── api/                # FastAPI app, schemas, service layer
│   ├── tests/                  # pytest suite (no API keys or network needed)
│   └── legacy/streamlit_app.py # Original Streamlit UI, kept for reference
├── frontend/                   # Next.js app
└── run.py                      # Starts backend + frontend together
```

## Setup

Requirements: [uv](https://docs.astral.sh/uv/getting-started/installation/), Node.js 20+, and API keys from [Groq](https://console.groq.com/keys) and [Tavily](https://app.tavily.com/).

```bash
# Backend: uv creates backend/.venv and installs the locked dependencies
cd backend
uv sync
cp .env.example .env        # then add your GROQ_API_KEY and TAVILY_API_KEY

# Frontend
cd ../frontend
npm install
cp .env.example .env.local  # NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run

To start both servers at once from the repo root:

```bash
python run.py
```

To run them separately:

```bash
# Terminal 1 – API on http://localhost:8000 (docs at /docs)
cd backend
uv run uvicorn wedplanner.api.main:app --reload --port 8000

# Terminal 2 – UI on http://localhost:3000
cd frontend
npm run dev
```

You can also plan from the terminal without the UI:

```bash
cd backend
uv run wedplanner                    # uses the built-in sample brief
uv run wedplanner my-brief.json -o plan.md
```

## Development

```bash
cd backend
uv run pytest            # API + domain tests with a fake planner (no network)
uv run ruff check .      # lint
uv run ruff format .     # format

cd ../frontend
npm run lint
npm run build
```

To add a dependency, run `uv add <package>` (or `uv add --dev <package>`) inside `backend/`.

## API

| Method | Route                | Description                                               |
| ------ | -------------------- | --------------------------------------------------------- |
| GET    | `/api/health`        | Key readiness, model name, saved plan count               |
| GET    | `/api/options`       | Dropdown options and a sample brief                       |
| POST   | `/api/plans/stream`  | Generate a plan, streaming NDJSON progress, then the plan |
| POST   | `/api/plans`         | Generate a plan and return it when finished (201)         |
| GET    | `/api/plans`         | List saved plans (`?limit=&offset=`)                      |
| GET    | `/api/plans/{id}`    | Fetch one plan                                            |
| DELETE | `/api/plans/{id}`    | Delete one plan                                           |
| DELETE | `/api/plans`         | Delete all plans                                          |

Each line of the stream is one JSON message:
`{"type":"progress","event":{"stage":"research_venues","status":"started","message":"…"}}`, then exactly one final line, either `{"type":"plan","plan":{…}}` or `{"type":"error","status_code":429,"detail":"…"}`. If the browser disconnects, the plan is still saved.

Errors return readable messages: 422 (invalid brief, e.g. a past date or max budget below min), 503 (missing or rejected API key), 429 (Groq rate limit), 504 (model timeout).

## How it works

```text
Next.js ──HTTP──> FastAPI ──> WeddingPlanner
                     │             ├─ Main planner agent (Groq)
                     │             │     ├─ research_venues_and_vendors  ──> Tavily ──> summariser LLM
                     │             │     └─ research_logistics_and_market ──> Tavily ──> summariser LLM
                     │             └─ Structured extraction (budget, timeline, risks…)
                     └──> SQLite (backend/data/planner.db)
```

A plan usually takes about a minute. Free-tier Groq keys have tight rate limits; the client retries automatically (`PLANNER_MAX_RETRIES`), which can add some time.

Generated plans are AI output based on live web research. Check the details yourself before making bookings, signing contracts, or committing money.
