# Local AI OCR to Excel

![Python](https://img.shields.io/badge/Python-3.11_|_3.12-3776AB?style=flat-square&logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite) ![OCR](https://img.shields.io/badge/OCR-10B981?style=flat-square) ![Receipts](https://img.shields.io/badge/Receipts-F59E0B?style=flat-square)

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
