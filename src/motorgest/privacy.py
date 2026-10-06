from __future__ import annotations

from copy import deepcopy
from typing import Any
import re


SECRET_KEYS = {
    "password", "passwordHash", "salt", "smtpPassword", "emailPassword",
    "appPassword", "client_secret", "access_token", "refresh_token", "token",
}

COLLECTION_PREFIXES = {
    "users": "USR",
    "clients": "CLI",
    "units": "UNI",
    "cases": "CAS",
    "inspections": "INS",
    "budgets": "PRE",
    "authorizations": "AUT",
    "works": "DIA",
    "remitos": "REM",
    "warranties": "GAR",
    "payments": "PAG",
    "inventory": "STK",
    "stockMovements": "MOV",
    "cashMovements": "CAJ",
    "audit": "AUD",
}

PERSON_KEYS = {"authorizedBy", "executor", "payer", "deliveredBy", "receivedBy", "responsible", "technician"}
PROVIDER_KEYS = {"provider", "supplier", "thirdPartyProvider"}
DIRECT_PII_KEYS = {
    "dni", "document", "email", "phone", "address", "street", "postalCode",
    "domain", "plate", "patent", "licensePlate", "serial", "chassis", "vin",
}
SMTP_KEYS = {"senderEmail", "username", "smtpServer", "server", "smtpPort", "port", "security", "emailProvider"}
BINARY_PII_KEYS = {"photo", "photos", "image", "imageData", "imageDataUrl", "signature", "signatureData", "clientSignature", "technicianSignature"}


def _collect_values(state: dict[str, Any]) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for index, client in enumerate(state.get("clients") or [], 1):
        if not isinstance(client, dict):
            continue
        alias = f"Cliente {index:04d}"
        for key in ("name", "dni", "document", "email", "phone", "address", "street"):
            value = str(client.get(key) or "").strip()
            if value:
                replacements[value] = alias if key == "name" else "[ANONIMIZADO]"
    for index, user in enumerate(state.get("users") or [], 1):
        if not isinstance(user, dict):
            continue
        alias = f"Usuario {index:04d}"
        for key in ("username", "fullName", "firstName", "lastName", "dni", "email", "phone"):
            value = str(user.get(key) or "").strip()
            if value:
                replacements[value] = alias if key in {"username", "fullName", "firstName", "lastName"} else "[ANONIMIZADO]"
    for index, unit in enumerate(state.get("units") or [], 1):
        if not isinstance(unit, dict):
            continue
        alias = f"Unidad {index:04d}"
        for key in ("domain", "plate", "patent", "licensePlate", "serial", "chassis", "vin", "internalNo"):
            value = str(unit.get(key) or "").strip()
            if value:
                replacements[value] = alias
    settings = state.get("settings") or {}
    if isinstance(settings, dict):
        for key in ("company", "manager", "senderEmail", "username"):
            value = str(settings.get(key) or "").strip()
            if value:
                replacements[value] = "[ANONIMIZADO]"
    return replacements


def _id_map(state: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for collection, prefix in COLLECTION_PREFIXES.items():
        for index, row in enumerate(state.get(collection) or [], 1):
            if isinstance(row, dict) and row.get("id"):
                mapping[str(row["id"])] = f"{prefix}-{index:04d}"
    return mapping


def _replace_text(value: str, replacements: dict[str, str], ids: dict[str, str]) -> str:
    if value in ids:
        return ids[value]
    result = value
    for original, alias in sorted(replacements.items(), key=lambda pair: len(pair[0]), reverse=True):
        if len(original) >= 3:
            result = result.replace(original, alias)
    for original, alias in ids.items():
        if original in result:
            result = result.replace(original, alias)
    result = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL ANONIMIZADO]", result)
    result = re.sub(r"(?<!\d)(?:\+?\d[\d .()/-]{6,}\d)(?!\d)", "[NUMERO ANONIMIZADO]", result)
    return result


def _scrub(value: Any, replacements: dict[str, str], ids: dict[str, str], key: str = "") -> Any:
    if key in SECRET_KEYS:
        return None
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for child_key, child_value in value.items():
            if child_key in SECRET_KEYS:
                continue
            if child_key in DIRECT_PII_KEYS or child_key in SMTP_KEYS:
                cleaned[child_key] = ""
                continue
            if child_key in BINARY_PII_KEYS:
                cleaned[child_key] = [] if isinstance(child_value, list) else ""
                continue
            if child_key in PERSON_KEYS:
                cleaned[child_key] = "Persona anonimizada" if child_value else ""
                continue
            if child_key in PROVIDER_KEYS:
                cleaned[child_key] = "Proveedor anonimizado" if child_value else ""
                continue
            cleaned[child_key] = _scrub(child_value, replacements, ids, child_key)
        return cleaned
    if isinstance(value, list):
        return [_scrub(item, replacements, ids, key) for item in value]
    if isinstance(value, str):
        return _replace_text(value, replacements, ids)
    return value


def sanitize_analysis_state(source: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied, relationship-preserving state safe for external analysis.

    Credentials are removed, primary IDs are pseudonymized consistently, direct PII is
    blanked, known personal values are scrubbed from free text, and operational/numeric
    information is retained where practical for debugging and analysis.
    """
    original = deepcopy(source or {})
    replacements = _collect_values(original)
    ids = _id_map(original)
    clean = _scrub(original, replacements, ids)

    for index, client in enumerate(clean.get("clients") or [], 1):
        if isinstance(client, dict):
            client["name"] = f"Cliente {index:04d}"
    for index, user in enumerate(clean.get("users") or [], 1):
        if isinstance(user, dict):
            user["username"] = f"usuario{index:04d}"
            user["fullName"] = f"Usuario {index:04d}"
            for key in ("firstName", "lastName"):
                if key in user:
                    user[key] = ""
    for index, unit in enumerate(clean.get("units") or [], 1):
        if isinstance(unit, dict):
            for key in ("domain", "plate", "patent", "licensePlate", "internalNo"):
                if key in unit:
                    unit[key] = f"UNIDAD-{index:04d}"
            for key in ("serial", "chassis", "vin"):
                if key in unit:
                    unit[key] = ""
    for index, case in enumerate(clean.get("cases") or [], 1):
        if isinstance(case, dict) and "caseNo" in case:
            case["caseNo"] = f"CASO-{index:04d}"

    settings = clean.get("settings")
    if isinstance(settings, dict):
        settings["company"] = "Empresa anonimizada"
        settings["manager"] = ""
        for key in SMTP_KEYS | SECRET_KEYS:
            settings.pop(key, None)

    clean.setdefault("meta", {})["analysisExport"] = "ANONYMIZED"
    return clean
