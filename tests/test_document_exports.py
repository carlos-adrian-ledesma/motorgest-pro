import base64
import io
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from motorgest.inspection_export import build_inspection_docx, build_inspection_pdf


def _image_data_url():
    buffer = io.BytesIO()
    Image.new("RGB", (900, 500), "white").save(buffer, "PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _payload():
    return {
        "imageDataUrl": _image_data_url(),
        "caseNo": "CAS-DEMO",
        "unitType": "Automóvil",
        "company": "Empresa Demo",
        "client": "Cliente Demo",
        "domainId": "DEMO",
        "brandModel": "Fiat Cronos",
        "year": "2021",
        "kmHours": "10000 km",
        "serial": "DEMO",
        "inspector": "Inspector Demo",
        "date": "2026-10-06",
        "marks": [],
        "notes": "Prueba automatizada",
    }


def test_pdf_and_docx_exports_are_generated():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        logo = ROOT / "assets" / "motorgest_logo.png"
        pdf = build_inspection_pdf(_payload(), td / "inspection.pdf", logo, "3.1.4")
        docx = build_inspection_docx(_payload(), td / "inspection.docx", logo, "3.1.4")
        assert pdf.exists() and pdf.stat().st_size > 10_000
        assert docx.exists() and docx.stat().st_size > 10_000
