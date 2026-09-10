#!/usr/bin/env python3
"""Produce a strict source report for outpatient apply candidates.
Writes clinical_runtime/strict_source_report.json listing evidence IDs and whether strict_source_gate_passed.
"""
import json
from pathlib import Path

# VÁ 12/08/2026: trước đây ROOT là đường dẫn Windows GHI CỨNG
# ("C:/Users/Admin/OneDrive/Claude AI") nên công cụ này chỉ chạy được trên đúng
# một máy và gãy im lặng trên MacBook. Suy ra từ vị trí file để chạy được ở cả
# hai máy, giống mọi công cụ khác trong tools/.
ROOT = Path(__file__).resolve().parents[1]
EBM = ROOT / "EBM_MASTER" / "EBM_MASTER.json"
OUT = ROOT / "clinical_runtime" / "strict_source_report.json"
FLAGS = ROOT / "clinical_runtime" / "CLINICAL_RUNTIME_FLAGS.json"


def require_strict_source_flag() -> bool:
    """Đọc cờ `require_strict_source` — thiếu file/lỗi đọc thì MẶC ĐỊNH True
    (fail-closed): một công cụ an toàn không được vì thiếu cờ mà tự coi kiểm
    tra nguồn là tuỳ chọn.

    VÌ SAO THÊM (10/09/2026): trước đây `CLINICAL_RUNTIME_FLAGS.json` khai cờ
    này nhưng KHÔNG NƠI NÀO trong repo đọc nó — kiểm tra bên dưới vẫn chạy
    (đúng, vì `main()` luôn kiểm), nhưng chạy vì mã CỨNG, không vì cờ nói vậy.
    Nối đọc thật vào đây để cờ có ý nghĩa: đổi `false` trong tương lai (quyết
    định của bác sĩ, không phải máy) sẽ THẬT SỰ tắt được kiểm tra.
    """
    try:
        return bool(json.loads(FLAGS.read_text(encoding="utf-8")).get("require_strict_source", True))
    except (OSError, ValueError, json.JSONDecodeError):
        return True


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
    require_strict_source = require_strict_source_flag()
    report = {
        'generated': None,
        'require_strict_source_flag': require_strict_source,
        'total': len(cards),
        'checked': 0,
        'results': [],
    }
    for c in cards:
        report['checked'] += 1
        cid = c.get('id')
        src = c.get('source') or c.get('references') or {}
        # determine candidate: if current decision is apply or recommendation contains 'recommend'
        decision = c.get('decision')
        candidate = (decision == 'apply') or ('recommend' in (c.get('recommendation') or '').lower())
        # Cờ tắt (bác sĩ tự quyết) vẫn TÍNH strict_source thật — chỉ khỏi bịa
        # 'đạt' cho thẻ chưa kiểm; caller đọc report tự quyết có chặn hay không
        # dựa vào require_strict_source_flag, không dựa suy đoán.
        strict = has_strict_source(src)
        report['results'].append({'id': cid, 'candidate': candidate, 'strict_source': strict, 'pmid': (src.get('pmid') if isinstance(src, dict) else None), 'doi': (src.get('doi') if isinstance(src, dict) else None)})
    import datetime
    # utcnow() bị loại bỏ dần từ Python 3.12 (DeprecationWarning) — dùng bản có
    # thông tin múi giờ tường minh để không kẹt khi nâng phiên bản.
    report['generated'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
