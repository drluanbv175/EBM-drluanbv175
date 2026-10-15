#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rà đồng bộ làn Chrome + EndNote (15/10/2026) — nhóm DẠY AGENT: doctrine, agent, skill, tác vụ lịch, CLAUDE.md.

VÌ SAO. Cổng và công cụ đã đổi (phiên uỷ quyền LƯU bản sao BH158/BH159, tầng Unpaywall BH160, bảng điều khoản NXB 28 khoá
«cấm», kho tóm tắt máy cho EndNote) nhưng tài liệu agent đọc còn dạy bản cũ:
  • doctrine `_CONNECTOR-CHUNG-CU.md` §2septies mục 7–8 cấm lưu toàn văn mà vẫn nhắc phiên lưu bản sao, không dạy `--kiem/--nhan`
    (G3-D1/W2); §0.8 liệt 15/28 NXB «cấm» nên danh sách trôi khỏi bảng (G3-D9);
  • skill `tong-thuat-chung-cu` bước 0 dạy WebFetch/Browser/chụp guideline mà không tra điều khoản NXB (G3-D3) và dạy lưu
    `PMID-<n>_MCP.md` — định dạng không công cụ nào nhận (W3);
  • agent `cap-nhat-guideline` dạy «đọc trên trang tạp chí qua quyền truy cập của bác sĩ» (G3-D4);
  • CLAUDE.md §6.4 ghi «Scopus: Claude không mở trang» không ngoại lệ, trái làn Chrome có uỷ quyền (G3-D6);
  • hai skill cập nhật chứng cứ liệt «quyền của bác sĩ» là nguồn toàn văn hợp pháp (G3-D7), dạy lệnh
    `nap_endnote_chu_de.py --tom-tat-vi` thiếu `--file`/`--ap-dung` (G3-D8/W7/DOC-01) và không dạy khuôn khoá kho tóm tắt máy (TT-08);
  • tác vụ lịch `goi-duyet-tuan-ebm` bước 4b gom toàn văn không `--unpaywall` và không nói tới bản `_CHR` (W5).
Mỗi ca kiểm đọc ĐÚNG khối văn bản agent sẽ đọc (không khớp cả tệp) và lấy hằng số từ chính công cụ để tài liệu không trôi khỏi mã.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
DOCTRINE = REPO / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"
AGENT_GUIDELINE = REPO / ".claude" / "agents" / "cap-nhat-guideline.md"
SKILLS = REPO / "sync" / "skills"
HAI_SKILL = ("cap-nhat-chung-cu-y-khoa", "dark-analyst")
SKILL_TONG_THUAT = SKILLS / "tong-thuat-chung-cu" / "SKILL.md"
SKILL_GOI_TUAN = REPO / "sync" / "scheduled-tasks" / "goi-duyet-tuan-ebm" / "SKILL.md"
TEN_NGOAI_LE = "PHIÊN UỶ QUYỀN LƯU BẢN SAO (BH158/BH159)"


def _nap(ten: str, tep: str):
    """Nạp một công cụ trong tools/ theo đường dẫn (không phụ thuộc thư mục chạy)."""
    spec = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


DTV = _nap("dtv_tl_20261015", "doc_toan_van_co_nguoi.py")
PHIEN = _nap("puqc_tl_20261015", "phien_uy_quyen_chrome.py")
TTV = _nap("ttev_tl_20261015", "tom_tat_endnote_vi.py")


def _doc(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _muc_2septies() -> str:
    van_ban = _doc(DOCTRINE)
    i = van_ban.index("## 2septies. ")
    j = van_ban.find("\n## ", i + 5)
    return van_ban[i:j if j > 0 else len(van_ban)]


def _dong_bat_dau(khoi: str, dau: str) -> str:
    """Dòng (một mục đánh số của doctrine nằm trên MỘT dòng) bắt đầu bằng `dau`."""
    dong = [d for d in khoi.splitlines() if d.startswith(dau)]
    assert len(dong) == 1, f"không tìm thấy đúng MỘT dòng bắt đầu bằng «{dau}» (thấy {len(dong)})"
    return dong[0]


# ───────────────────────── G3-D1 / W2 — doctrine dạy phiên lưu bản sao ─────────────────────────

def test_doctrine_muc_7_neu_ngoai_le_co_ten_phien_luu_ban_sao() -> None:
    """Mục 7 (bất biến «không lưu toàn văn») phải chỉ đích danh ngoại lệ — không thì nó mâu thuẫn với phiên lưu `_CHR`."""
    muc7 = _dong_bat_dau(_muc_2septies(), "7. **Bất biến")
    assert "PHIÊN UỶ QUYỀN LƯU BẢN SAO" in muc7, "mục 7 cấm lưu toàn văn mà không nêu ngoại lệ phiên uỷ quyền lưu bản sao"
    # Bất biến cho mọi trường hợp khác vẫn nguyên.
    for cum in ("không bấm «I am not a bot»", "không giải CAPTCHA", "không gõ tài khoản/mật khẩu", "không giả dạng trình duyệt",
                "không lưu toàn văn KHÔNG mang giấy phép mở"):
        assert cum in muc7, f"mục 7 mất bất biến «{cum}»"


def test_doctrine_muc_8_day_du_quy_trinh_phien_khop_hang_so_cong_cu() -> None:
    """Mục 8 dạy ĐỦ điều kiện của phiên — số trần/nhịp/hậu tố lấy từ chính `phien_uy_quyen_chrome.py` để không trôi."""
    muc8 = _dong_bat_dau(_muc_2septies(), "8. **Bác sĩ uỷ quyền")
    assert TEN_NGOAI_LE in muc8, f"mục 8 thiếu ngoại lệ có tên «{TEN_NGOAI_LE}»"
    k = muc8.index(TEN_NGOAI_LE)
    khoi = muc8[k:]
    can = [
        "tools/phien_uy_quyen_chrome.py --mo",
        "--kiem <PMID> --url",
        "--nhan <PMID> --tep",
        "--dung",
        f"toan_van_oa/PMID-<n>{PHIEN.HAU_TO}.",
        f"{PHIEN.TRAN_MOI_MIEN} bài/miền",
        f"≥ {PHIEN.NGHI_TOI_THIEU_GIAY} giây",
        "ngoài git",
        "uỷ quyền đọc còn hiệu lực",
        "LÚC KIỂM",
        "NXB chưa kiểm điều khoản",
    ]
    thieu = [c for c in can if c not in khoi]
    assert not thieu, f"ngoại lệ phiên lưu bản sao thiếu: {thieu}"
    # Ba cơ sở dữ liệu KHÔNG BAO GIỜ thuộc phiên — tên lấy từ hằng của công cụ.
    for ten in PHIEN.KHONG_BAO_GIO:
        ngan = ten.split(" (")[1].rstrip(")") if ten.startswith("EBSCO") else ten.split(" (")[0]
        if ten.startswith("Clarivate"):
            ngan = "Web of Science"
        assert ngan in khoi, f"ngoại lệ phiên không nêu «{ngan}» là KHÔNG BAO GIỜ thuộc phiên"
    # Câu cũ «vẫn chỉ lưu hồ sơ tóm lược…, không lưu toàn văn» phải trỏ sang ngoại lệ, không đứng trơ.
    truoc = muc8[:k]
    assert "không lưu toàn văn" not in truoc or "PHIÊN UỶ QUYỀN LƯU BẢN SAO" in truoc, \
        "mục 8 còn câu «không lưu toàn văn» không kèm ngoại lệ trước khi nêu phiên"


def test_doctrine_van_khop_bang_dieu_khoan() -> None:
    """Sửa mục 0.8/7/8 không được làm lệch phép đối chiếu bảng ↔ doctrine hiện có."""
    assert DTV.lech_doctrine(_doc(DOCTRINE)) == []


# ───────────────────────── G3-D9 — §0.8 trỏ bảng, không liệt kê dở dang ─────────────────────────

def _ten_cam_tru_co_so_du_lieu() -> list[str]:
    """Tên ngắn (trước « (») của mọi khoá «cam», TRỪ hai nền tảng tra cứu có làn riêng (Scopus/WoS)."""
    rieng = {"Scopus (Elsevier)", "Clarivate (Web of Science)"}
    return [t.split(" (")[0].strip() for t, d in DTV.DIEU_KHOAN_NXB.items() if d.get("ket_luan") == "cam" and t not in rieng]


def test_doctrine_0_8_tro_bang_khong_liet_ke_do_dang() -> None:
    dong = _dong_bat_dau(_doc(DOCTRINE), "8. **ĐIỀU KHOẢN NXB TRƯỚC TOÀN VĂN.**")
    assert "DIEU_KHOAN_NXB" in dong and "§2septies" in dong, "§0.8 phải trỏ bảng DIEU_KHOAN_NXB + §2septies"
    ten = _ten_cam_tru_co_so_du_lieu()
    co = [t for t in ten if re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", dong)]
    assert len(co) in (0, len(ten)), (f"§0.8 liệt kê dở dang {len(co)}/{len(ten)} NXB «cấm» — thiếu "
                                      f"{sorted(set(ten) - set(co))}; trỏ bảng thay vì liệt kê")
    assert "Scopus" in dong and "Web of Science" in dong, "§0.8 mất ghi chú Scopus/WoS có làn riêng"


# ───────────────────────── G3-D3 / W3 — skill tong-thuat-chung-cu ─────────────────────────

def _buoc(van_ban: str, dau: str, sau: str) -> str:
    i = van_ban.index(dau)
    j = van_ban.index(sau, i)
    return van_ban[i:j]


def test_tong_thuat_buoc_0_tra_dieu_khoan_truoc_khi_doc_hay_chup() -> None:
    buoc0 = _buoc(_doc(SKILL_TONG_THUAT), "0. **NGUỒN CHUẨN ĐI TRƯỚC", "1. **BỐN LÀN NGUỒN")
    assert "nxb_cua" in buoc0 and "DIEU_KHOAN_NXB" in buoc0, "bước 0 không tra bảng điều khoản NXB"
    i = buoc0.index("nxb_cua")
    for cum in ("WebFetch", "Browser pane", "luu_guideline.py"):
        assert cum in buoc0 and i < buoc0.index(cum), f"tra điều khoản phải đứng TRƯỚC «{cum}» ở bước 0"
    for cum in ("--bac-si-da-doc", "§2septies"):
        assert cum in buoc0, f"bước 0 thiếu «{cum}»"


def test_tong_thuat_khong_day_luu_mcp_ma_ghi_nhan_qua_lan_co_san() -> None:
    van_ban = _doc(SKILL_TONG_THUAT)
    assert "_MCP.md" not in van_ban, "skill còn dạy lưu PMID-<n>_MCP.md — không công cụ nào nhận định dạng này"
    buoc1d = _buoc(van_ban, "d. TOÀN VĂN:", "2. **KIỂM MỌI NGUỒN")
    for cum in ("get_fulltext", "doc_toan_van_co_nguoi.py --nap", "giay_phep_cc", "--bac-si-da-doc"):
        assert cum in buoc1d, f"bước 1d thiếu «{cum}»"
    # B1 (vòng sửa 15/10/2026): chuỗi OA nhiều tầng của `get_fulltext` có thể trả bản đọc miễn phí của NXB
    # hoặc bản Unpaywall KHÔNG mang giấy phép CC ⇒ cổng điều khoản phải đứng TRƯỚC lần đầu nhắc `get_fulltext`
    # (rẽ nhánh theo giấy phép SAU khi đã đọc là quá muộn — §2septies mục 1), và khoá «cam» phải bị cấm gọi hẳn.
    i_get = buoc1d.index("get_fulltext")
    assert "nxb_cua" in buoc1d[:i_get], "bước 1d nhắc bản MCP get_fulltext mà không tra điều khoản NXB (nxb_cua) TRƯỚC"
    assert "có thể ĐỌC bản MCP" in buoc1d, "bước 1d mất câu cho phép đọc bản MCP (để khớp đúng chỗ đặt điều kiện)"
    truoc_cho = buoc1d[:buoc1d.index("có thể ĐỌC bản MCP")]
    assert re.search(r"«cam»[^.]{0,160}KHÔNG gọi `get_fulltext`", truoc_cho), \
        "bước 1d không cấm gọi get_fulltext cho khoá «cam» của DIEU_KHOAN_NXB TRƯỚC câu cho phép đọc"
    # Câu CHO PHÉP phải tự mang điều kiện (không chỉ có cổng ở câu khác): cắt từ dấu chấm câu cuối trước nó.
    cau_cho = truoc_cho[truoc_cho.rfind(". ") + 2:]
    for cum in ("ĐIỀU KHOẢN", "chỉ khi", "giấy phép CC của CHÍNH bài"):
        assert cum in cau_cho, f"câu cho phép đọc bản MCP get_fulltext thiếu điều kiện «{cum}»: …{cau_cho[-160:]}"


# ───────────────────────── G3-D4 — agent cap-nhat-guideline ─────────────────────────

def test_agent_cap_nhat_guideline_ma_1_di_theo_dieu_khoan_nxb() -> None:
    van_ban = _doc(AGENT_GUIDELINE)
    assert "đọc trên trang tạp chí qua" not in van_ban, "agent còn dạy tự đọc trang tạp chí khi không có PMC OA"
    khoi = _buoc(van_ban, "**Đọc toàn văn bản guideline mới", "<!-- EBM-CHUAN-QUOC-TE-2026 -->")
    for cum in ("Mã 1", "§2septies", "doc_toan_van_co_nguoi.py --pmid", "--bac-si-da-doc", "không tự mở trang tạp chí"):
        assert cum in khoi, f"khối đọc toàn văn guideline thiếu «{cum}»"


# ───────────────────────── G3-D6 — CLAUDE.md §6.4 ngoại lệ làn Chrome ─────────────────────────

def test_claude_md_scopus_co_ngoai_le_lan_chrome_uy_quyen() -> None:
    dong = [d for d in _doc(REPO / "CLAUDE.md").splitlines() if "Tài khoản Scopus / Web of Science / DynaMed" in d]
    assert len(dong) == 1
    cau = dong[0][dong[0].index("Scopus (Elsevier"):]
    assert "TRỪ làn Chrome" in cau and "§2septies 2(b)" in cau, "CLAUDE.md §6.4 «Claude không mở trang Scopus» thiếu ngoại lệ làn Chrome"


# ───────────────────────── G3-D7 / G3-D8 / TT-08 — hai skill cập nhật chứng cứ ─────────────────────────

@pytest.mark.parametrize("ten", HAI_SKILL)
def test_skill_quyen_bac_si_chi_khi_dieu_khoan_cho_phep(ten: str) -> None:
    van_ban = _doc(SKILLS / ten / "SKILL.md")
    assert "ĐIỀU KHOẢN NXB TRƯỚC TOÀN VĂN KHÔNG OA" in van_ban, f"{ten}: thiếu luật điều khoản NXB cho toàn văn không OA"
    for m in re.finditer(r"quyền của bác sĩ", van_ban):
        sau = van_ban[m.end():m.end() + 160]
        assert "uỷ quyền ghi sổ" in sau, f"{ten}: «quyền của bác sĩ» không kèm điều kiện điều khoản/uỷ quyền: …{sau[:80]}"


@pytest.mark.parametrize("ten", HAI_SKILL)
def test_skill_lenh_tom_tat_vi_du_co(ten: str) -> None:
    van_ban = _doc(SKILLS / ten / "SKILL.md")
    lenh = [m.group(1) for m in re.finditer(r"`([^`]*nap_endnote_chu_de\.py[^`]*--tom-tat-vi[^`]*)`", van_ban)]
    assert lenh, f"{ten}: không có lệnh nap_endnote_chu_de.py … --tom-tat-vi"
    sai = [x for x in lenh if "--ap-dung" not in x or not ("--file" in x or "--tat-ca" in x)]
    assert not sai, f"{ten}: lệnh --tom-tat-vi thiếu --file/--tat-ca hoặc --ap-dung (chạy khô / mã 3): {sai}"
    assert "nap_endnote_chu_de.py --file <dashboard> --tom-tat-vi --ap-dung" in van_ban
    assert "chạy khô" in van_ban


@pytest.mark.parametrize("ten", HAI_SKILL)
def test_skill_day_khuon_khoa_kho_tom_tat_may(ten: str) -> None:
    van_ban = _doc(SKILLS / ten / "SKILL.md")
    i = van_ban.index("SOẠN mục cho kho")
    khoi = van_ban[i:i + 900]
    thieu = [k for k, _ in TTV.NHAN_TOM_TAT if f'"{k}"' not in khoi]
    assert not thieu, f"{ten}: khuôn kho tóm tắt máy thiếu trường {thieu} (lấy từ tom_tat_endnote_vi.NHAN_TOM_TAT)"
    for cum in ('"muc"', '"PMID <n>"', '"DOI <doi chữ thường>"', TTV.TEP_TOM_TAT_ABS, "tom_tat_endnote_vi.py --mau"):
        assert cum in khoi, f"{ten}: khuôn kho tóm tắt máy thiếu «{cum}»"


# ───────────────────────── W5 — tác vụ lịch goi-duyet-tuan-ebm bước 4b ─────────────────────────

def test_goi_tuan_4b_gom_co_unpaywall_va_day_ban_chr() -> None:
    buoc = _buoc(_doc(SKILL_GOI_TUAN), "4b. ĐỌC TOÀN VĂN", "\n5. ")
    lenh = [m.group(1) for m in re.finditer(r"`([^`]*gom_toan_van_dashboard\.py[^`]*)`", buoc)]
    assert lenh and all("--unpaywall" in x for x in lenh), f"lệnh gom ở bước 4b thiếu --unpaywall (tầng 2, BH160): {lenh}"
    assert f"PMID-<n>{PHIEN.HAU_TO}.*" in buoc, "bước 4b không dạy cách xử lý bản _CHR của phiên uỷ quyền"
