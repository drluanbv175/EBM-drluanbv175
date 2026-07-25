#!/usr/bin/env python3
"""Produce a strict source report for outpatient apply candidates.
Writes clinical_runtime/strict_source_report.json listing evidence IDs and whether strict_source_gate_passed.
"""
import json
from pathlib import Path

ROOT = Path("C:/Users/Admin/OneDrive/Claude AI")
EBM = ROOT / "EBM_MASTER" / "EBM_MASTER.json"
OUT = ROOT / "clinical_runtime" / "strict_source_report.json"

def has_strict_source(src):
    if not src:
        return False
    # prefer pmid/doi
    if isinstance(src, dict):
        if src.get('pmid'):
            return True
        if src.get('doi'):
            return True
        if src.get('agency') and src.get('agency').lower() in ('who','nice','esc','aha','kdigo','who guideline'):
            return True
    return False


def main():
    data = json.loads(EBM.read_text(encoding='utf-8'))
    cards = data.get('evidence_cards', [])
    report = {'generated': None, 'total': len(cards), 'checked': 0, 'results': []}
    for c in cards:
        report['checked'] += 1
        cid = c.get('id')
        src = c.get('source') or c.get('references') or {}
        # determine candidate: if current decision is apply or recommendation contains 'recommend'
        decision = c.get('decision')
        candidate = (decision == 'apply') or ('recommend' in (c.get('recommendation') or '').lower())
        strict = has_strict_source(src)
        report['results'].append({'id': cid, 'candidate': candidate, 'strict_source': strict, 'pmid': (src.get('pmid') if isinstance(src, dict) else None), 'doi': (src.get('doi') if isinstance(src, dict) else None)})
    import datetime
    report['generated'] = datetime.datetime.utcnow().isoformat() + 'Z'
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
