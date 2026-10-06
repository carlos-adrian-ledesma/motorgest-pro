import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from motorgest.database import StateDatabase


def test_sqlite_backup_restore_preserves_operational_snapshot():
    state = {
        "settings": {"company": "Demo"},
        "clients": [{"id": "C1"}],
        "units": [{"id": "U1", "clientId": "C1"}],
        "cases": [{"id": "K1", "clientId": "C1", "unitId": "U1"}],
        "inventory": [{"id": "I1", "stock": 8}],
        "payments": [{"id": "P1", "caseId": "K1", "status": "Confirmado", "amount": 100}],
        "cashMovements": [{"id": "M1", "sourcePaymentId": "P1", "caseId": "K1", "amount": 100}],
        "users": [{"id": "A1", "role": "Administrador"}],
    }
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        db = StateDatabase(td / "motorgest.db")
        assert db.save(json.dumps(state))
        backup = db.backup_to(td / "backup.sqlite3")
        restored = StateDatabase(backup)
        loaded = json.loads(restored.load())
        assert loaded["inventory"] == state["inventory"]
        assert loaded["payments"] == state["payments"]
        assert loaded["cashMovements"] == state["cashMovements"]
        assert loaded["users"] == state["users"]
        assert loaded["cases"] == state["cases"]
        assert restored.integrity_check() == "ok"
