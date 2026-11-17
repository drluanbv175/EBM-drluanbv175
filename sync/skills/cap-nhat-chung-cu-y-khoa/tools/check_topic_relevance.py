#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_topic_relevance.py — Kiểm mỗi item trong Web Dashboard EBM có THỰC SỰ thuộc chủ đề/
chuyên khoa đã khai báo hay không, bằng cách gọi Claude API chấm điểm.

BỐI CẢNH — lỗ hổng thật đã phát hiện: `verify_dashboard.py` (cổng liêm chính hiện có) chỉ xác
minh TÍNH TOÀN VẸN KỸ THUẬT (PMID có thật, đã dịch tiếng Việt, có disclaimer) — KHÔNG xác minh
NỘI DUNG mục có đúng thuộc chủ đề dashboard hay không. Dashboard "Tim mạch" từng lọt 8/20 mục
thực chất về sản khoa, nhi khoa, hô hấp, thận học — chỉ phát hiện được bằng cách ĐỌC TAY từng
mục, không có công cụ tự động nào bắt được. Module này lấp khoảng trống đó.

NGUYÊN TẮC AN TOÀN:
- CHỈ CẢNH BÁO, KHÔNG TỰ Ý XÓA/SỬA mục nào — phân loại LLM có sai số, quyết định cuối luôn
  thuộc về bác sĩ (giống mọi cổng khác trong hệ thống này).
- 3 mức phán quyết (in_topic/off_topic/uncertain) thay vì nhị phân — "uncertain" khi LLM không
  đủ tin cậy để kết luận, tránh ép buộc phân loại sai vào 1 trong 2 cực.
- Gộp TOÀN BỘ item của 1 dashboard vào MỘT lượt gọi API (batch) — vừa rẻ vừa tránh nhiễu ngữ
  cảnh khi chấm từng item riêng lẻ (mất khả năng so sánh chéo giữa các mục).
- Không có ANTHROPIC_API_KEY -> bỏ qua ÊM (status='skipped'), KHÔNG chặn pipeline hiện có
  (đúng khuôn mẫu claude_llm() trong app/integrations/ambient_scribe.py).

Cách dùng:
    python3 check_topic_relevance.py <dashboard.html>
    python3 check_topic_relevance.py <dashboard.html> --json   # in JSON thô để tool khác đọc
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_dashboard import extract_data_block, field, split_items  # noqa: E402

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong.
# Vá 14/08/2026: hai tool này bị bỏ sót vì chốt BH11 cũ chỉ liệt cứng 4 tên tool.
import sys as _sys_utf8
for _s in (_sys_utf8.stdout, _sys_utf8.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

VALID_VERDICTS = {"in_topic", "off_topic", "uncertain"}


class TopicCheckError(Exception):
    pass


class KetQuaApiHong(TopicCheckError):
    """API ĐÃ trả lời nhưng kết quả KHÔNG dùng được: cắt cụt ở max_tokens, model từ chối, JSON hỏng.

    Khác «chưa cấu hình» (thiếu khoá/SDK — `TopicCheckError` thường ⇒ status «skipped»): đây là HỎNG
    ⇒ status «error», để cảm biến ⑦r của hòm việc báo bác sĩ. VÁ 17/11/2026: trước đây JSON hỏng cũng
    quy về «skipped», mà ⑦r chỉ báo «skipped» khi lý do nhắc tên khoá ⇒ cổng trơ mà hòm việc im lặng.
    Là lớp con của `TopicCheckError` nên mọi chỗ bắt lớp cha vẫn bắt được."""


def _extract_meta_question(data_block: str) -> Optional[str]:
    """Lấy meta.question (câu hỏi/chủ đề khai báo của dashboard) từ khối DATA."""
    m = re.search(r"\bquestion\s*:\s*['\"]([^'\"]*)['\"]", data_block)
    return m.group(1) if m else None


def _items_for_prompt(data_block: str) -> List[Dict[str, str]]:
    """Trích (id, title, action) từng item — đủ ngữ cảnh để chấm chủ đề mà không cần toàn văn."""
    out = []
    for chunk in split_items(data_block):
        iid = field(chunk, "id")
        title = field(chunk, "title")
        action = field(chunk, "action")
        if iid and title:
            out.append({"id": iid, "title": title, "action": action or ""})
    return out


def build_prompt(dashboard_topic: str, items: List[Dict[str, str]]) -> str:
    lines = [
        "Bạn đang kiểm tra xem các mục chứng cứ y khoa dưới đây có THỰC SỰ thuộc "
        "chủ đề/chuyên khoa đã khai báo của dashboard hay không.",
        "",
        f'Chủ đề dashboard đã khai báo: "{dashboard_topic}"',
        "",
        "Với MỖI mục, đánh giá theo đúng 1 trong 3 mức:",
        '- "in_topic": nội dung CHÍNH của bài liên quan trực tiếp đến chủ đề trên (kể cả '
        "khi có góc nhìn liên chuyên khoa thật sự, ví dụ bài về biến chứng tim mạch của "
        "bệnh thận vẫn tính in_topic cho chủ đề Tim mạch nếu nội dung THỰC SỰ bàn về mối "
        "liên hệ đó).",
        '- "off_topic": nội dung CHÍNH không liên quan đến chủ đề trên (ví dụ bài về thai '
        "kỳ/nhi khoa/hô hấp/phương pháp luận guideline nói chung xuất hiện trong dashboard "
        "Tim mạch mà không có liên hệ tim mạch rõ ràng trong nội dung).",
        '- "uncertain": tiêu đề/tóm tắt không đủ thông tin để kết luận chắc chắn.',
        "",
        "Các mục:",
    ]
    for it in items:
        extra = f" — {it['action']}" if it["action"] else ""
        lines.append(f"[{it['id']}] {it['title']}{extra}")
    lines += [
        "",
        "CHỈ trả lời bằng JSON hợp lệ theo đúng định dạng sau, không thêm chữ nào khác, "
        "không thêm markdown code fence:",
        '{"ITEM-01": {"verdict": "in_topic", "reason": "một câu ngắn giải thích"}, ...}',
    ]
    return "\n".join(lines)


# Kho bí mật của bác sĩ nằm NGOÀI OneDrive (doctrine §5). Để thành hằng số để bộ kiểm trỏ sang
# tệp giả, không bao giờ đụng kho thật.
KHO_BI_MAT = os.path.join(os.path.expanduser("~"), ".ebm-secrets", "medical-ebm-automation.env")
# Bản chụp đường THẬT lúc nạp — kiểm thử vá KHO_BI_MAT/NHAT_KY_API sang tệp tạm thì không đụng các hằng này.
_KHO_THAT = KHO_BI_MAT


def _cham_trang_thai_that(duong: str, that: str) -> bool:
    """True khi đang chạy DƯỚI PYTEST mà sắp đọc/ghi đúng tệp THẬT ở thư mục nhà ⇒ phải từ chối.

    VÌ SAO (17/11/2026): `tools/test_xuat_goi_cap_nhat_workflow_20260904.py` chạy `xuat_goi_cap_nhat.py
    --online` thật; từ khi `--online` kéo theo `--check-topic`, tiến trình con ghi đè nhật ký sức khoẻ API
    THẬT (bản `ok` lúc 13:30 bị thay bằng «skipped — không có mục»), và nếu dashboard mẫu có mục thì sẽ gọi
    API THẬT bằng khoá THẬT — mỗi lượt CI/kiểm trên máy bác sĩ đều tốn tiền. Cùng luật CLAUDE.md §4 cho khoá
    ký cổng G: dưới pytest, trỏ vào kho khoá thật thì từ chối. `PYTEST_CURRENT_TEST` được tiến trình con kế
    thừa nên chặn cả đường gián tiếp. Chủ động đo thật thì đặt EBM_KIEM_API_THAT=1."""
    if not os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("EBM_KIEM_API_THAT") == "1":
        return False
    try:
        return os.path.realpath(duong) == os.path.realpath(that)
    except (OSError, ValueError):
        return True   # không phân định được ⇒ thận trọng: coi là tệp thật


def _khoa_tu_kho(ten: str = "ANTHROPIC_API_KEY", kho: Optional[str] = None) -> str:
    """Đọc MỘT khoá từ kho bí mật khi biến môi trường vắng mặt.

    VÌ SAO (17/11/2026): tool này trước chỉ đọc `os.getenv`, nên khoá cất trong kho KHÔNG tới được
    nó — lượt lịch, hook và mọi lượt chạy không qua shell có `export` sẽ lặng lẽ bỏ qua kiểm chủ đề,
    đúng kiểu âm tính giả mà doctrine cấm. Thứ tự lấy khoá theo §5: biến môi trường OS → kho secrets.
    Không dùng python-dotenv để khỏi thêm phụ thuộc cho một tool skill đi kèm bản phát hành.
    Mọi lỗi đọc đều nuốt: thiếu khoá là «bỏ qua êm», không bao giờ làm hỏng dây chuyền xuất gói.
    KHÔNG BAO GIỜ in giá trị khoá ra đâu cả.

    DÒNG CUỐI THẮNG (sửa 17/11/2026 sau một lượt hỏng thật): kho được ghi kiểu NỐI THÊM, nên khi
    bác sĩ ghi lại khoá mới mà dòng cũ còn đó, lấy dòng ĐẦU sẽ dùng đúng cái khoá hỏng vừa thay —
    im lặng và rất khó đoán. `load_dotenv` mà repo y khoa dùng cũng để giá trị sau đè giá trị
    trước, nên lấy dòng cuối là khớp hành vi đã có chứ không phải luật mới."""
    duong = kho or KHO_BI_MAT
    if _cham_trang_thai_that(duong, _KHO_THAT):
        return ""          # dưới pytest không bao giờ đọc kho khoá THẬT
    gia_tri = ""
    try:
        with open(duong, "r", encoding="utf-8", errors="replace") as fh:
            for dong in fh:
                dong = dong.strip()
                if not dong or dong.startswith("#") or "=" not in dong:
                    continue
                k, _, v = dong.partition("=")
                if k.strip() == ten:
                    v = v.strip().strip("'\"")
                    if v:
                        gia_tri = v          # không return sớm: dòng sau đè dòng trước
    except OSError:
        pass
    if gia_tri:
        return gia_tri
    return ""


# Model nhận `output_config.effort` và `fallbacks: "default"` (beta dự phòng khi model từ chối) — theo
# tài liệu Claude API 11/2026. Model khác (đặt qua TOPIC_CHECK_MODEL) gọi như cũ, không thêm tham số mới,
# để khỏi lỗi 400 với model không nhận chúng.
_MODEL_HIEN_HANH = {"claude-sonnet-5-5", "claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-fable-5-2"}
BETA_DU_PHONG = "server-side-fallback-2026-07-01"
MAX_TOKENS_MAC_DINH = 16000


def call_claude(prompt: str, *, model: Optional[str] = None, max_tokens: int = MAX_TOKENS_MAC_DINH) -> str:
    """Gọi Claude API. Đúng khuôn mẫu claude_llm() trong app/integrations/ambient_scribe.py.

    VÁ 17/11/2026 — max_tokens 2000 → 16000 và effort «low». Trên Sonnet 5.5 thinking LUÔN bật và ăn
    CHUNG ngân sách max_tokens với JSON phán quyết. Đo thật dashboard Suy tim 83 mục: stop_reason=
    max_tokens ở 2000/2000 token, JSON cụt ⇒ cổng trơ đúng trên dashboard tổng hợp lớn nhất (116/303
    dashboard có ≥ 40 mục). Phân loại là việc effort «low» làm tốt; token trần không tính tiền — chỉ
    token thật sinh ra mới tính. Kiểm stop_reason TRƯỚC khi đọc nội dung: cắt cụt hay từ chối ⇒
    `KetQuaApiHong` (status «error»), không bao giờ đưa nửa JSON cho bộ parse.
    """
    key = os.getenv("ANTHROPIC_API_KEY", "") or _khoa_tu_kho()
    if not key:
        raise TopicCheckError(
            "Thiếu ANTHROPIC_API_KEY — đặt trong biến môi trường hoặc kho bí mật ngoài OneDrive "
            "để bật kiểm chủ đề."
        )
    try:
        import anthropic  # type: ignore
    except ImportError as exc:  # pragma: no cover - phụ thuộc môi trường
        raise TopicCheckError(
            f"Chưa cài SDK `anthropic` trong trình Python {sys.executable} — cài bằng "
            f"`{sys.executable} -m pip install anthropic` hoặc chạy bằng Python của ~/.ebm-venv."
        ) from exc
    mdl = model or os.getenv("TOPIC_CHECK_MODEL", "claude-sonnet-5-5")
    client = anthropic.Anthropic(api_key=key)
    if mdl in _MODEL_HIEN_HANH:
        resp = client.beta.messages.create(  # pragma: no cover - cần mạng + key
            model=mdl, max_tokens=max_tokens,
            output_config={"effort": os.getenv("TOPIC_CHECK_EFFORT", "low")},
            betas=[BETA_DU_PHONG], fallbacks="default",
            messages=[{"role": "user", "content": prompt}],
        )
    else:
        resp = client.messages.create(  # pragma: no cover - cần mạng + key
            model=mdl, max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
    ly_do_dung = getattr(resp, "stop_reason", None)
    if ly_do_dung == "max_tokens":
        raise KetQuaApiHong(
            f"Kết quả bị CẮT CỤT ở max_tokens={max_tokens} — JSON phán quyết không trọn, không chấm.")
    if ly_do_dung == "refusal":
        nhom = getattr(getattr(resp, "stop_details", None), "category", None)
        raise KetQuaApiHong(f"Model từ chối chấm (refusal, nhóm {nhom or 'không rõ'}), kể cả sau dự phòng.")
    return "".join(getattr(b, "text", "") or "" for b in resp.content)


def parse_verdicts(raw_response: str) -> Dict[str, Dict[str, str]]:
    """Parse JSON trả về từ model. Ném TopicCheckError nếu không phải JSON hợp lệ hoặc verdict
    lạ — KHÔNG đoán mò/tự sửa để tránh diễn giải sai ý model."""
    text = raw_response.strip()
    # Model đôi khi vẫn bọc ```json...``` dù đã dặn không làm vậy -> gỡ an toàn trước khi parse.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KetQuaApiHong(f"Model không trả JSON hợp lệ: {exc}. Raw: {text[:200]}") from exc
    if not isinstance(parsed, dict):
        raise KetQuaApiHong(f"Model trả JSON không phải object: {type(parsed)}")
    for iid, v in parsed.items():
        if not isinstance(v, dict) or v.get("verdict") not in VALID_VERDICTS:
            raise KetQuaApiHong(f"Verdict không hợp lệ cho {iid}: {v!r}")
    return parsed


def _cham_chu_de(html_path: str) -> Dict:
    """Điểm vào chính: đọc dashboard, gọi Claude chấm chủ đề, trả kết quả có cấu trúc.

    Trả về dict {"status": "ok"|"skipped"|"error", ...}. KHÔNG BAO GIỜ raise ra ngoài —
    lỗi/thiếu cấu hình đều trả về status rõ ràng để caller (vd verify_dashboard.py) tự quyết
    định có chặn hay chỉ cảnh báo.
    """
    html = Path(html_path).read_text(encoding="utf-8")
    data_block = extract_data_block(html)
    if not data_block:
        return {"status": "error", "message": "Không tìm thấy khối DATA."}

    topic = _extract_meta_question(data_block)
    if not topic:
        return {"status": "error", "message": "Không tìm thấy meta.question (chủ đề dashboard)."}

    items = _items_for_prompt(data_block)
    if not items:
        return {"status": "skipped", "message": "Không có item nào để chấm."}

    prompt = build_prompt(topic, items)
    try:
        raw = call_claude(prompt)
        verdicts = parse_verdicts(raw)
    except KetQuaApiHong as exc:
        # API trả lời mà kết quả hỏng ⇒ «error» để ⑦r báo bác sĩ (bắt TRƯỚC lớp cha).
        return {"status": "error", "message": str(exc)}
    except TopicCheckError as exc:
        return {"status": "skipped", "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        # Lỗi TỪ SDK/mạng (401 khoá sai, hết hạn mức, timeout, DNS…) trước đây LỌT ra ngoài: chạy
        # tay thì văng traceback, chạy trong cổng thì rơi vào `except Exception` của verify_dashboard
        # nên thành cảnh báo khó đọc. Đo thật 17/11/2026: khoá sai ⇒ `AuthenticationError 401`.
        # Nay quy về một mối «error» như mọi nhánh khác. KHÔNG nuốt im: cổng vẫn in cảnh báo.
        # `Exception` không bắt KeyboardInterrupt/SystemExit nên Ctrl-C vẫn dừng được.
        return {"status": "error", "message": f"{type(exc).__name__}: {str(exc)[:200]}"}

    off_topic = [
        {"id": iid, "title": next((it["title"] for it in items if it["id"] == iid), ""),
         "reason": v.get("reason", "")}
        for iid, v in verdicts.items() if v.get("verdict") == "off_topic"
    ]
    uncertain = [iid for iid, v in verdicts.items() if v.get("verdict") == "uncertain"]

    return {
        "status": "ok",
        "topic": topic,
        "total_items": len(items),
        "off_topic": off_topic,
        "uncertain": uncertain,
        "verdicts": verdicts,
    }


# Nhật ký SỨC KHOẺ lượt gọi API — nằm ngoài repo, ngoài OneDrive. KHÔNG BAO GIỜ chứa khoá, chỉ
# chứa thời điểm, trạng thái và lý do đã cắt ngắn.
NHAT_KY_API = os.path.join(os.path.expanduser("~"), ".ebm-api-claude.json")
_NK_THAT = NHAT_KY_API   # bản chụp đường THẬT (xem _cham_trang_thai_that)


def ghi_nhat_ky_api(kq: Dict, tep: Optional[str] = None) -> None:
    """Ghi kết quả lượt gọi gần nhất (theo từng công cụ — `_gop_theo_nguon`) để hòm việc biết API còn sống.

    VÌ SAO (17/11/2026, bác sĩ: «khi API hết hạn báo lại tôi»): khoá Anthropic không hết hạn theo
    ngày — nó chết vì HẾT TÍN DỤNG, BỊ THU HỒI (401) hay VƯỢT HẠN MỨC (429), và chỉ lộ ra đúng lúc
    gọi. Thăm dò định kỳ thì tốn tiền vô ích, nên ta ghi lại kết quả của những lượt gọi mà dây
    chuyền VỐN ĐÃ thực hiện — chi phí thêm bằng 0. Giác quan `giac_quan_api_claude` đọc tệp này.
    Lỗi ghi đều nuốt: nhật ký hỏng không bao giờ được làm hỏng lượt xuất gói của bác sĩ."""
    duong = tep or NHAT_KY_API
    if _cham_trang_thai_that(duong, _NK_THAT):
        return             # dưới pytest không bao giờ ghi đè nhật ký THẬT
    try:
        import datetime as _dt
        ban_ghi = {
            "luc": _dt.datetime.now().isoformat(timespec="seconds"),
            "trang_thai": str(kq.get("status") or "?"),
            "ly_do": str(kq.get("message") or "")[:200],
            "so_muc": int(kq.get("total_items") or 0),
            "nguon": NGUON_NHAT_KY,
        }
        # «» là tên cũ của chính cổng này (bản trước không ghi «nguon») ⇒ bỏ, không để một lượt cũ nằm lại mãi.
        _ghi_nguyen_tu(duong, _gop_theo_nguon(duong, ban_ghi, bo_nguon_cu=("",)))
    except (OSError, TypeError, ValueError):
        pass


NGUON_NHAT_KY = "check_topic_relevance"
_TRUONG_LUOT = ("luc", "trang_thai", "ly_do", "so_muc")


def _gop_theo_nguon(duong: str, ban_ghi: Dict, bo_nguon_cu: tuple = ()) -> Dict:
    """Trộn lượt mới vào nhật ký đã có: giữ lượt GẦN NHẤT CỦA TỪNG CÔNG CỤ trong khoá «theo_nguon».

    VÌ SAO (17/11/2026, bác sĩ duyệt «mục 2»): tệp trước chỉ giữ MỘT lượt — 8 công cụ ghi chung một ô nên lượt
    sau xoá lượt trước. Công cụ A lỗi 401 rồi công cụ B chạy ổn ngay sau ⇒ lỗi của A biến mất trước khi hòm việc
    kịp đọc. Khoá cấp cao (luc · trang_thai · ly_do · so_muc · nguon) VẪN là lượt gần nhất, để bản đọc cũ (máy chưa
    cập nhật) đọc như trước. Nhật ký kiểu cũ (chưa có «theo_nguon») được giữ làm mục của nguồn đã ghi nó.
    Khuôn này có ở BA nơi ghi — cổng này · tools/nhat_ky_api_claude.py · cầu nối y khoa tools/api_claude_nc.py
    (skill và repo y khoa phải tự đứng được, không nhập chung một mô-đun) — sửa một nơi phải sửa cả ba."""
    try:
        with open(duong, "r", encoding="utf-8") as fh:
            cu = json.load(fh)
    except (OSError, ValueError):
        cu = None
    theo: Dict[str, Dict] = {}
    if isinstance(cu, dict):
        tn = cu.get("theo_nguon")
        if isinstance(tn, dict):
            theo = {str(k): v for k, v in tn.items() if isinstance(v, dict)}
        elif cu.get("trang_thai"):
            theo[str(cu.get("nguon") or "")] = {k: cu.get(k) for k in _TRUONG_LUOT}
    for k in bo_nguon_cu:
        theo.pop(k, None)
    theo[str(ban_ghi.get("nguon") or "")] = {k: ban_ghi.get(k) for k in _TRUONG_LUOT}
    return dict(ban_ghi, theo_nguon=theo)


def _ghi_nguyen_tu(duong: str, du_lieu: Dict) -> None:
    """Ghi qua tệp tạm rồi đổi tên: hai công cụ ghi cùng lúc không bao giờ để lại tệp cụt nửa chừng."""
    tam = f"{duong}.{os.getpid()}.tmp"
    try:
        with open(tam, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(du_lieu, fh, ensure_ascii=False, indent=1)
        os.replace(tam, duong)
    finally:
        if os.path.exists(tam):
            try:
                os.remove(tam)
            except OSError:
                pass


# ─────────────── chạy bằng Python của venv khi trình hiện tại thiếu SDK ───────────────
# VÌ SAO (17/11/2026, bác sĩ duyệt «mục 1»): dây chuyền xuất gói được gọi bằng `python3 tools/xuat_goi_cap_nhat.py`
# (skill cap-nhat-chung-cu-y-khoa, tác vụ lịch goi-duyet-tuan-ebm, CLAUDE.md) và cổng này chạy TRONG tiến trình đó.
# `python3` mặc định của máy bác sĩ KHÔNG có SDK `anthropic` — chỉ ~/.ebm-venv có. Đo thật: cổng trả «skipped — Chưa
# cài SDK», hòm việc im lặng, luật kiểm lạc chủ đề TẮT CÂM dù khoá vẫn tốt. Nay trình hiện tại thiếu SDK mà venv chuẩn
# có Python ⇒ chấm bằng tiến trình con chạy CHÍNH tệp này bằng Python của venv (đường Mac/Linux lẫn Windows).
THU_MUC_VENV = os.path.join(os.path.expanduser("~"), ".ebm-venv")
CO_QUA_VENV = "EBM_KIEM_CHU_DE_QUA_VENV"   # tiến trình con mang cờ này ⇒ không chuyển tiếp lần nữa (chống đệ quy)
GIAY_CHO_VENV = 900                         # một lượt chấm dashboard lớn (~80 mục) mất 1–3 phút


def _co_sdk() -> bool:
    """True khi trình Python ĐANG CHẠY nhập được `anthropic` (không nhập thật — chỉ dò)."""
    try:
        return importlib.util.find_spec("anthropic") is not None
    except (ImportError, ValueError):
        return False


def _python_venv() -> Optional[str]:
    """Đường Python của venv chuẩn (Mac/Linux `bin/python`, Windows `Scripts/python.exe`); None khi vắng."""
    for duong in (os.path.join(THU_MUC_VENV, "bin", "python"), os.path.join(THU_MUC_VENV, "Scripts", "python.exe")):
        if os.path.isfile(duong):
            return duong
    return None


def _dang_trong_venv() -> bool:
    """So THƯ MỤC venv (sys.prefix), không so tệp thực thi: Python của venv thường là symlink tới chính `python3`
    hệ thống, so realpath tệp thực thi sẽ tưởng «đang ở venv» và không bao giờ chuyển tiếp."""
    try:
        return os.path.realpath(sys.prefix) == os.path.realpath(THU_MUC_VENV)
    except (OSError, ValueError):
        return False


def _duoi_pytest() -> bool:
    """Bộ kiểm KHÔNG BAO GIỜ được chấm thật qua đường vòng venv (venv của máy bác sĩ có SDK + kho khoá thật ⇒ gọi
    API thật, tốn tiền). Cùng rào BH181; chủ động đo thật thì đặt EBM_KIEM_API_THAT=1."""
    return bool(os.environ.get("PYTEST_CURRENT_TEST")) and os.environ.get("EBM_KIEM_API_THAT") != "1"


def _cham_qua_venv(html_path: str) -> Optional[Dict]:
    """Chấm bằng Python của ~/.ebm-venv. None = không chuyển tiếp được (đã ở venv / đang là tiến trình con / dưới
    pytest / không có venv) ⇒ người gọi chấm tại chỗ như cũ, thiếu SDK thì ra «skipped» nêu rõ trình Python.
    Tiến trình con lỗi, quá giờ hay không trả JSON đọc được ⇒ «error» (không bao giờ im lặng thành «skipped»)."""
    if os.environ.get(CO_QUA_VENV) == "1" or _dang_trong_venv() or _duoi_pytest():
        return None
    py = _python_venv()
    if not py:
        return None
    env = dict(os.environ)
    env[CO_QUA_VENV] = "1"
    env["PYTHONIOENCODING"] = "utf-8"   # Windows: stdout tiến trình con mặc định cp1252, JSON tiếng Việt sẽ vỡ
    try:
        r = subprocess.run(
            [py, os.path.abspath(__file__), os.path.abspath(html_path), "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=GIAY_CHO_VENV, env=env,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"status": "error",
                "message": f"Chấm chủ đề bằng Python của venv ({py}) thất bại: {type(exc).__name__}: {exc}"[:300]}
    ra = r.stdout or ""
    kq = None
    for doan in (ra, ra[ra.find("{"):] if "{" in ra else ""):
        try:
            kq = json.loads(doan)
            break
        except ValueError:
            continue
    if not isinstance(kq, dict) or kq.get("status") not in ("ok", "skipped", "error"):
        cuoi = ((r.stderr or "") + ra).strip()[-160:]
        return {"status": "error",
                "message": f"Python của venv ({py}) không trả kết quả đọc được (mã {r.returncode}): {cuoi}"}
    kq["qua_venv"] = py
    return kq


def check_dashboard_topic_relevance(html_path: str) -> Dict:
    """Vỏ bọc của `_cham_chu_de`: chấm xong thì GHI LẠI sức khoẻ lượt gọi rồi mới trả kết quả.

    Tách vỏ thay vì sửa sáu chỗ `return` bên trong — mọi nhánh (ok/skipped/error) đều được ghi,
    không nhánh nào lọt. Trình Python đang chạy thiếu SDK ⇒ chấm bằng Python của ~/.ebm-venv
    (`_cham_qua_venv`); kết quả trả về cùng khuôn, thêm khoá `qua_venv` nêu trình đã dùng."""
    kq = _cham_qua_venv(html_path) if not _co_sdk() else None
    if kq is None:
        kq = _cham_chu_de(html_path)
    ghi_nhat_ky_api(kq)
    return kq


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dashboard", help="Đường dẫn file dashboard .html")
    ap.add_argument("--json", action="store_true", help="In JSON thô thay vì báo cáo đọc được")
    args = ap.parse_args()

    result = check_dashboard_topic_relevance(args.dashboard)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] != "error" else 1

    print("================================================================")
    print("KIỂM ĐỘ LIÊN QUAN CHỦ ĐỀ — (bổ sung cho verify_dashboard.py)")
    print("================================================================")
    if result["status"] == "skipped":
        print(f"  ⏭  BỎ QUA: {result['message']}")
        return 0
    if result["status"] == "error":
        print(f"  ⛔ LỖI: {result['message']}")
        return 1

    if result.get("qua_venv"):
        print(f"  (chấm bằng Python của venv: {result['qua_venv']} — trình đang chạy thiếu SDK anthropic)")
    print(f"  Chủ đề dashboard: {result['topic']}")
    print(f"  Tổng số mục đã chấm: {result['total_items']}")
    if result["off_topic"]:
        print(f"  ⚠ {len(result['off_topic'])} mục CÓ THỂ lạc chủ đề (bác sĩ rà lại, KHÔNG tự động gỡ):")
        for it in result["off_topic"]:
            print(f"     - [{it['id']}] {it['title'][:70]}")
            print(f"       Lý do model nêu: {it['reason']}")
    else:
        print("  ✓ Không mục nào bị nghi lạc chủ đề.")
    if result["uncertain"]:
        print(f"  ⚠ {len(result['uncertain'])} mục KHÔNG chắc chắn: {', '.join(result['uncertain'])}")
    print("----------------------------------------------------------------")
    print("LƯU Ý: đây là gợi ý từ LLM, có sai số — không thay thế thẩm định của bác sĩ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
