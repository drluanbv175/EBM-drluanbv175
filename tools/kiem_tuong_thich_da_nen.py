#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỐT TƯƠNG THÍCH ĐA NỀN TẢNG — quét tĩnh họ lỗi «viết cho một máy» (15/08/2026).

Vì sao: đây là HỌ LỖI TÁI PHÁT NHIỀU NHẤT của kho, toàn bộ đều gãy IM LẶNG trên
máy còn lại — mỗi lần một tool, chưa từng có chốt quét cả kho:
  · run_retraction_and_med_safety.py ghi cứng `C:/Users/Admin/...` → chưa từng chạy trên Mac
  · ensure_strict_source.py ghi cứng ROOT Windows → gãy trên Mac
  · docx_sang_pdf_giu_mau.py chỉ dò trình duyệt theo đường dẫn macOS → không in được PDF trên Windows
  · kiem_do_tuoi_chung_cu.py gọi os.getuid() → chết im lặng trên Windows TỪ LÚC RA ĐỜI
  · 7 script vietnamize print tiếng Việt vào stdout cp1252 → chết giữa chừng trên Windows
  · xuat_goi_cap_nhat gọi lệnh `python3` — Windows không có tên lệnh đó

Luật quét (chỉ mã Python trong các cây tool đang sống):
  🔴 CHẶN — gần chắc chắn gãy trên máy kia:
     R1 đường dẫn user ghi cứng (`C:/Users/`, `C:\\Users\\`, `/Users/<tên>/`)
     R2 os.getuid()/os.geteuid() không có guard sys.platform
     R3 subprocess gọi literal "python3"/"python" thay vì sys.executable
  🟡 CẢNH BÁO — đáng soi tay:
     R4 in ký tự ngoài-ASCII mà file không reconfigure stdout UTF-8
     R5 đường dẫn đặc thù nền tảng (`/Library/`, `AppData`) ngoài nhánh có guard

Miễn trừ TƯỜNG MINH bằng chú thích `# da-nen: bo-qua` trên cùng dòng (phải kèm lý do
ngay cạnh — miễn trừ câm là đường lách). Chốt chỉ ĐO và BÁO — không sửa file.
Mã thoát: 0 sạch 🔴 · 1 chỉ 🟡 · 2 có 🔴. Cần bác sĩ kiểm chứng (với nhóm 🟡).
"""
from __future__ import annotations

import io
import re
import sys
import tokenize
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
CAY_QUET = [REPO / "tools", REPO / "medical-ebm-automation" / "tools",
            REPO / "EBM-Dashboards" / "tools", REPO / "EBM_MASTER" / "tools",
            REPO / "ops"]
BO_QUA_TEN = {"__pycache__"}
MIEN_TRU = "da-nen: bo-qua"

R1 = re.compile(r"[\"'](?:[A-Za-z]:[/\\]Users[/\\]|/Users/(?!nguyenluan['\"])[A-Za-z])")
R1B = re.compile(r"[\"']/Users/[A-Za-z]")          # kể cả user hiện tại — vẫn là ghi cứng
R2 = re.compile(r"\bos\.gete?uid\s*\(")
R3 = re.compile(r"""(?:subprocess\.\w+|Popen)\(\s*\[\s*[\"'](?:python3?|py)[\"']""")
R5 = re.compile(r"[\"'](?:/Library/|/Applications/|AppData\\\\|AppData/)")
# R6 (16/08 — phát hiện CRLF từ CI Windows): write_text có encoding mà THIẾU
# newline="\n" trong vùng CHUỖI-KÝ (medical tools/runtime/tests/scripts) —
# Windows dịch \n→CRLF làm «ký hash → sinh lại artifact» lệch byte.
R6 = re.compile(r'\.write_text\([^\n]*encoding="utf-8"\)')
VUNG_KY = ("medical-ebm-automation/tools", "medical-ebm-automation/runtime",
           "medical-ebm-automation/tests", "medical-ebm-automation/scripts")


def _che_chu_thich_dong(s: str) -> str:
    """Cắt bỏ phần CHÚ THÍCH `#...` cuối dòng — CHỈ khi `#` nằm NGOÀI chuỗi
    ký tự (nháy đơn/kép/ba-nháy). Vá 09/09/2026 (BH55 tái phát, tự phát hiện
    khi xử lý chính bài học này): bản cũ (`if "#" in s: s = s.split("#",
    1)[0]`) cắt tại '#' ĐẦU TIÊN bất kể trong/ngoài chuỗi — một dòng THẬT
    trong repo, `md.write_text(head + ("# " + tail if tail else ""),
    encoding="utf-8")`, có literal `"# "` chứa `#` ⇒ bị cắt cụt TRƯỚC
    `encoding="utf-8"`, làm luật R6 (đang tìm đúng chuỗi đó) không thấy gì
    để so khớp — ÂM TÍNH GIẢ, và không chỉ cho R6: MỌI luật R1-R6 đều đọc
    từ cùng bản `code` đã che, nên bug này có thể giấu vi phạm của bất kỳ
    luật nào trên bất kỳ dòng nào có `#` bên trong một chuỗi ký tự (rất phổ
    biến trong test — regex, markdown, mô tả). Xác nhận bằng thực nghiệm:
    dòng trên qua bản cũ mất `encoding=\"utf-8\"`, R6.search() → False."""
    trong_chuoi: str | None = None  # None | "'" | '"' | "'''" | '\"\"\"'
    i, n = 0, len(s)
    while i < n:
        if trong_chuoi:
            if s.startswith(trong_chuoi, i):
                i += len(trong_chuoi)
                trong_chuoi = None
                continue
            if len(trong_chuoi) == 1 and s[i] == "\\":
                i += 2
                continue
            i += 1
            continue
        if s.startswith('"""', i) or s.startswith("'''", i):
            trong_chuoi = s[i:i + 3]
            i += 3
            continue
        c = s[i]
        if c in ("'", '"'):
            trong_chuoi = c
            i += 1
            continue
        if c == "#":
            return s[:i]
        i += 1
    return s


_TIEN_TO_CHUOI_RE = re.compile(r"^[a-zA-Z]*")

# Python ≥3.12 (PEP 701) tách f-string ba-nháy thành FSTRING_START/MIDDLE/END
# thay vì MỘT token STRING duy nhất như <3.12. `getattr(..., None)` để tương
# thích ngược: trên <3.12 hai hằng số này không tồn tại, nhánh so sánh
# `tok.type == _FSTRING_START` không bao giờ khớp (tok.type luôn là số
# nguyên ≥0, không thể == None) nên tự động không chạy — đúng ý, vì trên
# <3.12 f-string ba-nháy đã là MỘT token STRING, được `_la_chuoi_ba_nhay` xử
# lý đủ rồi.
_FSTRING_START = getattr(tokenize, "FSTRING_START", None)
_FSTRING_END = getattr(tokenize, "FSTRING_END", None)


def _la_chuoi_ba_nhay(nguyen_van_token: str) -> bool:
    """True nếu một token `tokenize.STRING` (hay `FSTRING_START`) là chuỗi BA
    NHÁY kiểu docstring (`'''...'''` hay `\"\"\"...\"\"\"`, có thể mang tiền tố
    r/b/f/u) — xét trên NGUYÊN VĂN token đã tokenize, không phải khớp chuỗi
    con trần trên văn bản thô. Nhờ vậy một chuỗi MỘT nháy có NỘI DUNG là ba
    ký tự nháy giống hệt dấu docstring — ví dụ `'\"\"\"'` (đúng dòng mã đã gây
    báo động giả 12/09/2026, xem docstring `_mask_khong_phai_code`) — KHÔNG
    bị coi là mở/đóng docstring: `tok.string` của nó là `'\"\"\"'` (bắt đầu
    bằng `'`, không phải ba dấu `\"`), nên hàm này trả `False` đúng."""
    phan_con_lai = _TIEN_TO_CHUOI_RE.sub("", nguyen_van_token, count=1)
    return phan_con_lai.startswith('"""') or phan_con_lai.startswith("'''")


def _che_khoang(dong_ky_tu: list[list[str]], bd: tuple[int, int], kt: tuple[int, int]) -> None:
    """Thay ký tự trong khoảng [bd, kt) (toạ độ (dòng 1-based, cột 0-based)
    của `tokenize`) bằng khoảng trắng, KHÔNG xoá — giữ nguyên số dòng và độ
    dài từng dòng để chỉ số dòng báo cáo ở `quet_file()`/`main()` không lệch
    so với `dong` (danh sách dòng GỐC chưa che, dùng để tra miễn trừ
    `# da-nen: bo-qua`)."""
    (dong_dau, cot_dau), (dong_cuoi, cot_cuoi) = bd, kt
    for so_dong in range(dong_dau, dong_cuoi + 1):
        idx = so_dong - 1
        if not (0 <= idx < len(dong_ky_tu)):
            continue
        ky_tu = dong_ky_tu[idx]
        c0 = cot_dau if so_dong == dong_dau else 0
        c1 = cot_cuoi if so_dong == dong_cuoi else len(ky_tu)
        for k in range(c0, min(c1, len(ky_tu))):
            ky_tu[k] = " "


def _mask_khong_phai_code_ngay_tho(dong: list[str]) -> list[str]:
    """Bản CŨ (che bằng TÁCH CHUỖI CON THÔ trên `\"\"\"`/`'''`, không qua
    `tokenize`) — CHỈ dùng khi `tokenize` không đọc được văn bản (file lỗi cú
    pháp Python từ trước), còn hơn không che gì cả. KHÔNG dùng cho đường đi
    bình thường: đây CHÍNH LÀ nguồn của một báo động giả đã vá 12/09/2026 —
    xem `_mask_khong_phai_code` để biết cơ chế thay thế.

    Bằng chứng thực nghiệm (không phải giả định — dò bằng cách in trạng thái
    `trong_ds` qua từng dòng của chính file bị báo động giả): file
    `medical-ebm-automation/tools/kiem_newline_vung_ky.py`, hàm
    `_la_chuoi_ba_nhay()`, có dòng MÃ THẬT
    `return phan_con_lai.startswith('\"\"\"') or phan_con_lai.startswith("'''")`
    — `'\"\"\"'` là một chuỗi MỘT NHÁY có NỘI DUNG là ba ký tự nháy kép. Hàm
    này chỉ tìm chuỗi con `\"\"\"`/`'''` bằng `in`/`.split()` trên văn bản thô,
    không phân biệt được "ba ký tự nháy đó là DẤU MỞ/ĐÓNG docstring thật" với
    "ba ký tự nháy đó chỉ là NỘI DUNG của một chuỗi một-nháy khác" — nên dòng
    mã trên bị hiểu nhầm là MỞ một docstring mới, làm trạng thái "đang ở
    trong docstring" LỆCH PHA cho TOÀN BỘ phần còn lại của file: docstring
    thật của hàm `_mask_ngay_tho()` ngay sau đó (chứa câu ví dụ minh hoạ
    `.write_text(..., encoding=\"utf-8\")` cho một bug CŨ đã vá) bị coi là MÃ
    THẬT (không được che), khiến luật R6 của `quet_file()` khớp trúng câu ví
    dụ trong văn xuôi thay vì một lời gọi `write_text()` thật đang thiếu
    `newline=`.

    `tokenize` (bản thay thế) không mắc lỗi này: nó là chính bộ phân tích cú
    pháp Python, nên `'\"\"\"'` LUÔN được nhận diện đúng là MỘT token STRING
    trọn vẹn mở/đóng bằng `'` — không bao giờ bị lẫn với dấu mở của một chuỗi
    ba-nháy khác (xem `_la_chuoi_ba_nhay`)."""
    ra: list[str] = []
    trong_ds = None  # dấu docstring đang mở (''' hoặc \"\"\") hoặc None
    for ln in dong:
        s = ln
        if trong_ds:
            if trong_ds in s:
                s = s.split(trong_ds, 1)[1]
                trong_ds = None
            else:
                ra.append("")
                continue
        # che chú thích — xem docstring _che_chu_thich_dong (không cắt '#' bên trong chuỗi)
        s = _che_chu_thich_dong(s)
        # docstring/chuỗi ba-nháy mở trên dòng này
        for dau in ('"""', "'''"):
            while dau in s:
                truoc, sau = s.split(dau, 1)
                if dau in sau:
                    s = truoc + sau.split(dau, 1)[1]
                else:
                    s = truoc
                    trong_ds = dau
                    break
        ra.append(s)
    return ra


def _mask_khong_phai_code(dong: list[str]) -> list[str]:
    """Trả bản sao các dòng với CHÚ THÍCH và DOCSTRING (chuỗi ba-nháy) đã che,
    dùng `tokenize` chuẩn của Python — thay cho bản cũ tách-chuỗi-con-thô
    (`_mask_khong_phai_code_ngay_tho`, nay chỉ còn là dự phòng khi tokenize
    thất bại; xem docstring của nó để có bằng chứng chi tiết về lỗi đã vá).

    Vá 12/09/2026: bản cũ tìm `\"\"\"`/`'''` bằng khớp CHUỖI CON trần trên văn
    bản thô, nên một dòng MÃ THẬT chứa chuỗi một-nháy có NỘI DUNG là ba ký tự
    nháy — ví dụ `'\"\"\"'` trong chính
    `medical-ebm-automation/tools/kiem_newline_vung_ky.py::_la_chuoi_ba_nhay()`
    — bị hiểu nhầm là MỞ một docstring mới, làm lệch pha trạng thái "đang
    trong docstring" cho TOÀN BỘ phần còn lại của file. Hậu quả đo được: một
    docstring thật ở xa hơn trong cùng file (chứa câu ví dụ minh hoạ
    `.write_text(..., encoding=\"utf-8\")` cho một bug CŨ đã vá) bị coi là MÃ
    THẬT nên không được che, khiến luật R6 báo 🔴 tại một dòng văn xuôi giải
    thích bug cũ, không phải một lời gọi `write_text()` thật đang thiếu
    `newline=`.

    `tokenize` không mắc lỗi này: nó là chính bộ phân tích cú pháp Python,
    nên một chuỗi một-nháy như `'\"\"\"'` LUÔN là một token STRING trọn vẹn —
    không bao giờ bị lẫn với DẤU MỞ/ĐÓNG của một chuỗi ba-nháy khác. Chỉ token
    COMMENT và token STRING dạng ba-nháy (`_la_chuoi_ba_nhay`) mới bị che;
    chuỗi một/hai nháy (kể cả chứa `#`/`\"\"\"`/`'''` làm nội dung, hay giá trị
    thật của `encoding=`) được GIỮ NGUYÊN VĂN để các luật R1-R6 vẫn so khớp
    được trên mã thật.

    F-STRING BA NHÁY (PEP 701, Python 3.12+): `tokenize` tách thành
    FSTRING_START/MIDDLE/(token biểu thức lồng trong `{...}`)/FSTRING_END
    thay vì một token STRING duy nhất — dò cặp START…END khớp (đếm độ sâu, vì
    có thể lồng f-string khác bên trong biểu thức) rồi che TRỌN khoảng đó,
    cùng khuôn với
    `medical-ebm-automation/tools/kiem_newline_vung_ky.py::_mask()` (đã giải
    quyết đúng lớp lỗi này từ 16/08/2026, cho chính họ lỗi đang vá ở đây).

    Chỉ THAY ký tự bị che bằng khoảng trắng (không xoá, không nối dòng) — giữ
    nguyên số dòng và độ dài từng dòng để chỉ số dòng ở `quet_file()`/
    `main()` không bị lệch. Nếu văn bản không tokenize được (file đã lỗi cú
    pháp Python từ trước), hạ về `_mask_khong_phai_code_ngay_tho()` — còn hơn
    không che được gì."""
    nguon = "\n".join(dong)
    dong_ky_tu = [list(ln) for ln in dong]
    try:
        cac_token = list(tokenize.generate_tokens(io.StringIO(nguon).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return _mask_khong_phai_code_ngay_tho(dong)

    so_token = len(cac_token)
    i = 0
    while i < so_token:
        tok = cac_token[i]
        if tok.type == tokenize.COMMENT:
            _che_khoang(dong_ky_tu, tok.start, tok.end)
            i += 1
            continue
        if tok.type == tokenize.STRING and _la_chuoi_ba_nhay(tok.string):
            _che_khoang(dong_ky_tu, tok.start, tok.end)
            i += 1
            continue
        if (
            _FSTRING_START is not None
            and tok.type == _FSTRING_START
            and _la_chuoi_ba_nhay(tok.string)
        ):
            do_sau = 1
            j = i + 1
            ket_thuc = tok.end
            while j < so_token and do_sau > 0:
                tk = cac_token[j]
                if tk.type == _FSTRING_START:
                    do_sau += 1
                elif tk.type == _FSTRING_END:
                    do_sau -= 1
                ket_thuc = tk.end
                j += 1
            _che_khoang(dong_ky_tu, tok.start, ket_thuc)
            i = j
            continue
        i += 1

    return ["".join(ky_tu) for ky_tu in dong_ky_tu]


def quet_file(p: Path) -> tuple[list[str], list[str]]:
    do, vang = [], []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return do, vang
    dong = text.splitlines()
    code = _mask_khong_phai_code(dong)
    co_utf8 = "reconfigure" in text or "PYTHONIOENCODING" in text
    co_in_ngoai_ascii = any(
        ln.lstrip().startswith("print(") and any(ord(c) > 127 for c in ln)
        for ln in code)
    # File có nhận thức nền tảng ở BẤT KỲ đâu → R2/R5 hạ xuống 🟡 (guard có thể
    # nằm xa hơn cửa sổ nhìn của chốt; đòi chốt hiểu luồng điều khiển là đòi nó
    # thành trình phân tích tĩnh thật — ngoài phạm vi, và 🔴 oan sẽ dạy bỏ 🔴).
    biet_nen_tang = ("sys.platform" in text or "os.name" in text
                     or "platform.system" in text)
    try:
        # Luật R6 đối chiếu với VUNG_KY dùng dấu "/" cố định. `str(Path)`
        # trên Windows sinh dấu "\\" nên mọi file trong vùng ký đều lọt chốt.
        # `as_posix()` cho một biểu diễn ổn định trên cả hai nền tảng.
        ten = p.relative_to(REPO).as_posix()
    except ValueError:
        ten = p.as_posix()
    for i, ln in enumerate(code, 1):
        if MIEN_TRU in dong[i - 1]:
            continue
        if R1.search(ln) or R1B.search(ln):
            do.append(f"{ten}:{i} R1 đường dẫn user ghi cứng: {dong[i-1].strip()[:80]}")
        if R2.search(ln):
            (vang if biet_nen_tang else do).append(
                f"{ten}:{i} R2 os.getuid — " +
                ("file CÓ nhận thức nền tảng, soi tay guard" if biet_nen_tang
                 else "file KHÔNG hề nhắc sys.platform (chết im lặng trên Windows)"))
        if R3.search(ln):
            do.append(f"{ten}:{i} R3 subprocess gọi literal python3 — dùng sys.executable")
        if R5.search(ln) and not biet_nen_tang:
            vang.append(f"{ten}:{i} R5 đường dẫn đặc thù nền tảng không guard: "
                        f"{dong[i-1].strip()[:70]}")
        if (R6.search(ln) and 'newline=' not in ln
                and any(v in ten for v in VUNG_KY)):
            do.append(f"{ten}:{i} R6 write_text thiếu newline='\\n' trong vùng chuỗi-ký (CRLF phá hash)")
    if co_in_ngoai_ascii and not co_utf8:
        vang.append(f"{ten} R4 print ngoài-ASCII mà không reconfigure UTF-8 (bẫy cp1252)")
    return do, vang


def main() -> int:
    do_tong, vang_tong, n = [], [], 0
    for cay in CAY_QUET:
        if not cay.exists():
            continue
        for p in sorted(cay.rglob("*.py")):
            if any(t in p.parts for t in BO_QUA_TEN) or ".bak" in p.name:
                continue
            n += 1
            d, v = quet_file(p)
            do_tong += d
            vang_tong += v
    # LƯỢT R6-RIÊNG cho phần còn lại của vùng chuỗi-ký (runtime/tests/scripts —
    # nằm trong VUNG_KY nhưng ngoài CAY_QUET; áp cả R1-R5 vào 3 cây này sẽ tạo
    # trăm cảnh báo R4 nhiễu từ test in tiếng Việt, nên chỉ soi đúng luật hash).
    for cay in (REPO / "medical-ebm-automation" / "runtime",
                REPO / "medical-ebm-automation" / "tests",
                REPO / "medical-ebm-automation" / "scripts"):
        if not cay.exists():
            continue
        for p in sorted(cay.rglob("*.py")):
            if any(x in p.parts for x in BO_QUA_TEN) or ".bak" in p.name:
                continue
            n += 1
            try:
                dong = p.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            code = _mask_khong_phai_code(dong)
            ten = p.relative_to(REPO).as_posix()
            for i, ln in enumerate(code, 1):
                if MIEN_TRU in dong[i - 1]:
                    continue
                if R6.search(ln) and 'newline=' not in ln:
                    do_tong.append(f"{ten}:{i} R6 write_text thiếu newline='\\n' "
                                   "trong vùng chuỗi-ký (CRLF phá hash)")
    print(f"CHỐT ĐA NỀN TẢNG — quét {n} file Python trong {len(CAY_QUET)} cây tool + vùng ký R6")
    for x in do_tong:
        print(f"  🔴 {x}")
    for x in vang_tong[:20]:
        print(f"  🟡 {x}")
    if len(vang_tong) > 20:
        print(f"  … và {len(vang_tong) - 20} cảnh báo nữa")
    print(f"KẾT: 🔴 {len(do_tong)} chặn · 🟡 {len(vang_tong)} cảnh báo. "
          "Cần bác sĩ kiểm chứng (nhóm 🟡).")
    return 2 if do_tong else (1 if vang_tong else 0)


if __name__ == "__main__":
    raise SystemExit(main())
