# -*- coding: utf-8 -*-
"""Gắn tag EndNote theo luật (07/11/2026, bác sĩ: «mỗi lần đưa trích dẫn vào Endnote sẽ gắn Tab luôn cho tôi … gắn tab với
những chứng cứ có độ tin cậy cao và áp dụng cho thực hành lâm sàng»; chọn «Thêm guideline không chấm GRADE» + «gắn ngay sau
mỗi lần nạp»).

Kiểm: (1) tiêu chí tag «★ Áp dụng – tin cậy cao» — chỉ mục `apply` ở phiên bản HIỆN HÀNH, high/moderate, hoặc `na` khi là
guideline/nhãn thuốc (consensus không đủ, low/vlow không đủ, bản cũ không tính — đo thật 07/11: 9 bài «apply/high» chỉ còn ở
bản cũ của dashboard tuần Tim mạch 09/06 là bài lạc đề); (2) tag theo nhóm: ánh xạ đã duyệt thắng luật suy, «NC ·» ⇒ Nghiên cứu
khoa học, «EBM ·» ⇒ chuyên khoa, nhóm lạ ⇒ KHÔNG đoán; (3) kế hoạch thiếu/thừa/tag chưa tạo; (4) đọc tag từ sdb.eni;
(5) không đo được ⇒ không bao giờ «đủ tag»; (6) lượt nạp thật gọi báo gắn tag; hòm việc báo 🛎/👤."""
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


G = _nap("_gte_test", "gan_tag_endnote.py")
tdxv = _nap("_tdxv_gte", "tu_de_xuat_viec.py")
AD = G.TAG_AP_DUNG


def _muc(decision="apply", grade="high", design="RCT", ban_cu=False, vai="muc") -> dict:
    return {"vai": vai, "decision": decision, "gradeLevel": grade, "design": design, "ban_cu": ban_cu}


# ───────────────────────── (1) tiêu chí tag Áp dụng – tin cậy cao ─────────────────────────

@pytest.mark.parametrize("muc", [_muc(grade="high"), _muc(grade="mod"), _muc(grade="moderate"),
                                 _muc(grade="na", design="Guideline — ESC (Class/Level)"),
                                 _muc(grade="na", design="Nhãn thuốc — EMA/PRAC"),
                                 _muc(grade="na", design="Hướng dẫn quốc gia Bộ Y tế")])
def test_dat_khi_apply_tin_cay(muc):
    assert G.dat_ap_dung_tin_cay([muc]) is True


@pytest.mark.parametrize("muc", [_muc(grade="low"), _muc(grade="vlow"), _muc(grade="na", design="Consensus"),
                                 _muc(grade="na", design="Expert consensus statement"), _muc(grade="na", design="RCT"),
                                 _muc(grade="na", design="Consensus — khuyến cáo chuyên gia"),
                                 _muc(decision="consider", grade="high"), _muc(decision="notyet", grade="high"),
                                 _muc(vai="tham_khao", grade="high"), _muc(grade="high", ban_cu=True)])
def test_khong_dat(muc):
    assert G.dat_ap_dung_tin_cay([muc]) is False


def test_ban_cu_khong_cuu_ban_hien_hanh():
    """Bản cũ apply/high + bản hiện hành chỉ consider ⇒ KHÔNG đạt (bản mới đổi quyết định)."""
    assert G.dat_ap_dung_tin_cay([_muc(grade="high", ban_cu=True), _muc(decision="consider", grade="high")]) is False


def test_mot_muc_dat_la_du():
    assert G.dat_ap_dung_tin_cay([_muc(grade="low"), _muc(grade="na", design="Guideline")]) is True
    assert G.dat_ap_dung_tin_cay([]) is False


# ───────────────────────── (2) tag theo nhóm ─────────────────────────

def _ck(q: str) -> str:
    return "Tim mạch" if "suy tim" in q.lower() else "Huyết học" if "thiếu máu" in q.lower() else "Tổng hợp / Đa khoa"


def test_anh_xa_thang_luat_suy():
    ax = {"9": {"ten": "EBM · Suy tim x", "tag": ["Lão khoa", "Tâm thần"]}}
    assert G.tag_cua_nhom(9, "EBM · Suy tim x", ax, _ck) == ["Lão khoa", "Tâm thần"]


def test_luat_suy_nhom_moi():
    assert G.tag_cua_nhom(1, "NC · hai-long", {}, _ck) == [G.TAG_NGHIEN_CUU]
    assert G.tag_cua_nhom(2, "EBM · Suy tim mạn ngoại trú", {}, _ck) == ["Tim mạch"]
    assert G.tag_cua_nhom(3, "TT · Suy tim toàn diện", {}, _ck) == ["Tim mạch"]
    assert G.tag_cua_nhom(4, "EBM · Thiếu máu", {}, _ck) == [G.TAG_CHUNG]  # chuyên khoa không có tag riêng


def test_nhom_la_khong_doan():
    assert G.tag_cua_nhom(5, "Nhóm bác sĩ tự tạo", {}, _ck) is None


# ───────────────────────── (3) kế hoạch ─────────────────────────

def _ke_hoach(**kw):
    mac_dinh = dict(ban_ghi={1: {"pmid": "11"}, 2: {"pmid": "22"}, 3: {"pmid": "33"}},
                    nhom=[{"group_id": 9, "ten": "EBM · Suy tim", "rec": [1, 2, 99]},
                          {"group_id": 7, "ten": "Nhóm riêng", "rec": [3]}],
                    tag_hien_co={1: {"Tim mạch"}, 3: {AD}, 99: {AD}},
                    ten_tag={"Tim mạch"}, anh_xa={}, chuyen_khoa=_ck,
                    ngu_canh_cua=lambda p, d: [_muc(grade="high")] if p == "22" else [])
    mac_dinh.update(kw)
    return G.lap_ke_hoach(**mac_dinh)


def test_ke_hoach_thieu_thua_va_tag_chua_tao():
    kh = _ke_hoach()
    assert kh["thieu"] == {AD: [2], "Tim mạch": [2]}
    assert list(kh["thieu"])[0] == AD                      # tag Áp dụng xếp đầu
    assert kh["thua_ap_dung"] == [3]                        # 99 không thuộc ban_ghi (thùng rác) ⇒ bỏ qua
    assert kh["tag_chua_tao"] == [AD]
    assert kh["nhom_chua_anh_xa"] == [{"group_id": 7, "ten": "Nhóm riêng", "so_ban_ghi": 1}]
    assert kh["dat_ap_dung"] == 1 and kh["tong_ban_ghi"] == 3
    assert G.con_viec(kh)


def test_ke_hoach_du_tag():
    kh = _ke_hoach(nhom=[{"group_id": 9, "ten": "EBM · Suy tim", "rec": [1, 2]}], tag_hien_co={1: {"Tim mạch"},
                   2: {"Tim mạch", AD}}, ten_tag={"Tim mạch", AD})
    assert kh["thieu"] == {} and kh["thua_ap_dung"] == [] and kh["tag_chua_tao"] == [] and not G.con_viec(kh)
    assert G.tom_tat_mot_dong(dict(kh, do_duoc=True)).startswith("✓")


def test_khong_bao_gio_de_xuat_go_tag_khac():
    """Bản ghi mang tag ngoài luật (bác sĩ tự gắn) ⇒ không vào «thừa» — chỉ tag Áp dụng có thể thừa."""
    kh = _ke_hoach(tag_hien_co={1: {"Tim mạch", "Tag riêng bác sĩ"}, 2: {"Tim mạch", AD}}, ten_tag={"Tim mạch", AD})
    assert kh["thua_ap_dung"] == []


# ───────────────────────── (4) đọc tag sdb.eni ─────────────────────────

def test_doc_tag():
    kn = sqlite3.connect(":memory:")
    kn.execute("create table tag_groups (group_id integer, spec blob)")
    kn.execute("create table tag_members_content (id integer, c0 text)")
    kn.executemany("insert into tag_groups values (?, ?)", [(10, "<name>Tim mạch</name>".encode()), (31, f"<name>{AD}</name>")])
    kn.executemany("insert into tag_members_content values (?, ?)", [(5, "a 1f"), (6, "zz a"), (7, None)])
    ten, theo = G.doc_tag(kn)
    assert ten == {"Tim mạch", AD}
    assert theo == {5: {"Tim mạch", AD}, 6: {"Tim mạch"}, 7: set()}


def test_doc_anh_xa(tmp_path):
    assert G.doc_anh_xa(tmp_path / "vang.json") == {}
    hong = tmp_path / "hong.json"
    hong.write_text(json.dumps({"nhom": []}), encoding="utf-8")
    with pytest.raises(ValueError):
        G.doc_anh_xa(hong)


def test_tep_anh_xa_trong_repo_hop_le():
    ax = G.doc_anh_xa()
    assert len(ax) >= 100
    assert all(isinstance(v.get("tag"), list) and v["tag"] and all(isinstance(t, str) and t for t in v["tag"])
               for v in ax.values())


# ───────────────────────── (5) không đo được ≠ đủ tag ─────────────────────────

def test_khong_do_duoc_khong_bao_gio_xanh(tmp_path):
    kh = G.ke_hoach_thu_vien(tmp_path / "khong-co.enl")
    assert kh["do_duoc"] is False
    assert G.tom_tat_mot_dong(kh).startswith("⚪")
    assert not G.tom_tat_mot_dong(kh).startswith("✓")


# ───────────────────────── (6) nối dây: lượt nạp + hòm việc ─────────────────────────

def test_luot_nap_that_goi_bao_gan_tag():
    """Khớp DÒNG THI HÀNH (không khớp cả tệp): sau lượt nạp `--ap-dung` có EndNote ⇒ gọi bao_gan_tag."""
    dong = (REPO / "tools" / "nap_endnote_chu_de.py").read_text(encoding="utf-8").splitlines()
    i = next(k for k, d in enumerate(dong) if d.strip() == "if a.ap_dung and endnote is not None:"
             and dong[k + 1].strip() == "bao_gan_tag(endnote.thu_vien)")
    assert not dong[i].lstrip().startswith("#")


def test_bao_gan_tag_khong_lam_sap_luot_nap(tmp_path, capsys):
    nap = _nap("_nap_gte_test", "nap_endnote_chu_de.py")
    dong = nap.bao_gan_tag(tmp_path / "khong-co.enl")
    assert dong.startswith("⚪") and "⚪" in capsys.readouterr().out


def test_huong_dan_giu_hai_bai_hoc_do_that():
    """Hai bẫy đo thật 07/11: thả lên chính khung đang xem không tác dụng; kéo tag thứ hai từ vùng chọn cũ gắn nhầm dòng khác."""
    assert "All References" in G.HUONG_DAN and "mỗi tag một lượt `--hien` riêng" in G.HUONG_DAN
    assert "ListAgents" in G.HUONG_DAN and "TẠM DỪNG" in G.HUONG_DAN


def test_giac_quan_hom_viec(monkeypatch):
    chet = []
    monkeypatch.setattr(tdxv, "_ghi_chet", lambda lenh, ly: chet.append(ly))
    assert tdxv.giac_quan_gan_tag_endnote(lambda: {"do_duoc": False, "ly_do": "chưa khai"}) == [] and chet == ["chưa khai"]
    kh = {"do_duoc": True, "thieu": {AD: [1, 2], "Tim mạch": [3]}, "thua_ap_dung": [4], "tag_chua_tao": [AD],
          "nhom_chua_anh_xa": [{"group_id": 7, "ten": "x", "so_ban_ghi": 1}]}
    ra = tdxv.giac_quan_gan_tag_endnote(lambda: kh)
    nhan = [r[1] for r in ra]
    assert nhan.count("🛎") == 2 and nhan.count("👤") == 1
    assert "3 cặp" in ra[0][2] and "1 bản ghi thừa" in ra[0][2]
    assert tdxv.giac_quan_gan_tag_endnote(lambda: {"do_duoc": True, "thieu": {}, "thua_ap_dung": [], "tag_chua_tao": [],
                                                   "nhom_chua_anh_xa": []}) == []
    src = (REPO / "tools" / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    assert "\n    de_xuat += giac_quan_gan_tag_endnote()\n" in src
