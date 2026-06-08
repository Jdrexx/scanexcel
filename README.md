# Local AI OCR to Excel

Turn scanned documents, receipts, handwritten notes, and pasted text into reviewed spreadsheet rows.

## Why this project exists

This is a portfolio-ready MVP in the **document automation** lane. It demonstrates practical API product thinking, clean documentation, tests, and a working local browser demo.

## Features

- Upload or paste document text
- Extract likely tables and key/value rows
- Review confidence scores
- Export normalized rows as CSV
- Local-first AI cleanup hook for Ollama

## Tech Stack

- Python 3.11+
- FastAPI
- SQLite
- Vanilla HTML/CSS/JS frontend served by the API
- Pytest API tests

## Quick Start

```bash
uv sync
uv run uvicorn src.main:app --reload --port 8101
```

Then open: http://localhost:8101

Windows one-click launcher: `run.bat`

## API

- `GET /` - browser demo
- `GET /api/health` - health check
- `GET /docs` - interactive FastAPI docs

## Verification

```bash
uv run pytest -q
```

## Roadmap

- Add authenticated user accounts
- Add production deployment config
- Replace deterministic helper logic with local Ollama model calls where useful
- Add screenshots and a short demo GIF
