import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRITY = ROOT / "web" / "assets" / "integrity.js"


def run_node(script: str):
    result = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def test_case_delete_reverses_used_stock_and_keeps_trace():
    data = run_node(f"""
const integrity=require({json.dumps(str(INTEGRITY))});
const state={{
  inventory:[{{id:'I1',description:'Filtro',stock:8}}],
  works:[{{id:'W1',caseId:'C1',stockItems:[{{itemId:'I1',quantity:2,status:'Utilizado'}}]}}],
  stockMovements:[]
}};
const r=integrity.reverseStockForCases(state,['C1'],{{date:'2026-10-06',createdAt:'NOW',idFactory:()=> 'MOV-REV'}});
console.log(JSON.stringify({{stock:state.inventory[0].stock,movement:state.stockMovements[0],result:r}}));
""")
    assert data["stock"] == 10
    assert data["movement"]["type"] == "Entrada"
    assert data["movement"]["quantity"] == 2
    assert data["movement"]["reversalOfWorkId"] == "W1"
    assert data["result"]["reversedItems"] == 1


def test_reversal_does_not_double_apply_without_source_work():
    data = run_node(f"""
const integrity=require({json.dumps(str(INTEGRITY))});
const state={{inventory:[{{id:'I1',stock:8}}],works:[{{id:'W1',caseId:'C1',stockItems:[{{itemId:'I1',quantity:2,status:'Utilizado'}}]}}],stockMovements:[]}};
integrity.reverseStockForCases(state,['C1'],{{idFactory:()=> 'M1'}});
state.works=state.works.filter(w=>w.caseId!=='C1');
integrity.reverseStockForCases(state,['C1'],{{idFactory:()=> 'M2'}});
console.log(JSON.stringify({{stock:state.inventory[0].stock,count:state.stockMovements.length}}));
""")
    assert data == {"stock": 10, "count": 1}
