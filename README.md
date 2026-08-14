# Sentinel

**Your AI academic weapon for RUET — cold, ruthless, and relentlessly on your side.**

Sentinel is a self-hosted, AI-powered academic platform built for RUET students. It turns your own lecture slides, textbooks, and past papers into a personal, relentless academic enforcer — one that answers questions grounded in *your* materials, drills you on exam patterns, guides (never spoon-feeds) your assignments, and tells you exactly what to study next.

Built for the **Reimagine Learning at RUET** hackathon challenge.

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [How AI Is Used](#how-ai-is-used)
- [Architecture](#architecture)
- [Features](#features)
- [Setup](#setup)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [File Structure](#file-structure)
- [How It Works](#how-it-works)
- [Built With](#built-with)
- [License](#license)

---

## Overview

RUET students juggle scattered course materials across drives, WhatsApp, and Telegram groups, with no smart way to prepare for exams from their own lecture slides, no guided help on assignments, and no personalized feedback on what they specifically need to study next.

Sentinel solves this by giving every RUET student a private, self-hosted AI academic assistant that:

- Knows your syllabus and reads your books
- Drills you on past exam questions
- Refuses to let you coast

## The Problem

RUET students juggle:

- Multiple courses with dense lecture slides and textbooks
- Class tests, sessional marks, and semester exams hitting simultaneously
- Assignment submissions with no one to explain the underlying concepts
- No centralized, intelligent access to their own study materials
- Zero personalization — everyone gets the same resources, regardless of where they're struggling

The result: surface-level cramming, last-minute panic, and wasted potential.

## The Solution

Sentinel reimagines the RUET learning experience with AI at its core:

| Feature | What It Does |
| --- | --- |
| **AI Course Assistant** | Upload lecture slides → ask anything → get answers grounded in *your* materials |
| **Smart Exam Prep** | Upload notes → auto-generate study plan → drill practice questions → identify weak topics |
| **Assignment Guidance** | Get targeted hints and concept explanations — never the direct answer |
| **Question Bank Drilling** | Past RUET exam patterns analyzed, high-yield topics identified |
| **Personalized Dashboard** | Sentinel analyzes your weak areas and tells you exactly what to study next |
| **Conversational Knowledge Base** | All uploaded materials become searchable through a chat interface |

## How AI Is Used

Sentinel uses the **Gemini API (via OpenRouter)** as its core intelligence, with AI woven into every layer:

- **RAG (Retrieval-Augmented Generation)** — Students upload their textbooks and lecture notes. FAISS vector search + BM25 keyword matching retrieves the most relevant excerpts and injects them into every prompt, so answers are always grounded in the student's own materials, not generic internet knowledge.
- **Intent Classification** — A lightweight classifier detects whether the student wants to learn a concept (`learn`), get code help (`code`), write a lab report (`lab`), or just chat. Each intent routes to a specialized structured output mode.
- **Structured Learning Modes** — The AI produces structured JSON output in Teacher, Coder, or Lab Report format — a formatted card with concept → explanation → math → takeaways, not just a chat bubble.
- **Exam Preparation Engine** — Sentinel identifies high-yield topics from uploaded syllabi, generates rapid-fire practice questions, critiques answers, and builds a personalized study schedule.
- **Assignment Drill** — The AI uses Socratic questioning; it never gives the answer directly. It exposes the gap in the student's understanding and guides them to the solution through targeted hints.
- **Multi-Agent Tool Pipeline** — LangGraph orchestrates background tools (web search, PDF download, YouTube transcript, repo analysis) before the LLM responds, so the AI always has current, relevant context.
- **User Vault** — The AI extracts facts about the student (weak topics, study habits, deadlines) and stores them in a persistent knowledge vault, enabling genuinely personalized recommendations over time.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/JS)                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│   │ Landing  │  │ Chat UI  │  │ Library (PDF.js)      │  │
│   │ Page     │  │ Streaming│  │ Tools + RAG Status    │  │
│   └──────────┘  └──────────┘  └──────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                          │ HTTP / SSE
┌─────────────────────────▼───────────────────────────────┐
│                 main.py (FastAPI :5090)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │Onboarding│  │ Settings │  │ Chat + Tool APIs      │   │
│  │Flow      │  │ API      │  │ Document APIs         │   │
│  └──────────┘  └──────────┘  └──────────────────────┘   │
└────────┬───────────────────────────────────┬─────────────┘
         │                                   │
┌────────▼──────────┐            ┌───────────▼────────────┐
│    marin.py        │            │   rag_server.py        │
│  (Sentinel Core)   │            │   (FastAPI :5091)      │
│  ┌──────────────┐  │   HTTP     │  ┌────────────────┐    │
│  │ Preprocessor  │  │───────────│  │ FAISS Index    │    │
│  │ (RAG + Page)  │  │            │  │ books/         │    │
│  └──────┬───────┘  │            │  │ Hybrid Search   │    │
│  ┌──────▼───────┐  │            │  └────────────────┘    │
│  │ Persona       │  │            └─────────────────────┘
│  │ (Streaming)   │  │
│  └──────────────┘  │
└─────────────────────┘
         │
┌────────▼──────────┐
│   database.py      │
│   PostgreSQL        │
│   (6 tables)        │
└────────────────────┘
```

**Ports:**

- `:5090` — Main FastAPI server (chat, settings, tools, library)
- `:5091` — RAG server (FAISS vector search, document indexing)

## Features

### Sentinel Persona — RUET-FORGE-01

Sentinel is a cold, relentless academic enforcer tuned specifically for RUET students:

- References RUET realities: semester exams, class tests, sessional marks, departmental projects
- Switches to **Exam Battle Mode** when a test is approaching — drills high-yield topics, generates practice questions, enforces study schedules
- Uses **Assignment Drill** mode — Socratic questioning, targeted hints, never direct answers
- Tracks deadlines and weaponizes accountability
- Dark, cutting academic tone

### Landing Page

Bold, atmospheric gateway. Enter your name, set your study preferences, and launch into the Forge.

### Core Chat

- Streaming responses with real-time token delivery
- Vibe detection (lovely, flirty, angry, sad, excited, playful, neutral) tuned for academic contexts
- Intent classification: `chat`, `image generation`, `learn`, `code`, `lab`
- Chat history persisted in PostgreSQL
- RAG context injection — relevant excerpts from your books injected into every prompt
- Page-aware context — when reading a PDF, Sentinel gets the current page text

### Library & PDF Viewer

- PDF.js rendering — browser-native PDF display with text selection
- Page navigation — editable page number input, prev/next buttons, zoom controls
- Reading color customizer — customizable background/text/highlight colors
- RAG progress indicator — pulsing dot + percentage bar when indexing new files
- Document management — upload, delete, open documents from the sidebar

### Library Tools

| Tool | Description |
| --- | --- |
| Repo/Link | Analyze GitHub repos and URLs |
| Quiz | Generate a quiz on any topic (perfect for RUET exam prep) |
| Translate | Translate text (9 languages) |
| Web Search | DuckDuckGo search |
| PDF Download | Download PDFs directly to `books/` with auto-RAG indexing |

Tools auto-send results to Sentinel so she responds about them in chat.

### RAG (Retrieval-Augmented Generation)

- Drop files into `books/` — your lecture slides, textbooks, past papers
- Auto-indexed on startup and after each upload
- Supports: PDF (with OCR fallback), DOCX, TXT, MD, PY, C/CPP/H
- Hybrid search: FAISS vector similarity + BM25 keyword search + cross-encoder re-ranking
- Page-aware context — PDF page text injected per-message
- Progress tracking — real-time indexing status via `/index_progress` endpoint

### Structured Output Modes

Triggered automatically when Sentinel detects academic intent:

- **Teacher Mode** (`learn`) — concept → explanation → math → takeaways
- **Coder Mode** (`code`) — language → snippet → explanation → dependencies
- **Lab Report Mode** (`lab`) — title → objective → equipment → procedure → results

### Study Tools

- **Flashcards** — SuperMemo-2 spaced repetition (quality 0–5)
- **Pomodoro Timer** — focus session tracking
- **Quiz Generator** — multiple-choice quizzes with explanations, grounded in your uploaded materials
- **Study Stats** — total focus time by topic

### Proactive Accountability Engine

- Monitors idle time: 20min → 2hr → 5hr → 48hr escalation
- Respects quiet hours (12:00 AM – 7:30 AM)
- SSE broadcast to connected clients
- Sentinel will come for you if you go quiet too long

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- OpenRouter API key (free tier works — <https://openrouter.ai>)

### Docker Install (Recommended)

```bash
# 1. Clone and start
git clone https://github.com/BayazidHabibSiddikee/Sentinel.git
cd Sentinel
docker-compose up --build

# 2. Access at http://localhost:5090
```

The Docker setup includes:

- `marin-server` — the app (ports 5090, 5091), runs as root to fix permissions on startup
- `marin-postgres` — PostgreSQL 15 (port 5432)
- `entrypoint.sh` — fixes `books/` permissions on every container start
- Persistent volumes for database, books, code, and generated files

### Local Install

```bash
# 1. Clone and setup
git clone https://github.com/BayazidHabibSiddikee/Sentinel.git
cd Sentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Ensure PostgreSQL is running
#    Tables are auto-created on first run

# 3. Run both servers
chmod +x run.sh
./run.sh

#    Or manually:
python3 rag_server.py &     # starts on :5091
python3 main.py             # starts on :5090
```

### First Run

1. Open <http://localhost:5090>
2. Onboarding wizard — enter your name, RUET department, study topics
3. Enter your OpenRouter API key
4. Click **Initialize** — Sentinel is ready to forge you

### Adding Study Materials

```bash
# Drop your RUET textbooks, lecture slides, past papers into books/
cp ~/Downloads/signals_and_systems.pdf books/
cp ~/Notes/control_systems_lecture.docx books/
cp ~/Downloads/past_questions_EEE.pdf books/
```

Files are automatically indexed on server startup. To re-index after adding new files:

```bash
curl -X POST http://127.0.0.1:5091/reindex
```

Or use the **PDF Download** tool in the library — it downloads and auto-indexes.

## Configuration

### `config.py`

| Constant | Default | Description |
| --- | --- | --- |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformer for FAISS |
| `IMAGE_MODEL` | `stabilityai/stable-diffusion-xl-beta-v2-2-2` | Image generation model |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter API base |
| `TOTAL_KB_MAX_MB` | `200` | Max total size for `books/` |
| `BOOKS_MAX_MB` | `96` | Max size for `books/` sub-limit |

### Environment Variables (Docker)

| Variable | Default | Description |
| --- | --- | --- |
| `PG_HOST` | `localhost` | PostgreSQL host |
| `PG_PORT` | `5432` | PostgreSQL port |
| `PG_DB_NAME` | `postgres` | Database name |
| `PG_USER` | `postgres` | Database user |
| `PG_PASSWORD` | `postgres` | Database password |
| `TZ` | `Asia/Dhaka` | Container timezone |

## API Reference

### Chat

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/chat` | Send message. Form fields: `message`, `theme`, `document`, `page`. Returns streaming response. |
| GET | `/api/chat/history` | Get chat history (last 50 messages). |
| POST | `/api/chat/context` | Save tool context for Sentinel. JSON: `{tool, result}`. |

### Settings

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/settings` | Get all user settings. |
| POST | `/api/settings` | Save settings. |

### Documents & Library

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/library` | Serve library HTML page. |
| GET | `/api/documents` | List all documents in `books/`. |
| GET | `/api/documents/{filename}/content` | Read document content. |
| GET | `/api/documents/{filename}/page/{n}` | Extract text from PDF page `n`. |
| POST | `/api/documents/upload` | Upload document to `books/`. |
| DELETE | `/api/documents/{filename}` | Delete a document. |

### RAG

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/rag/health` | RAG server health + storage stats. |
| GET | `/api/rag/index_progress` | Current indexing progress (state, current, total, file). |

### Tools

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/tools/search` | Web search. JSON: `{query, num_results}`. |
| POST | `/api/tools/translate` | Translate. JSON: `{text, to}`. |
| POST | `/api/tools/download_pdf` | Download PDF. JSON: `{url, filename}`. |
| POST | `/api/tools/quiz` | Generate quiz. JSON: `{topic, num_questions}`. |

## File Structure

```
sentinel/
├── main.py                 # FastAPI entry — all HTTP endpoints
├── marin.py                # Core AI — Sentinel persona, preprocessor, streaming
├── config.py                # Shared constants — model names, paths, limits
├── database.py               # PostgreSQL interface — 6 tables
├── classifier.py             # Regex intent/vibe classifier
├── llm_manager.py            # LLM provider management, API validation & tool capability testing
├── proactive_engine.py        # Idle detection, SSE broadcast
├── rag_server.py             # FAISS RAG server (:5091)
├── langgraph_agent.py         # 3-node LangGraph pipeline
├── run.sh                    # Launcher — RAG + main server
├── entrypoint.sh              # Docker entrypoint — fixes permissions
│
├── tools/                    # Tool modules
│   ├── web_search.py          # DuckDuckGo search
│   ├── pdf_downloader.py       # PDF download → books/ + RAG index
│   ├── repo_analyzer.py        # GitHub repo / webpage analysis
│   ├── quiz_generator.py       # Quiz generation (RUET exam style)
│   ├── translate.py            # Translation (9 languages)
│   ├── doc_tools.py            # PDF/Word conversion
│   ├── image_tool.py           # Image generation
│   ├── email_tool.py           # Gmail SMTP
│   ├── student_tools.py        # QR, unit conversion, calculator
│   ├── youtube_transcript.py
│   └── bangla.py               # Bangla voice translator
│
├── templates/
│   ├── landing.html           # Landing page
│   ├── marin_chat.html         # Main chat UI
│   └── library.html            # Library + PDF viewer + tools
│
├── static/
│   ├── images/                 # Avatars, screenshots
│   ├── uploads/                # User-uploaded images
│   └── generated/              # AI-generated images
│
├── books/                     # Study materials (PDFs, lecture slides, past papers) — RAG indexed
│
├── storage/
│   └── faiss_db/               # FAISS index files
│
├── docker-compose.yml           # App + PostgreSQL
├── Dockerfile                  # Container build
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## How It Works

### Input Processing Pipeline

```
RUET Student types message
       │
       ▼
┌──────────────┐
│ classifier.py │  Regex intent + vibe detection (zero RAM)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Preprocessor │  Enriches prompt with context
│  (marin.py)   │
│  ┌──────────┐ │
│  │ RAG      │ │  FAISS search → relevant excerpts from student's books
│  │ Page     │ │  If PDF open → current page text
│  └──────────┘ │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Sentinel     │  RUET-FORGE-01 persona + vibe modifier + RAG instruction
│  Persona      │  Last 30 messages from PostgreSQL
│  (Streaming)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Response     │  Streaming LLM generation
│  + Cleanup    │  Strips emoji headers + signatures
└──────────────┘
```

### Exam Preparation Flow

```
Student: "I have my Control Systems exam in 3 days"
       │
       ▼
Sentinel identifies high-yield topics from uploaded syllabus
       │
       ▼
Generates practice questions from past paper patterns
       │
       ▼
Drills student on weak areas identified from conversation history
       │
       ▼
Builds day-by-day study schedule. Enforces it.
```

### Assignment Guidance Flow

```
Student: "I don't understand this assignment question"
       │
       ▼
Sentinel reads the question context (via RAG or direct input)
       │
       ▼
Identifies the underlying concept gap
       │
       ▼
Guides with targeted hints and Socratic questions
       │
       ▼
Student arrives at the answer themselves. Learning happens.
```

## Built With

- **Gemini API** (via OpenRouter) — Core LLM intelligence
- **Google AI Studio** — Model testing and prompt engineering
- **LangChain** — LLM abstraction, message formatting
- **LangGraph** — Multi-agent tool pipeline orchestration
- **FAISS** — Vector similarity search for RAG
- **FastAPI** — Backend API server
- **PostgreSQL 15** — Persistent storage (chat history, user vault, state)
- **PDF.js** — Browser-native PDF rendering
- **sentence-transformers** — Local embedding model (`all-MiniLM-L6-v2`)
- **Google Cloud / Cloud Run** — Deployment target

## License

MIT License

Copyright (c) 2025 Bayazid

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
