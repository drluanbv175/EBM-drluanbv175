# -*- coding: utf-8 -*-
"""Hồi quy cầu nạp sổ cái hub — thiếu --today không được sinh thẻ «EVID-0000» (03/11/2026).

Ca thật 03/11/2026: một lượt nạp nối tiếp gọi tay `ingest_dashboard.py <dashboard> --noi-tiep --ap-dung` mà quên
`--today` ⇒ 31 thẻ mới mang mã EVID-0000-1903…1933, date_added rỗng, ngày history rỗng, bản sao lưu tên
«manual_pre-noi-tiep» (đã khôi phục và nạp lại). Sổ cái thật còn 58 thẻ EVID-0000 do các lượt gọi tay trước đó.

Chạy NGUỒN CHUẨN sync/ebm-master-tools/ingest_dashboard.py trên sổ cái TẠM (--hub) — không đụng EBM_MASTER thật.
Dashboard giả tối thiểu, không PII.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INGEST = REPO / "sync" / "ebm-master-tools" / "ingest_dashboard.py"

LAT = "WebDashboard_EBM_VanDeCuThe_ThuNgayMacDinh"
V1, V2 = LAT + "_20260101.html", LAT + "_20260201.html"


def _item(local_id, title, doi, pmid):
    return {"id": local_id, "title": title, "decision": "consider", "gradeLevel": "moderate",
            "gradeSource": "GRADE thử", "pmid": pmid, "doi": doi, "org": "Hội thử", "design": "Guideline",
            "effectText": "", "vn": "", "action": "Hành động " + local_id, "monitoring": "", "safety": ""}


def _dashboard(thu_muc: Path, ten: str, items) -> Path:
    parts = ["{ " + ", ".join("%s: %s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in it.items()) + " }"
             for it in items]
    html = ("<html><body><script>\nconst DATA = {\n  meta: { question: \"Câu hỏi thử ngày nạp\", updated: \"2026-01-01\" },\n"
            "  items: [\n%s\n  ]\n};\n// HẾT KHỐI DATA\n</script></body></html>\n" % ",\n".join(parts))
    p = thu_muc / ten
    p.write_text(html, encoding="utf-8")
    return p


def _hub(tmp: Path) -> Path:
    hub = tmp / "hub"
    hub.mkdir()
    (hub / "EBM_MASTER.json").write_text(json.dumps(
        {"meta": {"counts": {}}, "evidence_cards": [], "quarantined_cards": []}), encoding="utf-8")
    return hub


def _chay(hub: Path, *args: str) -> subprocess.CompletedProcess:
    """Gọi cầu nạp KHÔNG tự thêm --today (khác test_ingest_noi_tiep_20261018 — luôn truyền ngày nên không bắt được lỗi)."""
    env = dict(os.environ, EBM_MASTER_LEDGER_LOCK_HELD="1", PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-B", str(INGEST), *map(str, args), "--hub", str(hub)],
                          capture_output=True, text=True, encoding="utf-8", env=env, cwd=str(hub), timeout=120)


def _doc(hub: Path) -> dict:
    return json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))


def _hom_nay() -> set[str]:
    """Ngày hôm nay — gồm cả ngày kế tiếp phòng khi lượt chạy vắt qua nửa đêm."""
    d = datetime.date.today()
    return {d.isoformat(), (d + datetime.timedelta(days=1)).isoformat()}


def test_nap_thuong_thieu_today_dung_ngay_hom_nay(tmp_path):
    hub = _hub(tmp_path)
    dash = _dashboard(tmp_path, V1, [_item("ITEM-01", "Mục A", "10.1/a", "1001"),
                                     _item("ITEM-02", "Mục B", "10.1/b", "1002")])
    r = _chay(hub, dash)
    assert r.returncode == 0, r.stdout + r.stderr
    the = _doc(hub)["evidence_cards"]
    assert len(the) == 2
    ngay = _hom_nay()
    for c in the:
        assert not c["id"].startswith("EVID-0000"), c["id"]
        assert c["id"][5:9] in {n[:4] for n in ngay}, c["id"]
        assert c["date_added"] in ngay, c["date_added"]
        assert c["history"][0]["date"] in ngay, c["history"]
    sao_luu = [p.name for p in (hub / "BACKUPS").iterdir()]
    assert sao_luu and all("manual" not in n for n in sao_luu), sao_luu
    assert any(x.replace("-", "") in n for n in sao_luu for x in ngay), sao_luu


def test_noi_tiep_ap_dung_thieu_today_dung_ngay_hom_nay(tmp_path):
    """Đúng đường ca thật: --noi-tiep --ap-dung — thẻ mới và dòng history của thẻ cập nhật tại chỗ đều mang ngày."""
    hub = _hub(tmp_path)
    v1 = _dashboard(tmp_path, V1, [_item("ITEM-01", "Mục A", "10.1/a", "1001")])
    env = dict(os.environ, EBM_MASTER_LEDGER_LOCK_HELD="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-B", str(INGEST), str(v1), "--hub", str(hub), "--today", "2026-01-10"],
                       capture_output=True, text=True, encoding="utf-8", env=env, cwd=str(hub), timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    v2 = _dashboard(tmp_path, V2, [_item("ITEM-01", "Mục A — tiêu đề mới", "10.1/a", "1001"),
                                   _item("ITEM-02", "Mục B mới", "10.1/b", "1002")])
    r = _chay(hub, v2, "--noi-tiep", "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    the = {c["topic"]: c for c in _doc(hub)["evidence_cards"]}
    ngay = _hom_nay()
    moi = the["Mục B mới"]
    assert not moi["id"].startswith("EVID-0000"), moi["id"]
    assert moi["date_added"] in ngay, moi["date_added"]
    cu = the["Mục A — tiêu đề mới"]
    assert cu["date_added"] == "2026-01-10", "thẻ cập nhật tại chỗ phải giữ date_added gốc"
    assert cu["history"][-1]["date"] in ngay, cu["history"]


def test_today_sai_dang_bi_tu_choi_va_khong_ghi(tmp_path):
    hub = _hub(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    dash = _dashboard(tmp_path, V1, [_item("ITEM-01", "Mục A", "10.1/a", "1001")])
    r = _chay(hub, dash, "--today", "03/11/2026")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "YYYY-MM-DD" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc
    assert not (hub / "BACKUPS").exists()


def test_today_truyen_vao_van_duoc_dung(tmp_path):
    hub = _hub(tmp_path)
    dash = _dashboard(tmp_path, V1, [_item("ITEM-01", "Mục A", "10.1/a", "1001")])
    r = _chay(hub, dash, "--today", "2025-12-31")
    assert r.returncode == 0, r.stdout + r.stderr
    c = _doc(hub)["evidence_cards"][0]
    assert c["id"].startswith("EVID-2025-"), c["id"]
    assert c["date_added"] == "2025-12-31"
