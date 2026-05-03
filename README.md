# Know-Genius - Backend

FastAPI Backend For Know-Genius. Answers General Knowledge Questions Using A Two-Step Agentic Workflow Powered By Google Gemini.

## How It Works

Every Incoming Message Goes Through Two Gemini Calls — A Classifier That Determines Whether The Question Is General Knowledge, And An Answerer That Responds Only If It Passes. Out-Of-Scope Questions Are Declined With A Friendly Redirect Before Reaching The Answer Model.

## Setup

1. Create And Activate A Virtual Environment:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

2. Install Dependencies:

```bash
pip install -r requirements.txt
```

3. Configure Environment:

```bash
# .env
GEMINI_API_KEY=your_google_ai_studio_key_here
GEMINI_MODEL=gemini-2.5-flash
```

4. Run The Server:

```bash
python main.py
```

Server Starts At `http://localhost:8000`.

## API

**`GET /health`** — Health Check.

**`POST /api/chat/message`** — Send A Chat Message.

Request Body (`application/json`):

| Field     | Type   | Required | Description                          |
| --------- | ------ | -------- | ------------------------------------ |
| `message` | String | Yes      | The User's Question (Max 1000 Chars) |
| `history` | Array  | No       | Prior Turn Objects `{role, content}` |

Response:

```json
{
  "answer": "...",
  "category": "history",
  "answered_by_agent": true
}
```

## Agentic Workflow

| Step         | Model              | Purpose                                          |
| ------------ | ------------------ | ------------------------------------------------ |
| Classify     | `GEMINI_MODEL`     | Determines If Question Is General Knowledge      |
| Answer       | `GEMINI_MODEL`     | Generates A Friendly, Accurate Response          |

Out-Of-Scope Questions Are Short-Circuited After Step 1 — The Answer Model Is Never Called.

## Environment Variables

| Variable       | Required | Description                      |
| -------------- | -------- | -------------------------------- |
| `GEMINI_API_KEY` | Yes    | Google AI Studio API Key         |
| `GEMINI_MODEL`   | No     | Gemini Model Name (Default: `gemini-2.5-flash`) |

## Dependencies

| Package              | Version  | Purpose              |
| -------------------- | -------- | -------------------- |
| fastapi              | 0.115.5  | Web Framework        |
| uvicorn              | 0.32.1   | ASGI Server          |
| google-generativeai  | 0.8.3    | Gemini SDK           |
| pydantic             | 2.10.1   | Data Validation      |
| pydantic-settings    | 2.6.1    | Environment Settings |
| python-dotenv        | 1.0.1    | .env Loader          |
| slowapi              | 0.1.9    | Rate Limiting        |

## Deployment (Vercel)

1. Push The Repository To GitHub.

2. Import The Project In [Vercel](https://vercel.com) And Set The Following Environment Variables:

| Variable         | Value                          |
| ---------------- | ------------------------------ |
| `GEMINI_API_KEY` | Your Google AI Studio API Key  |
| `GEMINI_MODEL`   | `gemini-2.5-flash`             |

3. Vercel Automatically Detects `vercel.json` And Deploys Using `@vercel/python`.

The Module-Level `app = CreateApp()` In `main.py` Is The ASGI Entry Point Picked Up By Vercel.

## Project Structure

```
Know-Genius-Backend/
├── main.py                          — Uvicorn Entry Point
├── requirements.txt                 — Dependencies
├── .env                             — Environment Config (Gitignored)
├── .gitignore
└── app/
    ├── App.py                       — FastAPI App Factory, CORS, Rate Limiter
    ├── core/
    │   └── Config.py                — Central Config (All Secrets From .env)
    ├── services/
    │   └── GeminiService.py         — Gemini SDK Wrapper (GetModel, GenerateText)
    ├── agents/
    │   └── KnowledgeAgent.py        — Two-Step Agent (Classify → Answer)
    └── api/
        ├── schemas/
        │   └── Chat.py              — Pydantic Request / Response Models
        └── routes/
            └── Chat.py              — POST /api/chat/message
```