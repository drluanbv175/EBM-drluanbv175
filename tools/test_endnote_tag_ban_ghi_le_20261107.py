# -*- coding: utf-8 -*-
"""Tag bản ghi LẺ + cảm biến «chưa phân loại» + tag trùng tên (07/11/2026, bác sĩ: «Tiếp tục hoàn thiện» sau lời giao «gắn
tab tất cả cho phù hợp»).

Đo thật 07/11/2026: 74 bản ghi không thuộc nhóm nào và không có tag (kế hoạch cũ chỉ xét bản ghi trong nhóm nên báo «đủ tag»);
11 bản ghi chủ đề Chăm sóc giảm nhẹ mất cả nhóm lẫn tag trong khoảng 10:05–10:06 mà không lệnh nào báo; «Frailty» có hai tag
cùng tên. Kiểm: (1) tệp bản ghi lẻ góp tag cần có ⇒ tag lẻ mất thì hiện thành thiếu; (2) «chưa phân loại» = không nhóm, không
trong tệp lẻ, không tag nào ngoài tag Áp dụng; (3) đọc tệp lẻ fail-closed; (4) tag trùng tên; (5) dòng tóm tắt + hòm việc."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


G = _nap("_gte_le_test", "gan_tag_endnote.py")
tdxv = _nap("_tdxv_gte_le", "tu_de_xuat_viec.py")
AD = G.TAG_AP_DUNG


def _ck(q: str) -> str:
    return "Tim mạch"


def _ke_hoach(**kw):
    mac_dinh = dict(ban_ghi={1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}},
                    nhom=[{"group_id": 9, "ten": "EBM · Suy tim", "rec": [1]},
                          {"group_id": 7, "ten": "Nhóm riêng bác sĩ", "rec": [2]}],
                    tag_hien_co={1: {"Tim mạch"}, 4: {AD}, 5: {"Tag riêng"}},
                    ten_tag={"Tim mạch", "CAD", AD, "Tag riêng"}, anh_xa={}, chuyen_khoa=_ck,
                    ngu_canh_cua=lambda p, d: [],
                    tag_le={"3": {"tag": ["Tim mạch", "CAD"]}, "99": {"tag": ["CAD"]}})
    mac_dinh.update(kw)
    return G.lap_ke_hoach(**mac_dinh)


# ───────────────────────── (1) tệp bản ghi lẻ góp tag cần có ─────────────────────────

def test_tag_le_vao_thieu_va_bo_qua_thung_rac():
    kh = _ke_hoach()
    assert kh["thieu"] == {"CAD": [3], "Tim mạch": [3]}       # 99 không thuộc ban_ghi (thùng rác) ⇒ bỏ qua
    kh2 = _ke_hoach(tag_hien_co={1: {"Tim mạch"}, 3: {"Tim mạch", "CAD"}, 4: {AD}, 5: {"Tag riêng"}})
    assert kh2["thieu"] == {}                                  # đã đủ ⇒ không còn thiếu
    # tag lẻ MẤT (đồng bộ online, khôi phục…) ⇒ hiện lại thành thiếu, không lặng lẽ biến mất
    kh3 = _ke_hoach(tag_hien_co={1: {"Tim mạch"}, 3: {"Tim mạch"}, 4: {AD}, 5: {"Tag riêng"}})
    assert kh3["thieu"] == {"CAD": [3]}


def test_mac_dinh_khong_co_tag_le_van_chay():
    """Người gọi cũ không truyền tag_le ⇒ chạy như trước, nhưng vẫn báo bản ghi chưa phân loại."""
    kh = _ke_hoach(tag_le=None)
    assert kh["thieu"] == {}
    assert 3 in kh["chua_phan_loai"]


# ───────────────────────── (2) chưa phân loại ─────────────────────────

def test_chua_phan_loai_dung_dinh_nghia():
    kh = _ke_hoach()
    # 1 trong nhóm · 2 trong nhóm CHƯA ánh xạ (vẫn là đã có chỗ) · 3 trong tệp lẻ · 4 chỉ có tag Áp dụng (không nói chuyên
    # khoa) ⇒ CHƯA phân loại · 5 có tag bác sĩ tự gắn ⇒ đã phân loại · 6 trơn ⇒ CHƯA
    assert kh["chua_phan_loai"] == [4, 6]
    assert G.con_viec(kh)


def test_chua_phan_loai_mot_minh_van_la_con_viec():
    kh = _ke_hoach(ban_ghi={6: {}}, nhom=[], tag_hien_co={}, tag_le={})
    assert kh["thieu"] == {} and kh["thua_ap_dung"] == [] and kh["nhom_chua_anh_xa"] == []
    assert kh["chua_phan_loai"] == [6] and G.con_viec(kh)
    assert "1 bản ghi chưa phân loại" in G.tom_tat_mot_dong(dict(kh, do_duoc=True))
    kh_du = _ke_hoach(ban_ghi={6: {}}, nhom=[], tag_hien_co={6: {"Tim mạch"}}, tag_le={})
    assert kh_du["chua_phan_loai"] == [] and not G.con_viec(kh_du)


def test_in_ke_hoach_noi_cach_xu_ly(capsys):
    kh = dict(_ke_hoach(ban_ghi={6: {}}, nhom=[], tag_hien_co={}, tag_le={}), do_duoc=True, thu_vien="x.enl", tag_trung=[])
    G.in_ke_hoach(kh)
    ra = capsys.readouterr().out
    assert "CHƯA PHÂN LOẠI" in ra and "recNum 6" in ra and "sync/endnote-tag-ban-ghi-le.json" in ra


# ───────────────────────── (3) đọc tệp lẻ fail-closed ─────────────────────────

@pytest.mark.parametrize("noi_dung", [
    {"ban_ghi": []},
    {"ban_ghi": {"abc": {"tag": ["Tim mạch"]}}},
    {"ban_ghi": {"12": {"tag": []}}},
    {"ban_ghi": {"12": {"tag": ["Tim mạch", " "]}}},
    {"ban_ghi": {"12": {"tieu_de": "x"}}},
])
def test_doc_tag_le_hong_thi_bao(tmp_path, noi_dung):
    p = tmp_path / "le.json"
    p.write_text(json.dumps(noi_dung), encoding="utf-8")
    with pytest.raises(ValueError):
        G.doc_tag_le(p)


def test_doc_tag_le_vang_la_rong_va_hop_le_doc_duoc(tmp_path):
    assert G.doc_tag_le(tmp_path / "vang.json") == {}
    p = tmp_path / "le.json"
    p.write_text(json.dumps({"ban_ghi": {"12": {"tieu_de": "x", "tag": ["Tim mạch"]}}}), encoding="utf-8")
    assert G.doc_tag_le(p) == {"12": {"tieu_de": "x", "tag": ["Tim mạch"]}}


def test_tep_le_trong_repo_hop_le():
    le = G.doc_tag_le()
    assert len(le) >= 73
    # bản ghi đề tài đã loại (loai_bo) KHÔNG mang tag «Nghiên cứu khoa học»
    assert all(G.TAG_NGHIEN_CUU not in v["tag"] for v in le.values())


def test_tep_le_hong_thi_ke_hoach_khong_do_duoc(tmp_path):
    """Tệp lẻ hỏng ⇒ cả kế hoạch «không đo được», không bao giờ xanh (đi qua ke_hoach_thu_vien thật)."""
    p = tmp_path / "le.json"
    p.write_text("{hỏng", encoding="utf-8")
    kh = G.ke_hoach_thu_vien(tmp_path / "khong-co.enl", tag_le_tep=p)
    assert kh["do_duoc"] is False
    assert kh["ly_do"].startswith("JSONDecodeError")             # đúng lỗi của tệp lẻ, không phải «chưa khai thư viện»


# ───────────────────────── (4) tag trùng tên ─────────────────────────

def test_tag_trung_ten():
    kn = sqlite3.connect(":memory:")
    kn.execute("create table tag_groups (group_id integer, spec blob)")
    kn.executemany("insert into tag_groups values (?, ?)", [(76, "<name>Frailty</name>".encode()), (77, "<name>Frailty</name>"),
                                                            (5, "<name>Depression</name>"), (6, "<name>Depressive</name>")])
    assert G.tag_trung_ten(kn) == ["Frailty"]
    kh = dict(_ke_hoach(ban_ghi={}, nhom=[], tag_hien_co={}, tag_le={}), do_duoc=True, tag_trung=["Frailty"])
    assert G.con_viec(kh) and "tag trùng tên: Frailty" in G.tom_tat_mot_dong(kh)


# ───────────────────────── (5) hòm việc ─────────────────────────

def test_giac_quan_hom_viec_bao_chua_phan_loai_va_tag_trung():
    kh = {"do_duoc": True, "thieu": {}, "thua_ap_dung": [], "tag_chua_tao": [], "nhom_chua_anh_xa": [],
          "chua_phan_loai": [9080, 9081], "tag_trung": ["Frailty"]}
    ra = tdxv.giac_quan_gan_tag_endnote(lambda: kh)
    assert [(r[1], "2 bản ghi chưa phân loại" in r[2]) for r in ra] == [("🛎", True), ("👤", False)]
    assert "Frailty" in ra[1][2]
    # khoá vắng (bản kế hoạch cũ) ⇒ không báo gì thêm, không vỡ
    assert tdxv.giac_quan_gan_tag_endnote(lambda: {"do_duoc": True, "thieu": {}, "thua_ap_dung": [], "tag_chua_tao": [],
                                                   "nhom_chua_anh_xa": []}) == []


def test_huong_dan_che_do_nen():
    """Đo thật 07/11: chế độ nền kéo được cả vùng chọn tô sáng (43 bản ghi một lần); bấm vào danh sách làm mất vùng chọn."""
    assert "CHẾ ĐỘ NỀN" in G.HUONG_DAN and "KHÔNG bấm vào danh sách" in G.HUONG_DAN
    assert "app_drag" in G.HUONG_DAN and "app_zoom" in G.HUONG_DAN


def test_nhom_lam_viec_khong_doi_tag_va_khong_tinh_la_phan_loai():
    """Nhóm «_Can toan van 20261107 - Find Full Text» (agent tạo 07/11, 120 bản ghi) từng làm kế hoạch báo 👤 «chưa ánh xạ»."""
    nhom = [{"group_id": 170, "ten": "_Can toan van 20261107 - Find Full Text", "rec": [1, 2]},
            {"group_id": 9, "ten": "EBM · Suy tim", "rec": [1]}]
    kh = _ke_hoach(ban_ghi={1: {}, 2: {}}, nhom=nhom, tag_hien_co={1: {"Tim mạch"}}, tag_le={})
    assert kh["nhom_chua_anh_xa"] == [] and kh["thieu"] == {}
    assert kh["chua_phan_loai"] == [2]                         # chỉ nằm ở nhóm làm việc ⇒ vẫn chưa phân loại
    # ánh xạ khai rõ group_id thắng luật nhóm làm việc
    kh2 = _ke_hoach(ban_ghi={1: {}, 2: {}}, nhom=nhom, tag_hien_co={1: {"Tim mạch"}}, tag_le={},
                    anh_xa={"170": {"tag": ["CAD"]}})
    assert kh2["thieu"] == {"CAD": [1, 2]} and kh2["chua_phan_loai"] == []


def test_nhom_cho_thung_rac_khong_bao_chua_phan_loai():
    """Nhóm 39 «_Cho thung rac 20261106 …» giữ bản ghi chờ bác sĩ chuyển thùng rác ⇒ không đòi tag, không báo chưa phân loại;
    nhóm làm việc khác thì thành viên CHỈ ở đó vẫn bị báo (để bản ghi lạc không bị che)."""
    nhom = [{"group_id": 39, "ten": "_Cho thung rac 20261106 trung va khong phai chung cu", "rec": [1]},
            {"group_id": 170, "ten": "_Can toan van 20261107 - Find Full Text", "rec": [2]}]
    kh = _ke_hoach(ban_ghi={1: {}, 2: {}}, nhom=nhom, tag_hien_co={}, tag_le={})
    assert kh["chua_phan_loai"] == [2] and kh["nhom_chua_anh_xa"] == [] and kh["thieu"] == {}


def test_duong_dan_in_ra_dang_posix_ca_tren_windows(monkeypatch, capsys):
    """CI Windows 07/11/2026: dòng hướng dẫn in «sync\\endnote-tag-ban-ghi-le.json» ⇒ lệnh dán lại hỏng trên Mac (§0.9).
    Giả lập đường dẫn Windows để bắt được ngay trên Mac."""
    from pathlib import PureWindowsPath
    monkeypatch.setattr(G, "GOC", PureWindowsPath("C:/r"))
    monkeypatch.setattr(G, "TEP_TAG_LE", PureWindowsPath("C:/r/sync/endnote-tag-ban-ghi-le.json"))
    monkeypatch.setattr(G, "TEP_ANH_XA", PureWindowsPath("C:/r/sync/endnote-tag-theo-nhom.json"))
    kh = dict(_ke_hoach(ban_ghi={6: {}, 7: {}}, nhom=[{"group_id": 5, "ten": "Nhóm riêng", "rec": [7]}], tag_hien_co={},
                        tag_le={}), do_duoc=True, thu_vien="x.enl", tag_trung=[])
    G.in_ke_hoach(kh)
    ra = capsys.readouterr().out
    assert "sync/endnote-tag-ban-ghi-le.json" in ra and "sync/endnote-tag-theo-nhom.json" in ra and "\\" not in ra


def test_nhom_he_thong_find_full_text_bi_bo_qua():
    """Đo 07/11/2026: khi bác sĩ chạy Find Full Text, EndNote sinh nhóm «Searching…»/«Not found»/«Found PDF»/«Found URL»
    (loại «TYPE;7») ⇒ kế hoạch từng báo 4 nhóm 👤 «chưa ánh xạ». Chỉ nhóm «custom» là chỗ phân loại."""
    nhom = [{"group_id": 173, "ten": "Not found", "loai": "TYPE;7", "rec": [1, 2]},
            {"group_id": 9, "ten": "EBM · Suy tim", "loai": "custom", "rec": [1]}]
    kh = _ke_hoach(ban_ghi={1: {}, 2: {}}, nhom=nhom, tag_hien_co={1: {"Tim mạch"}}, tag_le={})
    assert kh["nhom_chua_anh_xa"] == [] and kh["thieu"] == {}
    assert kh["chua_phan_loai"] == [2]                         # chỉ ở nhóm hệ thống ⇒ vẫn chưa phân loại


def test_huong_dan_giu_bai_hoc_go_tag_nen_va_find_full_text():
    """Đo 07/11: gỡ tag nhầm ở chế độ nền qua Edit Reference (× trên chip); Find Full Text đang chạy làm thanh bên nhảy ⇒ hoãn."""
    assert "Edit Reference" in G.HUONG_DAN and "× trên chip" in G.HUONG_DAN
    assert "Find Full Text đang chạy ⇒ HOÃN kéo-thả" in G.HUONG_DAN and "zoom HAI lần" in G.HUONG_DAN
