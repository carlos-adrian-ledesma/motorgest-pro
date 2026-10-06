import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRITY = ROOT / "web" / "assets" / "integrity.js"


def run_node(script: str):
    result = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def test_removed_payment_reconciles_cash_without_orphan_reference():
    data = run_node(f"""
const integrity=require({json.dumps(str(INTEGRITY))});
const state={{cashMovements:[{{id:'CAJ1',sourcePaymentId:'P1',caseId:'C1',status:'Confirmado',type:'Ingreso',amount:100,detail:''}}]}};
const count=integrity.reconcileRemovedPaymentCash(state,['P1'],{{at:'NOW'}});
console.log(JSON.stringify({{count,m:state.cashMovements[0]}}));
""")
    assert data["count"] == 1
    assert data["m"]["status"] == "Anulado"
    assert data["m"]["sourcePaymentId"] == ""
    assert data["m"]["caseId"] == ""
    assert data["m"]["reversedSourcePaymentId"] == "P1"


def test_cash_totals_exclude_pending_and_protect_automatic_financial_fields():
    data = run_node(f"""
const integrity=require({json.dumps(str(INTEGRITY))});
const state={{cashMovements:[
 {{date:'2026-10-01',status:'Confirmado',type:'Ingreso',amount:100}},
 {{date:'2026-10-02',status:'Pendiente',type:'Ingreso',amount:50}},
 {{date:'2026-10-03',status:'Confirmado',type:'Egreso',amount:20}}
]}};
const totals=integrity.cashTotalsForMonth(state,'2026-10');
const edited=integrity.protectedAutomaticCashEdit({{sourcePaymentId:'P1',type:'Ingreso',amount:100,status:'Confirmado',caseId:'C1',method:'QR',category:'Cobro',concept:'A',detail:''}},{{type:'Egreso',amount:1,status:'Anulado',caseId:'X',method:'Cheque',category:'Nueva',concept:'B',detail:'ok'}});
console.log(JSON.stringify({{totals,edited}}));
""")
    assert data["totals"] == {"income": 100, "expense": 20, "pendingIncome": 50, "pendingExpense": 0}
    edited = data["edited"]
    assert edited["amount"] == 100 and edited["type"] == "Ingreso"
    assert edited["status"] == "Confirmado" and edited["caseId"] == "C1" and edited["method"] == "QR"
    assert edited["category"] == "Nueva" and edited["concept"] == "B" and edited["detail"] == "ok"
