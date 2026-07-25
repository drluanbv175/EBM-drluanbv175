#!/usr/bin/env python3
"""Check PubMed retraction status for candidate PMIDs and scan medication safety flags.
Writes clinical_runtime/retraction_med_safety_report.json
"""
import json
from pathlib import Path
import time

import urllib.request
import urllib.parse

ROOT = Path("C:/Users/Admin/OneDrive/Claude AI")
SSR = ROOT / "clinical_runtime" / "strict_source_report.json"
EBM = ROOT / "EBM_MASTER" / "EBM_MASTER.json"
DRUG_FLAGS = ROOT / "sync" / "skills" / "dark-analyst" / "data" / "drug_flags.json"
OUT = ROOT / "clinical_runtime" / "retraction_med_safety_report.json"


def fetch_pubmed_esummary(pmid: str):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {"db": "pubmed", "id": pmid, "retmode": "json"}
    url = base + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}


def check_retracted_from_esummary(esum: dict):
    # Look for PubStatus or PubType marking retraction
    try:
        result = list(esum.get('result', {}).values())
        for item in result:
            if isinstance(item, dict):
                pubtypes = item.get('pubtype', []) or item.get('pubtypes', [])
                if isinstance(pubtypes, list):
                    for pt in pubtypes:
                        if 'retract' in str(pt).lower():
                            return True
                # title check
                title = item.get('title','')
                if 'retract' in title.lower() or 'retracted' in title.lower():
                    return True
    except Exception:
        pass
    return False


def med_safety_scan(text: str, drug_db: dict):
    norm = text.lower()
    hits = []
    for f in drug_db.get('flags', []):
        names = [f['drug']] + f.get('aliases', [])
        for n in names:
            if n.lower() in norm:
                hits.append({"drug": f['drug'], "found": n, "flag": f['flag']})
                break
    return hits


def main():
    ss = json.loads(SSR.read_text(encoding='utf-8'))
    ebm = json.loads(EBM.read_text(encoding='utf-8'))
    drug_db = json.loads(DRUG_FLAGS.read_text(encoding='utf-8'))
    results = {"generated": None, "checked": 0, "retracted": [], "med_safety_flags": []}
    for r in ss.get('results', []):
        if not r.get('candidate'):
            continue
        pmid = r.get('pmid') or ''
        doi = r.get('doi') or ''
        cid = r.get('id')
        entry = {"id": cid, "pmid": pmid, "doi": doi}
        # retraction check
        retracted = False
        esum = None
        if pmid:
            esum = fetch_pubmed_esummary(pmid)
            retracted = check_retracted_from_esummary(esum)
            time.sleep(0.34)  # throttle to avoid eutils limit
        entry['retracted'] = retracted
        entry['esummary_ok'] = isinstance(esum, dict) and 'result' in esum

        # med safety scan: look into evidence_basis titles and recommendation if present
        card = next((c for c in ebm.get('evidence_cards', []) if c.get('id') == cid), {})
        text_blobs = []
        text_blobs.append(card.get('recommendation') or '')
        for ev in (card.get('evidence_basis') or card.get('references') or []):
            if isinstance(ev, dict):
                text_blobs.append(ev.get('title',''))
                text_blobs.append(ev.get('study_type',''))
        joined = '\n'.join([t for t in text_blobs if t])
        meds = med_safety_scan(joined, drug_db)
        if meds:
            results['med_safety_flags'].append({"id": cid, "flags": meds})
        if retracted:
            results['retracted'].append(entry)
        results['checked'] += 1
    import datetime
    results['generated'] = datetime.datetime.utcnow().isoformat() + 'Z'
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
