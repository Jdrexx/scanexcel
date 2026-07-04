# ScanExcel — Document Text to Spreadsheet Rows

![Python](https://img.shields.io/badge/Python-3.11_%7C_3.12-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite)

Turn scanned document text, receipts, handwritten notes, and pasted text into structured spreadsheet rows. Upload a photo of a receipt or paste an invoice's text, and get back a CSV of line items.

## Features

- Upload or paste document text for parsing
- Extracts likely table rows and key/value pairs from unstructured text
- Confidence scores per extracted field
- Export normalized rows as CSV
- Optional local Ollama hook for improved extraction on messy documents

## Tech Stack

- Python 3.11+ / FastAPI / SQLite
- Vanilla HTML/CSS/JS frontend served by the API
- Pytest

## Quick Start

```bash
uv sync
uv run uvicorn src.main:app --reload --port 8101
```

Open: http://localhost:8101

Windows: double-click `run.bat`

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Browser demo UI |
| GET | `/api/health` | Health check |
| GET | `/docs` | Interactive API docs |

## Tests

```bash
uv run pytest -q
```
