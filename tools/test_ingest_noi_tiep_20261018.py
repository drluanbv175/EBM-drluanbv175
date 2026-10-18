# -*- coding: utf-8 -*-
"""Hồi quy cầu nạp sổ cái hub — phiên bản nối tiếp + gốc rễ thẻ trùng (18/10/2026).

Chạy NGUỒN CHUẨN sync/ebm-master-tools/ingest_dashboard.py trên sổ cái TẠM (--hub) — không đụng
EBM_MASTER thật; chạy được cả trên CI (dang_ky_chu_de.py + ban_sao_tran.py đều trong git).
Dashboard giả tối thiểu, không PII.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INGEST = REPO / "sync" / "ebm-master-tools" / "ingest_dashboard.py"
HOM_NAY = "2026-03-15"

LAT = "WebDashboard_EBM_VanDeCuThe_ThuNoiTiep"
V1, V2, V3 = LAT + "_20260101.html", LAT + "_20260201.html", LAT + "_20260301.html"
LAT_KHAC_V2 = "WebDashboard_EBM_VanDeCuThe_ThuNoiTiep_DoiTuong_20260201.html"


def _nap_module():
    sys.path.insert(0, str(INGEST.parent))
    spec = importlib.util.spec_from_file_location("ingest_noi_tiep_test", INGEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _item(local_id, title, doi, pmid="", decision="consider", action="", grade="moderate", **them):
    it = {"id": local_id, "title": title, "decision": decision, "gradeLevel": grade,
          "gradeSource": "GRADE thử", "pmid": pmid, "doi": doi, "org": "Hội thử",
          "design": "Guideline", "effectText": "", "vn": "", "action": action,
          "monitoring": "", "safety": ""}
    it.update(them)
    return it


def _dashboard(thu_muc: Path, ten: str, items, question="Câu hỏi thử nối tiếp") -> Path:
    parts = ["{ " + ", ".join("%s: %s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in it.items()) + " }"
             for it in items]
    html = ("<html><body><script>\nconst DATA = {\n  meta: { question: %s, updated: \"2026-01-01\" },\n"
            "  items: [\n%s\n  ]\n};\n// HẾT KHỐI DATA\n</script></body></html>\n"
            % (json.dumps(question, ensure_ascii=False), ",\n".join(parts)))
    p = thu_muc / ten
    p.write_text(html, encoding="utf-8")
    return p


def _hub(tmp: Path) -> Path:
    hub = tmp / "hub"
    hub.mkdir()
    (hub / "EBM_MASTER.json").write_text(json.dumps(
        {"meta": {"counts": {}}, "evidence_cards": [], "quarantined_cards": []}), encoding="utf-8")
    return hub


def _chay(hub: Path, *args: str, today: str = HOM_NAY) -> subprocess.CompletedProcess:
    env = dict(os.environ, EBM_MASTER_LEDGER_LOCK_HELD="1", PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-B", str(INGEST), *map(str, args), "--hub", str(hub), "--today", today],
                          capture_output=True, text=True, encoding="utf-8", env=env, cwd=str(hub), timeout=120)


def _doc(hub: Path) -> dict:
    return json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))


def _theo_tieu_de(hub: Path) -> dict:
    out = {}
    for c in _doc(hub)["evidence_cards"]:
        out.setdefault(c["topic"], []).append(c)
    return out


def _ghi(hub: Path, data: dict) -> None:
    (hub / "EBM_MASTER.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _v1_items():
    return [
        _item("ITEM-01", "Khung dự phòng A", "10.1/a", "1001", decision="consider", action="Hành động A cũ"),
        _item("ITEM-02", "Mục B tiêu đề cũ", "10.1/b", "1002", action="Hành động B"),
        _item("ITEM-03", "Mục C không đổi", "10.1/a", "1001", decision="apply", action="Hành động C"),
        _item("ITEM-05", "Mục E sẽ biến mất", "10.1/e", "1005", action="Hành động E"),
    ]


def _v2_items():
    return [
        _item("ITEM-01", "Khung dự phòng A", "10.1/a", "1001", decision="apply", action="Hành động A MỚI"),
        _item("ITEM-02", "Mục B — tiêu đề mới", "10.1/b2", "2002", action="Hành động B"),
        _item("ITEM-03", "Mục C không đổi", "10.1/a", "1001", decision="apply", action="Hành động C"),
        _item("ITEM-04", "Mục D mới", "10.1/d", "1004", action="Hành động D"),
    ]


def _chuan_bi_v1(tmp: Path):
    hub = _hub(tmp)
    dash = tmp / "dash"
    dash.mkdir()
    v1 = _dashboard(dash, V1, _v1_items())
    r = _chay(hub, v1, today="2026-01-10")
    assert r.returncode == 0, r.stdout + r.stderr
    assert len(_doc(hub)["evidence_cards"]) == 4
    return hub, dash, v1


# ---------------------------------------------------------------------------------------------
# Gốc rễ thẻ trùng (bài toán 2): nạp lặp CÙNG một dashboard có nhiều mục chung DOI không sinh thêm thẻ
# ---------------------------------------------------------------------------------------------
def test_nap_lap_khong_sinh_ban_sao_khi_nhieu_muc_chung_doi(tmp_path):
    """Bản cầu nạp 11–13/07/2026 so thẻ mới với MỘT thẻ mỗi khoá ⇒ mục thứ hai cùng DOI bị coi là
    «nội dung khác» và được nạp lại MỖI lượt (193 thẻ thừa ngày 13/07). Phải so với MỌI thẻ cùng khoá."""
    hub = _hub(tmp_path)
    p = _dashboard(tmp_path, "WebDashboard_EBM_VanDeCuThe_ThuNapLap_20260101.html", [
        _item("ITEM-01", "Mục tiêu huyết áp dưới 130/80", "10.9/guideline", "9001"),
        _item("ITEM-02", "Dự phòng tiên phát đột quỵ — khung", "10.9/guideline", "9001"),
        _item("ITEM-03", "Statin cường độ cao", "10.9/guideline", "9001"),
    ])
    for _ in range(3):
        r = _chay(hub, p)
        assert r.returncode == 0, r.stdout + r.stderr
    the = _doc(hub)["evidence_cards"]
    assert len(the) == 3, [c["topic"] for c in the]
    assert sorted(c["topic"] for c in the) == sorted(
        ["Mục tiêu huyết áp dưới 130/80", "Dự phòng tiên phát đột quỵ — khung", "Statin cường độ cao"])


# ---------------------------------------------------------------------------------------------
# Bài toán 1: phiên bản nối tiếp
# ---------------------------------------------------------------------------------------------
def test_noi_tiep_cap_nhat_tai_cho_giu_dinh_danh(tmp_path):
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    data = _doc(hub)
    for c in data["evidence_cards"]:
        if c["topic"] == "Khung dự phòng A":
            c["specialty"] = "Thần kinh"                     # chuyên khoa gán sau khi nạp — phải giữ
            c["source"]["type"] = "khoá con lạ do công cụ khác ghi"
    _ghi(hub, data)
    truoc = {c["topic"]: c for c in _doc(hub)["evidence_cards"]}
    v2 = _dashboard(dash, V2, _v2_items())

    r = _chay(hub, v2, "--thay-ban", v1, "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    sau = _theo_tieu_de(hub)
    the = _doc(hub)["evidence_cards"]
    assert len(the) == 5, [c["topic"] for c in the]              # +1 đúng cho ITEM-04

    a = sau["Khung dự phòng A"]
    assert len(a) == 1
    a = a[0]
    a0 = truoc["Khung dự phòng A"]
    assert (a["id"], a["date_added"], a["specialty"], a["provenance"]) == (
        a0["id"], "2026-01-10", "Thần kinh", a0["provenance"])
    assert a["recommendation"] == "Hành động A MỚI"
    assert a["practice"]["action"] == "Hành động A MỚI"
    assert a["decision"] == "apply"
    assert a["source"]["type"] == "khoá con lạ do công cụ khác ghi"
    assert len(a["history"]) == len(a0["history"]) + 1
    cuoi = a["history"][-1]
    assert cuoi["date"] == HOM_NAY and "phiên bản nối tiếp " + V2 in cuoi["change"]
    assert "decision consider → apply" in cuoi["change"]

    # Mục đổi tiêu đề + đổi nguồn: CẬP NHẬT TẠI CHỖ, không sinh thẻ song song.
    assert "Mục B tiêu đề cũ" not in sau
    b = sau["Mục B — tiêu đề mới"]
    assert len(b) == 1 and b[0]["id"] == truoc["Mục B tiêu đề cũ"]["id"]
    assert (b[0]["source"]["pmid"], b[0]["source"]["doi"]) == ("2002", "10.1/b2")
    assert "PMID:2002" in b[0]["references"] and "PMID:1002" not in b[0]["references"]
    assert "nguồn PMID 1002/DOI 10.1/b → PMID 2002/DOI 10.1/b2" in b[0]["history"][-1]["change"]

    # Mục không đổi: không đụng (không thêm history).
    assert sau["Mục C không đổi"][0]["history"] == truoc["Mục C không đổi"]["history"]

    # Mục biến mất: GIỮ thẻ + báo.
    e_id = truoc["Mục E sẽ biến mất"]["id"]
    assert [c["id"] for c in sau["Mục E sẽ biến mất"]] == [e_id]
    assert "KHÔNG còn ở bản mới" in r.stdout and e_id in r.stdout

    # Mục mới: thẻ mới từ bản mới.
    d = sau["Mục D mới"]
    assert len(d) == 1 and d[0]["history"][0]["change"] == "nạp từ dashboard " + V2
    assert (hub / "BACKUPS" / ("EBM_MASTER_%s_pre-noi-tiep.json" % HOM_NAY.replace("-", ""))).is_file()


def test_noi_tiep_mac_dinh_chay_kho_khong_ghi(tmp_path):
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    v2 = _dashboard(dash, V2, _v2_items())
    r = _chay(hub, v2, "--thay-ban", v1)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "CHẠY KHÔ" in r.stdout and "✎" in r.stdout              # có in kế hoạch
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc
    assert not list(hub.glob("BACKUPS/*pre-noi-tiep*"))


def test_nap_thuong_khong_hoi_sinh_ban_cu_sau_noi_tiep(tmp_path):
    """Ca thật 18/10/2026: sync_all.py nạp CẢ bản cũ lẫn bản mới ⇒ bản cũ hồi sinh thẻ nội dung cũ."""
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    v2 = _dashboard(dash, V2, _v2_items())
    assert _chay(hub, v2, "--thay-ban", v1, "--ap-dung").returncode == 0
    so_truoc = len(_doc(hub)["evidence_cards"])
    r = _chay(hub, v1, v2)                                        # đúng cách sync_all gọi: cả lô
    assert r.returncode == 0, r.stdout + r.stderr
    sau = _theo_tieu_de(hub)
    assert len(_doc(hub)["evidence_cards"]) == so_truoc, list(sau)
    assert "Mục B tiêu đề cũ" not in sau
    assert "Bỏ qua " + V1 in r.stdout


def test_nap_thuong_chan_ban_moi_chua_noi_tiep(tmp_path):
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    v2 = _dashboard(dash, V2, _v2_items())
    r = _chay(hub, v2)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "--noi-tiep" in r.stdout and "CHƯA nạp " + V2 in r.stdout
    data = json.loads(truoc)
    assert len(_doc(hub)["evidence_cards"]) == len(data["evidence_cards"])
    assert {c["recommendation"] for c in _doc(hub)["evidence_cards"]} == {
        c["recommendation"] for c in data["evidence_cards"]}


def test_lan_dau_ca_lo_nhieu_phien_ban_chi_nap_ban_moi_nhat(tmp_path):
    hub = _hub(tmp_path)
    v1 = _dashboard(tmp_path, V1, _v1_items())
    v2 = _dashboard(tmp_path, V2, _v2_items())
    r = _chay(hub, v1, v2)
    assert r.returncode == 0, r.stdout + r.stderr
    sau = _theo_tieu_de(hub)
    assert "Mục B tiêu đề cũ" not in sau and "Mục B — tiêu đề mới" in sau
    assert len(_doc(hub)["evidence_cards"]) == 4


def test_khac_lat_cat_tu_choi_noi_tiep(tmp_path):
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    khac = _dashboard(dash, LAT_KHAC_V2, _v2_items())
    r = _chay(hub, khac, "--thay-ban", v1, "--ap-dung")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "KHÁC lát cắt" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc


def test_tron_ba_chieu_khong_ghi_de_sua_doi_ngoai_dashboard(tmp_path):
    """integrity_guard/khôi phục cách ly hạ decision, bản tổng hợp điền recommendation — nối tiếp
    KHÔNG được ghi đè (đó là «tự đổi decision ngoài dashboard»); trường trống thì được bù."""
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    data = _doc(hub)
    for c in data["evidence_cards"]:
        if c["topic"] == "Khung dự phòng A":
            c["decision"] = "notyet"                               # sửa ngoài dashboard
        if c["topic"] == "Mục C không đổi":
            c["recommendation"] = "Bản tổng hợp tiếng Việt đã điền"
            c["practice"]["safety"] = ""
    _ghi(hub, data)
    # Ca thật: dashboard CŨ bị sửa tại chỗ SAU khi nạp (vd .bak-20260816-gradeby) ⇒ sổ ≠ bản cũ hiện tại.
    v1_items = _v1_items()
    v1_items[2] = _item("ITEM-03", "Mục C không đổi", "10.1/a", "1001", decision="apply",
                        action="Hành động C", safety="Cờ đỏ cũ thêm tại chỗ")
    _dashboard(dash, V1, v1_items)
    v2_items = _v2_items()
    v2_items[2] = _item("ITEM-03", "Mục C không đổi", "10.1/a", "1001", decision="apply",
                        action="Hành động C", safety="Cờ đỏ mới thêm")
    v2 = _dashboard(dash, V2, v2_items)
    r = _chay(hub, v2, "--thay-ban", v1, "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    sau = _theo_tieu_de(hub)
    a = sau["Khung dự phòng A"][0]
    assert a["decision"] == "notyet"                               # GIỮ — bác sĩ quyết
    assert a["recommendation"] == "Hành động A MỚI"               # sổ còn y bản cũ ⇒ theo bản mới
    assert "GIỮ NGUYÊN" in r.stdout and "decision" in r.stdout
    c = sau["Mục C không đổi"][0]
    assert c["recommendation"] == "Bản tổng hợp tiếng Việt đã điền"
    assert c["practice"]["safety"] == "Cờ đỏ mới thêm"
    assert "practice.safety [bù trường trống]" in c["history"][-1]["change"]


def test_truong_nghiem_bac_si_da_xoa_khong_tu_bu(tmp_path):
    """Sổ để TRỐNG một trường nghiêm (vd bác sĩ bỏ PMID sai khi «THAY NGUỒN») ⇒ không được tự «bù
    trường trống» từ dashboard — luật bù chỉ dành cho trường mô tả."""
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    data = _doc(hub)
    for c in data["evidence_cards"]:
        if c["topic"] == "Mục B tiêu đề cũ":
            c["source"]["pmid"] = ""
    _ghi(hub, data)
    v2_items = _v2_items()
    v2_items[1] = _item("ITEM-02", "Mục B tiêu đề cũ", "10.1/b", "3003", action="Hành động B")
    v2 = _dashboard(dash, V2, v2_items)
    r = _chay(hub, v2, "--thay-ban", v1, "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    b = _theo_tieu_de(hub)["Mục B tiêu đề cũ"][0]
    assert b["source"]["pmid"] == ""
    assert "PMID:3003" not in b["references"]                    # không đưa lại nguồn qua cửa sau
    assert "GIỮ NGUYÊN" in r.stdout and "source.pmid" in r.stdout


def test_khong_dung_the_cua_lat_cat_khac(tmp_path):
    """Thẻ trùng khoá + tiêu đề nhưng nội dung đến từ LÁT CẮT KHÁC không thuộc dòng phiên bản."""
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    data = _doc(hub)
    goc = next(c for c in data["evidence_cards"] if c["topic"] == "Khung dự phòng A")
    khac = json.loads(json.dumps(goc))
    khac["id"] = "EVID-2026-0098"
    khac["history"] = [{"date": "2026-01-05", "change": "nạp từ dashboard " + LAT_KHAC_V2}]
    data["evidence_cards"].append(khac)
    _ghi(hub, data)
    v2 = _dashboard(dash, V2, _v2_items())
    r = _chay(hub, v2, "--thay-ban", v1, "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    sau = {c["id"]: c for c in _doc(hub)["evidence_cards"]}
    assert sau["EVID-2026-0098"]["recommendation"] == "Hành động A cũ"
    assert sau[goc["id"]]["recommendation"] == "Hành động A MỚI"


def test_noi_tiep_ba_phien_ban_nhan_the_tu_ban_dau(tmp_path):
    """v1→v2 không đụng thẻ không đổi (thẻ chỉ mang «nạp từ v1»); v2→v3 vẫn phải nhận ra thẻ đó."""
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    v2 = _dashboard(dash, V2, _v2_items())
    assert _chay(hub, v2, "--thay-ban", v1, "--ap-dung").returncode == 0
    c_id = _theo_tieu_de(hub)["Mục C không đổi"][0]["id"]
    v3_items = _v2_items()
    v3_items[2] = _item("ITEM-03", "Mục C không đổi", "10.1/a", "1001", decision="apply",
                        action="Hành động C bản ba")
    v3 = _dashboard(dash, V3, v3_items)
    r = _chay(hub, v3, "--noi-tiep", "--ap-dung")                # tự tìm bản trước (v2)
    assert r.returncode == 0, r.stdout + r.stderr
    assert V2 + " → " + V3 in r.stdout
    c = _theo_tieu_de(hub)["Mục C không đổi"]
    assert len(c) == 1 and c[0]["id"] == c_id
    assert c[0]["recommendation"] == "Hành động C bản ba"


def test_cum_trung_duoc_cap_nhat_ca_cum_va_bao(tmp_path):
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    data = _doc(hub)
    goc = next(c for c in data["evidence_cards"] if c["topic"] == "Khung dự phòng A")
    ban_sao = json.loads(json.dumps(goc))
    ban_sao["id"] = "EVID-2026-0099"
    data["evidence_cards"].append(ban_sao)
    _ghi(hub, data)
    v2 = _dashboard(dash, V2, _v2_items())
    r = _chay(hub, v2, "--thay-ban", v1, "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    a = _theo_tieu_de(hub)["Khung dự phòng A"]
    assert len(a) == 2 and {c["recommendation"] for c in a} == {"Hành động A MỚI"}
    assert "CỤM 2 thẻ" in r.stdout


def test_hai_muc_cung_ma_trong_mot_ban_dung_fail_closed(tmp_path):
    hub, dash, v1 = _chuan_bi_v1(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    loi = _v2_items() + [_item("ITEM-01", "Trùng mã", "10.1/z", "9")]
    v2 = _dashboard(dash, V2, loi)
    r = _chay(hub, v2, "--thay-ban", v1, "--ap-dung")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "hai mục cùng khoá" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc


def test_phan_loai_phien_ban_theo_so_cai_va_lo():
    m = _nap_module()
    assert m.phan_loai_phien_ban(V1, set(), [V1, V2]) == ("bo_qua_ban_cu", V2)
    assert m.phan_loai_phien_ban(V2, set(), [V1, V2]) == ("nap", None)
    assert m.phan_loai_phien_ban(V2, {V1}, [V2]) == ("can_noi_tiep", V1)
    assert m.phan_loai_phien_ban(V2, {V1, V2}, [V2]) == ("nap", None)
    assert m.phan_loai_phien_ban(V1, {V1, V2}, [V1]) == ("bo_qua_ban_cu", V2)
    # Lát cắt khác không liên quan nhau.
    assert m.phan_loai_phien_ban(LAT_KHAC_V2, {V1}, [LAT_KHAC_V2]) == ("nap", None)
    # Tên không theo quy ước ⇒ hành vi cũ.
    assert m.phan_loai_phien_ban("dashboard-tu-do.html", {V1}, []) == ("nap", None)


def test_card_dashboard_names_doc_ca_cap_nhat_tai_cho():
    m = _nap_module()
    card = {"history": [
        {"change": "nạp từ dashboard " + V1},
        {"change": "cập nhật tại chỗ theo phiên bản nối tiếp %s (ITEM-02; bác sĩ duyệt): recommendation" % V2},
        {"change": "bù trường pmid còn thiếu (đối chiếu trùng với %s)" % V3},
    ]}
    assert m.card_dashboard_names(card) == {V1, V2}
