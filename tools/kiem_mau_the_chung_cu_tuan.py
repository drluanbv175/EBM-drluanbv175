#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm CẤU TRÚC thẻ trong gói duyệt tuần (12/09/2026) so với
sync/scheduled-tasks/goi-duyet-tuan-ebm/MAU-THE-CHUNG-CU-TUAN.md.

Vì sao có: đối chiếu W33 (6 khối) với W35-W37 (8 khối) cho thấy định dạng thẻ
đã trôi dạt qua 5 tuần mà không có gì kiểm — đúng loại lỗi "tài liệu nói một
đằng, mã sống chạy một nẻo" mà repo này đã nhiều lần gọi tên. Chốt này KHÔNG
thẩm định NỘI DUNG khoa học (số liệu đúng/sai, GRADE đúng/sai) — đó là việc
của bác sĩ lúc duyệt. Nó CHỈ kiểm CẤU TRÚC máy đọc được: có đủ khối bắt buộc,
nhãn đề xuất hợp lệ, PMID/DOI có mặt, và luật cứng đã có từ trước
(appraisalCompleteness=partial không được mang nhãn "Áp dụng ngay").

CỐ Ý KHÔNG kiểm: câu đầu "Điều gì thay đổi" có phải bottom-line tự đứng được
không — đó là phán đoán ngữ nghĩa, quy về đếm chuỗi sẽ chỉ tạo ảo giác kiểm
tra (BH28: không thay phán đoán ngữ nghĩa bằng độ giống từ vựng).

Dùng: python3 tools/kiem_mau_the_chung_cu_tuan.py <file.md> [--nghiem-ngat]
Mã thoát: 0 (🟢 sạch) · 1 (🟡 có cảnh báo, không chặn) · 2 (🔴 vi phạm cứng).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

DE_XUAT_HOP_LE = {"Áp dụng ngay", "Cân nhắc", "Chưa đủ"}

_TIEU_DE_RE = re.compile(
    r"^\*\*\[(?P<ma>[^\]]+)\]\s*(?P<chu_de>.+?)\s*—\s*(?P<loai_nguon>.+?)\s*—\s*"
    r"(?P<de_xuat>[^()*]+?)(?:\s*\((?P<nhan_uu_tien>[^)]+)\))?\*\*\s*$",
    re.MULTILINE,
)

_PMID_DOI_RE = re.compile(r"PMID\s*\d+|doi:\s*10\.\S+", re.IGNORECASE)
_AI_BI_ANH_HUONG_RE = re.compile(r"^Ai bị ảnh hưởng:", re.MULTILINE)
_RUI_RO_RE = re.compile(r"^Rủi ro nếu áp dụng sai:.*\|\s*Nếu bỏ qua:", re.MULTILINE | re.DOTALL)
_THAM_DINH_RE = re.compile(r"^Thẩm định toàn văn:\s*(?P<noi_dung>.+?)$", re.MULTILINE)
_NGUON_RE = re.compile(r"^Nguồn:\s*(?P<noi_dung>.+?)$", re.MULTILINE)
_DIEU_GI_THAY_DOI_RE = re.compile(r"^Điều gì thay đổi:", re.MULTILINE)

_PARTIAL_TU_KHOA = ("chưa đọc được", "partial", "không truy cập mở", "chưa có bản")
_FULL_TU_KHOA = ("full", "đã đọc")


@dataclass
class KetQuaThe:
    ma: str
    do: list[str] = field(default_factory=list)  # 🔴
    vang: list[str] = field(default_factory=list)  # 🟡


def tim_khoi_the(text: str) -> list[tuple[str, str]]:
    """Trả [(tiêu_đề_dòng, nội_dung_thân_thẻ)] — thân thẻ là mọi thứ từ sau
    tiêu đề tới tiêu đề thẻ kế tiếp hoặc hết văn bản/gặp `---`."""
    matches = list(_TIEU_DE_RE.finditer(text))
    ra = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        than = text[start:end]
        # cắt tại '---' (ranh giới mục) nếu thẻ cuối của mục
        cut = than.find("\n---")
        if cut != -1:
            than = than[:cut]
        ra.append((m, than))
    return ra


def cham_the(m: re.Match, than: str) -> KetQuaThe:
    ma = m.group("ma")
    kq = KetQuaThe(ma=ma)
    de_xuat = m.group("de_xuat")

    if de_xuat not in DE_XUAT_HOP_LE:
        kq.do.append(f"nhãn đề xuất '{de_xuat}' không hợp lệ (chỉ nhận: {sorted(DE_XUAT_HOP_LE)})")

    nguon_m = _NGUON_RE.search(than)
    if nguon_m is None:
        kq.do.append("thiếu khối 'Nguồn:'")
    elif not _PMID_DOI_RE.search(nguon_m.group("noi_dung")):
        kq.do.append("khối 'Nguồn:' không có PMID hoặc doi phân giải được")

    if not _DIEU_GI_THAY_DOI_RE.search(than):
        kq.do.append("thiếu khối 'Điều gì thay đổi:'")

    if not _AI_BI_ANH_HUONG_RE.search(than):
        kq.vang.append("thiếu khối 'Ai bị ảnh hưởng:' (khuyến nghị, xem mẫu)")

    if not _RUI_RO_RE.search(than):
        kq.vang.append("thiếu khối 'Rủi ro nếu áp dụng sai: ... | Nếu bỏ qua: ...' đúng dạng hai chiều")

    tham_dinh_m = _THAM_DINH_RE.search(than)
    if tham_dinh_m is None:
        kq.vang.append("thiếu khối 'Thẩm định toàn văn:' — không rõ appraisalCompleteness")
    else:
        noi_dung = tham_dinh_m.group("noi_dung").lower()
        la_partial = any(tk in noi_dung for tk in _PARTIAL_TU_KHOA)
        la_full = any(tk in noi_dung for tk in _FULL_TU_KHOA)
        if la_partial and not la_full and de_xuat == "Áp dụng ngay":
            kq.do.append(
                "đề xuất 'Áp dụng ngay' nhưng Thẩm định toàn văn ghi PARTIAL — "
                "luật cứng: partial không được mang nhãn Áp dụng ngay"
            )

    return kq


def kiem_file(duong: Path) -> tuple[int, list[KetQuaThe]]:
    text = duong.read_text(encoding="utf-8", errors="replace")
    ket_qua = [cham_the(m, than) for m, than in tim_khoi_the(text)]
    if not ket_qua:
        return 2, []
    co_do = any(k.do for k in ket_qua)
    if co_do:
        return 2, ket_qua
    co_vang = any(k.vang for k in ket_qua)
    return (1 if co_vang else 0), ket_qua


def in_bao_cao(duong: Path, ma_thoat: int, ket_qua: list[KetQuaThe]) -> None:
    print(f"KIỂM MẪU THẺ CHỨNG CỨ TUẦN — {duong.name}")
    print(f"Đối chiếu: sync/scheduled-tasks/goi-duyet-tuan-ebm/MAU-THE-CHUNG-CU-TUAN.md")
    if not ket_qua:
        print("🔴 Không tìm thấy thẻ nào khớp định dạng tiêu đề — file rỗng hoặc sai mẫu hoàn toàn.")
        return
    print(f"Tổng số thẻ: {len(ket_qua)}")
    for k in ket_qua:
        for d in k.do:
            print(f"  🔴 [{k.ma}] {d}")
        for v in k.vang:
            print(f"  🟡 [{k.ma}] {v}")
    mau = {0: "🟢", 1: "🟡", 2: "🔴"}[ma_thoat]
    tong_do = sum(len(k.do) for k in ket_qua)
    tong_vang = sum(len(k.vang) for k in ket_qua)
    print(f"KẾT: {mau} {tong_do} vi phạm cứng · {tong_vang} cảnh báo (không chặn).")
    print("Chỉ kiểm CẤU TRÚC, không thẩm định nội dung khoa học. Cần bác sĩ kiểm chứng.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=Path)
    ap.add_argument("--nghiem-ngat", action="store_true",
                     help="coi cảnh báo 🟡 như lỗi cứng (mã thoát 2 nếu có 🟡)")
    a = ap.parse_args()
    if not a.file.exists():
        print(f"🔴 Không tìm thấy file: {a.file}")
        return 2
    ma_thoat, ket_qua = kiem_file(a.file)
    in_bao_cao(a.file, ma_thoat, ket_qua)
    if a.nghiem_ngat and ma_thoat == 1:
        return 2
    return ma_thoat


if __name__ == "__main__":
    raise SystemExit(main())
