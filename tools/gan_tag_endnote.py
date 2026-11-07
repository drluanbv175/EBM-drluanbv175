#!/usr/bin/env python3
"""Gắn tag EndNote theo luật — ĐO và LẬP KẾ HOẠCH; việc gắn là kéo-thả trong giao diện (07/11/2026, bác sĩ giao).

Bác sĩ 07/11/2026: «Cập nhật để mỗi lần đưa trích dẫn vào Endnote sẽ gắn Tab luôn cho tôi; … hãy gắn tab với những chứng cứ
có độ tin cậy cao và áp dụng cho thực hành lâm sàng». Bác sĩ chọn tiêu chí «Thêm guideline không chấm GRADE» và «Gắn ngay sau
mỗi lần nạp».

Ba nguồn tag cho mỗi bản ghi (ngoài thùng rác):
  1. TAG_AP_DUNG «★ Áp dụng – tin cậy cao»: bản ghi là nguồn chính của một mục `apply` ở PHIÊN BẢN HIỆN HÀNH của dashboard
     (trích dẫn chỉ còn ở bản cũ — bản mới đã bỏ — KHÔNG tính), mục đó có gradeLevel high/moderate, hoặc `na` khi thiết kế là
     guideline / nhãn thuốc / chống chỉ định chính thức (cổng `verify_dashboard` đã đòi normativeBasis cho `apply` trên `na`).
     low/vlow KHÔNG nhận, kể cả khi mục `apply` nhờ khuyến cáo mạnh. Consensus không bao giờ đủ.
  2. Tag theo nhóm đã ánh xạ ở `sync/endnote-tag-theo-nhom.json` (khoá group_id; bác sĩ duyệt cách làm 07/11/2026).
  3. Nhóm mới chưa ánh xạ: «NC · …» ⇒ «Nghiên cứu khoa học»; «EBM · …»/«TT · …» ⇒ tag chuyên khoa suy từ câu hỏi bằng ĐÚNG
     luật chuyên khoa của Antifacts (`build_antifacts.specialty_of_dashboard`); chuyên khoa không có tag riêng ⇒ «Nội ngoại chung».
     Nhóm khác (nhóm bác sĩ tự tạo) ⇒ báo «chưa ánh xạ», KHÔNG đoán. Nhóm LÀM VIỆC tên bắt đầu bằng «_» (agent tạo tạm: chờ
     thùng rác, cần toàn văn…) ⇒ không đòi tag và không tính là chỗ phân loại.
  4. Bản ghi LẺ (không thuộc nhóm nào) đã phân loại theo tiêu đề ở `sync/endnote-tag-ban-ghi-le.json` (khoá recNum; phiên
     Claude 07/11/2026 làm theo lời bác sĩ «gắn tab tất cả cho phù hợp» — bác sĩ sửa tệp là đổi tag). Ghi lại để tag lẻ đã
     gắn cũng được ĐO lại: tag mất (đồng bộ online, khôi phục từ thùng rác…) ⇒ hiện thành thiếu, không lặng lẽ biến mất.

Bản ghi CHƯA PHÂN LOẠI = không thuộc nhóm nào, không có trong tệp bản ghi lẻ và không mang tag nào ngoài tag Áp dụng ⇒ 🛎
(phiên Claude đọc tiêu đề, đề xuất tag, ghi vào tệp bản ghi lẻ rồi kéo; bản ghi của một chủ đề dashboard thì đưa về nhóm của
chủ đề). Đo 07/11/2026: 11 bản ghi chủ đề Chăm sóc giảm nhẹ mất cả nhóm lẫn tag trong 20 phút mà không lệnh nào báo.
Tag trùng tên (hai tag cùng tên) ⇒ 👤 bác sĩ quyết gộp (đo 07/11: «Frailty» ×2).

Vì sao không tự gắn: EndNote không có lệnh AppleScript nào cho tag (đo EndNote.sdef 07/11/2026) và luật dự án cấm ghi thẳng
`sdb.eni`. Công cụ chỉ đọc `sdb.eni` (chế độ chỉ-đọc), tính cặp bản ghi×tag còn thiếu, và `--hien "<tag>"` cho EndNote CHỈ hiện
và tô sáng đúng các bản ghi thiếu tag đó (AppleScript show/highlight — không ghi gì) để phiên Claude kéo một lần lên dòng tag
(`--huong-dan`). Chỉ ĐỀ XUẤT gỡ tag Áp dụng khỏi bản ghi không còn đạt (bản mới đổi quyết định/bỏ trích dẫn); không bao giờ đề
xuất gỡ tag khác — bác sĩ có thể tự gắn.

Lệnh:
  python3 tools/gan_tag_endnote.py                  # kế hoạch: thiếu theo từng tag + thừa tag Áp dụng + nhóm chưa ánh xạ
                                                    #   + bản ghi chưa phân loại + tag trùng tên
  python3 tools/gan_tag_endnote.py --hien "<tag>"   # EndNote chỉ hiện + tô sáng các bản ghi đang thiếu tag đó
  python3 tools/gan_tag_endnote.py --huong-dan      # quy trình kéo-thả cho phiên Claude (chế độ nền app_drag)
  python3 tools/gan_tag_endnote.py --giu-khoa [PHÚT] # CHẠY NỀN: giữ khoá ghi EndNote suốt phiên kéo-thả (mặc định 30, tối đa 60)
  python3 tools/gan_tag_endnote.py --nha-khoa       # nhả khoá phiên giao diện
  python3 tools/gan_tag_endnote.py --json
Mã thoát: 0 đủ tag · 1 còn việc (thiếu/thừa/tag chưa tạo/nhóm chưa ánh xạ/chưa phân loại/tag trùng tên) · 2 không đo được
· 3 tham số sai.

Khoá phiên giao diện (07/11/2026): khoá ghi `khoa_ghi_endnote` giữ theo TIẾN TRÌNH và nhả khi tiến trình thoát; phiên kéo-thả
gồm nhiều lượt công cụ ⇒ giữa hai lượt (rảnh ≥ 20 giây) phiên khác ghi chen được — đo 07/11 một lượt nhập bản ghi lúc đó làm
EndNote đổi vùng chọn ⇒ gắn nhầm tag. `--giu-khoa` là MỘT tiến trình nền giữ và làm mới khoá suốt phiên (ly_do bắt đầu bằng
`khoa_ghi_endnote.LY_DO_GIAO_DIEN`) ⇒ mọi lệnh ghi qua `EndNoteMac` của mọi phiên chờ rồi bỏ lượt, và show/highlight của phiên
khác bị từ chối; tự nhả khi hết hạn, khi nhận SIGTERM (`--nha-khoa`) hoặc khi thoát.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import signal
import sqlite3
import sys
import time
from collections.abc import Callable
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
TEP_ANH_XA = GOC / "sync" / "endnote-tag-theo-nhom.json"
TEP_TAG_LE = GOC / "sync" / "endnote-tag-ban-ghi-le.json"

TAG_AP_DUNG = "★ Áp dụng – tin cậy cao"
TAG_NGHIEN_CUU = "Nghiên cứu khoa học"
TAG_CHUNG = "Nội ngoại chung"
MUC_TIN_CAY = frozenset({"high", "mod", "moderate"})
# `na` chỉ đạt khi nguồn là chuẩn mực chính thức (guideline / nhãn thuốc / chống chỉ định) — đúng ba điều kiện cổng đòi.
THIET_KE_CHUAN_MUC = re.compile(r"guideline|hướng dẫn|khuyến cáo|nhãn thuốc|drug[\s-]*label|smpc|chống chỉ định", re.I)
CHI_CONSENSUS = re.compile(r"^\s*(expert\s+)?consensus\b|^\s*đồng thuận", re.I)

# Chuyên khoa của Antifacts → tag chuyên khoa trong EndNote. Chuyên khoa không có tag riêng ⇒ TAG_CHUNG.
CHUYEN_KHOA_TAG = {
    "Tim mạch": "Tim mạch", "Hô hấp": "Hô hấp", "Tiêu hóa – Gan mật": "Tiêu hoá", "Nội tiết – Chuyển hóa": "Nội tiết",
    "Thận – Tiết niệu": "Thận tiết niệu", "Thần kinh – Đột quỵ": "Thần kinh", "Cơ xương khớp – Thấp khớp": "Khớp",
    "Tâm thần kinh": "Tâm thần", "Lão khoa – Đa bệnh lý": "Lão khoa",
}
TIEN_TO_NHOM_CHU_DE = ("EBM ·", "TT ·")
TIEN_TO_NHOM_NGHIEN_CUU = ("NC ·",)
# Nhóm LÀM VIỆC tạm («_Cho thung rac …», «_Can toan van … - Find Full Text» do agent tạo 06–07/11/2026): không phải phân loại
# ⇒ không đòi tag, và thuộc nhóm này KHÔNG tính là «đã phân loại». Ánh xạ khai rõ group_id vẫn thắng.
TIEN_TO_NHOM_LAM_VIEC = ("_",)
# Nhóm làm việc chờ bác sĩ chuyển thùng rác (vd «_Cho thung rac 20261106 trung va khong phai chung cu») ⇒ thành viên CHỈ ở đó
# không bị báo «chưa phân loại» (sắp bỏ, gắn tag là thừa). Nhóm làm việc khác ⇒ thành viên chỉ ở đó VẪN là chưa phân loại.
NHOM_CHO_THUNG_RAC = re.compile(r"thung\s*rac|thùng\s*rác|trash", re.I)

MA_OK, MA_CON_VIEC, MA_KHONG_DO, MA_THAM_SO = 0, 1, 2, 3
PHUT_GIU_MAC_DINH, PHUT_GIU_TOI_DA = 30, 60
NHIP_LAM_MOI = 30  # giây — làm mới luc_epoch của khoá (HAN_KHOA 15 phút)
# Ngủ từng giây: Python thử lại time.sleep sau trình xử lý tín hiệu (PEP 475) ⇒ ngủ một lèo 30 s làm `--nha-khoa` chậm tới 30 s
# (đo thật 07/11/2026: SIGTERM nhận lúc đang ngủ, khoá chỉ nhả khi hết giấc).
NHIP_NGU = 1.0

HUONG_DAN = """Gắn tag bằng giao diện EndNote (phiên Claude; ƯU TIÊN chế độ NỀN app_* — không cần điều khiển toàn màn hình):
  0. CHẠY NỀN `python3 tools/gan_tag_endnote.py --giu-khoa 30` (Bash run_in_background) và đợi dòng «✓ đang giữ khoá» — mọi
     lệnh ghi EndNote qua EndNoteMac của mọi phiên (nhập, gắn PDF, ghi trường, show/highlight) chờ rồi bỏ lượt tới khi nhả.
     Vẫn ListAgents và nhắn phiên khác TẠM DỪNG (agent tự viết AppleScript riêng không đi qua khoá) — đo 07/11/2026: một lượt
     nhập giữa lúc kéo-thả làm EndNote đổi vùng chọn ⇒ bản ghi mới bị gắn nhầm tag.
  1. Tag chưa có ⇒ Tags › Create Tag… (tên đúng như kế hoạch in; tag Áp dụng màu xanh lá). Tạo xong EndNote CHỌN luôn tag đó
     làm khung đang xem ⇒ bấm «All References» trước bước 2: thả bản ghi lên CHÍNH khung đang xem không có tác dụng (đo 07/11).
  2. Với TỪNG tag còn thiếu — mỗi tag một lượt `--hien` riêng, KHÔNG kéo tag thứ hai từ vùng chọn cũ: sau mỗi lần thả EndNote
     có thể trở về danh sách đầy đủ, lần kéo sau chỉ mang dòng dưới con trỏ ⇒ gắn nhầm (đo 07/11: bản ghi 6412 nhận nhầm
     «Tiêu hoá»). `python3 tools/gan_tag_endnote.py --hien "<tag>"` ⇒ EndNote chỉ hiện và tô sáng các bản ghi đó (tiêu đề khung
     ghi đúng «N References»; các dòng tô sáng CHÍNH LÀ vùng chọn).
     CHẾ ĐỘ NỀN (đo 07/11/2026: 22 tag · 153 cặp, 43 bản ghi một lần kéo, 0 nhầm): KHÔNG bấm vào danh sách (bấm làm mất vùng chọn)
     — app_drag với path 5–7 điểm từ MỘT dòng đang tô sáng tới dòng tag ở thanh bên. Tìm dòng tag: app_scroll thanh bên
     (KHÔNG gõ ô lọc bằng app_type — rơi vào gõ-để-chọn của danh sách) rồi app_zoom đọc toạ độ hàng.
     Toàn màn hình (dự phòng): bấm dòng đầu (chờ 0,5 s) → cmd+A (chờ 0,8 s) → gõ tên tag vào ô lọc cột trái (góc dưới) → kéo
     từ một dòng đã chọn, nhả lên dòng tag (nhấn chuột · chờ 0,3 s · di qua vài điểm · chờ 0,5 s · nhả).
  3. Chạy lại `python3 tools/gan_tag_endnote.py` (đọc sdb.eni, sau vài giây) tới khi tag đó hết thiếu — số đếm cạnh tag trên
     giao diện làm mới chậm một nhịp, KHÔNG dùng làm căn cứ. Số đếm tăng lệch số bản ghi (vd +1 thay vì +36) ⇒ đã gắn nhầm
     dòng khác: tìm bản ghi mới nhận tag mà không thuộc kế hoạch rồi gỡ (bước 4).
  4. Thừa tag Áp dụng / tag gắn nhầm ⇒ chuột phải bản ghi › Manage Tags › bấm × trên chip tag › OK (menu Tags/References không
     có lệnh gỡ).
  5. Xong: xoá ô lọc, nhả điều khiển toàn màn hình / app_release, `python3 tools/gan_tag_endnote.py --nha-khoa`, nhắn các
     phiên đã nhờ tạm dừng.
  Bản ghi CHƯA PHÂN LOẠI (kế hoạch in 🛎): thuộc một chủ đề dashboard (khoá «EBM: <chủ đề>» ở Keywords) ⇒ đưa về nhóm của chủ
  đề (nhóm có tag riêng); bản ghi lẻ thật ⇒ đọc tiêu đề, ghi tag vào sync/endnote-tag-ban-ghi-le.json (PR) rồi kéo như bước 2."""


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parent / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ───────────────────────── luật (thuần, test được) ─────────────────────────

def dat_ap_dung_tin_cay(ngu_canh: list[dict]) -> bool:
    """Bản ghi đạt tag Áp dụng – tin cậy cao? `ngu_canh` theo khuôn `tom_tat_chung_cu_word._ngu_canh_cua` (vai · decision ·
    gradeLevel · design · ban_cu). CHỈ ngữ cảnh phiên bản hiện hành (ban_cu = False) — trích dẫn bản mới đã bỏ không đạt."""
    for x in ngu_canh:
        if x.get("ban_cu") or x.get("vai") != "muc" or str(x.get("decision") or "").strip().lower() != "apply":
            continue
        muc = str(x.get("gradeLevel") or "").strip().lower()
        if muc in MUC_TIN_CAY:
            return True
        thiet_ke = str(x.get("design") or "")
        if muc == "na" and THIET_KE_CHUAN_MUC.search(thiet_ke) and not CHI_CONSENSUS.search(thiet_ke):
            return True
    return False


def tag_cua_nhom(group_id: int, ten: str, anh_xa: dict[str, dict], chuyen_khoa: Callable[[str], str]) -> list[str] | None:
    """Tag cho bản ghi của một nhóm; None = nhóm chưa ánh xạ và không suy được (KHÔNG đoán)."""
    m = anh_xa.get(str(group_id))
    if m is not None:
        return [str(t) for t in m.get("tag") or []]
    ten = (ten or "").strip()
    if ten.startswith(TIEN_TO_NHOM_NGHIEN_CUU):
        return [TAG_NGHIEN_CUU]
    for tt in TIEN_TO_NHOM_CHU_DE:
        if ten.startswith(tt):
            return [CHUYEN_KHOA_TAG.get(chuyen_khoa(ten[len(tt):].strip()), TAG_CHUNG)]
    return None


def lap_ke_hoach(*, ban_ghi: dict[int, dict], nhom: list[dict], tag_hien_co: dict[int, set[str]], ten_tag: set[str],
                 anh_xa: dict[str, dict], chuyen_khoa: Callable[[str], str],
                 ngu_canh_cua: Callable[[str | None, str | None], list[dict]],
                 tag_le: dict[str, dict] | None = None) -> dict:
    """Kế hoạch thuần: {thieu: {tag: [rec]}, thua_ap_dung: [rec], tag_chua_tao: [tag], nhom_chua_anh_xa: [...],
    chua_phan_loai: [rec], dat_ap_dung: n, tong_ban_ghi: n}. `ban_ghi` = {rec: {pmid, doi}} ngoài thùng rác; `tag_le` =
    {"<recNum>": {"tag": [...]}} của bản ghi lẻ đã phân loại (tệp `TEP_TAG_LE`)."""
    can: dict[int, set[str]] = {}
    chua_anh_xa = []
    trong_nhom: set[int] = set()
    cho_thung_rac: set[int] = set()
    for n in nhom:
        rec = [r for r in (n.get("rec") or []) if r in ban_ghi]
        ten_n = n.get("ten") or ""
        if rec and ten_n.startswith(TIEN_TO_NHOM_LAM_VIEC) and str(n["group_id"]) not in anh_xa:
            # chỉ bỏ qua CHÍNH nhóm làm việc: bản ghi còn ở nhóm chủ đề khác vẫn nhận tag của nhóm đó
            if NHOM_CHO_THUNG_RAC.search(ten_n):
                cho_thung_rac.update(rec)
            continue
        if not rec:
            continue
        trong_nhom.update(rec)
        tags = tag_cua_nhom(n["group_id"], n.get("ten") or "", anh_xa, chuyen_khoa)
        if tags is None:
            chua_anh_xa.append({"group_id": n["group_id"], "ten": n.get("ten") or "", "so_ban_ghi": len(rec)})
            continue
        for r in rec:
            can.setdefault(r, set()).update(tags)
    da_phan_loai_le: set[int] = set()
    for k, v in (tag_le or {}).items():
        r = int(k)
        if r in ban_ghi:
            da_phan_loai_le.add(r)
            can.setdefault(r, set()).update(str(t) for t in v.get("tag") or [])
    # Không nhóm, không trong tệp bản ghi lẻ, không tag nào ngoài tag Áp dụng (tag Áp dụng không nói chuyên khoa).
    chua_phan_loai = sorted(r for r in ban_ghi if r not in trong_nhom and r not in da_phan_loai_le
                            and r not in cho_thung_rac and not (tag_hien_co.get(r, set()) - {TAG_AP_DUNG}))
    dat = set()
    for r, bg in ban_ghi.items():
        if dat_ap_dung_tin_cay(ngu_canh_cua(bg.get("pmid"), bg.get("doi"))):
            dat.add(r)
            can.setdefault(r, set()).add(TAG_AP_DUNG)
    thieu: dict[str, list[int]] = {}
    for r, tags in can.items():
        for t in tags - tag_hien_co.get(r, set()):
            thieu.setdefault(t, []).append(r)
    thua = sorted(r for r, tags in tag_hien_co.items() if TAG_AP_DUNG in tags and r in ban_ghi and r not in dat)
    can_dung = {t for tags in can.values() for t in tags}
    return {"thieu": {t: sorted(v) for t, v in sorted(thieu.items(), key=lambda kv: (kv[0] != TAG_AP_DUNG, kv[0]))},
            "thua_ap_dung": thua, "tag_chua_tao": sorted(can_dung - ten_tag),
            "nhom_chua_anh_xa": sorted(chua_anh_xa, key=lambda x: -x["so_ban_ghi"]),
            "chua_phan_loai": chua_phan_loai, "dat_ap_dung": len(dat), "tong_ban_ghi": len(ban_ghi)}


def con_viec(kh: dict) -> bool:
    return bool(kh.get("thieu") or kh.get("thua_ap_dung") or kh.get("tag_chua_tao") or kh.get("nhom_chua_anh_xa")
                or kh.get("chua_phan_loai") or kh.get("tag_trung"))


# ───────────────────────── đọc thư viện thật (chỉ đọc) ─────────────────────────

def doc_anh_xa(tep: Path = TEP_ANH_XA) -> dict[str, dict]:
    """Tệp vắng ⇒ {} (mọi nhóm đi luật suy); tệp hỏng ⇒ ValueError — không im lặng coi là rỗng."""
    if not tep.is_file():
        return {}
    d = json.loads(tep.read_text(encoding="utf-8"))
    nhom = d.get("nhom") if isinstance(d, dict) else None
    if not isinstance(nhom, dict):
        raise ValueError(f"{tep.name}: thiếu khoá «nhom» dạng object")
    return nhom


def doc_tag_le(tep: Path = TEP_TAG_LE) -> dict[str, dict]:
    """Bản ghi lẻ đã phân loại {"<recNum>": {"tieu_de", "tag": [...]}}. Tệp vắng ⇒ {}; tệp hỏng / khoá không phải số / tag
    rỗng ⇒ ValueError — không im lặng bỏ qua (một mục hỏng là một bản ghi lặng lẽ thôi được đo)."""
    if not tep.is_file():
        return {}
    d = json.loads(tep.read_text(encoding="utf-8"))
    bg = d.get("ban_ghi") if isinstance(d, dict) else None
    if not isinstance(bg, dict):
        raise ValueError(f"{tep.name}: thiếu khoá «ban_ghi» dạng object")
    for k, v in bg.items():
        tags = v.get("tag") if isinstance(v, dict) else None
        if not re.fullmatch(r"\d+", str(k)) or not isinstance(tags, list) or not tags \
                or not all(isinstance(t, str) and t.strip() for t in tags):
            raise ValueError(f"{tep.name}: mục «{k}» cần khoá recNum dạng số và «tag» là danh sách tên tag không rỗng")
    return bg


def tag_trung_ten(kn: sqlite3.Connection) -> list[str]:
    """Tên tag xuất hiện ở ≥ 2 tag khác nhau (đo 07/11/2026: «Frailty» ×2 — bản ghi chia ở hai tag cùng tên)."""
    dem: dict[str, int] = {}
    for (spec,) in kn.execute("select spec from tag_groups"):
        s = spec.decode("utf-8", "replace") if isinstance(spec, bytes) else str(spec or "")
        m = re.search(r"<name>(.*?)</name>", s, re.S)
        if m:
            dem[m.group(1)] = dem.get(m.group(1), 0) + 1
    return sorted(t for t, n in dem.items() if n > 1)


def doc_tag(kn: sqlite3.Connection) -> tuple[set[str], dict[int, set[str]]]:
    """(tên mọi tag, {rec: {tên tag}}) từ `tag_groups` + `tag_members_content` (c0 = các mã tag hex cách bằng dấu cách)."""
    ten: dict[int, str] = {}
    for gid, spec in kn.execute("select group_id, spec from tag_groups"):
        s = spec.decode("utf-8", "replace") if isinstance(spec, bytes) else str(spec or "")
        m = re.search(r"<name>(.*?)</name>", s, re.S)
        if m:
            ten[int(gid)] = m.group(1)
    theo_rec: dict[int, set[str]] = {}
    for rid, c0 in kn.execute("select id, c0 from tag_members_content"):
        ma = []
        for x in str(c0 or "").split():
            try:
                ma.append(int(x, 16))
            except ValueError:
                continue
        theo_rec[int(rid)] = {ten[g] for g in ma if g in ten}
    return set(ten.values()), theo_rec


def ke_hoach_thu_vien(thu_vien: Path | None = None, *, anh_xa_tep: Path = TEP_ANH_XA, tag_le_tep: Path = TEP_TAG_LE) -> dict:
    """Kế hoạch cho thư viện thật. Không đo được ⇒ {"do_duoc": False, "ly_do": …} — không bao giờ coi là «đủ tag»."""
    try:
        # Tệp cấu hình đọc TRƯỚC thư viện: tệp hỏng phải báo đúng tên lỗi cả trên máy chưa có EndNote.
        anh_xa, tag_le = doc_anh_xa(anh_xa_tep), doc_tag_le(tag_le_tep)
        sk = _nap("_sk_gte", "endnote_suc_khoe.py")
        tv = Path(thu_vien) if thu_vien else sk.thu_vien_cau_hinh()
        if not tv or not Path(tv).is_file():
            return {"do_duoc": False, "ly_do": "chưa khai thư viện EndNote (~/.ebm-endnote.json) hoặc tệp .enl vắng"}
        ttw = _nap("_ttw_gte", "tom_tat_chung_cu_word.py")
        ba = _nap("_ba_gte", "build_antifacts.py")
        nec = ttw.mod("nec")
        kn = sk._ket_noi(Path(tv))
        try:
            ban_ghi = {}
            for rec, acc, erd in kn.execute(
                    "select id, accession_number, electronic_resource_number from refs where trash_state = 0"):
                pmid = acc if acc and re.fullmatch(r"\d{1,9}", str(acc).strip()) else None
                ban_ghi[int(rec)] = {"pmid": pmid, "doi": nec.chuan_doi(erd) if erd else None}
            ten_tag, tag_hien_co = doc_tag(kn)
            trung = tag_trung_ten(kn)
        finally:
            kn.close()
        nhom = sk.doc_nhom(Path(tv))
        ds = ttw.ngu_canh_dashboard()
        if not ds:
            return {"do_duoc": False, "ly_do": "không thấy dashboard nào (EBM-Dashboards vắng) — không xét được tag Áp dụng"}
        kh = lap_ke_hoach(ban_ghi=ban_ghi, nhom=nhom, tag_hien_co=tag_hien_co, ten_tag=ten_tag, anh_xa=anh_xa,
                          chuyen_khoa=lambda q: ba.specialty_of_dashboard("", q),
                          ngu_canh_cua=lambda p, d: ttw._ngu_canh_cua(ds, p, d), tag_le=tag_le)
    except (OSError, sqlite3.Error, ValueError, UnicodeDecodeError) as e:
        return {"do_duoc": False, "ly_do": f"{type(e).__name__}: {str(e)[:200]}"}
    kh.update(do_duoc=True, thu_vien=str(tv), tag_trung=trung)
    return kh


# ───────────────────────── in / lệnh ─────────────────────────

def _ds(rec: list[int], toi_da: int = 30) -> str:
    return ", ".join(map(str, rec[:toi_da])) + (f" … (+{len(rec) - toi_da})" if len(rec) > toi_da else "")


def tom_tat_mot_dong(kh: dict) -> str:
    """Một dòng cho bộ năm/hòm việc."""
    if not kh.get("do_duoc"):
        # chữ thường có chủ ý: cụm IN HOA «KHÔNG ĐO ĐƯỢC» trong báo cáo lượt nạp thuộc phép đo kho toàn văn (test 17/10/2026)
        return f"⚪ gắn tag EndNote: không đo được — {kh.get('ly_do')}"
    if not con_viec(kh):
        return f"✓ tag EndNote đủ ({kh['dat_ap_dung']} bản ghi mang «{TAG_AP_DUNG}»)"
    so = sum(len(v) for v in kh["thieu"].values())
    phan = [f"{so} cặp bản ghi×tag chờ gắn ({len(kh['thieu'])} tag)"] if so else []
    if kh["thua_ap_dung"]:
        phan.append(f"{len(kh['thua_ap_dung'])} bản ghi thừa «{TAG_AP_DUNG}»")
    if kh["tag_chua_tao"]:
        phan.append(f"tag chưa tạo: {', '.join(kh['tag_chua_tao'])}")
    if kh["nhom_chua_anh_xa"]:
        phan.append(f"{len(kh['nhom_chua_anh_xa'])} nhóm chưa ánh xạ tag")
    if kh.get("chua_phan_loai"):
        phan.append(f"{len(kh['chua_phan_loai'])} bản ghi chưa phân loại (không nhóm, không tag)")
    if kh.get("tag_trung"):
        phan.append(f"tag trùng tên: {', '.join(kh['tag_trung'])}")
    return "🛎 gắn tag EndNote: " + " · ".join(phan) + " — phiên Claude: python3 tools/gan_tag_endnote.py --huong-dan"


def in_ke_hoach(kh: dict) -> None:
    if not kh.get("do_duoc"):
        print(tom_tat_mot_dong(kh))
        return
    print(f"Thư viện: {kh['thu_vien']} — {kh['tong_ban_ghi']} bản ghi ngoài thùng rác; {kh['dat_ap_dung']} đạt «{TAG_AP_DUNG}»")
    if not con_viec(kh):
        print("✓ Mọi bản ghi đã đủ tag theo luật.")
        return
    for t in kh["tag_chua_tao"]:
        print(f"🛎 cần tạo tag «{t}» (Tags › Create Tag…) trước khi kéo")
    for t, rec in kh["thieu"].items():
        print(f"🛎 «{t}»: thiếu {len(rec)} bản ghi — recNum {_ds(rec)}")
        print(f"     python3 tools/gan_tag_endnote.py --hien \"{t}\"")
    if kh["thua_ap_dung"]:
        print(f"🛎 «{TAG_AP_DUNG}» THỪA ở {len(kh['thua_ap_dung'])} bản ghi (không còn là nguồn của mục Áp dụng tin cậy cao ở "
              f"phiên bản hiện hành) — gỡ qua Manage Tags: recNum {_ds(kh['thua_ap_dung'])}")
    for n in kh["nhom_chua_anh_xa"]:
        print(f"👤 nhóm «{n['ten'][:70]}» (group_id {n['group_id']}, {n['so_ban_ghi']} bản ghi) chưa ánh xạ tag — thêm vào "
              f"{TEP_ANH_XA.relative_to(GOC)} (bác sĩ chọn tag)")
    if kh.get("chua_phan_loai"):
        print(f"🛎 {len(kh['chua_phan_loai'])} bản ghi CHƯA PHÂN LOẠI (không thuộc nhóm nào, không tag chuyên khoa): recNum "
              f"{_ds(kh['chua_phan_loai'])} — bản ghi của chủ đề dashboard (Keywords «EBM: …») ⇒ đưa về nhóm của chủ đề; "
              f"bản ghi lẻ ⇒ đọc tiêu đề, ghi tag vào {TEP_TAG_LE.relative_to(GOC)} rồi kéo")
    for t in kh.get("tag_trung") or []:
        print(f"👤 tag trùng tên «{t}» (≥ 2 tag cùng tên) — bác sĩ quyết gộp; gộp = chuyển bản ghi sang một tag rồi Tags › "
              "Delete Tag tag còn lại")
    print("Quy trình: python3 tools/gan_tag_endnote.py --huong-dan")


def hien_thieu(tag: str, kh: dict, endnote_cls=None) -> int:
    rec = (kh.get("thieu") or {}).get(tag)
    if rec is None and tag == TAG_AP_DUNG and kh.get("thua_ap_dung"):
        rec = kh["thua_ap_dung"]
        print(f"(không còn bản ghi thiếu — hiện {len(rec)} bản ghi THỪA «{tag}» để gỡ qua Manage Tags)")
    if not rec:
        print(f"✓ «{tag}»: không có bản ghi nào cần xử lý")
        return MA_OK
    nap = _nap("_nap_gte", "nap_endnote_chu_de.py")
    ch = nap.doc_cau_hinh() or {}
    try:
        en = (endnote_cls or nap.EndNoteMac)(ch.get("ung_dung") or nap.UNG_DUNG_MAC_DINH, Path(kh["thu_vien"]))
    except nap.KhongChayDuoc as e:
        print(f"⚪ {e}")
        return MA_KHONG_DO
    if not en.dang_mo_dung_thu_vien():
        print("⚪ EndNote chưa mở đúng thư viện — mở EndNote rồi chạy lại")
        return MA_KHONG_DO
    kg = nap.nap_khoa_ghi()
    if kg is not None and not kg.khoa_giao_dien_khac():
        print("⚠ chưa có khoá phiên giao diện — chạy NỀN `python3 tools/gan_tag_endnote.py --giu-khoa 30` trước khi kéo-thả "
              "(phiên khác có thể ghi chen giữa các lượt và làm đổi vùng chọn)")
    en.hien_ban_ghi(rec, trong_phien_gan_tag=True)
    print(f"✓ EndNote đang CHỈ hiện {len(rec)} bản ghi (đã tô sáng). Bấm dòng đầu → cmd+A → lọc cột trái «{tag}» → kéo lên tag.")
    return MA_CON_VIEC


# ───────────────────────── khoá phiên giao diện ─────────────────────────

def _khoa():
    """Bản mô-đun khoá DÙNG CHUNG với `EndNoteMac` (nạp qua `nap_endnote_chu_de.nap_khoa_ghi`, xem lý do ở đó)."""
    kg = _nap("_nap_khoa_gte", "nap_endnote_chu_de.py").nap_khoa_ghi()
    if kg is None:
        raise OSError("không nạp được tools/khoa_ghi_endnote.py")
    return kg


def giu_khoa_giao_dien(phut: float, *, kg=None, tep: Path | None = None, ngu=time.sleep, dong_ho=time.monotonic,
                       dung: dict | None = None, kiem_giao_dich=None, dang_dung=None, in_ra=print) -> int:
    """Giữ khoá ghi EndNote suốt một phiên kéo-thả (chạy NỀN). Lấy khoá như mọi lệnh ghi (chờ tiến trình khác/bác sĩ, không
    lấy khi giao dịch treo), rồi làm mới mỗi NHIP_LAM_MOI giây tới khi hết `phut`, khi `dung["co"]` (SIGTERM/SIGINT) — nhả khi
    ra khỏi phạm vi, kể cả khi lỗi. Các tham số còn lại tiêm được để test."""
    kg = kg or _khoa()
    phut = max(1.0, min(float(phut), PHUT_GIU_TOI_DA))
    ly_do = f"{kg.LY_DO_GIAO_DIEN} — tối đa {phut:g} phút (python3 tools/gan_tag_endnote.py --nha-khoa để nhả)"
    tu_cli = dung is None
    dung = dung if dung is not None else {"co": False}
    if tu_cli:
        def _dung(*_):
            dung["co"] = True
        signal.signal(signal.SIGTERM, _dung)
        signal.signal(signal.SIGINT, _dung)
        kiem_giao_dich = kiem_giao_dich or (lambda: kg.kiem_giao_dich_treo(None))
    with kg.pham_vi_ghi():
        try:
            kg.cho_phep_ghi_loi("EndNote", ly_do, tep=tep, kiem_giao_dich=kiem_giao_dich, dang_dung=dang_dung, ngu=ngu,
                                dong_ho=dong_ho, thong_bao=None if tu_cli else (lambda _n: None))
        except (kg.DangCoTienTrinhKhacGhi, kg.BacSiDangDungEndNote, kg.GiaoDichEndNoteTreo) as e:
            in_ra(f"⚪ chưa giữ được khoá ghi EndNote: {e}")
            return MA_KHONG_DO
        in_ra(f"✓ đang giữ khoá phiên giao diện (pid {os.getpid()}, tối đa {phut:g} phút) — kéo-thả được; xong chạy --nha-khoa")
        if tu_cli:
            sys.stdout.flush()
        het = dong_ho() + phut * 60
        lan_lam_moi = dong_ho()
        while not dung["co"] and dong_ho() < het:
            ngu(min(NHIP_NGU, max(0.0, het - dong_ho())))
            if dung["co"]:
                break
            if dong_ho() - lan_lam_moi < NHIP_LAM_MOI:
                continue
            lan_lam_moi = dong_ho()
            try:
                kg.cho_phep_ghi_loi("EndNote", ly_do, tep=tep, dang_dung=lambda: False, thong_bao=lambda _n: None)
            except (kg.DangCoTienTrinhKhacGhi, OSError) as e:  # mất khoá giữa chừng ⇒ báo, KHÔNG coi như vẫn giữ
                in_ra(f"⚪ mất khoá phiên giao diện giữa chừng: {e} — dừng kéo-thả, đo lại sdb.eni")
                return MA_KHONG_DO
    in_ra("✓ đã nhả khoá phiên giao diện")
    return MA_OK


def nha_khoa_giao_dien(*, kg=None, tep: Path | None = None, gui=os.kill, ngu=time.sleep, in_ra=print) -> int:
    """Nhả khoá phiên giao diện: gửi SIGTERM cho tiến trình `--giu-khoa` đang giữ. Khoá KHÁC (lượt nạp, MCP…) ⇒ KHÔNG đụng."""
    kg = kg or _khoa()
    d = kg.doc_khoa(tep)
    if not d:
        in_ra("✓ không có khoá ghi EndNote nào đang giữ")
        return MA_OK
    if not str(d.get("ly_do") or "").startswith(kg.LY_DO_GIAO_DIEN):
        in_ra(f"✗ khoá đang giữ không phải khoá phiên giao diện (pid {d.get('pid')}: «{str(d.get('ly_do'))[:80]}») — không đụng")
        return MA_THAM_SO
    if not kg.khoa_giao_dien_khac(tep):
        in_ra("✓ khoá phiên giao diện đã hết hiệu lực (tiến trình đã thoát hoặc quá hạn)")
        return MA_OK
    try:
        gui(int(d["pid"]), signal.SIGTERM)
    except ProcessLookupError:
        in_ra("✓ tiến trình giữ khoá đã thoát")
        return MA_OK
    for _ in range(40):
        if not kg.khoa_giao_dien_khac(tep):
            in_ra("✓ đã nhả khoá phiên giao diện")
            return MA_OK
        ngu(0.25)
    in_ra(f"⚪ đã gửi tín hiệu dừng cho pid {d.get('pid')} nhưng khoá chưa nhả — kiểm lại sau vài giây")
    return MA_KHONG_DO


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hien", metavar="TAG", help="EndNote chỉ hiện + tô sáng các bản ghi đang thiếu tag này")
    ap.add_argument("--huong-dan", action="store_true", help="in quy trình kéo-thả cho phiên Claude")
    ap.add_argument("--giu-khoa", nargs="?", type=float, const=PHUT_GIU_MAC_DINH, metavar="PHUT",
                    help=f"CHẠY NỀN: giữ khoá ghi EndNote suốt phiên kéo-thả (mặc định {PHUT_GIU_MAC_DINH}, tối đa {PHUT_GIU_TOI_DA})")
    ap.add_argument("--nha-khoa", action="store_true", help="nhả khoá phiên giao diện")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.huong_dan:
        print(HUONG_DAN)
        return MA_OK
    if a.giu_khoa is not None or a.nha_khoa:
        if a.giu_khoa is not None and a.nha_khoa:
            print("✗ --giu-khoa và --nha-khoa không đi cùng nhau")
            return MA_THAM_SO
        try:
            return giu_khoa_giao_dien(a.giu_khoa) if a.giu_khoa is not None else nha_khoa_giao_dien()
        except OSError as e:
            print(f"⚪ {e}")
            return MA_KHONG_DO
    kh = ke_hoach_thu_vien()
    if a.json:
        print(json.dumps(kh, ensure_ascii=False, indent=1))
    elif not a.hien:
        in_ke_hoach(kh)
    if not kh.get("do_duoc"):
        return MA_KHONG_DO
    if a.hien:
        return hien_thieu(a.hien, kh)
    return MA_CON_VIEC if con_viec(kh) else MA_OK


if __name__ == "__main__":
    sys.exit(main())
