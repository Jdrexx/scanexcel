from fastapi.testclient import TestClient
from src.main import app


def _clean_db():
    from src.main import db

    with db() as conn:
        conn.execute("delete from records")


def test_health():
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["ok"] is True


def test_process_document():
    _clean_db()
    with TestClient(app) as client:
        data = client.post(
            "/api/process",
            json={"source": "test", "text": "1/1 Staples $12.30\n2/2 GitHub $4.00"},
        ).json()
        assert data["row_count"] == 2
        assert data["rows"][0]["amount"] == "12.30"


def test_no_wildcard_cors():
    """No CORS middleware: responses must not carry permissive CORS headers."""
    with TestClient(app) as client:
        r = client.get("/api/health", headers={"Origin": "https://evil.example"})
        assert "access-control-allow-origin" not in r.headers


def test_export_neutralizes_formula_injection():
    """A scanned '=...' line must not round-trip as a live spreadsheet formula."""
    _clean_db()
    with TestClient(app) as client:
        client.post(
            "/api/process",
            json={
                "source": "inj",
                "text": '=HYPERLINK("http://evil.example","x") 1/15 $42.18',
            },
        )
        body = client.get("/api/export.csv").text
        assert "=HYPERLINK" not in body or "'=HYPERLINK" in body


def test_upload_rejects_oversized_file():
    _clean_db()
    with TestClient(app) as client:
        r = client.post(
            "/api/upload",
            files={"file": ("big.txt", b"x" * (11 * 1024 * 1024), "text/plain")},
        )
        assert r.status_code == 413


def test_process_rejects_oversized_text():
    with TestClient(app) as client:
        r = client.post("/api/process", json={"source": "big", "text": "x" * 200_001})
        assert r.status_code == 422