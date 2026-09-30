#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cho câu 'trạm web hội' trong tuyen_bo_do_phu.tra_khoi() (vá 13/09/2026).

Vì sao có: câu này trước đây hardcode "CHƯA CHẠY (chờ phê duyệt egress)" cho
MỌI lần sinh báo cáo — kể cả sau khi nhiều trạm html-watch (GOLD/GINA/KDIGO/
ADA/ESC/ACC-AHA) đã chạy thật qua kênh Browser (--nap-van-ban). Test này khoá
hành vi ĐÚNG: câu phải tính từ last_success_at thật, không phải chuỗi cố định."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("tbdp_test_mod", ROOT / "tools" / "tuyen_bo_do_phu.py")
assert SPEC and SPEC.loader
T = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = T
SPEC.loader.exec_module(T)


def _nguon(sid: str, access: str = "html-watch", status: str = "active",
           last_success_at: str | None = None, org: str = "X",
           name: str = "Nguồn X — web hội") -> dict:
    return {"id": sid, "org": org, "name": name, "access": access,
            "status": status, "last_success_at": last_success_at}


def _don_dep(monkeypatch, tmp_path: Path, sources: list[dict]) -> None:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "sources.json").write_text(
        json.dumps({"updated": "2026-09-13", "sources": sources}), encoding="utf-8")
    monkeypatch.setattr(T, "GOC", tmp_path)


def test_tram_web_hoi_da_chay_het_khong_con_noi_cho_phe_duyet(monkeypatch, tmp_path: Path) -> None:
    """Mọi trạm html-watch đều có last_success_at ⇒ câu phải nói ĐÃ CHẠY, không
    còn được phép in cụm cố định cũ 'chờ phê duyệt egress'."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon("SRC-A", last_success_at="2026-09-13"),
        _nguon("SRC-B", last_success_at="2026-09-13"),
    ])
    khoi = T.tra_khoi()
    dong_do_tre = next(d for d in khoi.splitlines() if d.startswith("Độ trễ đo được"))
    assert "2/2 đã chạy thật qua kênh Browser" in dong_do_tre
    assert "chờ phê duyệt egress" not in dong_do_tre
    assert "CHƯA CHẠY" not in dong_do_tre


def test_tram_web_hoi_con_mot_phan_chua_chay_neu_dung_ten(monkeypatch, tmp_path: Path) -> None:
    """Còn trạm chưa chạy thì phải liệt kê ĐÚNG tên trạm đó (không phải chuỗi
    'nhiều' lấy nhầm từ trường org khi org là nhãn gộp nhiều tổ chức)."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon("SRC-A", last_success_at="2026-09-13"),
        _nguon("SRC-B", last_success_at=None, org="nhiều",
               name="IDSA · AGS Beers · USPSTF web · WHO web · NICE web"),
    ])
    khoi = T.tra_khoi()
    assert "1/2 đã chạy thật qua kênh Browser" in khoi
    assert "còn 1 trạm CHƯA CHẠY" in khoi
    assert "IDSA" in khoi
    assert "(nhiều)" not in khoi


def test_khong_co_tram_web_hoi_nao_khong_bien_thanh_chuoi_cam(monkeypatch, tmp_path: Path) -> None:
    """Sổ nguồn rỗng access=html-watch: không được crash, không được bịa số."""
    _don_dep(monkeypatch, tmp_path, [_nguon("SRC-A", access="api", last_success_at="2026-09-13")])
    khoi = T.tra_khoi()
    assert "CHƯA CÓ TRẠM NÀO KHAI TRONG SỔ NGUỒN" in khoi


# ── VÁ 30/09/2026: «Đang giám sát tự động» không được gộp nguồn gọi-theo-yêu-cầu ─────────────────────────────
# Đo trên sổ thật 30/09: 9/30 nguồn in dưới «Đang giám sát tự động … nhịp tuần/tháng» có `scan_frequency: ad-hoc`
# (connector MCP tương tác, connector toàn văn gọi tay, bậc thang dự phòng) — «active» bị đọc thành «đang được quét».

def _nguon_nhip(sid: str, ten: str, nhip: str | None, status: str = "active", access: str = "api") -> dict:
    s = {"id": sid, "org": "X", "name": ten, "access": access, "status": status, "last_success_at": "2026-09-30"}
    if nhip is not None:
        s["scan_frequency"] = nhip
    return s


def _dong(khoi: str, dau: str) -> str:
    khop = [d for d in khoi.splitlines() if d.startswith(dau)]
    assert len(khop) == 1, (dau, khop)
    return khop[0]


def test_nguon_goi_theo_yeu_cau_khong_bi_dem_la_giam_sat_tu_dong(monkeypatch, tmp_path: Path) -> None:
    _don_dep(monkeypatch, tmp_path, [
        _nguon_nhip("SRC-A", "PubMed — làn tuần", "weekly"),
        _nguon_nhip("SRC-B", "Retraction Watch — nền tháng", "monthly", access="file"),
        _nguon_nhip("SRC-C", "RxNorm — chuẩn hoá tên thuốc", "ad-hoc"),
        _nguon_nhip("SRC-D", "Cochrane MCP — phiên tương tác", "ad-hoc"),
    ])
    khoi = T.tra_khoi()
    tu_dong = _dong(khoi, "Đang giám sát tự động")
    assert tu_dong.startswith("Đang giám sát tự động: 2 nguồn — PubMed; Retraction Watch;")
    assert "RxNorm" not in tu_dong and "Cochrane MCP" not in tu_dong
    theo_yc = _dong(khoi, "Gọi theo yêu cầu")
    assert "KHÔNG tự quét định kỳ: 2 nguồn/công cụ — RxNorm; Cochrane MCP." in theo_yc
    assert "PubMed" not in theo_yc


def test_nguon_theo_yeu_cau_dang_hong_khong_duoc_liet_ke_la_dung_duoc(monkeypatch, tmp_path: Path) -> None:
    """Dòng «gọi theo yêu cầu» liệt kê thứ DÙNG ĐƯỢC: nguồn ad-hoc đang degraded/not-covered không được lọt vào."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon_nhip("SRC-A", "PubMed — làn tuần", "weekly"),
        _nguon_nhip("SRC-C", "RxNorm — chuẩn hoá tên thuốc", "ad-hoc"),
        _nguon_nhip("SRC-E", "EMA medicines — 403", "ad-hoc", status="degraded"),
        _nguon_nhip("SRC-F", "Epistemonikos — chờ token", "ad-hoc", status="not-covered"),
    ])
    theo_yc = _dong(T.tra_khoi(), "Gọi theo yêu cầu")
    assert ": 1 nguồn/công cụ — RxNorm." in theo_yc
    assert "EMA" not in theo_yc and "Epistemonikos" not in theo_yc


def test_khong_co_nguon_theo_yeu_cau_thi_khong_in_dong_rong(monkeypatch, tmp_path: Path) -> None:
    _don_dep(monkeypatch, tmp_path, [_nguon_nhip("SRC-A", "PubMed — làn tuần", "weekly")])
    khoi = T.tra_khoi()
    assert "Gọi theo yêu cầu" not in khoi
    assert _dong(khoi, "Đang giám sát tự động").startswith("Đang giám sát tự động: 1 nguồn — PubMed;")


def test_nhip_in_ra_la_nhip_co_that_trong_so(monkeypatch, tmp_path: Path) -> None:
    """Câu cũ viết cứng «nhịp tuần/tháng» dù sổ có trạm quý; nay in đúng các nhịp ĐANG có, theo thứ tự ngày→quý."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon_nhip("SRC-Q", "GOLD — web hội", "quarterly", access="html-watch"),
        _nguon_nhip("SRC-A", "PubMed — làn tuần", "weekly"),
    ])
    assert _dong(T.tra_khoi(), "Đang giám sát tự động").endswith("; nhịp tuần/quý.")


def test_nguon_thieu_scan_frequency_giu_hanh_vi_cu(monkeypatch, tmp_path: Path) -> None:
    """Fixture cũ không khai `scan_frequency`: vẫn đếm ở nhóm định kỳ (không đổi hành vi với dữ liệu thiếu trường)."""
    _don_dep(monkeypatch, tmp_path, [_nguon_nhip("SRC-A", "Nguồn cũ — không khai nhịp", None)])
    khoi = T.tra_khoi()
    assert _dong(khoi, "Đang giám sát tự động").startswith("Đang giám sát tự động: 1 nguồn — Nguồn cũ;")
    assert _dong(khoi, "Đang giám sát tự động").endswith("; nhịp tuần/tháng.")


def test_so_that_khong_con_in_cong_cu_theo_yeu_cau_duoi_giam_sat_tu_dong() -> None:
    """Trên SỔ THẬT của repo: mọi nguồn `ad-hoc` đang active phải nằm ở dòng «gọi theo yêu cầu», không nguồn nào
    nằm ở «giám sát tự động» (đúng ca đo 30/09: Cochrane MCP, Wiley, RxNorm… từng bị in là đang được quét)."""
    so = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]
    ad_hoc = [T._ten(s) for s in so if s["status"] == "active" and s.get("scan_frequency") == "ad-hoc"]
    assert ad_hoc, "sổ thật không còn nguồn ad-hoc nào đang active — test này đang đo nhầm chỗ"
    khoi = T.tra_khoi()
    tu_dong = _dong(khoi, "Đang giám sát tự động")
    theo_yc = _dong(khoi, "Gọi theo yêu cầu")
    danh_sach_tu_dong = tu_dong.split(" — ", 1)[1].rsplit("; nhịp ", 1)[0].split("; ")
    for ten in ad_hoc:
        assert ten in theo_yc, ten
        assert ten not in danh_sach_tu_dong, ten
    assert f": {len(ad_hoc)} nguồn/công cụ — " in theo_yc


def test_main_chay_duoc_tren_ban_sao_tran_khong_co_thu_muc_reports(monkeypatch, tmp_path: Path, capsys) -> None:
    """`reports/` nằm ngoài git nên bản sao trần (worktree tươi, phiên Cloud) không có: `main()` phải tự tạo thư mục
    rồi ghi, không sập FileNotFoundError sau khi đã dựng xong khối (đo 30/09/2026 trong một worktree)."""
    _don_dep(monkeypatch, tmp_path, [_nguon_nhip("SRC-A", "PubMed — làn tuần", "weekly")])
    assert not (tmp_path / "reports").exists()
    assert T.main() == 0
    ra = tmp_path / "reports" / "do-phu-hien-hanh.md"
    noi_dung = ra.read_text(encoding="utf-8")
    assert noi_dung.startswith("# ĐỘ PHỦ NGUỒN (cập nhật 2026-09-13)\n\nĐang giám sát tự động: 1 nguồn — PubMed;")
    assert "reports/do-phu-hien-hanh.md" in capsys.readouterr().out.replace("\\", "/")


# ── VÁ 30/09/2026 (tiếp): dòng «Nhập thủ công» đọc TÊN và trạng thái từng làn từ sổ, không viết cứng ────────────────
# Đo trên sổ thật 30/09: dòng cũ in «Nhập thủ công (VN): 3 làn (BYT · Cục QLD) — số văn bản đã nhập: 1». Ba mục
# `access: manual` lúc đó là Cục QLD, Epistemonikos (API chờ token) và Wiley Scholar Gateway (connector MCP); BYT đã là
# làn tự động từ 22/09; «1 văn bản» là ngày kiểm sống của Wiley — không văn bản Việt Nam nào từng được nhập.

def test_dong_nhap_thu_cong_in_ten_va_trang_thai_tung_lan(monkeypatch, tmp_path: Path) -> None:
    _don_dep(monkeypatch, tmp_path, [
        _nguon("SRC-A", access="api", last_success_at="2026-09-13", name="PubMed — làn tuần"),
        _nguon("SRC-M", access="manual", status="not-covered", name="Cục Quản lý Dược VN — công văn/thu hồi"),
        _nguon("SRC-N", access="manual", status="not-covered", last_success_at="2026-09-01",
               name="Sở Y tế — công văn nhập tay"),
    ])
    khoi = T.tra_khoi()
    assert _dong(khoi, "Nhập thủ công") == (
        "Nhập thủ công: 2 làn — Cục Quản lý Dược VN (CHƯA nhập văn bản nào); "
        "Sở Y tế (lần nhập gần nhất 2026-09-01); còn [CẦN XÁC NHẬN TẠI ĐƠN VỊ].")
    assert "BYT · Cục QLD" not in khoi and "số văn bản đã nhập" not in khoi


def test_khong_co_lan_nhap_thu_cong_thi_noi_ro_khong_in_so_0_tran_trui(monkeypatch, tmp_path: Path) -> None:
    _don_dep(monkeypatch, tmp_path, [_nguon("SRC-A", access="api", last_success_at="2026-09-13")])
    assert _dong(T.tra_khoi(), "Nhập thủ công") == (
        "Nhập thủ công: không có làn nào khai trong sổ; còn [CẦN XÁC NHẬN TẠI ĐƠN VỊ].")


def test_lan_nhap_tay_dang_active_khong_duoc_in_la_giam_sat_tu_dong(monkeypatch, tmp_path: Path) -> None:
    """Nhập tay không phải giám sát tự động: mục `access: manual` dù active chỉ được nằm ở dòng «Nhập thủ công» — đúng ca
    Wiley Scholar Gateway (manual + active + ad-hoc) từng hiện ở CẢ «gọi theo yêu cầu» lẫn con số «3 làn»."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon_nhip("SRC-A", "PubMed — làn tuần", "weekly"),
        _nguon_nhip("SRC-W", "Connector khai nhầm — manual mà ad-hoc", "ad-hoc", access="manual"),
        _nguon_nhip("SRC-V", "Làn nhập tay theo quý — văn bản trong nước", "quarterly", access="manual"),
    ])
    khoi = T.tra_khoi()
    assert _dong(khoi, "Đang giám sát tự động").startswith("Đang giám sát tự động: 1 nguồn — PubMed;")
    assert "Gọi theo yêu cầu" not in khoi
    thu_cong = _dong(khoi, "Nhập thủ công")
    assert thu_cong.startswith("Nhập thủ công: 2 làn — Connector khai nhầm (lần nhập gần nhất 2026-09-30); Làn nhập tay theo quý (")


def test_khoang_trong_da_khai_phai_hien_trong_tuyen_bo(monkeypatch, tmp_path: Path) -> None:
    """Mọi mục `not-covered` phải hiện bằng TÊN: mục API/không truy cập ở dòng «KHÔNG phủ», làn nhập tay ở «Nhập thủ công»."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon("SRC-A", access="api", last_success_at="2026-09-13", name="PubMed — làn tuần"),
        _nguon("SRC-K", access="api", status="not-covered", name="Epistemonikos — API chờ token"),
        _nguon("SRC-U", access="none", status="not-covered", name="UpToDate · DynaMed · Embase (thương mại)"),
        _nguon("SRC-M", access="manual", status="not-covered", name="Cục Quản lý Dược VN — công văn/thu hồi"),
    ])
    khoi = T.tra_khoi()
    assert _dong(khoi, "KHÔNG phủ") == "KHÔNG phủ (2 nhóm, khai rõ): Epistemonikos; UpToDate · DynaMed · Embase (thương mại)."
    assert "Cục Quản lý Dược VN (CHƯA nhập văn bản nào)" in _dong(khoi, "Nhập thủ công")


def test_so_that_moi_khoang_trong_hien_ten_va_dong_nhap_thu_cong_khong_dem_connector() -> None:
    """Trên SỔ THẬT: (1) mọi mục not-covered hiện TÊN ở «KHÔNG phủ» hoặc «Nhập thủ công»; (2) hai mục từng khai nhầm
    `manual` (Wiley Scholar Gateway SRC-041, Epistemonikos SRC-036) không còn là làn nhập tay; (3) dòng «Nhập thủ công»
    chỉ nói một làn «đã nhập» khi chính mục đó có `last_success_at`."""
    so = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]
    theo = {s["id"]: s for s in so}
    khoi = T.tra_khoi()
    thu_cong, khong_phu = _dong(khoi, "Nhập thủ công"), _dong(khoi, "KHÔNG phủ")
    for s in so:
        if s["status"] == "not-covered":
            assert T._ten(s) in (thu_cong if s["access"] == "manual" else khong_phu), s["id"]
    assert theo["SRC-041"]["access"] == "api" and theo["SRC-036"]["access"] == "api"
    assert "Wiley" not in thu_cong and "Epistemonikos" not in thu_cong
    for s in so:
        if s["access"] == "manual":
            da_nhap = f"{T._ten(s)} (lần nhập gần nhất " in thu_cong
            assert da_nhap == bool(s.get("last_success_at")), s["id"]
