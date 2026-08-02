#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_danh_muc.py — Sinh DANH MỤC tiếng Việt của mọi thứ gọi được trong Claude Code.

Đọc catalog_raw.json (do extract_catalog.py sinh) + vi_descriptions.json rồi xuất
DANH-MUC-CONG-CU.md: nhóm theo tầng ưu tiên và theo plugin, mỗi mục ghi cách gọi.

File này là thứ lệnh `/cong-cu-gi` đọc để trả lời "việc này thì dùng gì".
Sinh lại sau mỗi lần cập nhật plugin: extract_catalog.py -> apply_vi.py -> build_danh_muc.py
"""
from __future__ import annotations

import json
import pathlib
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "DANH-MUC-CONG-CU.md"

TEN_TANG = {
    1: "TẦNG 1 — Y khoa, nghiên cứu, tài liệu (dùng thường xuyên)",
    2: "TẦNG 2 — Kỹ thuật, dùng khi sửa chính hệ EBM",
    3: "TẦNG 3 — Ngoài chuyên môn (biết là có, hiếm khi dùng)",
}
TEN_LOAI = {"skill": "kỹ năng", "command": "lệnh", "agent": "agent"}


def main() -> int:
    items = json.loads((HERE / "catalog_raw.json").read_text("utf-8"))
    vi = json.loads((HERE / "vi_descriptions.json").read_text("utf-8"))

    dong: list[str] = []
    dong.append("# Danh mục công cụ gọi được trong Claude Code\n")
    dong.append("> Sinh tự động bằng `tools/vietnamize/build_danh_muc.py`. "
                "KHÔNG sửa tay — chạy lại script sau mỗi lần cập nhật plugin.\n")
    dong.append(f"\n**Tổng cộng {len(items)} mục.** Cách gọi: gõ `/` rồi tên lệnh, "
                "hoặc nói thẳng nhu cầu để hệ thống tự chọn.\n")

    # Bảng tra nhanh theo nhu cầu thường gặp của bác sĩ
    dong.append("\n## Tra nhanh theo nhu cầu\n")
    dong.append("| Cần làm gì | Gọi cái gì |")
    dong.append("|---|---|")
    for nhu_cau, cong_cu in [
        ("Khám một ca bệnh theo 5 bước EBM", "agent `dieu-phoi-lam-sang`"),
        ("Chạy một đề tài nghiên cứu qua các cổng G0–G10", "agent `dieu-phoi-nghien-cuu`"),
        ("Tra chứng cứ cho một câu hỏi lâm sàng", "agent `tra-cuu-chung-cu`"),
        ("Tính cỡ mẫu", "agent `co-mau-nghien-cuu`"),
        ("Thẩm định chứng cứ, tính NNT", "agent `tham-dinh-grade-nnt`"),
        ("Rà an toàn một đơn thuốc", "agent `ke-don-an-toan`"),
        ("Kiểm trích dẫn PMID/DOI có thật không", "agent `kiem-chung-trich-dan`"),
        ("Tra mã ICD-10", "`/tra-ma-icd10`"),
        ("Tra thử nghiệm lâm sàng đang tuyển", "`/tra-thu-nghiem-lam-sang`"),
        ("Tra bản thảo tiền in (preprint)", "`/tra-preprint`"),
        ("Tra mức đồng thuận của y văn", "`/tra-consensus`"),
        ("Tra dược lý, cơ chế tác dụng của thuốc", "`/tra-thuoc`"),
        ("Bóc thông tin có cấu trúc từ bệnh án", "`/trich-xuat-benh-an`"),
        ("Khử định danh bệnh án trước khi nghiên cứu", "`/khu-dinh-danh`"),
        ("Cập nhật chứng cứ + dựng dashboard", "kỹ năng `cap-nhat-chung-cu-y-khoa`"),
        ("Kiểm bản thảo theo chuẩn báo cáo (47 chuẩn)", "`/medsci-review:check-reporting`"),
        ("Chọn tạp chí để nộp bài", "`/medsci-submission:find-journal`"),
        ("Viết thư phản hồi phản biện", "`/medsci-submission:revise`"),
        ("Khử định danh dữ liệu nghiên cứu", "`/medsci-data:deidentify` hoặc `/khu-dinh-danh`"),
        ("Làm sạch và khảo sát bộ dữ liệu", "`/medsci-data:clean-data` · `/medsci-data:generate-codebook`"),
        ("Tổng quan hệ thống / phân tích gộp", "`/medsci-analysis:meta-analysis`"),
        ("Vẽ hình đạt chuẩn đăng bài", "`/medsci-presentation:make-figures`"),
        ("Gọt tiếng Anh học thuật trước khi nộp", "`/medsci-writing:polish-language`"),
        ("Không biết dùng gì", "`/cong-cu-gi <việc cần làm>`"),
    ]:
        dong.append(f"| {nhu_cau} | {cong_cu} |")

    # Skill DỰNG SẴN của Claude Code — không có file trên máy (nhúng trong binary),
    # nên không nằm trong catalog. Mô tả lấy từ vi_skill_mac_dinh.json.
    f_mac_dinh = HERE / "vi_skill_mac_dinh.json"
    if f_mac_dinh.exists():
        md = json.loads(f_mac_dinh.read_text("utf-8"))
        muc = {k: v for k, v in md.items() if not k.startswith("_")}
        dong.append("\n---\n")
        dong.append(f"## Skill DỰNG SẴN của Claude Code  ({len(muc)} mục)\n")
        dong.append("> Nhóm này **không có file trên máy** — chúng nhúng trong chính phần mềm "
                    "nên không Việt hoá tại chỗ được (sửa sẽ phá chữ ký và mất khi cập nhật). "
                    "Mô tả dưới đây là bản giải thích để tra cứu.\n")
        dong.append("| Gọi bằng | Là gì | Dùng khi nào | Lưu ý |")
        dong.append("|---|---|---|---|")
        for ten, v in sorted(muc.items()):
            lu = v.get("luu_y", "—").replace("|", "\\|")
            dong.append(f"| `/{ten}` — {v['ten_viet']} | {v['vi'].replace('|', chr(92)+'|')} "
                        f"| {v.get('dung_khi','—').replace('|', chr(92)+'|')} | {lu} |")

    # Danh sách đầy đủ, theo tầng rồi theo plugin
    theo_tang: dict[int, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for i in items:
        theo_tang[i["tier_guess"]][i["plugin"] or i["source"]].append(i)

    for tang in (1, 2, 3):
        nhom = theo_tang.get(tang, {})
        tong = sum(len(v) for v in nhom.values())
        dong.append(f"\n---\n\n## {TEN_TANG[tang]}  ({tong} mục)\n")
        for plugin in sorted(nhom, key=lambda p: -len(nhom[p])):
            ds = sorted(nhom[plugin], key=lambda x: (x["kind"], x["name"]))
            dong.append(f"\n### {plugin}  ({len(ds)})\n")
            dong.append("| Gọi bằng | Loại | Làm gì |")
            dong.append("|---|---|---|")
            for i in ds:
                mo_ta = vi.get(i["id"], {}).get("vi") or i["desc_en"]
                mo_ta = " ".join(mo_ta.split())
                if len(mo_ta) > 240:
                    mo_ta = mo_ta[:237] + "…"
                mo_ta = mo_ta.replace("|", "\\|")
                dong.append(f"| `{i['invoke']}` | {TEN_LOAI[i['kind']]} | {mo_ta} |")

    OUT.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print(f"✓ Đã sinh {OUT.name}: {len(items)} mục, {len(dong)} dòng")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
