# Bharat Krishi AI — Farmer Advisory Assistant

A working advisory prototype integrated into the existing FastAPI + React app. The assistant accepts typed or spoken questions, detects English/Hindi/Telugu, retrieves curated agriculture guidance from ChromaDB, personalizes with a saved farmer profile and recent history, and returns text plus browser speech.

## Project structure

```text
bharat-krishi-ai-web/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                         # Registers /api/advisory with FastAPI
│   │   └── advisory/
│   │       ├── query_processing.py         # Language, intent, entity parsing
│   │       ├── knowledge_base.py           # ChromaDB vectors and top-k retrieval
│   │       ├── seed_knowledge.json         # 24 curated multilingual entries
│   │       ├── ingest.py                   # Re-ingests the JSON seed file
│   │       ├── advisory_service.py         # Grounded generation and RAG context
│   │       ├── history_store.py            # SQLite farmer profiles/interactions
│   │       ├── schemas.py                  # Validated API request/response models
│   │       └── router.py                   # Query, profile, and history endpoints
│   └── tests/
│       └── test_farmer_advisory.py         # Query parsing and SQLite tests
└── frontend/
    └── src/
        ├── App.jsx                         # Sidebar entry and page route
        └── pages/
            ├── FarmerAdvisory.jsx          # Text/voice chat, profile, history
            └── FarmerAdvisory.css          # Responsive, mobile-friendly UI
```

## Flowchart mapped to code

| Flow block | Implementation |
|---|---|
| Farmer | The Farmer Advisory page and locally assigned farmer ID in `frontend/src/pages/FarmerAdvisory.jsx`. |
| Text input | The question textarea in the Farmer Advisory page. |
| Voice input | Browser Web Speech API speech recognition. The selected transcript is appended to the same textarea/query string as typed text. |
| Agricultural query processing | `backend/app/advisory/query_processing.py` normalizes whitespace/Unicode, detects Devanagari/Telugu scripts, classifies eight requested intents, and extracts crop, stage, symptoms, season, and a simple location phrase. |
| Agriculture knowledge base | `seed_knowledge.json` supplies 24 English/Hindi/Telugu entries. `knowledge_base.py` stores multilingual sentence-transformer embeddings in persistent ChromaDB and retrieves top-k chunks by cosine similarity. |
| Context & advisory processing | `advisory_service.py` combines parsed query, top-k retrieved entries, SQLite profile, and the five most recent interactions. If `GEMINI_API_KEY` is set, it sends these to Gemini with an instruction to use retrieved knowledge only. Without a key, the local response uses only the retrieved entries and their safety warnings. |
| Personalized advisory | The farmer's saved location fills an unspecified query location; profile and recent history are included in the grounded generation context. Unavailable knowledge triggers a localized message directing the farmer to the local agriculture officer. |
| Text response | The returned advisory and retrieved source titles are shown in the page. |
| Voice response | “Read aloud” uses browser speech synthesis (`en-IN`, `hi-IN`, or `te-IN`). |
| Interaction history | `history_store.py` persists farmer profiles and every interaction in SQLite; the UI loads and displays the latest 10. |

The seed guide is educational and deliberately avoids prescribing chemical rates. It does not contain live weather or mandi feeds and does not determine individual government-scheme eligibility.

## Install and run

Use Python 3.10–3.11 for the existing pinned ML dependencies in this repository.

### Backend

From PowerShell:

```powershell
cd bharat-krishi-ai-web\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.advisory.ingest
uvicorn app.main:app --reload
```

The first ingestion downloads the multilingual embedding model (unless it is already cached) and creates `backend/data/chroma/`; farmer profiles and interactions are stored in `backend/data/advisory.sqlite3`. Both stores are local, persistent, and git-ignored. Use the assistant at `http://localhost:8000` after building the frontend, or run the Vite development server as below. Interactive API documentation is at `http://localhost:8000/docs`.

To enable Gemini, add a key to `backend/.env`:

```dotenv
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash
```

Without a key, the assistant still runs with the local curated-knowledge response path. Model/API errors are returned explicitly rather than silently replaced with generated advice.

### Frontend

In a second PowerShell window:

```powershell
cd bharat-krishi-ai-web\frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Vite proxies `/api` to the backend on port 8000. Speech recognition requires a browser that implements Web Speech API and microphone permission; speech synthesis support varies by installed browser voices.

## Test

Run the focused backend tests:

```powershell
cd bharat-krishi-ai-web\backend
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
```

Build the frontend:

```powershell
cd bharat-krishi-ai-web\frontend
npm run build
```

Manual API smoke test:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/advisory/query `
  -ContentType 'application/json' `
  -Body '{"farmer_id":"demo-farmer","query":"My rice has yellow leaves and leaf blast in Karimnagar","input_type":"text"}'
```

The response includes `parsed_query`, `advisory`, `language`, `retrieved_sources`, and a `history_id`. Save profile data with `PUT /api/advisory/profile/{farmer_id}` and read stored turns with `GET /api/advisory/history/{farmer_id}`.

## Five sample test queries and expected outputs

Use the first three as typed queries. For the last two, choose the indicated recognition language, tap **Speak**, say the phrase, review the recognized text, then submit.

| Input | Query | Expected result |
|---|---|---|
| Text, English | `My rice has yellow leaves and leaf blast in Karimnagar` | `intent=crop_disease`, `crop=rice`, `language=en`, `location=Karimnagar`; retrieves Rice leaf blast and gives field hygiene/confirmation steps plus a pesticide safety warning. |
| Text, Hindi | `धान में पत्तियों पर रोग के धब्बे दिख रहे हैं` | `intent=crop_disease`, `crop=rice`, `language=hi`; Hindi advisory recommends checking/confirming the disease and avoiding unconfirmed spraying. |
| Text, Telugu | `వరిలో పసుపు ఆకులు మరియు తెగులు` | `intent=crop_disease`, `crop=rice`, `language=te`; Telugu advisory includes crop confirmation steps and localized safety advice. |
| Voice, English | `What is today's tomato mandi price in Guntur?` | `intent=market_price`, `crop=tomato`, `location=Guntur`; explains that this knowledge base has no live mandi price and points to official Agmarknet/eNAM sources. |
| Voice, Hindi | `पीएम किसान योजना की पात्रता कैसे जांचूं?` | `intent=government_scheme`, `language=hi`; Hindi steps point to the official PM-KISAN portal/service centre and clarify that the assistant cannot confirm personal eligibility. |

## API

- `POST /api/advisory/query` — `{ "farmer_id": "...", "query": "...", "input_type": "text|voice" }`
- `GET /api/advisory/profile/{farmer_id}`
- `PUT /api/advisory/profile/{farmer_id}` — `{ "location": "...", "crops_grown": "...", "soil_type": "...", "land_size": "..." }`
- `GET /api/advisory/history/{farmer_id}?limit=20`

The browser voice transcript and typed input use the same `query` field. Each signed-in account and guest browser receives a separate opaque, persistent farmer ID for this prototype. Production deployments should enforce authorization for farmer IDs at the API.
