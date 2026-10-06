import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from motorgest.privacy import sanitize_analysis_state


def test_external_analysis_export_removes_known_pii_and_credentials():
    state = {
        "settings": {"company": "Taller Secreto", "senderEmail": "owner@example.com", "smtpPassword": "TOPSECRET"},
        "users": [{"id": "U-REAL", "username": "carlos", "fullName": "Carlos Ledesma", "dni": "30111222", "email": "carlos@example.com", "phone": "3804000000", "passwordHash": "HASH", "salt": "SALT", "role": "Administrador"}],
        "clients": [{"id": "C-REAL", "name": "Juan Perez", "dni": "28999888", "email": "juan@example.com", "phone": "3804111111", "address": "Calle Privada 123"}],
        "units": [{"id": "V-REAL", "clientId": "C-REAL", "domain": "AA123BB", "serial": "CHASIS-SECRETO", "brand": "Fiat"}],
        "cases": [{"id": "CASE-REAL", "clientId": "C-REAL", "unitId": "V-REAL", "caseNo": "CAS-009", "notes": "Llamar a Juan Perez al 3804111111"}],
        "payments": [{"id": "PAY-REAL", "caseId": "CASE-REAL", "payer": "Juan Perez", "amount": 12345}],
        "cashMovements": [{"id": "CASH-REAL", "sourcePaymentId": "PAY-REAL", "caseId": "CASE-REAL", "amount": 12345}],
        "works": [{"id": "W-REAL", "caseId": "CASE-REAL", "notes": "Contacto alternativo unknown@example.com +54 380 422-3333"}], "inspections": [{"id": "IN-REAL", "caseId": "CASE-REAL", "photo": "data:image/jpeg;base64,SECRETIMAGE"}], "budgets": [], "authorizations": [], "remitos": [], "warranties": [], "inventory": [], "stockMovements": [], "audit": [],
    }
    clean = sanitize_analysis_state(state)
    encoded = json.dumps(clean, ensure_ascii=False)
    for forbidden in ["TOPSECRET", "HASH", "SALT", "30111222", "28999888", "carlos@example.com", "juan@example.com", "3804111111", "Calle Privada 123", "AA123BB", "CHASIS-SECRETO", "Juan Perez", "Carlos Ledesma", "SECRETIMAGE", "unknown@example.com", "380 422-3333"]:
        assert forbidden not in encoded
    assert clean["cases"][0]["clientId"] == clean["clients"][0]["id"]
    assert clean["cashMovements"][0]["sourcePaymentId"] == clean["payments"][0]["id"]
    assert clean["meta"]["analysisExport"] == "ANONYMIZED"
