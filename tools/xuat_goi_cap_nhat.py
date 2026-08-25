#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xuất ĐỒNG THỜI bộ bốn sản phẩm của một lần cập nhật chứng cứ.

Một lệnh duy nhất, từ file Dashboard đã dựng xong:

    Dashboard (.html)  →  ① Dashboard (đầu vào, kiểm liêm chính)
                          ② Bản đọc (.html)  — trang đọc ngay tại phòng khám
                          ③ Bản Word (.docx) — tài liệu lưu trữ đầy đủ
                          ④ Bản Word dạng HTML — để ĐỌC THẲNG trong khung chat

Cách dùng:
    python3 tools/xuat_goi_cap_nhat.py <dashboard>.html [--online] [--parts parts.json]

    --online   chạy cổng liêm chính có phân giải PMID/DOI thật TRƯỚC khi xuất.
               Chỉ khi cổng PASS thì bản Word mới được truyền cờ --verified —
               nếu không, tool docx tự hạ câu chữ thành "CẦN xác minh" thay vì
               khẳng định sai là đã xác minh.
    --json     in kết quả dạng JSON (đường dẫn các file) để tự động hoá.

Vì sao gộp thành một lệnh: các sản phẩm này phải sinh từ CÙNG một khối DATA và
cùng một thời điểm. Chạy rời rạc thì dễ xảy ra tình trạng bản Word hoặc bản đọc
tụt lại một phiên bản so với dashboard mà không ai nhận ra.

Vì sao có bước ④ (thêm 05/08/2026, theo yêu cầu của bác sĩ): `.docx` là tệp nén
nhị phân nên khung chat của Claude KHÔNG mở thẳng được — nó chỉ hiện thẻ tải về,
bác sĩ phải rời khung chat mới đọc được tài liệu đầy đủ. Bước này dựng thêm một
bản HTML tự chứa từ CHÍNH file `.docx` vừa sinh (không dựng lại từ dữ liệu, để
không có đường nào làm hai bản lệch nhau).

    GIỮ: toàn bộ chữ, bảng, đề mục, thứ tự.
    MẤT: màu nền ô của bản Word — huy hiệu mức chứng cứ/quyết định chỉ còn phần
         chữ. Bản `.docx` vẫn là bản lưu trữ chuẩn; trang này chỉ để ĐỌC NHANH.

Bước ④ cần `pandoc`. Nếu máy KHÔNG có pandoc thì bỏ qua bước này và báo rõ ra
màn hình, KHÔNG làm hỏng ba sản phẩm còn lại và KHÔNG đổi mã thoát — pandoc là
tiện ích đọc, không phải cổng chất lượng. (Đã kiểm 05/08/2026: Mac có pandoc
3.10; máy Windows chưa kiểm, nên nhánh thiếu pandoc phải chạy êm.)

Chạy được trên cả macOS lẫn Windows: gọi trình thông dịch bằng sys.executable
(Windows không có lệnh `python3`) và tự ép UTF-8 cho stdout (Windows mặc định
cp1252 sẽ chết khi in tiếng Việt).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path



ROOT = Path(__file__).resolve().parent.parent
DASH_TOOLS = ROOT / "EBM-Dashboards" / "tools"
BAN_DOC = ROOT / "tools" / "build_ban_doc_chung_cu.py"
VERIFY = DASH_TOOLS / "verify_dashboard.py"
DOCX = DASH_TOOLS / "build_dashboard_docx.py"

# CSS nhúng thẳng vào file Python (KHÔNG tách ra file asset riêng) để bước ④ không
# tạo thêm một thứ phải đồng bộ tay giữa Mac và Windows.
HTML_STYLE = """<style>
 body{font-family:"Times New Roman",Times,serif;max-width:900px;margin:0 auto;
      padding:28px 22px;line-height:1.55;color:#111;background:#fff}
 h1{font-size:1.9rem;border-bottom:3px solid #0e7490;padding-bottom:.4rem}
 h2{font-size:1.35rem;margin-top:2rem;color:#0f172a;border-left:5px solid #0e7490;
    padding-left:.55rem}
 h3{font-size:1.1rem;margin-top:1.4rem}
 table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95rem}
 td,th{border:1px solid #cbd5e1;padding:7px 9px;vertical-align:top}
 tr:first-child td{background:#f1f5f9;font-weight:700}
 blockquote{border-left:4px solid #ca8a04;background:#fffbeb;margin:1rem 0;padding:.6rem 1rem}
 .hz-note{border:1px solid #fcd34d;background:#fffbeb;border-radius:8px;
          padding:.7rem .9rem;margin:0 0 1.4rem;font-size:.92rem;line-height:1.5}
 @media (max-width:700px){body{padding:16px 12px}table{font-size:.85rem}}
</style>"""

# Cảnh báo đặt NGAY ĐẦU trang: người đọc phải biết bản này mất màu, tránh hiểu nhầm
# là đã xem đủ như bản Word.
HTML_BANNER = """<div class="hz-note">
 <strong>Bản HTML sinh tự động từ file Word cùng tên.</strong> Giữ đủ chữ, bảng và
 đề mục; nhưng <strong>mất màu nền ô</strong> — huy hiệu mức chứng cứ và quyết định
 chỉ còn phần chữ. Cần bản có màu: mở file <code>.docx</code> hoặc dashboard.
</div>"""

# Banner cho NHÁNH DỰ PHÒNG (dựng bằng python-docx, không qua pandoc): nhánh này
# đọc màu từ chính .docx nên màu nền ô CÒN NGUYÊN — không được dùng lại câu cảnh
# báo "mất màu" ở trên, vì nói sai với người đọc.
HTML_BANNER_GIU_MAU = """<div class="hz-note">
 <strong>Bản HTML sinh tự động từ file Word cùng tên.</strong> Giữ đủ chữ, bảng,
 đề mục và <strong>màu nền ô</strong> (huy hiệu mức chứng cứ · quyết định).
 Không tái tạo ảnh nhúng và đánh số tự động của Word — bản <code>.docx</code> vẫn
 là bản lưu trữ chuẩn.
</div>"""


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def run(cmd: list, cwd: Path | None = None) -> tuple[int, str]:
    """Chạy một tool con, trả về (mã thoát, đầu ra gộp)."""
    proc = subprocess.run(
        [str(c) for c in cmd], cwd=str(cwd) if cwd else None,
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def ghi_sidecar_hash_data(dash: Path, word_path: str) -> None:
    """VÁ 25/08/2026 (BH76) — ghi sidecar `<tên>.data-sha256` cạnh bản Word, chứa
    SHA256 của khối `const DATA` trong dashboard TẠI THỜI ĐIỂM xuất.

    Vì sao cần: `tu_de_xuat_viec.py` từng đo độ tươi phái sinh bằng MTIME của
    file (docx cũ hơn html ⇒ "lỗi thời"). Một lần reskin THUẦN VỎ CSS/HTML (Sprint
    9, task 9.2 — đã xác nhận `DATA` byte-for-byte không đổi trên 66/67 dashboard)
    bump mtime của MỌI dashboard đã reskin, khiến CẢ 66 bản bị báo "lỗi thời" dù
    nội dung khoa học không đổi một ký tự — đẩy bác sĩ vào việc xuất lại 66 lần
    (mỗi lần gọi PubMed thật) cho một thay đổi thuần trình bày.

    Sidecar này cho phép so CONTENT thay vì MTIME: `tu_de_xuat_viec.py` chỉ báo
    "lỗi thời" khi hash hiện tại của DATA KHÁC hash lúc xuất — sống sót qua mọi
    thao tác không đụng DATA (reskin, đổi khoảng trắng ngoài DATA...). Không có
    sidecar (dashboard chưa từng xuất qua cơ chế này) thì cảm biến lùi về heuristic
    mtime cũ, không thay đổi hành vi cho dashboard cũ.

    Lỗi khi ghi sidecar KHÔNG được làm hỏng lượt xuất chính — đây là tiện ích tối
    ưu cho một cảm biến khác, không phải một trong bộ năm sản phẩm đã hứa."""
    try:
        sys.path.insert(0, str(DASH_TOOLS))
        import verify_dashboard as vd  # noqa: E402 — cần sys.path.insert trước
        html = dash.read_text(encoding="utf-8", errors="replace")
        data_block = vd.extract_data_block(html)
        if not data_block:
            return
        h = hashlib.sha256(data_block.encode("utf-8")).hexdigest()
        Path(word_path).with_suffix(".data-sha256").write_text(h + "\n", encoding="utf-8")
    except (OSError, ImportError, UnicodeDecodeError):
        pass


def doc_tieu_de(dash: Path) -> str:
    """Lấy câu hỏi lâm sàng trong khối DATA để làm <title> cho trang HTML.

    Chấp nhận CẢ nháy đơn LẪN nháy kép vì hai template EW/DA dùng quy ước khác
    nhau (đúng cái bẫy đã làm vỡ parser của build_dashboard_docx.py hồi 18/07).
    Không đọc được thì lùi về tên file — đây chỉ là nhãn hiển thị, không được
    phép làm hỏng cả bước.
    """
    try:
        text = dash.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return dash.stem
    m = re.search(r"question\s*:\s*(['\"])(.*?)\1", text, re.S)
    if m and m.group(2).strip():
        return m.group(2).strip()
    return dash.stem


def xuat_ban_word_html(docx_path: Path, dash: Path) -> tuple[Path | None, str]:
    """Dựng bản HTML tự chứa TỪ file .docx vừa sinh, để đọc thẳng trong khung chat.

    Trả về (đường dẫn hoặc None, lý do khi không sinh được).
    """
    out = docx_path.with_suffix(".html")
    pandoc = shutil.which("pandoc")
    if not pandoc:
        # NHÁNH DỰ PHÒNG (12/08/2026): máy không có pandoc — trước đây bỏ luôn cả
        # bước ④ VÀ bước ⑤, khiến Windows chỉ ra 3/5 sản phẩm trong khi Mac ra đủ
        # 5 từ cùng một dashboard. Dựng thẳng bằng python-docx (có sẵn trong venv).
        # Nhánh này còn GIỮ ĐƯỢC màu nền ô — thứ pandoc bỏ mất — nên không kèm
        # cảnh báo "mất màu".
        try:
            sys.path.insert(0, str(ROOT / "tools"))
            from docx_sang_html_khong_pandoc import dung_html_tu_docx

            dung_html_tu_docx(docx_path, out, tieu_de=doc_tieu_de(dash),
                              style=HTML_STYLE, banner=HTML_BANNER_GIU_MAU)
            return out, ""
        except Exception as e:  # noqa: BLE001 — bước đọc, không phải cổng chất lượng
            return None, (f"không có pandoc và nhánh dự phòng cũng lỗi ({e}); "
                          "ba sản phẩm kia KHÔNG bị ảnh hưởng")
    with tempfile.TemporaryDirectory() as tmp:
        style = Path(tmp) / "style.html"
        banner = Path(tmp) / "banner.html"
        style.write_text(HTML_STYLE, encoding="utf-8")
        banner.write_text(HTML_BANNER, encoding="utf-8")
        base = [pandoc, "-f", "docx", "-t", "html5", "--standalone",
                "--include-in-header", str(style),
                "--include-before-body", str(banner),
                "--metadata", f"title={doc_tieu_de(dash)}",
                str(docx_path), "-o", str(out)]
        # --embed-resources là cờ của pandoc ≥ 2.19; bản cũ hơn dùng --self-contained.
        # Thử cờ mới trước, lỗi thì lùi về cờ cũ (máy Windows chưa rõ phiên bản).
        for co_nhung in ("--embed-resources", "--self-contained"):
            rc, msg = run(base[:1] + [co_nhung] + base[1:])
            if rc == 0 and out.exists():
                return out, ""
            loi = msg.strip()
        return None, f"pandoc lỗi: {loi.splitlines()[-1] if loi else 'không rõ'}"


KHOI_BO_NAM = (("Dashboard     ", "dashboard"), ("Bản đọc       ", "ban_doc"),
               ("Bản Word      ", "word"), ("Word dạng HTML", "word_html"),
               ("PDF giữ màu   ", "pdf"))


def tom_tat_bo_nam(result: dict) -> str:
    """Dòng tiêu đề tổng kết — PHẢI nói đúng số sản phẩm THẬT SỰ sinh được.

    VÌ SAO CÓ (vá 13/08/2026): bản cũ in "── Bộ năm đã sẵn sàng ──" VÔ ĐIỀU KIỆN, kể
    cả khi chỉ sinh được 3/5. Ca thật cùng ngày: `AnToanThuoc_EMA_PRAC_20260614` hỏng
    ở bước ③ (chuỗi nối kiểu JS làm chết bộ dựng Word) nên mất cả ④ lẫn ⑤ — mà dòng
    tiêu đề vẫn tuyên bố "đã sẵn sàng". Người đọc lướt sẽ tin gói đã đủ và đem bản
    Word cũ đi dùng.

    Cùng họ với BH14/BH15/BH16: hệ NÓI SAI với bác sĩ mà không sai một phép tính nào.
    """
    co = [nhan.strip() for nhan, key in KHOI_BO_NAM if result.get(key)]
    thieu = [nhan.strip() for nhan, key in KHOI_BO_NAM if not result.get(key)]
    if thieu:
        return f"── Bộ năm: {len(co)}/5 — THIẾU {', '.join(thieu)} ──"
    return "── Bộ năm đã sẵn sàng (5/5) ──"


def main() -> int:
    configure_utf8_stdio()
    ap = argparse.ArgumentParser(
        description="Xuất đồng thời Dashboard + Bản đọc + Bản Word + Bản Word dạng HTML"
                    " cho một lần cập nhật chứng cứ")
    ap.add_argument("dashboard", help="đường dẫn WebDashboard_*.html")
    ap.add_argument("--online", action="store_true",
                    help="chạy cổng liêm chính có phân giải PMID/DOI thật trước khi xuất")
    ap.add_argument("--parts", help="file JSON nhóm 'phần' lớn cho bản Word (tuỳ chọn)")
    ap.add_argument("--json", action="store_true", help="in kết quả dạng JSON")
    a = ap.parse_args()

    dash = Path(a.dashboard).resolve()
    if not dash.exists():
        print(f"✗ Không thấy dashboard: {dash}", file=sys.stderr)
        return 2

    missing = [p.name for p in (BAN_DOC, DOCX) if not p.exists()]
    if missing:
        print(f"✗ Thiếu tool: {', '.join(missing)}", file=sys.stderr)
        print("  Tool trong EBM-Dashboards/tools/ đồng bộ qua OneDrive, không qua git —"
              " đợi OneDrive xanh rồi chạy lại.", file=sys.stderr)
        return 2

    py = sys.executable
    result = {"dashboard": str(dash), "ban_doc": None, "word": None,
              "word_html": None, "word_html_ly_do": None,
              "pdf": None, "pdf_ly_do": None,
              "cong_liem_chinh": "KHÔNG CHẠY", "verified_flag": False}
    rc_final = 0

    # ── ① Cổng liêm chính (tuỳ chọn nhưng nên chạy cho dashboard thật) ──────────
    verified = False
    if a.online:
        if not VERIFY.exists():
            print("✗ Thiếu verify_dashboard.py — bỏ qua cổng liêm chính", file=sys.stderr)
            result["cong_liem_chinh"] = "THIẾU TOOL"
            rc_final = 1
        else:
            print("① Cổng liêm chính (--online)…")
            rc, out = run([py, VERIFY, dash, "--online"], cwd=DASH_TOOLS.parent)
            tail = [ln for ln in out.splitlines() if ln.strip()][-1:] or [""]
            print("   " + tail[0].strip())
            if rc == 0:
                verified = True
                result["cong_liem_chinh"] = "PASS"
            else:
                result["cong_liem_chinh"] = "FAIL"
                rc_final = 1
                print("   ⚠ Cổng KHÔNG đạt — vẫn xuất file nhưng bản Word sẽ KHÔNG"
                      " khẳng định 'đã xác minh'.")

            # ── ①-bis Cổng NGUỒN NGHIÊM NGẶT (thêm 2026-08-11) ────────────────
            # `DESIGN-SPEC.md` §6 đòi `--online --strict-sources` từ đầu, nhưng dây
            # chuyền chỉ chạy `--online` nên nhóm luật mạnh nhất chưa bao giờ thi
            # hành. Rà 58 dashboard đã phát hành ngày 11/08 cho thấy vì sao phải
            # tách hai loại lỗi thay vì chặn tất:
            #   · 47/52 bản FAIL chỉ vì THIẾU `DATA.standards` — khối siêu dữ liệu
            #     ra đời SAU những bản đó. Nội dung lâm sàng không sai. Chặn cả
            #     nhóm này là chặn oan, và "sửa" bằng cách bịa ra hợp đồng nguồn
            #     cho một lần tìm kiếm đã xảy ra từ lâu chính là bịa provenance.
            #   · 4 bản mang lỗi THẬT: `decision='apply'` trên `gradeLevel` na/low,
            #     hoặc apply chỉ dựa Consensus. Đây là lỗi AN TOÀN — một khuyến cáo
            #     "áp dụng ngay" tựa trên chứng cứ chưa đủ mạnh.
            # Nên: lỗi an toàn thì CHẶN xuất; thiếu siêu dữ liệu thì cảnh báo.
            rc_s, out_s = run([py, VERIFY, dash, "--online", "--strict-sources"],
                              cwd=DASH_TOOLS.parent)
            if rc_s == 0:
                result["cong_nguon_nghiem"] = "PASS"
            else:
                loi_an_toan = [ln.strip() for ln in out_s.splitlines()
                               if "decision='apply'" in ln]
                if loi_an_toan:
                    result["cong_nguon_nghiem"] = "CHẶN"
                    print(f"   ⛔ CHẶN XUẤT — {len(loi_an_toan)} mục khai"
                          " 'Áp dụng ngay' trên chứng cứ chưa đủ mạnh:")
                    for ln in loi_an_toan[:8]:
                        print("      " + ln)
                    if len(loi_an_toan) > 8:
                        print(f"      … và {len(loi_an_toan)-8} mục nữa")
                    print("   Cách sửa ĐÚNG: HẠ `decision` xuống consider/notyet."
                          " TUYỆT ĐỐI không nâng `gradeLevel` — đó là lỗi tự gán mức.")
                    result["cong_liem_chinh"] = "CHẶN BỞI CỔNG NGUỒN"
                    if a.json:
                        print(json.dumps(result, ensure_ascii=False, indent=2))
                    return 3
                # Nhánh KHÔNG-an-toàn có nhiều nguyên nhân khác nhau; trước 12/08/2026
                # chỗ này gán CỨNG một nguyên nhân duy nhất là "thiếu DATA.standards".
                # Đo thật hôm đó: một dashboard CÓ ĐỦ khối standards rớt cổng chỉ vì
                # DNS gãy khi hỏi Crossref, mà vẫn bị in ra là thiếu siêu dữ liệu ⇒ đẩy
                # bác sĩ đi bổ sung thứ đã có sẵn, và che mất nguyên nhân thật là mạng.
                thieu_std = any("THIẾU DATA.standards" in ln or "standards thiếu" in ln
                                for ln in out_s.splitlines())
                loi_mang = [ln.strip() for ln in out_s.splitlines()
                            if "CHƯA XÁC MINH ĐƯỢC" in ln or "lỗi mạng" in ln]
                if thieu_std:
                    result["cong_nguon_nghiem"] = "THIẾU DATA.standards"
                    print("   ⚠ Cổng nguồn nghiêm ngặt không đạt vì thiếu"
                          " `DATA.standards` (bản cũ) — không chặn, nhưng nên bổ sung"
                          " khối hợp đồng nguồn khi cập nhật lần sau.")
                elif loi_mang:
                    result["cong_nguon_nghiem"] = "CHƯA KẾT LUẬN ĐƯỢC (mạng)"
                    print(f"   ⚠ Cổng nguồn nghiêm ngặt CHƯA kết luận được:"
                          f" {len(loi_mang)} định danh không phân giải được do MẠNG/DNS."
                          " Đây KHÔNG phải kết luận nguồn sai — chạy lại khi mạng ổn,"
                          " hoặc dùng `tools/so_xac_minh_nguon.py` để tích luỹ bằng"
                          " chứng qua nhiều vòng.")
                else:
                    result["cong_nguon_nghiem"] = "FAIL (lý do khác)"
                    print("   ⚠ Cổng nguồn nghiêm ngặt không đạt — KHÔNG phải lỗi an"
                          " toàn, cũng không phải thiếu `DATA.standards`. Nguyên văn:")
                    for ln in [l for l in out_s.splitlines() if l.strip().startswith("✗")][:8]:
                        print("      " + ln.strip())
    else:
        print("① Bỏ qua cổng liêm chính (không có --online) —"
              " bản Word sẽ ghi 'CẦN xác minh'.")

    result["verified_flag"] = verified

    # ── ② Bản đọc ─────────────────────────────────────────────────────────────
    print("② Bản đọc…")
    rc, out = run([py, BAN_DOC, dash])
    if rc != 0:
        print(out.strip(), file=sys.stderr)
        return 2
    for line in out.splitlines():
        if line.startswith("✓ Đã ghi"):
            result["ban_doc"] = line.replace("✓ Đã ghi", "").strip()
    print("   " + (result["ban_doc"] or "(không rõ đường dẫn)"))

    # ── ③ Bản Word ────────────────────────────────────────────────────────────
    print("③ Bản Word…")
    cmd = [py, DOCX, dash]
    if verified:
        cmd.append("--verified")
    if a.parts:
        cmd += ["--parts", str(Path(a.parts).resolve())]
    rc, out = run(cmd, cwd=DASH_TOOLS.parent)
    if rc != 0:
        print(out.strip(), file=sys.stderr)
        rc_final = 1
    else:
        for line in out.splitlines():
            if line.startswith("✓ Đã ghi"):
                result["word"] = line.replace("✓ Đã ghi", "").split("—")[0].strip()
        print("   " + (result["word"] or "(không rõ đường dẫn)"))
        if result["word"]:
            ghi_sidecar_hash_data(dash, result["word"])

    # ── ④ Bản Word dạng HTML (đọc thẳng trong khung chat) ─────────────────────
    # Chỉ chạy khi ③ đã ra file thật — không dựng HTML từ một bản Word không tồn tại.
    print("④ Bản Word dạng HTML (đọc thẳng trong khung chat)…")
    if not result["word"]:
        result["word_html_ly_do"] = "chưa có file .docx ở bước ③"
        print("   ⚠ Bỏ qua: " + result["word_html_ly_do"])
    else:
        html, ly_do = xuat_ban_word_html(Path(result["word"]), dash)
        if html:
            result["word_html"] = str(html)
            result["word_html_bo_may"] = "pandoc" if shutil.which("pandoc") else "python-docx"
            print("   " + str(html))
            # Nói đúng theo nhánh đã dùng: pandoc bỏ màu nền ô, nhánh python-docx giữ.
            if result["word_html_bo_may"] == "pandoc":
                print("   (giữ đủ chữ và bảng; MẤT màu nền ô — bản .docx vẫn là bản lưu trữ chuẩn)")
            else:
                print("   (dựng bằng python-docx vì máy không có pandoc; giữ cả chữ, bảng "
                      "VÀ màu nền ô)")
        else:
            result["word_html_ly_do"] = ly_do
            print("   ⚠ Bỏ qua: " + ly_do)
            # VÁ 13/08/2026: bản HTML của Word là MỘT trong bộ năm đã hứa (bác sĩ đọc
            # thẳng trong khung chat vì .docx không mở được ở đó) — thiếu nó là thiếu
            # một sản phẩm, phải phản ánh vào mã thoát. KHÁC bước ⑤ PDF: PDF là tiện
            # ích đọc, cố ý KHÔNG đổi mã thoát (đã ghi trong doctrine).
            rc_final = 1

    # ── ⑤ Bản PDF GIỮ MÀU ─────────────────────────────────────────────────────
    # pandoc bỏ hết màu nền ô khi chuyển .docx → HTML, nên bước ④ chỉ còn chữ.
    # Bước này đọc màu TỪ CHÍNH .docx rồi bơm lại vào HTML, sau đó in bằng Chrome
    # headless — cách duy nhất trên máy này giữ đúng huy hiệu mức chứng cứ.
    print("⑤ Bản PDF giữ màu…")
    if not result["word"]:
        result["pdf_ly_do"] = "chưa có file .docx ở bước ③"
        print("   ⚠ Bỏ qua: " + result["pdf_ly_do"])
    else:
        cmd = [py, str(ROOT / "tools" / "docx_sang_pdf_giu_mau.py"), result["word"]]
        if result.get("word_html"):
            cmd += ["--html-co-san", result["word_html"]]   # khỏi gọi lại pandoc
        rc, out = run(cmd)
        dong_ok = [l for l in out.splitlines() if l.strip().startswith("✓")]
        if rc == 0 and dong_ok:
            result["pdf"] = str(Path(result["word"]).with_suffix(".pdf"))
            for l in out.splitlines():
                if l.strip():
                    print("   " + l.strip())
        else:
            result["pdf_ly_do"] = (out.strip().splitlines() or ["không rõ"])[-1][:120]
            print("   ⚠ Bỏ qua: " + result["pdf_ly_do"])
            # PDF là tiện ích đọc, KHÔNG phải cổng chất lượng → không đổi mã thoát

    # VÁ 13/08/2026 — TIÊU ĐỀ PHẢI NÓI ĐÚNG SỰ THẬT.
    # Bản cũ in "── Bộ năm đã sẵn sàng ──" VÔ ĐIỀU KIỆN, kể cả khi chỉ sinh được 3/5.
    # Ca thật cùng ngày: `AnToanThuoc_EMA_PRAC_20260614` hỏng bước ③ nên mất cả ④ và
    # ⑤, mà dòng tiêu đề vẫn tuyên bố "đã sẵn sàng" — người đọc lướt sẽ tin gói đủ.
    # Cùng họ lỗi với BH14/BH15/BH16: hệ NÓI SAI mà không sai một phép tính nào.
    print("\n" + tom_tat_bo_nam(result))
    for nhan, key in KHOI_BO_NAM:
        print(f"  {nhan}  {result.get(key) or '(CHƯA SINH ĐƯỢC)'}")
    print(f"  Cổng liêm chính: {result['cong_liem_chinh']}")
    print("\nCần bác sĩ kiểm chứng trước khi áp dụng cho người bệnh cụ thể.")

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return rc_final


if __name__ == "__main__":
    raise SystemExit(main())
