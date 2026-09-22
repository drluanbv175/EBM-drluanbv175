#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRA CỨU TẠI ĐIỂM KHÁM — Clinical Quick View (PHA 5 LÔ 2, 15/08/2026).

Khác hẳn dashboard đọc-lúc-rảnh: giữa hai bệnh nhân chỉ có vài giây. Luật cứng:

  • CHỈ thẻ ĐÃ DUYỆT (N4): decision do bác sĩ chốt trong dashboard đã xác minh
    (`from_doctor_master`/`from_dashboard_master`). Ứng viên CANDIDATE (hàng quét
    tuần, `from_engine`) TUYỆT ĐỐI không hiện lúc đang khám.
  • KHÔNG có thẻ ⇒ nói thẳng «CHƯA ĐƯỢC GIÁM SÁT» + chỉ nguồn tra tay. CẤM sinh
    câu trả lời từ trí nhớ mô hình (mục 10) — câu hỏi được GHI LẠI làm tín hiệu
    bổ sung watchlist (LÔ 5, `state/cau-hoi-chua-giam-sat.jsonl`).
  • Thẻ có bản tổng hợp MỚI HƠN chưa rà (danh sách quét quý) → hiện kèm cờ 🟠
    «có bản mới hơn chưa rà» — đọc xong phải biết mình đang đứng trên nền nào.
  • Ngoại tuyến 100%% — mất mạng phòng khám không làm mất tra cứu.

VÁ 21/09/2026 (đánh giá hoàn thiện, việc #1) — bộ xếp hạng cũ TRẢ THẺ SAI CHỦ ĐỀ cho câu phổ biến nhất (đo sống trên 1.100 thẻ:
«tăng huyết áp mới chẩn đoán chọn thuốc gì» → thẻ cơn tăng đường huyết/tân sinh tủy/H. pylori; «hen bậc 3» → thẻ chẹn beta;
«gút cấp» → thẻ phù mạch; «viêm họng liên cầu» → thẻ viêm túi thừa) — đúng loại lỗi mà chính docstring này gọi là nguy hiểm hơn
«chưa giám sát». Ba nguyên nhân đọc được từ mã: (1) `_bo_dau` không gấp «đ»→«d» nên «đau»/«điều» KHÔNG khớp danh sách từ chung
«dau»/«dieu» và lọt vào token đặc hiệu; (2) khớp CHỨA-CHUỖI trên từng ÂM TIẾT («tang» ⊂ «tăng sinh», «hen» ⊂ «khen»); (3) ngưỡng
«một nửa số token» + điểm cộng từ ở phần khuyến cáo. Nay: gấp đ→d; khớp theo TỪ NGUYÊN; trọng số IDF trên toàn kho; một token NẶNG (≥75% token hiếm nhất) PHẢI khớp ở TIÊU ĐỀ thẻ;
phủ ≥70% khối lượng IDF VÀ ≥70% số token (hoặc ≥2 token đặc hiệu ở tiêu đề với phủ ≥50%); token ngắn có dấu (gút/đau/áp/cấp)
đòi khớp đúng dấu (tránh «gút»≠«gut», «đau»≠«dấu»; «đau đầu» là HAI token, không gộp thành một); từ ghép («đau đầu»,
«tăng huyết áp», «lợi tiểu») phải KỀ NHAU ở tiêu đề thẻ — không thì «đau»+«ban đầu» ở thẻ đau ngực trả lời câu hỏi đau đầu;
tiền tố đổi nghĩa «tiền/hậu» luôn phải kề. Thẻ cùng khuyến cáo khác quyết định KHÔNG bị gộp âm thầm (đặt cờ xung đột).
Không đủ tin cậy ⇒ «CHƯA GIÁM SÁT», KHÔNG bao giờ trả thẻ gần đúng.
VÁ 22/09/2026 (phản biện độc lập VÒNG 2, sau khi #1-#3 đã commit) — thêm 6 cơ chế nữa, mỗi cái có tái hiện thật trên kho 1.100
thẻ: (a) PHỦ ĐỊNH — từ đứng ngay sau «không/chưa» (hoặc cách một từ nối «có/bị/mắc») ở TIÊU ĐỀ thẻ mà câu hỏi KHÔNG phủ định
cùng từ đó bị loại khỏi phần khớp («KHÔNG lọc máu» không trả lời câu hỏi về người ĐANG lọc máu; «…KHI KHÔNG CÓ HEN» không trả
lời câu hỏi về hen); (b) VIẾT TẮT IN HOA 2-4 chữ đòi khớp ĐÚNG DẠNG HOA trong tiêu đề gốc (case-sensitive) — phân biệt «DM»
(tiếng Anh) khỏi «ĐM» (chữ Đ khác D), «MI» khỏi «mì», «PSA» khỏi «PsA»; (c) TIỀN TỐ «u» (khối u) như «tiền/hậu» — «u gan»
không còn ra thẻ xơ gan chỉ vì «u» bị bỏ như mã lẻ; (d) LUẬT «MỘT VẾ CỦA TỪ GHÉP TRƯỢT» (vd «phổi» của «viêm phổi») nay áp
cho MỌI độ dài câu, không chỉ ≤3 token — có bảng miễn trừ ĐÓNG cho từ ghép ĐỒNG NGHĨA («chống đông»≈«kháng đông») để không
loại oan; (e) TOKEN NGẮN GÕ KHÔNG DẤU MƠ HỒ — kho có ≥2 dạng có dấu cạnh tranh (không dạng nào áp đảo ≥70%) thì không dùng
làm bằng chứng riêng lẻ («ho» → hô/hỗ/hở, không có "ho"=cough thật trong kho); (f) MỎ NEO QUÁ PHỔ BIẾN sau khi loại token mơ
hồ — không bám vào từ còn lại nếu nó cũng quá chung («ho ra máu» sau khi loại «ho» chỉ còn «máu», quá phổ biến để làm neo).
Gấp dấu nay TÁCH-TỪ-TRƯỚC-RỒI-MỚI-GẤP (không gấp cả chuỗi rồi tách) — ký hiệu/phân số (℃,½,№…) từng làm 3 mảng song song
LỆCH ĐỘ DÀI, xoá sạch thông tin dấu («đau chân ℃» từng ra thẻ đau ngực); nay không còn lệch được về cấu trúc.
GIỚI HẠN THẬT CÒN LẠI, KHÔNG SỬA ĐƯỢC BẰNG LUẬT TỪ VỰNG (đo bằng bộ vàng `quality/eval/tra-diem-kham/bo-vang.json`, mục
`da_biet_chua_dat`) — thiên về ĐỘ CHÍNH XÁC hơn độ phủ (bác sĩ tra tay là an toàn, không nguy hiểm) — và ĐA NGHĨA THẬT của
tiếng Việt: «lá» trong «thuốc lá»(điếu thuốc) và «hai lá»(van tim) là CÙNG MỘT TỪ, không phải lỗi gấp dấu; «già» trong «người
già» và «ruột già» cũng vậy; «hạ kali máu» có thể là TÌNH TRẠNG (hạ kali) hay TÁC DỤNG THUỐC (thuốc làm hạ kali, tức điều trị
TĂNG kali) — cùng cụm từ, khác vai trò ngữ pháp; và một số fold KHÔNG có dạng có dấu cạnh tranh trong kho («sốt» không hề
xuất hiện, chỉ có «sót» — cơ chế mơ hồ cần ≥2 dạng để so sánh nên không bắt được). Muốn giải triệt để cần truy hồi ngữ nghĩa
(embedding + nhãn chủ đề bác sĩ duyệt), không phải thêm luật từ vựng — xem `audit/12-danh-gia-hoan-thien-he-thong_2026-09-21.md`.

Dùng:  python3 tools/tra_diem_kham.py "copd đợt cấp bộ ba"
       python3 tools/tra_diem_kham.py --demo   # 5 câu mô phỏng + đo tốc độ
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
LEDGER = GOC / "EBM_MASTER" / "EBM_MASTER.json"
NGUON_DUYET = {"from_doctor_master", "from_dashboard_master"}
STATE = GOC / "state"          # nơi ghi nhật ký/tín hiệu — test đổi được để KHÔNG ghi vào state thật


def _bo_dau(s: str) -> str:
    """Gấp dấu về ASCII thường. GẤP CẢ «đ»→«d»: NFD không tách được «đ» nên bản cũ giữ nguyên «đau»/«điều» — trong khi
    danh sách từ chung viết «dau»/«dieu» ⇒ mọi từ có «đ» lọt thành token đặc hiệu (nguyên nhân số 1 của thẻ lạc đề)."""
    # NFKD (không phải NFD): «CHA₂DS₂-VASc» (chỉ số dưới) phải trùng «CHA2DS2-VASc» gõ ASCII.
    s = unicodedata.normalize("NFKD", (s or "").replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


_RE_TU = re.compile(r"\w+", re.UNICODE)
# Ký hiệu/phân số ĐƠN KÝ TỰ (℃ ℉ № ™ ® © ‰ ½ ¼ ¾ ⅓ ⅔ ⅛ ⅜ ⅝ ⅞) là \w (Unicode coi chúng "alnum") nên `_RE_TU` bắt được, nhưng
# gấp dấu (NFKD) làm chúng RÃ RA thành CHỮ SỐ/CHỮ CÁI rác («½»→«1⁄2») — không sai lệch số token nữa (đã sửa ở `_tach`/
# `_phan_tich_cau_hoi`, tách-rồi-gấp), nhưng vẫn để lại một token vô nghĩa có IDF cao (hiếm) VÀ có thể bị chọn làm mỏ neo,
# khiến MỌI thẻ bị loại (không thẻ nào chứa chuỗi rác đó). Bỏ hẳn cho sạch — đây là bệnh án hay gặp («sốt 39℃»).
_RE_KY_HIEU_BO = re.compile("[℃℉№™®©‰½¼¾⅓⅔⅛⅜⅝⅞]")


# «típ / tuýp / type 2» là MỘT từ ở y văn Việt (đái tháo đường TÝP 2 / type 2) — gộp để câu hỏi «tuýp 2» không rơi «ngoài kho».
_DONG_NGHIA = {"type": "tip", "tuyp": "tip", "typ": "tip"}
_DONG_NGHIA_THO = {"type": "tip", "tuýp": "tip", "típ": "tip", "typ": "tip", "tuyp": "tip"}
# Cụm CỐ ĐỊNH mà từ đầu đứng riêng đổi nghĩa hẳn («phù» ⊂ «phù hợp», «khó thở» ⊄ «khó chịu», «thiếu máu» ⊂ «thiếu máu cục bộ»):
# gộp thành MỘT token cả ở thẻ lẫn ở câu hỏi. Danh sách ĐÓNG, ngắn, mỗi mục có bằng chứng lạc đề đo được (phản biện 21/09).
_CUM_CO_DINH = (("thieu", "mau", "cuc", "bo"), ("phu", "hop"), ("kho", "chiu"), ("da", "thuoc"), ("can", "nhac"))


def _gop_cum(tok: list[str]) -> list[str]:
    ra: list[str] = []
    k = 0
    while k < len(tok):
        for cum in _CUM_CO_DINH:
            if tuple(tok[k:k + len(cum)]) == cum:
                ra.append("".join(cum))
                k += len(cum)
                break
        else:
            ra.append(tok[k])
            k += 1
    return ra


def _tach(s: str) -> list[str]:
    """Các TỪ NGUYÊN đã gấp dấu (không phải chuỗi con), đã gộp đồng nghĩa và cụm cố định.

    TÁCH TỪ trên NFC TRƯỚC, rồi mới gấp dấu TỪNG TỪ — không gấp dấu cả chuỗi rồi tách lại. Gấp-trước-tách từng làm LỆCH SỐ
    TOKEN với `_tach_tho`/dạng-hoa khi một ký hiệu (℃, ½, №, ™…) NFKD ra thêm chữ cái mà bản NFC không tách ra (phản biện
    22/09: «đau chân ℃» → 3 mảng song song có độ dài khác nhau ⇒ MẤT TOÀN BỘ thông tin dấu, «chân» lọt thành «chẩn»/từ đệm).
    Tách-rồi-gấp loại bỏ khả năng này TẬN GỐC: số token luôn bằng số token của `_tach_tho`/dạng-hoa vì cả ba đều tách từ
    CÙNG một lượt `_RE_TU.findall` trên CÙNG chuỗi NFC — gấp dấu chỉ đổi NỘI DUNG từng token, không thể đổi SỐ token."""
    return _gop_cum([_DONG_NGHIA.get(_bo_dau(t), _bo_dau(t)) for t in _RE_TU.findall(unicodedata.normalize("NFC", s or ""))])


def _tach_tho(s: str) -> list[str]:
    """Các từ nguyên GIỮ DẤU (chỉ hạ chữ thường, NFC) — để phân biệt «gút»≠«gut», «đau»≠«dấu» ở từ ngắn."""
    return [_DONG_NGHIA_THO.get(t, t) for t in _RE_TU.findall(unicodedata.normalize("NFC", s or "").lower())]


# Từ chức năng + từ lâm sàng CHUNG (mồi nhiễu). Đã gấp dấu. KHÔNG đưa «dau» (đau≠dấu sau khi gấp «đ») — cặp «dấu hiệu»
# được gỡ riêng bằng cụm (xem _phan_tich_cau_hoi) để «đau đầu»/«đau ngực» vẫn còn token đặc hiệu.
_TU_CHUNG = frozenset("""
co la thi cua va voi cho khi nao gi sao the nhu ra vao len xuong duoc bi se da dang nen can hay hoac roi nay do kia mot cac
nhung moi chi tai tu den trong ngoai tren duoi sau truoc ma thuong luon hoan rat qua hon nhat khong ko nhieu it lan
tri dieu chan doan chon thuoc benh nhan nguoi lon tuoi cao nang nhe hieu canh bao nhap vien tru xu lam nhu bao lieu
dung phac do huong dan khuyen nguy tot xau lieu bn pt bnhan
""".split())

# Viết tắt hay gõ tại điểm khám → cụm đầy đủ (đã gấp dấu). Chỉ thêm khi chắc nghĩa duy nhất.
# Tiền tố ĐỔI NGHĨA thực thể y khoa đứng ngay trước danh từ («TIỀN đái tháo đường», «HẬU phẫu»): cặp có tiền tố này
# luôn phải kề nhau ở thẻ — nếu không, thẻ «đái tháo đường» trả lời câu hỏi «tiền đái tháo đường». Danh sách ĐÓNG, có chủ ý
# ngắn: mọi từ đệm khác (sau, đa, không…) quá nhập nhằng, thêm vào sẽ chặn oan.
_TIEN_TO_DOI_NGHIA = frozenset({"tien", "hau"})
# Từ chức năng NHƯNG khi gõ CÓ DẤU là từ y khoa («não» ≠ «nào», «chân» ≠ «chẩn», «thượng» ≠ «thường», «da»/«đa» ≠ «đã»):
# bản đầu gấp dấu rồi coi mọi «nao/can/chan/da/la/thuong» là từ đệm ⇒ «xuất huyết não» ra thẻ xuất huyết TIÊU HOÁ, «đau chân»
# ra thẻ đau NGỰC, «ung thư da» ra thẻ ung thư DẠ dày (phản biện độc lập 21/09). Quy tắc: gõ CÓ dấu ⇒ theo dạng có dấu;
# gõ KHÔNG dấu ⇒ chỉ giữ các từ ở `_GIU_KHI_KHONG_DAU` (thà thiếu độ phủ còn hơn trả sai họ).
_Y_KHOA_CO_DAU = {"co": {"co"}, "nao": {"não"}, "can": {"cân"}, "chan": {"chân"}, "da": {"da", "đa"}, "la": {"lá"}, "thuong": {"thượng"},
                  "thap": {"thấp"}, "doan": {"đoạn"}, "tu": {"tử"}, "gia": {"già"}}
# Từ ghép «đoạn»/«đoán» gấp cùng thành «doan» (khác dấu, không khác chữ cái) — «giai ĐOẠN 3» khác «chẩn ĐOÁN»; «TỬ» trong
# «đột tử»/«tương tác thuốc gây độc TÍNH»… khác «tự»/«từ»; «GIÀ» trong «người già»/«suy tim giai đoạn cuối» khác «đã».
# MỞ RỘNG 22/09/2026 (phản biện độc lập vòng 2): trước chỉ 3 từ (nao/da/thap) được luôn giữ khi gõ KHÔNG DẤU cả câu — quá
# hẹp, «dau chan» (không dấu) vẫn mất «chân» thành từ đệm dù đã bảo vệ dạng CÓ dấu. Nay: TOÀN BỘ từ trong _Y_KHOA_CO_DAU đều
# không bao giờ bị coi là từ đệm dù gõ không dấu — thà mất độ phủ (an toàn) còn hơn để một âm tiết rơi thành mồi nhiễu.
_GIU_KHI_KHONG_DAU = frozenset(_Y_KHOA_CO_DAU)
# Hướng ngược nhau: «hạ kali máu» KHÔNG được ra thẻ «tăng kali máu».
_DOI_NGUOC = {"tang": {"ha", "giam"}, "ha": {"tang"}, "giam": {"tang"}}
_NGUONG_TIEU_DE = 0.5      # khối lượng IDF khớp Ở TIÊU ĐỀ ≥50% tổng — token chỉ khớp ở khuyến cáo không đủ nêu chủ đề
_TU_PHAN_DO = frozenset({"tip", "doan", "stage", "cap", "nhom", "loai", "do", "he", "class"})
# Cặp từ ghép ĐỒNG NGHĨA (khác nửa đầu, cùng nghĩa lâm sàng): «chống đông»≈«kháng đông», «chống viêm»≈«kháng viêm» — một thẻ
# viết theo dạng NÀY vẫn phải trả lời câu hỏi viết theo dạng KIA. Danh sách ĐÓNG, ngắn, chỉ thêm khi chắc chắn đồng nghĩa
# (khác «cường/suy giáp» — đổi nửa đầu ĐỔI HẲN bệnh, không phải đồng nghĩa).
_TU_GHEP_DONG_NGHIA = {("chong", "dong"): ("khang", "dong"), ("chong", "viem"): ("khang", "viem")}
_VIET_TAT_HOA = {"RA": ["viem", "khop", "dang", "thap"]}     # «RA» chỉ nhận khi VIẾT HOA (còn «ra» là từ đệm)


def _la_tu_chung(fold: str, raw: str, co_dau: bool = False) -> bool:
    """`co_dau` = câu hỏi CÓ gõ dấu ở chỗ khác: khi đó một từ gõ TRẦN («co» trong «co giật», «da» trong «viêm da») là chính từ
    trần đó chứ không phải «có»/«đã» gõ thiếu dấu — giữ làm từ nội dung."""
    if fold not in _TU_CHUNG:
        return False
    y_khoa = _Y_KHOA_CO_DAU.get(fold)
    if not y_khoa:
        return True
    if raw in y_khoa and raw != fold:
        return False                       # gõ đúng dạng có dấu của từ y khoa
    if raw == fold:
        if co_dau:
            return False                   # câu có dấu mà từ này trần ⇒ là từ trần thật («co giật»), giữ
        return fold not in _GIU_KHI_KHONG_DAU   # gõ không dấu cả câu: nhập nhằng — chỉ giữ vài từ (an toàn hơn độ phủ)
    return True
_VIET_TAT = {"tha": ["tang", "huyet", "ap"], "dtd": ["dai", "thao", "duong"], "nmct": ["nhoi", "mau", "co", "tim"]}

# PHỦ ĐỊNH (22/09/2026, phản biện độc lập vòng 2): tiêu đề thẻ hay dùng «KHÔNG/CHƯA X» để nêu điều KHÔNG làm hoặc tiêu chí
# LOẠI TRỪ («…khi KHÔNG CÓ HEN», «…KHÔNG lọc máu»), còn câu hỏi tại điểm khám thường mô tả QUẦN THỂ KHẲNG ĐỊNH («đang lọc
# máu», «đã lọc máu»). Bag-of-words cũ không phân biệt được «X» (chủ đề chính) với «không X»/«chưa X» (điều bị loại trừ) —
# thẻ hướng dẫn cho quần thể KHÔNG lọc máu trả lời câu hỏi về quần thể ĐANG lọc máu là SAI QUẦN THỂ ở cấp guideline.
# `_LINK_TU`: từ nối một-bước giữa marker và danh từ thật («không CÓ hen», «chưa CÓ chỉ định») — bỏ qua để tới đúng đích.
_PHU_DINH_MARKER = frozenset({"khong", "chua"})
_LINK_TU = frozenset({"co", "bi", "mac"})


def _phu_dinh_tu_chuoi(seq: list[str]) -> set[str]:
    """Từ đứng ngay sau (hoặc cách một `_LINK_TU`) một marker phủ định trong `seq` — dùng CHUNG cho tiêu đề thẻ lẫn câu hỏi."""
    ra: set[str] = set()
    for i, w_ in enumerate(seq):
        if w_ not in _PHU_DINH_MARKER:
            continue
        if i + 1 >= len(seq):
            continue
        if seq[i + 1] in _LINK_TU and i + 2 < len(seq):
            ra.add(seq[i + 2])
        else:
            ra.add(seq[i + 1])
    return ra


_CHI_MUC: dict = {"khoa": None, "du_lieu": None}


def _dung_chi_muc(cards: list[dict]) -> dict:
    """Chỉ mục toàn kho: token nào xuất hiện ở bao nhiêu thẻ (IDF), và từng thẻ có những từ/cặp từ nào."""
    # Khoá theo NỘI DUNG (id + tiêu đề + độ dài khuyến cáo), không theo id(list): khoá cũ (id, len) trả chỉ mục CŨ khi thẻ bị
    # sửa tại chỗ cùng độ dài, và trả nhầm khi id được tái dùng sau khi danh sách bị giải phóng.
    khoa = hash(tuple((str(c.get("id")), str(c.get("topic")), str(c.get("pico_question")),
                       len(str(c.get("recommendation") or ""))) for c in cards))
    if _CHI_MUC["khoa"] == khoa:
        return _CHI_MUC["du_lieu"]
    df: Counter = Counter()
    df_cap: Counter = Counter()
    df_cap2: Counter = Counter()
    # BIẾN THỂ DẤU toàn kho (22/09/2026): fold → SỐ LẦN mỗi dạng CÓ DẤU xuất hiện («quan» → {quản:65,quan:46,quần:10,quán:6}).
    # Đếm (không chỉ tập hợp) để phân biệt MƠ HỒ THẬT (không dạng nào áp đảo, vd «ho»→hô/hỗ/hở gần đều nhau, «hô» KHÔNG
    # BAO GIỜ đúng nghĩa «ho») khỏi lệch-tần-số-vô-hại (vd «hen»→hen:8/hẹn:2 — «hen» rõ ràng là dạng thường gặp, đo 22/09
    # trên kho thật: chặn nhầm cả «hen»/«gut» sẽ mất độ phủ cho đúng câu hỏi phổ biến nhất) — xem `tra_chi_tiet`.
    bien_the_dau: dict[str, Counter] = {}
    the: list[dict] = []
    for c in cards:
        tieu_de = f"{c.get('topic', '')} {c.get('pico_question', '')}"
        dai = _tach(tieu_de)
        rec = set(_tach(str(c.get("recommendation") or "")))
        the.append({"chinh": set(dai), "cap": set(zip(dai, dai[1:])), "cap2": set(zip(dai, dai[2:])), "rec": rec,
                    "tho": set(_tach_tho(tieu_de)), "rec_tho": set(_tach_tho(str(c.get("recommendation") or ""))),
                    "phu_dinh": _phu_dinh_tu_chuoi(dai), "tieu_de_goc": tieu_de})
        df.update(set(dai) | rec)
        df_cap.update(set(zip(dai, dai[1:])))
        df_cap2.update(set(zip(dai, dai[2:])))
        for goc_tu in _RE_TU.findall(unicodedata.normalize("NFC", tieu_de)):
            bien_the_dau.setdefault(_bo_dau(goc_tu), Counter())[goc_tu.lower()] += 1
    n = max(1, len(cards))
    idf = {t: math.log((n + 1) / (k + 0.5)) + 1.0 for t, k in df.items()}
    du_lieu = {"df": df, "df_cap": df_cap, "df_cap2": df_cap2, "idf": idf, "idf_toi_da": math.log((n + 1) / 0.5) + 1.0,
               "the": the, "bien_the_dau": bien_the_dau}
    _CHI_MUC.update({"khoa": khoa, "du_lieu": du_lieu})
    return du_lieu


def _phan_tich_cau_hoi(cau_hoi: str) -> dict:
    """Phân tích câu hỏi → {'tk': token NỘI DUNG (gấp-dấu, dạng-có-dấu-nếu-cần), 'chuoi': chuỗi gấp-dấu ĐÃ BUNG viết tắt và
    GIỮ từ đệm (để xét «kề nhau» không bắc cầu qua từ đệm), 'dinh_danh': cặp (từ, mã 1 ký tự/số) bắt buộc kề}.

    Dạng có dấu CHỈ giữ cho từ NGẮN (≤4 ký tự gấp dấu) mà người gõ CÓ gõ dấu — đúng chỗ gấp dấu gây nhập nhằng thật:
    «gút»≠«gut», «đau»≠«đầu»≠«dấu», «họng»≠«hồng», «tiền»≠«tiến», «cấp»≠«cáp». Người gõ không dấu (raw None) thì khớp
    mọi dạng. Hai token cùng gấp-dấu nhưng khác dạng có dấu («đau đầu») là HAI token — bản cũ gộp thành một.
    Mã 1 ký tự/số đứng ngay sau một từ nội dung («viêm gan C», «vitamin D», «típ 2») là ĐỊNH DANH — bản cũ bỏ mọi token <2 ký
    tự nên «viêm gan C» ra thẻ viêm gan B; nay định danh phải kề từ đứng trước ở tiêu đề thẻ."""
    # TÁCH TỪ MỘT LẦN trên NFC, rồi suy ba dạng song song từ CÙNG danh sách token — đảm bảo LUÔN cùng độ dài (xem `_tach`).
    cau_hoi = _RE_KY_HIEU_BO.sub(" ", cau_hoi or "")
    hoa = _RE_TU.findall(unicodedata.normalize("NFC", cau_hoi))
    tho = [_DONG_NGHIA_THO.get(t.lower(), t.lower()) for t in hoa]
    dau = [_DONG_NGHIA.get(_bo_dau(t), _bo_dau(t)) for t in hoa]
    chuoi: list[str] = []
    ket: list[tuple[str, str | None]] = []
    dinh_danh: list[tuple[str, str]] = []
    hoa_viet_tat: dict[str, str] = {}   # fold → dạng VIẾT HOA nguyên văn (DM, MI, PSA…) — đòi khớp ĐÚNG DẠNG ở thẻ, không lẫn chữ thường
    co_dau = any(a != b for a, b in zip(tho, dau))
    bo_nhap_nhang = False       # đã bỏ một từ nhập nhằng gõ trần («chan», «can») — nội dung còn lại có thể là nửa câu
    k = 0
    while k < len(dau):
        t = dau[k]
        # cụm cố định (thiếu máu cục bộ / phù hợp / khó chịu) → MỘT token
        gop = next((c for c in _CUM_CO_DINH if tuple(dau[k:k + len(c)]) == c), None)
        if gop:
            tt = "".join(gop)
            chuoi.append(tt)
            ket.append((tt, None))
            k += len(gop)
            continue
        # «dấu hiệu» và «tiền sử» là từ đệm của câu hỏi lâm sàng, không phải chủ đề
        if t == "dau" and k + 1 < len(dau) and dau[k + 1] == "hieu" and tho[k] == "dấu":
            chuoi += ["dau", "hieu"]
            k += 2
            continue
        if t == "tien" and k + 1 < len(dau) and dau[k + 1] == "su":
            chuoi += ["tien", "su"]
            k += 2
            continue
        bung = _VIET_TAT_HOA.get(hoa[k]) or _VIET_TAT.get(t) or [t]
        if len(bung) > 1:
            chuoi += bung
            ket += [(x, None) for x in bung]
            k += 1
            continue
        tt = bung[0]
        chuoi.append(tt)
        if _la_tu_chung(tt, tho[k], co_dau):
            if tt in _Y_KHOA_CO_DAU and tho[k] == tt:
                bo_nhap_nhang = True
            k += 1
            continue
        # TIỀN TỐ «u» (khối u) — như «tiền/hậu»: một CHỮ đứng TRƯỚC danh từ cơ quan, không phải mã đứng SAU. «u gan»/«u phổi»/
        # «u tuyến giáp»/«u não» trước đây bỏ «u» rồi để «gan/phổi/giáp/não» trần khớp bất kỳ thẻ nào chứa từ đó (xơ gan, viêm
        # phổi, suy giáp, nhồi máu não…) — CỜ ĐỎ ngoại trú nghiêm trọng đáng ra phải AN TOÀN hơn (phản biện 22/09).
        if t == "u" and tho[k] == "u" and k + 1 < len(dau) and dau[k + 1] not in _TU_CHUNG:
            dinh_danh.append(("u", dau[k + 1]))
            chuoi.append("u")
            k += 1
            continue
        if len(tt) == 1 or tt.isdigit():
            # mã định danh: chỉ nhận khi ngay trước là một từ NỘI DUNG (không phải từ đệm)
            # raw == fold: «ở» (fold «o») là từ đệm, không phải mã «O»; chỉ mã GÕ ĐÚNG ký tự ASCII mới là định danh
            # chữ cái: sau mọi từ nội dung («viêm gan C»); chữ số: chỉ sau từ phân độ («típ 2», «giai đoạn 3», «nhóm 1») —
            # «đau đầu 3 ngày» không được thành ràng buộc «đau kề 3» (phản biện 22/09)
            sau_tu_phan_do = bool(ket) and ket[-1][0] in _TU_PHAN_DO
            if len(tt) == 1 and tho[k] == tt and ket and len(chuoi) >= 2 and chuoi[-2] == ket[-1][0] \
                    and (not tt.isdigit() or sau_tu_phan_do):
                dinh_danh.append((chuoi[-2], tt))     # chỉ là RÀNG BUỘC kề nhau, KHÔNG vào phủ/IDF (mã 1 ký tự nhiễu điểm)
            k += 1
            continue
        # từ nhập nhằng gõ ĐÚNG ASCII («da» = da, «nao»…) đòi khớp CHÍNH dạng đó ở thẻ: «ung thư da» không được ra «ung thư dạ dày»
        raw = tho[k] if (len(tt) <= 4 and (tho[k] != tt or tt in _Y_KHOA_CO_DAU)) else None
        ket.append((tt, raw))
        # VIẾT TẮT IN HOA (DM, MI, PSA, HA…) — chỉ «RA» có bảng bung riêng; mọi viết-tắt-hoa 2-4 chữ KHÁC đều đi qua đường
        # gấp-dấu thường nên trùng chữ THƯỜNG đồng âm («DM»≈«ĐM», «MI»≈«mì», «PSA»≈«PsA», «HA»≈«hạ»). Ghi lại DẠNG HOA NGUYÊN
        # VĂN; `tra_chi_tiet` đòi khớp ĐÚNG chuỗi hoa đó (phân biệt hoa/thường) trong tiêu đề thẻ trước khi nhận (phản biện 22/09).
        if 2 <= len(hoa[k]) <= 4 and hoa[k].isupper() and hoa[k].isalpha():
            hoa_viet_tat[tt] = hoa[k]
        k += 1
    return {"tk": list(dict.fromkeys(ket)), "chuoi": chuoi, "dinh_danh": list(dict.fromkeys(dinh_danh)),
            "bo_nhap_nhang": bo_nhap_nhang, "so_lan": Counter(t for t, _ in ket), "hoa_viet_tat": hoa_viet_tat,
            "phu_dinh": _phu_dinh_tu_chuoi(dau)}


def _duong_dan_vuot_qua():
    """Nạp `kiem_chung_cu_vuot_qua.doc_bao_cao_vuot_qua` — nguồn sự thật duy nhất về báo cáo «bị vượt qua» hợp lệ."""
    import importlib.util as _ilu
    sp = _ilu.spec_from_file_location("_kcv_tdk", Path(__file__).resolve().parent / "kiem_chung_cu_vuot_qua.py")
    m = _ilu.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.doc_bao_cao_vuot_qua


def _bao_cao_vuot_qua() -> dict:
    """Báo cáo «bị vượt qua» hợp lệ mới nhất. Lỗi nạp ⇒ hop_le=False kèm lý do (KHÔNG âm thầm coi là «không có cờ»)."""
    try:
        return _duong_dan_vuot_qua()(GOC / "EBM-Dashboards" / "derivatives")
    except Exception as exc:  # noqa: BLE001 — cờ phụ; hỏng thì nói ra, không làm hỏng câu trả lời điểm khám
        return {"hop_le": False, "pmids": set(), "da_do": set(), "nguon": None, "ngay": None, "cu": False,
                "ly_do": f"không nạp được bộ đọc báo cáo ({type(exc).__name__})"}


def _vuot_qua_pmids() -> set[str]:
    """Tương thích ngược (tập PMID). Dùng `_bao_cao_vuot_qua()` khi cần biết báo cáo có HỢP LỆ không."""
    return set(_bao_cao_vuot_qua()["pmids"])


NGUONG_PHU = 0.70   # phủ tối thiểu theo khối lượng IDF VÀ theo số token nội dung (nhánh A)


def tra(cau_hoi: str, cards: list[dict], vq: set[str]) -> list[dict]:
    """Tối đa 3 thẻ ĐÃ DUYỆT thật sự đúng chủ đề; rỗng = «chưa giám sát» (độ chính xác trước độ phủ)."""
    ket, _loai = tra_chi_tiet(cau_hoi, cards)
    return ket


def tra_chi_tiet(cau_hoi: str, cards: list[dict]) -> tuple[list[dict], str]:
    """Như `tra` nhưng trả thêm loại kết cục rỗng: 'khop' | 'khong_co' (không thẻ nào ĐẾN GẦN chủ đề) | 'khop_yeu' (có thẻ
    đã qua neo + phủ tiêu đề ≥50% nhưng dưới ngưỡng tin cậy — KHÔNG hiển thị, chỉ để ghi sổ). 'khop_yeu' là CẬN-TRÚNG thật:
    bản trước gán nó cho mọi thẻ chỉ chạm một từ chung ⇒ 83/97 câu ra khop_yeu và khoảng trống thật (viêm họng, ung thư vú…)
    bị loại khỏi số đếm miss."""
    pt = _phan_tich_cau_hoi(cau_hoi)
    tk_nd = pt["tk"]
    if not tk_nd:
        return [], "khong_co"
    if pt["bo_nhap_nhang"] and len(tk_nd) < 2:
        # «dau chan» gõ trần: «chan» (chân) bị bỏ như «chẩn» ⇒ còn mỗi «dau» khớp mọi thẻ đau ngực. Câu chỉ còn MỘT token sau khi
        # bỏ từ nhập nhằng thì không đủ tin cậy để trả thẻ (phản biện 22/09: «đau chân»=khong_co nhưng «dau chan»=3 thẻ đau ngực).
        return [], "khong_co"
    ci = _dung_chi_muc(cards)
    idf, df, n = ci["idf"], ci["df"], max(1, len(cards))
    folds = [t for t, _r in tk_nd]
    # NGOÀI PHẠM VI: từ đặc hiệu ≥4 ký tự KHÔNG có ở BẤT KỲ thẻ nào toàn kho (vd «dengue») ⇒ chủ đề chưa được giám sát.
    if any(len(t) >= 4 and t not in df for t in folds):
        return [], "khong_co"
    def _mo_ho(f: str) -> bool:
        """MƠ HỒ SAU KHI GẤP DẤU: kho có ≥2 dạng CÓ dấu cho fold này mà KHÔNG dạng nào áp đảo rõ rệt (dạng thứ hai chiếm
        ≥30% tổng và ≥3 lần) — «ho»→hô 22/hỗ 12/hở 8 (không áp đảo, VÀ «ho»=cough không hề có mặt) là MƠ HỒ THẬT; «hen»→
        hen 8/hẹn 2 (25%, «hen» áp đảo) KHÔNG mơ hồ — chặn cả hai như nhau sẽ mất độ phủ cho câu hỏi phổ biến nhất."""
        bt = ci["bien_the_dau"].get(f)
        if not bt or len(bt) < 2:
            return False
        top = bt.most_common()
        return top[1][1] >= 3 and top[1][1] / top[0][1] >= 0.3

    # Token ngắn (≤4 ký tự) gõ KHÔNG dấu, KHÔNG lặp lại trong câu hỏi (loại «dau dau»=«đau đầu» viết liền — lặp lại là bằng
    # chứng cụm thật), mà MƠ HỒ theo `_mo_ho` — không biết người hỏi muốn dạng nào. Nếu MỌI token nội dung của câu hỏi đều
    # mơ hồ kiểu này thì không đủ căn cứ trả thẻ nào — một dạng SAI có thể là cờ đỏ thật bị bỏ lỡ («ho ra máu» ra thẻ «HỒ sơ
    # chảy máu» của thuốc kháng đông thay vì «chưa giám sát»). Phản biện độc lập 22/09.
    mo_ho = frozenset(f for f, r in tk_nd
                      if r is None and len(f) <= 4 and pt["so_lan"].get(f, 1) < 2 and _mo_ho(f))
    if mo_ho and set(folds) <= mo_ho:
        return [], "khong_co"
    w = {t: idf.get(t, ci["idf_toi_da"]) for t in folds}          # từ chưa từng thấy (ngắn): nặng nhất và KHÔNG thể khớp
    tong = sum(w.values())
    _neo_uu_tien = [t for t in folds if t not in mo_ho] or folds     # mỏ neo KHÔNG ưu tiên token mơ hồ (nếu còn lựa chọn khác)
    neo = max(_neo_uu_tien, key=lambda t: w[t])                     # token hiếm nhất = mỏ neo chủ đề
    # MỎ NEO QUÁ PHỔ BIẾN SAU KHI ĐÃ LOẠI TOKEN MƠ HỒ: câu hỏi có từ mơ hồ bị loại khỏi vai trò neo (như «ho» trong «ho ra
    # máu»), và token còn lại làm neo cũng QUÁ CHUNG (ngưỡng TUYỆT ĐỐI, đo trên kho thật 1.100 thẻ: «máu»/«tim»/«quan» đều
    # >150 thẻ) — không đủ căn cứ. CHỈ áp khi có mo_ho (không áp đại trà: «đau» một mình cũng >150 thẻ nhưng LÀ triệu chứng
    # chính đáng, không phải hệ quả của việc loại bỏ một token mơ hồ) — phản biện 22/09.
    if mo_ho and df.get(neo, 0) > 150:
        return [], "khong_co"
    dac_hieu = math.log((n + 1) / (0.03 * n + 0.5)) + 1.0           # idf của token có mặt ở ≤3% số thẻ
    tap_nd = set(folds)
    goc = pt["chuoi"]
    # Cặp KỀ NHAU trong câu gốc (đã bung viết tắt, GIỮ từ đệm nên không bắc cầu) mà cả hai vế đều là token nội dung.
    cap_cau = list(dict.fromkeys((a, b) for a, b in zip(goc, goc[1:]) if a in tap_nd and b in tap_nd))
    # Cặp là TỪ GHÉP khi chính cặp đó từng kề nhau ở tiêu đề ≥1 thẻ trong kho («đau đầu», «lợi tiểu», «suy giáp»). Cặp ngang
    # qua ranh giới cụm («chống đông | rung nhĩ», «dài hạn | COPD», «béo phì | semaglutide») không bao giờ kề ở kho nên không
    # bị đòi — nếu đòi thì mọi câu ghép hai cụm đều trượt.
    cap_ghep = [cp for cp in cap_cau if ci["df_cap"].get(cp, 0) >= 1]
    # Cặp cách nhau MỘT từ đệm trong câu hỏi («cai THUỐC lá», «thận NHÂN tạo»): từng gặp cách-một-từ ở kho thì thẻ có cả hai vế
    # phải có chúng trong khoảng ≤2 từ — «cai … lá» rải rác («cải thiện … van ba lá») không phải «cai thuốc lá».
    cap_cach = list(dict.fromkeys((a, b) for a, x, b in zip(goc, goc[1:], goc[2:])
                                  if a in tap_nd and b in tap_nd and x not in tap_nd
                                  and ci["df_cap2"].get((a, b), 0) >= 1))
    diem: list[tuple[float, str, dict, list[str]]] = []
    gan_dat = False
    for c, t in zip(cards, ci["the"]):
        def khop(tk: tuple, tap: set, tap_tho: set) -> bool:
            return tk[0] in tap and (tk[1] is None or tk[1] in tap_tho)
        kc = [tk for tk in tk_nd if khop(tk, t["chinh"], t["tho"])]
        kr = [tk for tk in tk_nd if tk not in kc and khop(tk, t["rec"], t["rec_tho"])]
        # PHỦ ĐỊNH: từ được TIÊU ĐỀ nêu ngay sau «không/chưa» (hoặc cách một từ nối) mà câu hỏi KHÔNG phủ định từ đó — thẻ
        # đang dùng từ này để nói ĐIỀU LOẠI TRỪ/KHÔNG LÀM, không phải chủ đề chính («…khi KHÔNG CÓ HEN» không trả lời câu hỏi
        # về HEN; «KHÔNG lọc máu» không trả lời câu hỏi về người ĐANG lọc máu). Không đối xứng: mệnh đề phủ định hợp lệ
        # của CHÍNH thuốc/can thiệp đang hỏi («KHÔNG dùng aspirin…») không bị mất vì marker đứng ngay trước từ ĐỘNG TỪ
        # («dùng»), không phải trước chủ đề, nên chủ đề vẫn giữ nguyên trong kc (phản biện 22/09).
        kc = [tk for tk in kc if not (tk[0] in t["phu_dinh"] and tk[0] not in pt["phu_dinh"])]
        # VIẾT TẮT IN HOA: đòi khớp ĐÚNG chuỗi hoa trong TIÊU ĐỀ GỐC (case-sensitive, biên từ) — phân biệt «DM» (tiếng Anh)
        # khỏi «ĐM» (động mạch, dùng chữ Đ khác D), «MI» khỏi «mì», «PSA» khỏi «PsA» (khác hoa/thường).
        kc = [tk for tk in kc if tk[0] not in pt["hoa_viet_tat"]
              or re.search(r"\b" + re.escape(pt["hoa_viet_tat"][tk[0]]) + r"\b", t["tieu_de_goc"])]
        if not kc:
            continue
        khoi_tieu_de = sum(w[tk[0]] for tk in kc)
        khoi = khoi_tieu_de + 0.6 * sum(w[tk[0]] for tk in kr)
        so_tk = len(kc) + len(kr)
        # MỎ NEO: token hiếm nhất của câu hỏi PHẢI khớp ở TIÊU ĐỀ thẻ. Đã thử hai cách nới và cả hai làm hỏng độ chính xác:
        # «≥75% mỏ neo» cho «ung thư PHỔI» ra thẻ JAKi (chỉ khớp «ung thư»); «≥3 token nặng» cho «…bảo tồn EMPAGLIFLOZIN» ra
        # thẻ suy tim EF bảo tồn không nói gì về empagliflozin. Thà «chưa giám sát» (bác sĩ tra tay) hơn thẻ sai chủ thể.
        if neo not in {tk[0] for tk in kc}:
            continue
        cov, dem, cov_tieu_de = khoi / tong, so_tk / len(tk_nd), khoi_tieu_de / tong
        if cov_tieu_de < 0.5:
            continue
        gan_dat = True                                              # đến gần: từ đây trở đi rớt = «khớp yếu», không phải «không có»
        # Ba luật «từ ghép»:
        #  (1) cặp kề nhau của câu hỏi mà CẢ HAI vế khớp ở tiêu đề thẻ này VÀ từng là từ ghép ở kho thì phải kề nhau ở tiêu
        #      đề («đái tháo đường … giai đoạn tiền lâm sàng» không phải «tiền đái tháo đường»; «suy tim … cường giáp» không
        #      phải «suy giáp»); vế không khớp thì không đòi («oxy dài hạn COPD»);
        #  (2) tiền tố đổi nghĩa (tiền/hậu) và mã định danh 1 ký tự/số («gan C», «típ 2») luôn phải kề từ đứng cạnh;
        #  (3) thẻ CHƯA khớp từ hiếm nào ở tiêu đề thì ≥1 cặp kề bất kỳ phải trùng — chặn khớp rải rác toàn từ thường.
        kc_fold = {tk[0] for tk in kc}
        # «dinh_danh» nay có CẢ hai chiều: (từ_nội_dung, mã) cho hậu tố («gan», «C») lẫn ("u", từ_cơ_quan) cho tiền tố «u» —
        # chỉ đòi khi vế THUỘC NỘI DUNG (không phải "u"/mã 1 ký tự) có mặt trong kc_fold của thẻ này.
        bat_buoc = [cp for cp in cap_ghep if cp[0] in kc_fold and cp[1] in kc_fold] + \
                   [cp for cp in cap_cau if cp[0] in _TIEN_TO_DOI_NGHIA] + \
                   [cp for cp in pt["dinh_danh"] if cp[0] in kc_fold or cp[1] in kc_fold]
        co_hiem = any(w[tk[0]] >= dac_hieu for tk in kc)              # đã khớp một từ HIẾM ở tiêu đề = tự nó nêu chủ đề
        if any(cp not in t["cap"] for cp in bat_buoc):
            continue
        if any(cp not in t["cap"] and cp not in t["cap2"] for cp in cap_cach if cp[0] in kc_fold and cp[1] in kc_fold):
            continue
        if cap_cau and not co_hiem and not any(cp in t["cap"] for cp in cap_cau):
            continue
        # TỪ GHÉP CHỈ MỘT VẾ: thẻ chỉ mang MỘT nửa của một cặp đã biết là từ ghép trong kho («giáp» của «cường giáp», «phổi»
        # của «viêm phổi»), vế kia cũng có ở câu hỏi nhưng KHÔNG khớp — trước đây chỉ áp cho câu ≤3 token nên câu dài («kháng
        # sinh viêm PHỔI» → thẻ viêm TÚI THỪA chỉ nhờ «kháng sinh» khớp) vẫn lọt (phản biện 22/09). Miễn trừ CHỈ cho cặp có
        # trong `_TU_GHEP_DONG_NGHIA` VÀ thẻ có đủ cặp đồng nghĩa đó ở tiêu đề («KHÁNG đông» trả lời «chống đông»).
        if any((cp[0] in kc_fold) != (cp[1] in kc_fold) and _TU_GHEP_DONG_NGHIA.get(cp) not in t["cap"]
               for cp in cap_ghep):
            continue
        # Câu NGẮN (≤3 token) là một cụm chủ đề: token không khớp ở tiêu đề chỉ được là từ THƯỜNG và thẻ phải khớp một từ HIẾM
        # («đau đầu MIGRAINE» → thẻ migraine không có chữ «đau» vẫn được). «huyết áp THẤP» (không từ hiếm) không được ra thẻ
        # tăng huyết áp; «CƯỜNG giáp» (token không khớp là từ hiếm) không được ra thẻ chỉ có «giáp». Câu dài mới được lệch
        # nhiều hơn (đã có phủ tiêu đề ≥50%).
        if len(tk_nd) <= 3:
            khong_khop = [tk for tk in tk_nd if tk not in kc]
            if khong_khop and (not co_hiem or any(w[tk[0]] >= dac_hieu for tk in khong_khop)):
                continue
        # ĐỐI NGHĨA: câu hỏi «hạ kali» + thẻ chỉ mang «tăng kali» = thẻ ngược chiều.
        nguoc = False
        for d, sj in cap_cau:
            for d2 in _DOI_NGUOC.get(d, ()):
                if (d2, sj) in t["cap"] and (d, sj) not in t["cap"]:
                    nguoc = True
        if nguoc:
            continue
        n_dac_hieu = sum(1 for tk in kc if w[tk[0]] >= dac_hieu)
        # (A) phủ chặt; hoặc (B) khớp ≥2 token ĐẶC HIỆU (hiếm) ở tiêu đề với phủ ≥50% — cho câu dài có chữ thừa
        # («…viêm khớp dạng thấp JAK inhibitor…» vs thẻ «JAK inhibitor: nguy cơ tim mạch…»). Một token hiếm đơn lẻ
        # («gút» + «cấp» không khớp) KHÔNG đủ — đó chính là ca thẻ lạc đề. Cả hai nhánh đòi phủ TIÊU ĐỀ ≥50%.
        dat = ((cov >= NGUONG_PHU and dem >= NGUONG_PHU) or (n_dac_hieu >= 2 and cov >= 0.5)) \
            and cov_tieu_de >= _NGUONG_TIEU_DE
        if not dat:
            continue
        cap_khop = sum(w[a] + w[b] for a, b in cap_cau if (a, b) in t["cap"])
        # Người gõ KHÔNG dấu («hen») khớp mọi biến thể có dấu («hen» ≠ «hẹn») — gấp dấu là cố ý cho người gõ nhanh, nên
        # không dùng làm ngưỡng loại; chỉ xếp thẻ mang ĐÚNG dạng người gõ lên trước thẻ chỉ trùng sau khi gấp dấu.
        chinh_xac = sum(0.3 * w[tk[0]] for tk in kc if tk[1] is None and tk[0] in t["tho"])
        diem.append((khoi + cap_khop + chinh_xac, str(c.get("date_added") or ""), c, sorted({tk[0] for tk in kc + kr})))
    if not diem:
        return [], ("khop_yeu" if gan_dat else "khong_co")
    diem.sort(key=lambda x: x[1], reverse=True)     # cùng điểm ⇒ thẻ cập nhật GẦN đây hơn trước (sắp ổn định)
    diem.sort(key=lambda x: -x[0])
    ra: list[dict] = []
    da_thay: dict = {}
    for _d, _ngay, c, khop_tk in diem:
        _src = c.get("source") if isinstance(c.get("source"), dict) else {}
        khoa = (_bo_dau(str(c.get("recommendation") or ""))[:400], str(_src.get("pmid") or ""))
        if khoa in da_thay:
            if da_thay[khoa]["decision"] != c.get("decision"):
                da_thay[khoa]["_xung_dot"] = True       # cùng khuyến cáo, KHÁC quyết định: không tự chọn bản «mới hơn»
            continue
        ban = dict(c, _khop=khop_tk, _xung_dot=False)
        da_thay[khoa] = ban
        ra.append(ban)
        if len(ra) == 3:
            break
    return ra, "khop"


def _ghi_nhat_ky_tac_dong(ket: list[dict], giay: float, loai: str = "khong_co") -> None:
    """VÒNG ĐO TÁC ĐỘNG (Tầng-2, 16/08/2026 — bác sĩ duyệt) — KHÔNG-PII TỪ GỐC.

    Chỉ ghi TRƯỜNG PHÁI SINH: id thẻ khớp / cờ miss / thời điểm / độ trễ.
    CÂU HỎI THÔ TUYỆT ĐỐI KHÔNG LƯU ở đây — câu hỏi tại điểm khám có thể chứa
    chi tiết người bệnh; log tác động không được là nơi PII rò vào. (Riêng
    nhánh miss vẫn ghi câu hỏi vào watchlist-signal như LÔ 5 đã thiết kế —
    đó là kênh khác, phục vụ bổ sung giám sát, bác sĩ đã duyệt trước.)
    Ghi hỏng không được làm hỏng câu trả lời điểm khám — nuốt lỗi CÓ CHỦ ĐÍCH."""
    try:
        p = STATE / "nhat-ky-tac-dong.jsonl"
        p.parent.mkdir(exist_ok=True)
        import datetime as _dt
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "luc": _dt.datetime.now().isoformat(timespec="seconds"),
                "khop": [c.get("id") for c in ket] if ket else [],
                "miss": not ket,
                # 'khop_yeu' = có thẻ chạm chủ đề nhưng dưới ngưỡng ⇒ có thể là câu hỏi lệch từ khoá chứ KHÔNG phải khoảng
                # trống giám sát; người tiêu thụ sổ (do_tac_dong · tu_de_xuat_viec) không được đếm chung với miss THẬT.
                "loai": loai if not ket else "khop",
                "ms": round(giay * 1000),
            }, ensure_ascii=False) + "\n")
    except OSError:
        pass


def in_quick_view(cau_hoi: str, ket: list[dict], vq: set[str], giay: float, loai: str = "khong_co",
                  vq_info: dict | None = None, ghi: bool = True) -> None:
    if ghi:                                   # --demo KHÔNG ghi: câu mô phỏng không phải lượt tra thật, làm nhiễu số đo tác động
        _ghi_nhat_ky_tac_dong(ket, giay, loai)
    print(f"\n❓ {cau_hoi}   ({giay*1000:.0f} ms)")
    if vq_info is not None and not vq_info.get("hop_le"):
        print(f"  ⚪ Cờ «có bản tổng hợp mới hơn» KHÔNG ĐO ĐƯỢC ({vq_info.get('ly_do')}) — 'chưa biết', không phải 'không có'."
              + (f" Chỉ hiện các cờ DƯƠNG TÍNH từ báo cáo cũ {vq_info.get('ngay')}." if vq_info.get("cu") else ""))
    elif vq_info is not None and vq_info.get("ngay"):
        print(f"  (cờ «bản tổng hợp mới hơn» theo báo cáo dò ngày {vq_info['ngay']} — {vq_info.get('nguon')})")
    if not ket:
        print("  ⛔ CHỦ ĐỀ NÀY CHƯA ĐƯỢC GIÁM SÁT (chưa có thẻ ĐÃ DUYỆT khớp đủ chủ đề) — hệ KHÔNG sinh câu trả lời thay thế.")
        if loai == "khop_yeu":
            print("     (Có thẻ GẦN chủ đề nhưng chưa đủ tin cậy nên KHÔNG hiển thị — thử hỏi ngắn hơn/đúng từ khoá thẻ, "
                  "hoặc tra tay.)")
        print("     Tra tay: PubMed/guideline hội chuyên khoa · phác đồ BYT (kcb.vn).")
        # Ghi tín hiệu bổ sung watchlist. `loai` tách «không có thẻ nào chạm» khỏi «có thẻ chạm nhưng dưới ngưỡng» để
        # người đọc sổ không lẫn ca thiếu-phủ thật với ca hỏi lệch từ khoá.
        if not ghi:
            print("     (chế độ --demo: không ghi sổ ứng viên watchlist)")
            return
        st = STATE / "cau-hoi-chua-giam-sat.jsonl"
        try:
            st.parent.mkdir(exist_ok=True)
            # Câu hỏi tại điểm khám có thể chứa định danh người bệnh (email, số điện thoại, dãy ≥9 số): câu nghi PII KHÔNG được
            # lưu nguyên văn — chỉ lưu dấu «đã bỏ» để vòng phản hồi vẫn đếm được lượt miss.
            nghi_pii = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|\d{9,}|\(?\b0\d{1,2}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b|\b(?:\+?84)[\s.-]?\d{2,3}[\s.-]?\d{3}[\s.-]?\d{3,4}\b|\b\d{3}[\s.-]\d{3}[\s.-]\d{3,4}\b", cau_hoi or ""))
            with st.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"cau_hoi": "[đã bỏ — nghi chứa định danh người bệnh]" if nghi_pii else cau_hoi,
                                    "luc": date.today().isoformat(), "loai": loai}, ensure_ascii=False) + "\n")
            print("     → đã ghi câu hỏi làm ứng viên BỔ SUNG WATCHLIST (vòng phản hồi LÔ 5).")
        except OSError:
            print("     (không ghi được sổ ứng viên watchlist — không ảnh hưởng câu trả lời)")
        return
    for c in ket:
        src = c.get("source") if isinstance(c.get("source"), dict) else {}
        pm = src.get("pmid") or ""
        co = " 🟠 CÓ BẢN TỔNG HỢP MỚI HƠN CHƯA RÀ (quét quý)" if pm in vq else ""
        # «Chưa dò» ≠ «không có cờ»: báo cáo quý chỉ dò PMID của thẻ decision='apply' (đo 21/09: 163/657 PMID) — các thẻ còn lại
        # im lặng nghĩa là CHƯA ĐƯỢC HỎI, không phải sạch.
        if pm and not co and vq_info is not None and vq_info.get("hop_le") and pm not in (vq_info.get("da_do") or set()):
            co = " ⚪ CHƯA DÒ «bản tổng hợp mới hơn» (quét quý chỉ dò thẻ 'apply')"
        rec = re.sub(r"\s+", " ", str(c.get("recommendation") or ""))[:220]
        tieu_de = re.sub(r"\s+", " ", str(c.get("topic") or ""))[:110]
        print(f"  ▶ [{str(c.get('decision') or '?').upper()}] {tieu_de}")
        print(f"    Khuyến cáo: {rec}{co}")
        if c.get("_khop"):
            print(f"    (khớp theo: {', '.join(c['_khop'])})")
        if c.get("_xung_dot"):
            print("    ⚠️ Có thẻ KHÁC quyết định cho cùng khuyến cáo — đối chiếu EBM-Dashboards/quyet-dinh-da-duyet.json "
                  "và mau-thuan-da-duyet.json trước khi dựa vào.")
        print(f"    Nguồn: {src.get('agency') or src.get('title','')[:40]} · "
              f"PMID {pm or '—'} / DOI {src.get('doi') or '—'} · "
              f"thẻ cập nhật {str(c.get('date_added') or '?')[:10]} · mức {c.get('gradeLevel')}")
        goi = GOC / "implementation" / f"{c.get('id')}.md"
        if goi.exists():
            print(f"    📋 Gói triển khai: implementation/{c.get('id')}.md (cờ đỏ · nhóm đặc biệt · tái khám)")
    print("    ⚠️ Cờ đỏ/nhóm đặc biệt: xem gói triển khai hoặc dashboard chủ đề. "
          "Cần bác sĩ kiểm chứng — quyết định cuối thuộc bác sĩ điều trị.")


def main() -> int:
    t0 = time.perf_counter()
    d = json.loads(LEDGER.read_text(encoding="utf-8"))
    cards = [c for c in d["evidence_cards"]
             if c.get("provenance") in NGUON_DUYET
             and str(c.get("verification_status", "")).startswith("đã xác minh")]
    vq_info = _bao_cao_vuot_qua()
    vq = set(vq_info["pmids"])
    t_nap = time.perf_counter() - t0

    if "--demo" in sys.argv:
        cau = ["COPD đợt cấp nhiều lần có nên bộ ba ICS LABA LAMA",
               "viêm khớp dạng thấp JAK inhibitor người cao tuổi nguy cơ tim mạch",
               "sàng lọc lao tiềm ẩn trước thuốc sinh học",
               "người cao tuổi đa thuốc benzodiazepine Beers",
               "sốt xuất huyết dengue ngoại trú dấu hiệu cảnh báo"]
        print(f"NẠP {len(cards)} thẻ đã duyệt trong {t_nap*1000:.0f} ms (ngoại tuyến)")
        for q in cau:
            t1 = time.perf_counter()
            ket, loai = tra_chi_tiet(q, cards)
            in_quick_view(q, ket, vq, time.perf_counter() - t1, loai, vq_info, ghi=False)
        return 0
    la = [a for a in sys.argv[1:] if a.startswith("--") and a != "--demo"]
    if la:
        print(f"Cờ không hỗ trợ: {' '.join(la)} — chỉ có --demo. (Không ghi nhật ký; câu hỏi phải đặt trong dấu nháy.)")
        return 2
    q = " ".join(a for a in sys.argv[1:] if a != "--demo").strip()
    if not q:
        print("Cách dùng: tra_diem_kham.py \"<câu hỏi>\" | --demo")
        return 2
    t1 = time.perf_counter()
    ket, loai = tra_chi_tiet(q, cards)
    in_quick_view(q, ket, vq, time.perf_counter() - t1, loai, vq_info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
