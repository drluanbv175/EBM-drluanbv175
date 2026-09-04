#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_danh_muc.py — Sinh DANH MỤC tiếng Việt của mọi thứ gọi được trong Claude Code.

Đọc bản chụp danh mục của MỌI máy (catalog_may/*.json do extract_catalog.py sinh)
+ vi_descriptions.json rồi xuất DANH-MUC-CONG-CU.md: nhóm theo tầng ưu tiên và theo
plugin, mỗi mục ghi cách gọi và MÁY NÀO gọi được.

Gộp nhiều máy (03/08/2026) vì bác sĩ dùng Mac lẫn Windows với bộ plugin khác nhau:
sinh danh mục từ một máy sẽ vừa thiếu mục của máy kia, vừa mời gọi những thứ máy
đang dùng không có. File này lại đang track Git nên mỗi lần đổi máy sẽ ghi đè lẫn nhau.

File này là thứ lệnh `/cong-cu-gi` đọc để trả lời "việc này thì dùng gì".
Sinh lại sau mỗi lần cập nhật plugin: extract_catalog.py -> apply_vi.py -> build_danh_muc.py
"""
from __future__ import annotations

# --- Ép stdout sang UTF-8 (vá 05/08/2026) ---------------------------------
# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt làm script chết giữa
# chừng bằng UnicodeEncodeError, trong khi phần việc chính đã chạy xong. Ép ở
# đây thay vì bắt người dùng nhớ đặt PYTHONIOENCODING trước mỗi lệnh.
import sys as _sys

for _luong in (_sys.stdout, _sys.stderr):
    if _luong is not None and (getattr(_luong, "encoding", "") or "").lower().replace("-", "") != "utf8":
        try:
            _luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass          # luồng bị chuyển hướng kiểu không reconfigure được — bỏ qua
# --------------------------------------------------------------------------

import json
import pathlib
import re
from collections import defaultdict

from extract_catalog import nhom_cua      # cùng thư mục — dùng chung cách gom nhóm nguồn

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "DANH-MUC-CONG-CU.md"
SNAP_DIR = HERE / "catalog_may"

TEN_TANG = {
    1: "TẦNG 1 — Y khoa, nghiên cứu, tài liệu (dùng thường xuyên)",
    2: "TẦNG 2 — Kỹ thuật, dùng khi sửa chính hệ EBM",
    3: "TẦNG 3 — Ngoài chuyên môn (biết là có, hiếm khi dùng)",
}
TEN_LOAI = {"skill": "kỹ năng", "command": "lệnh", "agent": "agent"}


def nap_danh_muc() -> tuple[list[dict], list[str], dict[str, str], dict[str, set[str]]]:
    """Gộp danh mục của mọi máy.

    Trả (danh sách mục — mỗi mục thêm khoá `may` là danh sách máy có mục đó,
    danh sách tên máy, ngày quét theo máy). Chưa có bản chụp nào thì lùi về
    catalog_raw.json của máy đang chạy để công cụ vẫn chạy được như trước.
    """
    snaps = sorted(SNAP_DIR.glob("*.json")) if SNAP_DIR.is_dir() else []
    if not snaps:
        muc = json.loads((HERE / "catalog_raw.json").read_text("utf-8"))
        for i in muc:
            i["may"] = ["máy này"]
        return muc, ["máy này"], {}, {}

    gop: dict[str, dict] = {}
    may_ds: list[str] = []
    ngay: dict[str, str] = {}
    nhom_da_quet: dict[str, set[str]] = {}
    for f in snaps:
        d = json.loads(f.read_text("utf-8"))
        may = d.get("may") or f.stem
        # OneDrive có thể đẻ ra bản trùng ("Mac-DESKTOP-XYZ.json") khi hai máy ghi
        # cùng lúc. Nhận diện máy bằng trường `may` BÊN TRONG file, không bằng tên
        # file, và chỉ giữ bản quét MỚI NHẤT — nếu không, một máy sẽ bị đếm hai lần
        # và mọi con số "có ở cả 2 máy" thành sai.
        if may in ngay:
            if d.get("ngay_quet", "") <= ngay[may]:
                continue
            may_ds.remove(may)
            gop = {k: v for k, v in gop.items() if v["may"] != [may]}
            for v in gop.values():
                if may in v["may"]:
                    v["may"].remove(may)
        may_ds.append(may)
        ngay[may] = d.get("ngay_quet", "?")
        # Bản chụp cũ không khai trường này → coi như đã quét mọi nhóm nó CÓ mục,
        # không suy diễn thêm (thà im lặng còn hơn khẳng định sai).
        nhom_da_quet[may] = set(d.get("nhom_da_quet")
                                or {nhom_cua(i["source"]) for i in d.get("muc", [])})
        for i in d.get("muc", []):
            cu = gop.get(i["id"])
            if cu is None:
                gop[i["id"]] = {**i, "may": [may]}
            elif may not in cu["may"]:
                cu["may"].append(may)
    return list(gop.values()), may_ds, ngay, nhom_da_quet


def mo_ta_vi(vi: dict, item: dict) -> str:
    """Bản dịch tiếng Việt cho MỘT mục catalog — tra khoá `id` trước, rồi
    fallback khoá `name:<tên>`, cuối cùng mới rơi về mô tả tiếng Anh gốc.

    SỬA 2026-09-04 (Workflow đối kháng đa-agent, phát hiện MEDIUM) — trước
    đây chỉ tra `vi.get(item["id"])`, thiếu fallback `name:<tên>` mà
    apply_vi.py/verify_vi.py đã có (bản dịch DÙNG CHUNG cho mọi bản sao cùng
    tên, vd bmad-method lặp nguyên bộ skill ở 6 plugin con). Xác nhận trên
    chính catalog thật: 75/1070 mục ở `catalog_may/Linux.json` chỉ tra được
    bản dịch qua khoá `name:`, không có khoá `id` trực tiếp trong
    `vi_descriptions.json` — trước bản vá, các mục này luôn rơi về
    `desc_en` (tiếng Anh) dù đã có bản dịch sẵn. `id` luôn thắng fallback,
    khớp đúng thứ tự ưu tiên của `apply_vi.py`."""
    entry_id = vi.get(item["id"])
    entry_name = vi.get(f"name:{item['name']}")
    return ((entry_id or entry_name or {}).get("vi")) or item["desc_en"]


def nhan_may(may: list[str], tat_ca: list[str], nhom: str = "",
             nhom_theo_may: dict[str, set[str]] | None = None) -> str:
    """Nhãn máy hiển thị — chỉ nói rõ khi mục KHÔNG có đủ trên mọi máy.

    Phân biệt hai chuyện rất khác nhau mà bản đầu gộp làm một: máy kia THẬT SỰ
    không có mục này, và máy kia CHƯA TỪNG QUÉT nhóm nguồn đó (bản chụp cũ hơn
    lần công cụ học thêm một nguồn mới). Nói "chỉ Windows" cho trường hợp sau là
    khẳng định sai — 03/08/2026 đúng 11 lệnh tiếng Việt bị dán nhãn kiểu này.
    """
    if len(tat_ca) > 1 and len(may) == len(tat_ca):
        return "cả 2 máy"
    nhan = "+".join(may)
    if nhom and nhom_theo_may:
        chua_quet = [m for m in tat_ca
                     if m not in may and nhom not in nhom_theo_may.get(m, set())]
        if chua_quet:
            nhan += f" · {'+'.join(chua_quet)} chưa quét nhóm này"
    return nhan


def main() -> int:
    items, may_ds, ngay_quet, nhom_theo_may = nap_danh_muc()
    vi = json.loads((HERE / "vi_descriptions.json").read_text("utf-8"))
    # Tra "cách gọi này có trên máy nào" cho bảng tra nhanh viết tay bên dưới.
    theo_invoke = {i["invoke"]: i["may"] for i in items}
    nhom_theo_invoke = {i["invoke"]: nhom_cua(i["source"]) for i in items}
    # Cùng một skill có thể mang id/cách gọi KHÁC nhau ở hai máy (vd
    # cap-nhat-chung-cu-y-khoa: Windows nối thẳng nên gọi `/tên`, Mac đi qua nhóm
    # Cowork nên gọi `/anthropic-skills:tên`). Tra thêm theo TÊN để khỏi kết luận
    # nhầm là "chỉ có ở một máy".
    theo_ten: dict[str, set[str]] = defaultdict(set)
    for i in items:
        theo_ten[i["name"]].update(i["may"])

    dong: list[str] = []
    dong.append("# Danh mục công cụ gọi được trong Claude Code\n")
    dong.append("> Sinh tự động bằng `tools/vietnamize/build_danh_muc.py`. "
                "KHÔNG sửa tay — chạy lại script sau mỗi lần cập nhật plugin.\n")
    dong.append(f"\n**Tổng cộng {len(items)} mục.** Cách gọi: gõ `/` rồi tên lệnh, "
                "hoặc nói thẳng nhu cầu để hệ thống tự chọn.\n")
    if len(may_ds) > 1:
        dong.append("\n> **Gộp danh mục của cả 2 máy** — bộ plugin trên Mac và Windows "
                    "khác nhau, nên cột **Máy** cho biết mục đó gọi được ở đâu. "
                    "Mục ghi tên một máy sẽ KHÔNG hiện khi bác sĩ đang ngồi máy kia.\n")
        for m in may_ds:
            n = sum(1 for i in items if m in i["may"])
            dong.append(f"> - **{m}**: {n} mục (quét ngày {ngay_quet.get(m, '?')})")
        chung = sum(1 for i in items if len(i["may"]) == len(may_ds))
        dong.append(f"> - có ở **cả 2 máy**: {chung} mục\n")
        dong.append("> Nhãn máy chỉ đúng TỚI NGÀY QUÉT ghi trên. Máy nào quét trước một "
                    "lần nâng cấp công cụ có thể thiếu cả một nhóm mục (và bị hiểu nhầm "
                    "là \"máy kia mới có\") — chạy lại `extract_catalog.py` trên máy đó "
                    "rồi sinh lại danh mục.\n")

    # Bảng tra nhanh theo nhu cầu thường gặp của bác sĩ.
    # Bảng này viết TAY nên từng mời gọi cả những thứ chỉ cài ở một máy (vd nhóm
    # /medsci-* chỉ có trên Mac). Dò ngược cách gọi về danh mục thật để tự gắn nhãn
    # máy, thay vì để bác sĩ gõ xong mới biết là máy này không có.
    def may_cua_dong(cong_cu: str) -> tuple[list[str], str]:
        co: set[str] = set()
        nhom = ""
        for tok in re.findall(r"`([^`]+)`", cong_cu):
            for ung_vien in (tok, f"agent {tok}", f"/{tok}"):
                if ung_vien in theo_invoke:
                    co.update(theo_invoke[ung_vien])
                    nhom = nhom or nhom_theo_invoke.get(ung_vien, "")
                    break
            # LUÔN cộng thêm kết quả tra theo TÊN, kể cả khi cách gọi đã khớp: cùng
            # một skill có thể mang cách gọi khác nhau ở hai máy, khớp được một máy
            # rồi dừng sẽ kết luận "chỉ máy này" trong khi máy kia vẫn gọi được.
            ten = tok.split()[-1].lstrip("/").split(":")[-1]
            co.update(theo_ten.get(ten, set()))
        return [m for m in may_ds if m in co], nhom

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
        may, nhom = may_cua_dong(cong_cu)
        if may and len(may) < len(may_ds):
            cong_cu += f" *({nhan_may(may, may_ds, nhom, nhom_theo_may)})*"
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
            # Cả plugin chỉ có ở một máy thì nói ngay ở tiêu đề, khỏi đọc từng dòng
            may_plugin = sorted({m for i in ds for m in i["may"]}, key=may_ds.index)
            gan = "" if len(may_plugin) == len(may_ds) else f" · chỉ {'+'.join(may_plugin)}"
            dong.append(f"\n### {plugin}  ({len(ds)}{gan})\n")
            dong.append("| Gọi bằng | Loại | Máy | Làm gì |")
            dong.append("|---|---|---|---|")
            for i in ds:
                mo_ta = mo_ta_vi(vi, i)
                mo_ta = " ".join(mo_ta.split())
                if len(mo_ta) > 240:
                    mo_ta = mo_ta[:237] + "…"
                mo_ta = mo_ta.replace("|", "\\|")
                dong.append(f"| `{i['invoke']}` | {TEN_LOAI[i['kind']]} "
                            f"| {nhan_may(i['may'], may_ds, nhom_cua(i['source']), nhom_theo_may)} "
                            f"| {mo_ta} |")

    OUT.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print(f"✓ Đã sinh {OUT.name}: {len(items)} mục, {len(dong)} dòng")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
