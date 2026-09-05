from __future__ import annotations
import csv, io, json, re, sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

# Spreadsheet formula-injection guard: Excel/Sheets evaluate cells starting
# with these characters as formulas. Extracted rows come from untrusted OCR
# text, so a scanned line like "=HYPERLINK(...)" would execute when the export
# is opened. Prefixing with a single quote forces text interpretation.
_CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _csv_safe(value: object) -> object:
    text = str(value)
    if text.startswith(_CSV_FORMULA_PREFIXES):
        return "'" + text
    return value


APP_NAME = "Local AI OCR to Excel"
DB_FILE = Path(__file__).resolve().parent.parent / "data" / "app.sqlite"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB per upload

DB_FILE.parent.mkdir(exist_ok=True)


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma journal_mode=wal")
    # A concurrent writer surfaces "database is locked" instantly without this.
    conn.execute("pragma busy_timeout=5000")
    return conn


@asynccontextmanager
async def lifespan(_: FastAPI):
    with db() as conn:
        conn.execute(
            "create table if not exists records (id integer primary key autoincrement, kind text not null, title text not null, payload text not null, created_at text not null)"
        )
    yield


app = FastAPI(title=APP_NAME, version="0.1.0", lifespan=lifespan)


def save_record(kind: str, title: str, payload: str) -> int:
    with db() as conn:
        cur = conn.execute(
            "insert into records(kind,title,payload,created_at) values (?,?,?,?)",
            (kind, title, payload, datetime.now(timezone.utc).isoformat()),
        )
        return int(cur.lastrowid)


def rows(kind: str | None = None) -> list[dict[str, Any]]:
    with db() as conn:
        data = (
            conn.execute(
                "select * from records where kind=? order by id desc", (kind,)
            ).fetchall()
            if kind
            else conn.execute("select * from records order by id desc").fetchall()
        )
    return [dict(r) for r in data]


@app.get("/api/health")
def health():
    return {"ok": True, "app": APP_NAME, "records": len(rows())}


@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML


class DocumentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=200_000)
    source: str = Field(default="manual", max_length=500)


def parse_document(text: str) -> list[dict[str, Any]]:
    parsed = []
    for line in [l.strip() for l in text.splitlines() if l.strip()]:
        amount_matches = re.findall(r"-?\$?\d+\.\d{2}|\$\d+", line)
        date_match = re.search(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", line)
        amount = amount_matches[-1].replace("$", "") if amount_matches else ""
        vendor = re.sub(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", "", line)
        vendor = (
            re.sub(r"-?\$?\d+(?:\.\d{2})?", "", vendor).strip(" -,:\t") or line[:40]
        )
        parsed.append(
            {
                "date": date_match.group(0) if date_match else "",
                "description": vendor,
                "amount": amount,
                "confidence": 0.86 if amount else 0.62,
                "raw": line,
            }
        )
    return parsed


@app.post("/api/process")
def process(req: DocumentRequest):
    extracted = parse_document(req.text)
    save_record(
        "document", req.source, json.dumps({"source": req.source, "rows": extracted})
    )
    return {"row_count": len(extracted), "rows": extracted}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    # Content-Length is advisory (absent/spoofable under chunked encoding), so
    # the bounded read below is the real cap; both checks stay.
    content_length = int(file.headers.get("content-length", 0))
    if content_length > MAX_UPLOAD_SIZE:
        raise HTTPException(413, detail=f"File too large. Maximum 10MB allowed.")
    raw = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(raw) > MAX_UPLOAD_SIZE:
        raise HTTPException(413, detail=f"File too large. Maximum 10MB allowed.")
    content = raw.decode("utf-8", errors="ignore")
    return process(DocumentRequest(text=content, source=file.filename or "upload"))


@app.get("/api/export.csv")
def export_csv():
    out = io.StringIO()
    writer = csv.DictWriter(
        out, fieldnames=["date", "description", "amount", "confidence", "raw"]
    )
    writer.writeheader()
    for rec in rows("document"):
        for row in json.loads(rec["payload"]).get("rows", []):
            safe = dict(row)
            # Guard only free-text columns; amounts may legitimately start with
            # "-" (refunds/credits) and must stay numeric for Excel.
            safe["description"] = _csv_safe(safe.get("description", ""))
            safe["raw"] = _csv_safe(safe.get("raw", ""))
            writer.writerow(safe)
    out.seek(0)
    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ocr_export.csv"},
    )


INDEX_HTML = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local AI OCR to Excel</title><style>body{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#e5e7eb;margin:0}main{max-width:980px;margin:auto;padding:32px}.card{background:#111827;border:1px solid #334155;border-radius:18px;padding:24px;margin:18px 0}h1{font-size:42px}textarea,input{width:100%;box-sizing:border-box;border-radius:12px;border:1px solid #475569;background:#020617;color:#e5e7eb;padding:14px;margin:8px 0}button{background:#22c55e;color:#04130a;border:0;border-radius:12px;padding:12px 18px;font-weight:700}pre{white-space:pre-wrap;background:#020617;border-radius:12px;padding:16px}.pill{background:#1e293b;border:1px solid #475569;border-radius:999px;padding:6px 10px}</style></head><body><main><div class="card"><span class="pill">document automation</span><h1>Local AI OCR to Excel</h1><p>Turn scanned documents, receipts, handwritten notes, and pasted text into reviewed spreadsheet rows.</p><ul><li>Upload or paste document text</li><li>Extract likely tables and key/value rows</li><li>Review confidence scores</li><li>Export normalized rows as CSV</li><li>Local-first AI cleanup hook for Ollama</li></ul></div><div class="card"><h2>Live API Demo</h2><textarea id="input" rows="7">1/15 Office Depot $42.18\n1/16 GitHub Pro $4.00</textarea><button onclick="runDemo()">Run Demo</button><pre id="out">Click Run Demo to call the FastAPI backend.</pre></div><div class="card"><h2>API</h2><p>Health: <code>/api/health</code> · Docs: <code>/docs</code></p></div><script>async function runDemo(){const res = await (fetch(\'/api/process\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({source:\'demo receipt\',text:document.getElementById(\'input\').value})})); const data = await res.json(); document.getElementById(\'out\').textContent = JSON.stringify(data,null,2);}</script></main></body></html>'