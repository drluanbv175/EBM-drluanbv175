# -*- coding: utf-8 -*-
"""Test công cụ đóng gói skill để bác sĩ tải lên tài khoản claude.ai (04/10/2026, BH163).

Khoá các hành vi:
  • ZIP có gốc là thư mục <tên>/ (đúng cấu trúc package_skill.py của Anthropic), bỏ rác (__pycache__, *.pyc, .DS_Store,
    evals/ ở gốc) nhưng GIỮ evals/ lồng sâu; chỉ tệp git track khi nguồn là cây git;
  • `name` khác tên thư mục ⇒ ZIP ghi name = tên thư mục, mọi byte khác giữ nguyên, nguồn không đổi;
  • luật tải lên chặn: mô tả có < >, mô tả quá dài, tên chứa «claude», thừa SKILL.md;
  • so CẢ tệp phụ với bản tài khoản (SKILL.md trùng mà tools/ khác ⇒ «cập nhật»); trùng hết ⇒ «đã mới», không đóng mặc định;
  • ZIP tất định; lượt sau chỉ xoá ZIP do lượt trước ghi; skill chỉ-Claude-Code không đóng mặc định; thiếu bộ tài khoản ⇒ mã 3;
  • `doi_chieu_ba_ben.doi_chieu` cũng xếp «SKILL.md trùng + tệp phụ khác» vào lệch bản.
Ngoại tuyến (thư mục tạm).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DG = _nap("_dg_test", "dong_goi_skill_tai_khoan.py")
DC = _nap("_dc_test_dg", "doi_chieu_ba_ben.py")


def _skill(goc: Path, ten: str, name: str | None = None, mo_ta: str = "Mô tả hợp lệ của skill.", them: dict | None = None,
           than: str = "Hướng dẫn.\n") -> Path:
    d = goc / ten
    d.mkdir(parents=True)
    (d / "SKILL.md").write_bytes(f"---\nname: {name or ten}\ndescription: {mo_ta}\n---\n{than}".encode("utf-8"))
    for rel, nd in (them or {}).items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_bytes(nd if isinstance(nd, bytes) else nd.encode("utf-8"))
    return d


def _ten_zip(p: Path) -> list[str]:
    with zipfile.ZipFile(p) as z:
        return sorted(z.namelist())


def test_zip_goc_la_thu_muc_skill_va_bo_rac(tmp_path):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    _skill(hub, "abc", them={"references/a.md": "x", "__pycache__/m.pyc": b"\0", "tools/t.pyc": b"\0", ".DS_Store": b"\0",
                             "evals/e.json": "{}", "sub/evals/k.json": "{}"})
    ket = DG.danh_gia(hub, None)
    DG.dong_goi(ket, hub, ra, None, "t")
    assert _ten_zip(ra / "abc.zip") == ["abc/SKILL.md", "abc/references/a.md", "abc/sub/evals/k.json"]


def test_chi_tep_git_track(tmp_path):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    d = _skill(hub, "abc", them={"references/da-track.md": "x", "references/chua-track.md": "y"})
    subprocess.run(["git", "init", "-q", str(hub)], check=True)
    subprocess.run(["git", "-C", str(hub), "add", "abc/SKILL.md", "abc/references/da-track.md"], check=True)
    ket = DG.danh_gia(hub, None)
    DG.dong_goi(ket, hub, ra, None, "t")
    assert _ten_zip(ra / "abc.zip") == ["abc/SKILL.md", "abc/references/da-track.md"]
    assert any("chưa git track" in c for c in ket[0]["canh"]), "phải nhắc tệp chưa track bị bỏ"
    assert (d / "references" / "chua-track.md").exists()


def test_ghi_lai_name_theo_thu_muc_nguon_khong_doi(tmp_path):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    d = _skill(hub, "abc-kdense", name="abc", than="Thân giữ nguyên: name: abc trong thân không bị đổi.\n")
    goc = (d / "SKILL.md").read_bytes()
    ket = DG.danh_gia(hub, None)
    DG.dong_goi(ket, hub, ra, None, "t")
    with zipfile.ZipFile(ra / "abc-kdense.zip") as z:
        moi = z.read("abc-kdense/SKILL.md")
    assert moi == goc.replace(b"name: abc\n", b"name: abc-kdense\n", 1), "chỉ dòng name trong frontmatter được đổi"
    assert (d / "SKILL.md").read_bytes() == goc, "nguồn không được đổi"
    assert ket[0]["doi_ten"] == "abc" and not ket[0]["loi"]


@pytest.mark.parametrize("ten,mo_ta,them,mau", [
    ("abc", "Cần Python ≥3.12,<3.14 để chạy.", None, "dấu < hoặc >"),
    ("abc", "x" * 1025, None, "1025 ký tự"),
    ("claude-helper", "Mô tả.", None, "từ dành riêng «claude»"),
    ("abc", "Mô tả.", {"phu/SKILL.md": "---\nname: phu\n---\n"}, "ĐÚNG MỘT SKILL.md"),
])
def test_luat_tai_len_chan_va_khong_dong_goi(tmp_path, ten, mo_ta, them, mau):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    _skill(hub, ten, mo_ta=mo_ta, them=them)
    assert DG.main(["--hub", str(hub), "--ra", str(ra), "--khong-so"]) == 1
    assert not (ra / f"{ten}.zip").exists()
    assert mau in (ra / DG.DANH_SACH).read_text(encoding="utf-8")


def test_frontmatter_khoan_dung():
    vb = ("---\nname: abc\ndescription: Quy trình: đối chiếu thuốc · kiểm tương tác\nmetadata:\n  version: 1.2.0\n"
          "license: 'MIT ''bản'' sửa'\nghi-chu: >-\n  dòng một\n  dòng hai\n---\nThân\n")
    fm = DG.doc_frontmatter(vb)
    assert fm["description"] == "Quy trình: đối chiếu thuốc · kiểm tương tác", "«: » không bọc nháy vẫn đọc trọn"
    assert fm["license"] == "MIT 'bản' sửa" and fm["ghi-chu"] == "dòng một dòng hai"
    assert set(fm) == {"name", "description", "metadata", "license", "ghi-chu"}
    assert DG._thong_tin_fm(vb)[0] == "1.2.0"


def test_so_ca_tep_phu_voi_tai_khoan(tmp_path):
    hub, tk, ra = tmp_path / "hub", tmp_path / "tk", tmp_path / "ra"
    _skill(hub, "cu", them={"tools/a.py": "print(2)\n"})
    _skill(tk, "cu", them={"tools/a.py": "print(1)\n"})
    _skill(hub, "khop", them={"tools/a.py": "x\n"})
    _skill(tk, "khop", them={"tools/a.py": "x\n"})
    _skill(hub, "chua-co")
    ket = {m["ten"]: m for m in DG.danh_gia(hub, tk)}
    assert ket["cu"]["trang_thai"] == "cap_nhat" and ket["cu"]["chi_tiet"]["tep_khac"] == 1
    assert ket["cu"]["chi_tiet"]["skill_md_khac"] is False, "SKILL.md trùng nhưng vẫn phải là «cập nhật»"
    assert ket["khop"]["trang_thai"] == "da_moi" and not ket["khop"]["dong_goi"]
    assert ket["chua-co"]["trang_thai"] == "moi" and ket["chua-co"]["dong_goi"]
    assert DG.danh_gia(hub, tk, tat_ca=True)[1]["dong_goi"], "--tat-ca đóng cả skill đã mới"


def test_doi_chieu_ba_ben_xep_tep_phu_khac_vao_lech_ban(tmp_path):
    cloud, repo = tmp_path / "cloud", tmp_path / "repo"
    _skill(cloud, "x", them={"tools/a.py": "print(1)\n"})
    _skill(repo, "x", them={"tools/a.py": "print(2)\n"})
    kq = DC.doi_chieu(DC.quet_thu_muc(cloud), DC.quet_thu_muc(repo), {}, chi_custom=True)
    assert [m["ten"] for m in kq["lech_ban"]] == ["x"] and kq["lech_ban"][0]["tep_phu_khac"] == 1
    assert kq["giong"] == []


def test_zip_tat_dinh_va_chi_xoa_zip_cua_luot_truoc(tmp_path):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    _skill(hub, "a", them={"r/1.md": "1"})
    _skill(hub, "b")
    DG.dong_goi(DG.danh_gia(hub, None), hub, ra, None, "t1")
    ban1 = (ra / "a.zip").read_bytes()
    (ra / "cua-bac-si.zip").write_bytes(b"giu")
    import shutil
    shutil.rmtree(hub / "b")
    DG.dong_goi(DG.danh_gia(hub, None), hub, ra, None, "t2")
    assert (ra / "a.zip").read_bytes() == ban1, "cùng nội dung phải cùng từng byte"
    assert not (ra / "b.zip").exists(), "ZIP của lượt trước không còn nguồn phải được dọn"
    assert (ra / "cua-bac-si.zip").read_bytes() == b"giu", "tệp không do công cụ ghi thì không đụng"
    assert json.loads((ra / DG.SO_LUOT).read_text(encoding="utf-8"))["zip"] == {"a.zip": DG.hashlib.sha256(ban1).hexdigest()}


def test_chi_claude_code_khong_dong_mac_dinh(tmp_path):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    _skill(hub, "plugin-router-chatgpt")
    DG.dong_goi(DG.danh_gia(hub, None), hub, ra, None, "t")
    assert not (ra / "plugin-router-chatgpt.zip").exists()
    DG.dong_goi(DG.danh_gia(hub, None, chon={"plugin-router-chatgpt"}), hub, ra, None, "t")
    assert (ra / "plugin-router-chatgpt.zip").exists(), "--skill vẫn đóng được khi bác sĩ muốn"


def test_thieu_bo_tai_khoan_ma_3_khong_ghi(tmp_path):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    _skill(hub, "a")
    assert DG.main(["--hub", str(hub), "--ra", str(ra), "--cloud", str(tmp_path / "khong-co")]) == 3
    assert not ra.exists()


def test_giac_quan_hom_viec(tmp_path):
    """Hòm việc nhắc khi skill tài khoản CŨ (ưu tiên 2); chỉ còn skill mới (tuỳ chọn) ⇒ ưu tiên 3; thiếu bộ tài khoản ⇒ giác quan
    chết (rỗng + ghi «chết»), KHÔNG phải «đã khớp»."""
    tdx = _nap("_tdx_dg_test", "tu_de_xuat_viec.py")
    hub, tk = tmp_path / "hub", tmp_path / "tk"
    _skill(hub, "cu", them={"tools/a.py": "2\n"})
    _skill(tk, "cu", them={"tools/a.py": "1\n"})
    _skill(hub, "moi-1")
    viec = tdx.giac_quan_skill_tai_khoan(bundle=tk, hub=hub)
    assert len(viec) == 1 and viec[0][0] == 2, viec
    assert "1 skill của bác sĩ" in viec[0][1] and "thêm 1 skill chưa từng lên" in viec[0][1]
    (tk / "cu" / "tools" / "a.py").write_bytes(b"2\n")  # write_text đổi \n thành \r\n trên Windows ⇒ tệp vẫn khác (CI 04/10)
    viec2 = tdx.giac_quan_skill_tai_khoan(bundle=tk, hub=hub)
    assert len(viec2) == 1 and viec2[0][0] == 3, "chỉ còn skill chưa từng lên ⇒ tuỳ chọn, ưu tiên thấp"
    assert tdx.giac_quan_skill_tai_khoan(bundle=tmp_path / "khong-co", hub=hub) == []


def test_chay_kho_khong_ghi(tmp_path):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    _skill(hub, "a")
    assert DG.main(["--hub", str(hub), "--ra", str(ra), "--khong-so", "--chay-kho"]) == 0
    assert not ra.exists()
