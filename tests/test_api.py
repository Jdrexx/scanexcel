from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
def test_health():
    r=client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['ok'] is True

def test_process_document():
    data=client.post('/api/process', json={'source':'test','text':'1/1 Staples $12.30\n2/2 GitHub $4.00'}).json()
    assert data['row_count'] == 2
    assert data['rows'][0]['amount'] == '12.30'
