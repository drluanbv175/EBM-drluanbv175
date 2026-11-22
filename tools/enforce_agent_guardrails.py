#!/usr/bin/env python3
"""Cấy cổng guardrail bắt buộc vào mọi agent nguồn Claude.

Nguồn biên tập chính là `.claude/agents/*.md`; sau khi chạy script này cần chạy:
  python3 tools/kiem_suc_khoe_agent.py

Script chỉ chèn block chuẩn nếu file agent chưa có marker, không đụng tài liệu hạ tầng `_*.md`.
Dùng `--refresh` để CẬP NHẬT block đã cấy trước đó về đúng nội dung BLOCK hiện tại (khớp
chính xác OLD_BLOCK_V1 cũ mới thay — không đụng file nào đã bị sửa tay khác bản gốc).
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
MARKER = "<!-- EBM-MANDATORY-FINAL-GUARDRAIL -->"

# SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 7, phát hiện LOW): dòng
# "Lớp 2 CHẤT LƯỢNG Med-PaLM Q1-Q7 cho gói lâm sàng" trước đây được cấy Y HỆT
# vào MỌI agent không phân biệt lâm sàng/nghiên cứu — tự mâu thuẫn với các
# agent thuần nghiên cứu tự khai "Lớp 2 N/A cho gói NGHIÊN CỨU" ngay trong
# thân bài (vd dieu-phoi-nghien-cuu.md, phan-tich-thong-ke.md, co-mau-nghien-
# cuu.md, viet-ban-thao.md). Đổi câu này thành ĐIỀU KIỆN tự nhất quán — không
# còn khẳng định trơn "cho gói lâm sàng" mà nêu rõ N/A cho gói thuần nghiên
# cứu, để không mâu thuẫn với bất kỳ agent nào cấy vào.
OLD_BLOCK_LOP2_LINE = (
    "   - Lớp 2 CHẤT LƯỢNG Med-PaLM Q1-Q7 cho gói lâm sàng: dễ đọc, đúng đắn, đầy đủ-an toàn,\n"
    "     không thiên kiến, không gây hại, cập nhật, nguồn có thẩm quyền.\n"
)
NEW_BLOCK_LOP2_LINE = (
    "   - Lớp 2 CHẤT LƯỢNG Med-PaLM Q1-Q7: áp dụng khi gói CÓ yếu tố lâm sàng (khuyến cáo\n"
    "     điều trị/an toàn thuốc cho bệnh nhân cụ thể) — dễ đọc, đúng đắn, đầy đủ-an toàn,\n"
    "     không thiên kiến, không gây hại, cập nhật, nguồn có thẩm quyền. N/A cho gói THUẦN\n"
    "     nghiên cứu/thống kê (dùng chuẩn báo cáo CONSORT/STROBE/PRISMA + completeness-critic\n"
    "     A1-A18 thay thế).\n"
)

OLD_RUT_BAI = '     khuyến cáo/điều chỉnh thuốc mà thiếu rà tương tác/CCĐ/chỉnh liều (2026-07-07).\n'
NEW_RUT_BAI = '     khuyến cáo/điều chỉnh thuốc mà thiếu rà tương tác/CCĐ/chỉnh liều (2026-07-07).\n   - RÚT BÀI — PHẢI TRA, KHÔNG ĐƯỢC TỰ NHỚ (2026-08-14): mọi PMID/DOI đưa vào kết luận\n     phải kiểm bằng `python medical-ebm-automation/tools/check_citation_retraction.py\n     --pmid <PMID…>` (chuỗi 3 tầng: Retraction Watch ngoại tuyến → NCBI → Europe PMC).\n     Một vụ rút bài có thể xảy ra SAU ngày cắt kiến thức nên trí nhớ mô hình không biết\n     được; ca thật PMID 30267080 — cả PubMed lẫn Europe PMC đều trả \'ok\', chỉ nền ngoại\n     tuyến bắt được. Không tra được ⇒ ghi "chưa kiểm rút bài", TUYỆT ĐỐI không ghi\n     "chưa bị rút". Bài quá mới thường CHƯA có publication type (MEDLINE gán sau) —\n     đừng loại nó vì lý do đó.\n'

# THÊM 15/11/2026 (sự cố G2 gieo `design_code` vào ô «bác sĩ ghim», thẩm định y khoa #277/#281 — bác sĩ: «cập nhật vào
# hệ thống nghiên cứu y khoa VÀ hệ thống cập nhật chứng cứ y khoa cho thực hành lâm sàng»). Luật chung cho CẢ đội (lâm
# sàng + nghiên cứu): máy không gieo vào ô quyết định của người, không ghi khoá phụ vào tệp mà biên bản/chữ ký băm.
OLD_KET_THUC = '3. Kết thúc mọi đầu ra y khoa bằng: "Cần bác sĩ kiểm chứng."\n'
NEW_KET_THUC = (
    '3. Kết thúc mọi đầu ra y khoa bằng: "Cần bác sĩ kiểm chứng."\n'
    '4. Ô QUYẾT ĐỊNH CỦA NGƯỜI — máy KHÔNG gieo (15/11/2026, sự cố G2 gieo `design_code` vào ô ghim của PI): ô chỉ\n'
    '   người ghi (ghim thiết kế `gate_params.Gx`/`design_code`, xác nhận/duyệt/ký, `decision`/`gradeLevel` của\n'
    '   dashboard, sổ `*-da-duyet.json`/`*-da-xet.json`/`rut-bai-da-xem-xet.json`) KHÔNG được ghi giá trị máy suy —\n'
    '   kể cả «chỉ điền khi còn trống». Bản sao của máy để ở checkpoint/tệp riêng (vd `.cho-ky.json`); không ghi\n'
    '   khoá phụ vào tệp mà biên bản/chữ ký/vân tay băm (đổi byte ⇒ xác nhận mất hiệu lực oan). Chỉ coi một giá trị\n'
    '   là quyết định của người khi có dấu người (ô chỉ người ghi, xác nhận tường minh, nhãn nguồn).\n'
)

# THÊM 22/11/2026 — chỉ thị của bác sĩ cùng ngày, phủ CẢ đội (lâm sàng + nghiên cứu), nhắc lại ở mọi agent:
# (5) nguyên tắc tổng «Mỗi quyết định trong nghiên cứu phải dựa trên bằng chứng khoa học, được thực hiện một cách đạo
#     đức, được kiểm chứng khách quan, và chỉ được chuyển sang bước tiếp theo khi bước hiện tại đã đạt chuẩn xác định
#     trước.» — triển khai bằng «quay lại bước đó để sửa, kiểm tra lại, sau khi đạt chuẩn thì "khóa" bước đó»;
# (6) «Khi tôi đã giao nhiệm vụ thì hãy bám vào nguyên tắc xây dựng hệ thống và giao cho tôi sản phẩm đúng; Đừng bao giờ
#     để nói là phần việc máy, phần của tôi … Hãy tiếp tục nhắc đi nhắc lại nhiều lần»;
# (7) «ghi nhỏ sổ nợ sẽ không ghi sổ nợ nữa, giải quyết theo nguyên tắc».
# Cặp (NEW_KET_THUC → NEW_KET_THUC_2211) chỉ NỐI THÊM mục 5–7 sau mục 4 đã cấy; agent mới nhận thẳng bản đủ qua BLOCK.
NEW_KET_THUC_2211 = NEW_KET_THUC + (
    '5. NGUYÊN TẮC TỔNG NGHIÊN CỨU (bác sĩ 22/11/2026): «Mỗi quyết định trong nghiên cứu phải dựa trên bằng chứng khoa\n'
    '   học, được thực hiện một cách đạo đức, được kiểm chứng khách quan, và chỉ được chuyển sang bước tiếp theo khi bước\n'
    '   hiện tại đã đạt chuẩn xác định trước.» Triển khai — SỬA ĐÚNG KHÂU RỒI KHOÁ: lỗi phát hiện ở khâu nào thì quay\n'
    '   lại sửa tại NGUỒN của khâu đó (đề tài: `gate_params`, bộ biến G3, SAP G4, bộ sinh của cổng; chứng cứ: dashboard,\n'
    '   bộ sinh) — không vá văn bản ở khâu sau → kiểm bằng chốt của chính khâu đó → đạt chuẩn thì khoá (dấu vân tay/chữ\n'
    '   ký của vai có thẩm quyền) → mới sinh lại và làm khâu kế. Đề tài: chạy `python\n'
    '   medical-ebm-automation/tools/buoc_dang_mo.py --study <mã>` trước khi sửa tài liệu một cổng; không sửa cổng nằm\n'
    '   sau khâu cần hoàn thiện; trình MỘT gói ký theo thứ tự; đề cương chấm theo ma trận phần × chuẩn × 8 nguyên tắc\n'
    '   (`_HOI-DONG-CONG.md` §1c).\n'
    '6. GIAO SẢN PHẨM, KHÔNG CHIA PHẦN (bác sĩ 22/11/2026 — nhắc lại mỗi lần giao việc): bám nguyên tắc xây hệ, giao\n'
    '   sản phẩm đúng; đầu ra/báo cáo nói đã giao gì, đạt chuẩn nào, khâu nào đã khoá — KHÔNG viết «phần của bác sĩ»,\n'
    '   «việc còn lại cho người», «máy không làm thay được»; việc dở thì làm tiếp cho xong. Chữ ký pháp lý không giả\n'
    '   được ⇒ trình là GÓI KÝ đã chuẩn bị (vai · mục ký · lệnh khoá), không phải danh sách việc treo. Khoá máy-đọc\n'
    '   (`cho_nguoi`, `con_lai_cho_nguoi`…) giữ nguyên — chỉ đổi lời trình bày.\n'
    '7. KHÔNG SỔ NỢ (bác sĩ 22/11/2026): không dùng sổ nợ, miễn trừ tay hay bánh cóc «chỉ giảm» để chốt/CI xanh khi\n'
    '   chuẩn chưa đạt; thiếu mục thì sửa tại nguồn tới 0; chốt đỏ khi thiếu bất kỳ mục nào; sổ nợ cũ chỉ được xoá về 0,\n'
    '   không ghi thêm, không gia hạn.\n'
)

BLOCK = f"""

{MARKER}
## Cổng bắt buộc trước khi trả lời

Trước mọi đầu ra cuối cùng có yếu tố lâm sàng, nghiên cứu y khoa, dashboard chứng cứ,
khuyến cáo điều trị, an toàn thuốc, thống kê y khoa hoặc tài liệu cho người bệnh:

1. Tự áp dụng guardrail `tham-dinh-dau-ra` theo 2 lớp:
   - Lớp 1 LIÊM CHÍNH R1-R7 (+ phụ lục R8 thống kê / R14 an toàn kê đơn khi áp dụng):
     nguồn PMID/DOI/URL, không PII, không vượt cổng bác sĩ duyệt,
     không tự gán GRADE khi nguồn không cấp, tách độ chắc chứng cứ với độ mạnh khuyến cáo,
     gắn nhãn `[CẦN...]` khi thiếu dữ liệu, có disclaimer. R14 HARD-RED khi gói CÓ
{NEW_RUT_BAI}{NEW_BLOCK_LOP2_LINE}2. Nếu còn lỗi đỏ, thiếu nguồn, nghi sai guideline, thiếu cảnh báo nguy cơ hại, hoặc có PII:
   không phát hành như khuyến cáo; trả về dạng `[CẦN BÁC SĨ PHÁN ĐỊNH]` / `[CẦN KIỂM CHỨNG]`.
{NEW_KET_THUC_2211}"""


def is_agent(path: Path) -> bool:
    return path.suffix == ".md" and path.name != "README.md" and not path.name.startswith("_")


# DANH SÁCH cặp thay thế, không phải MỘT cặp cứng (đổi 2026-08-14). Trước đây `_refresh`
# chỉ biết đúng một cặp, nên mỗi lần thêm luật mới cho toàn đội lại phải sửa cơ chế. Đó
# chính là lý do khiến doctrine TRÔI TỤT sau cổng: thêm luật ở cổng thì dễ, lan luật xuống
# 50 agent thì không có đường — xem BH39.
THAY_THE: list[tuple[str, str]] = [
    (OLD_BLOCK_LOP2_LINE, NEW_BLOCK_LOP2_LINE),
    (OLD_RUT_BAI, NEW_RUT_BAI),
    (OLD_KET_THUC, NEW_KET_THUC),
    (NEW_KET_THUC, NEW_KET_THUC_2211),
]


def _refresh(path: Path) -> bool:
    """Áp mọi cặp thay thế còn khớp trong file ĐÃ có marker.

    Bỏ qua im lặng cặp nào không khớp chính xác — file có thể đã bị sửa tay khác bản gốc,
    KHÔNG ép ghi đè. Chỉ báo True khi thực sự có thay đổi.
    """
    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        return False
    goc = text
    for cu, moi in THAY_THE:
        if cu in text and moi not in text:
            text = text.replace(cu, moi)
    if text == goc:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true",
                         help="Cập nhật dòng Lớp 2 đã cấy trước đó về bản mới (khớp chính xác, không ép ghi đè).")
    args = parser.parse_args()

    if args.refresh:
        refreshed: list[Path] = []
        for path in sorted(AGENTS.glob("*.md")):
            if not is_agent(path):
                continue
            if _refresh(path):
                refreshed.append(path)
        print("Agent guardrail refresh: done")
        print(f"- refreshed files: {len(refreshed)}")
        for path in refreshed:
            print(f"  {path.relative_to(ROOT)}")
        return 0

    changed: list[Path] = []
    for path in sorted(AGENTS.glob("*.md")):
        if not is_agent(path):
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        path.write_text(text.rstrip() + BLOCK + "\n", encoding="utf-8")
        changed.append(path)

    print("Agent guardrail enforcement: done")
    print(f"- checked agents: {len([p for p in AGENTS.glob('*.md') if is_agent(p)])}")
    print(f"- changed files: {len(changed)}")
    for path in changed:
        print(f"  {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
