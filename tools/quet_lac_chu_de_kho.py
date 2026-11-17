#!/usr/bin/env python3
"""Quét MỘT LẦN toàn kho dashboard tìm mục LẠC CHỦ ĐỀ — bản mới nhất của mỗi chủ đề, qua Batch API (rẻ 50%).

Bác sĩ duyệt 17/11/2026 (ước ~2,3 USD qua Batch: 115 chủ đề, 3.519 mục). Cổng kiểm lạc chủ đề chỉ chấm gói xuất
MỚI; kho cũ chưa từng được chấm — mà loại lỗi này từng chỉ phát hiện được bằng đọc tay (dashboard Tim mạch 06/2026
có 8 bài lạc). Kết quả là DANH SÁCH ĐỂ BÁC SĨ RÀ: không tự gỡ mục, không sửa dashboard, Cổng A/B nguyên vẹn.

Dùng lại TRỌN prompt và bộ parse của cổng (`check_topic_relevance`) — một nguồn sự thật. Khác cổng ở đường gửi:
Batch API không nhận `fallbacks`, nên model từ chối ⇒ dashboard đó ghi «error», không đoán.

  python3 tools/quet_lac_chu_de_kho.py              chạy khô: danh sách + ước chi phí (không gọi API)
  python3 tools/quet_lac_chu_de_kho.py --ap-dung    gửi batch, chờ xong, ghi báo cáo
  python3 tools/quet_lac_chu_de_kho.py --tiep ID    lượt trước gián đoạn: lấy kết quả batch đã gửi, KHÔNG gửi lại

Báo cáo: EBM-Dashboards/derivatives/QUET-LAC-CHU-DE_<ngày>.md (+ .json). Trạng thái batch: state/quet-lac-chu-de.json
(để --tiep không phải gửi lại, tức không trả tiền hai lần). Mã thoát: 0 xong · 1 có dashboard không chấm được ·
2 lỗi vận hành. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
CTR_REL = Path("sync/skills/cap-nhat-chung-cu-y-khoa/tools/check_topic_relevance.py")
MODEL = "claude-sonnet-5-5"
# Giá Batch = 50% giá Sonnet 5.5 ($2/$10 mỗi triệu token) — tài liệu Claude API, đọc 17/11/2026.
GIA_BATCH = {"vao": 1.00, "ra": 5.00}
# Đơn giá đo thật 17/11 (chỉ để ƯỚC khi chạy khô): ~307 token vào/mục, ~70 token ra/mục ở effort low.
TOKEN_MUC = {"vao": 307, "ra": 70}
_TEN = re.compile(r"^(WebDashboard_.+?)_(\d{8})\.html$")


def nap_cong(goc: Path):
    """Nạp `check_topic_relevance` (cạnh nó là `verify_dashboard` mà nó import)."""
    duong = goc / CTR_REL
    if str(duong.parent) not in sys.path:
        sys.path.insert(0, str(duong.parent))
    spec = importlib.util.spec_from_file_location("_ctr_quet_kho", duong)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def chon_ban_moi_nhat(thu_muc: Path) -> list[Path]:
    """Mỗi chủ đề (tên trước `_YYYYMMDD.html`) giữ đúng bản ngày lớn nhất — bản cũ là phiên bản đã được thay."""
    moi: dict[str, tuple[str, Path]] = {}
    for f in thu_muc.glob("WebDashboard_*.html"):
        m = _TEN.match(f.name)
        khoa, ngay = (m.group(1), m.group(2)) if m else (f.stem, "00000000")
        if khoa not in moi or ngay > moi[khoa][0]:
            moi[khoa] = (ngay, f)
    return sorted(p for _, p in moi.values())


def dung_yeu_cau(C, f: Path) -> dict | None:
    """Prompt của cổng cho một dashboard; None nếu không có chủ đề hoặc không có mục (không có gì để chấm)."""
    try:
        db = C.extract_data_block(f.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None
    if not db:
        return None
    chu_de = C._extract_meta_question(db)
    muc = C._items_for_prompt(db)
    if not chu_de or not muc:
        return None
    return {"tep": f.name, "chu_de": chu_de, "muc": muc, "prompt": C.build_prompt(chu_de, muc)}


def tham_so(C, prompt: str) -> dict:
    """Đúng tham số của cổng (max_tokens, effort «low») — trừ `fallbacks`, mà Batch API không nhận."""
    return {"model": MODEL, "max_tokens": C.MAX_TOKENS_MAC_DINH, "output_config": {"effort": "low"},
            "messages": [{"role": "user", "content": prompt}]}


def cham_mot(C, yc: dict, kq: dict) -> dict:
    """Biến kết quả batch của MỘT dashboard thành phán quyết; mọi hỏng hóc ⇒ «error» kèm lý do, không đoán."""
    ra = {"tep": yc["tep"], "chu_de": yc["chu_de"], "so_muc": len(yc["muc"])}
    if kq.get("loai") != "succeeded":
        return {**ra, "status": "error", "ly_do": f"batch: {kq.get('loai')} {kq.get('loi', '')}"[:200]}
    if kq.get("stop_reason") == "max_tokens":
        return {**ra, "status": "error", "ly_do": "CẮT CỤT ở max_tokens — không chấm"}
    if kq.get("stop_reason") == "refusal":
        return {**ra, "status": "error", "ly_do": f"model từ chối (nhóm {kq.get('nhom') or 'không rõ'})"}
    try:
        v = C.parse_verdicts(kq.get("text", ""))
    except C.TopicCheckError as e:
        return {**ra, "status": "error", "ly_do": str(e)[:200]}
    tieu_de = {m["id"]: m["title"] for m in yc["muc"]}
    def _ds(muc):
        return [{"id": i, "title": tieu_de.get(i, ""), "reason": x.get("reason", "")}
                for i, x in v.items() if x.get("verdict") == muc]
    return {**ra, "status": "ok", "off_topic": _ds("off_topic"), "uncertain": _ds("uncertain")}


def doc_ket_qua(client, batch_id: str) -> dict:
    """custom_id → kết quả gọn (không giữ đối tượng SDK)."""
    ket = {}
    for r in client.messages.batches.results(batch_id):
        loai = r.result.type
        if loai == "succeeded":
            m = r.result.message
            u = getattr(m, "usage", None)
            ket[r.custom_id] = {
                "loai": loai, "stop_reason": m.stop_reason,
                "nhom": getattr(getattr(m, "stop_details", None), "category", None),
                "text": "".join(getattr(b, "text", "") or "" for b in m.content),
                "vao": getattr(u, "input_tokens", 0) or 0, "ra": getattr(u, "output_tokens", 0) or 0}
        else:
            loi = getattr(getattr(r.result, "error", None), "type", "") or ""
            ket[r.custom_id] = {"loai": loai, "loi": str(loi)}
    return ket


def cho_xong(client, batch_id: str, nghi: float = 30.0, tran_giay: float = 6 * 3600, ngu=time.sleep) -> bool:
    bat_dau = time.monotonic()
    while True:
        b = client.messages.batches.retrieve(batch_id)
        if b.processing_status == "ended":
            return True
        rc = b.request_counts
        print(f"  … batch {batch_id}: đang xử lý {rc.processing}, xong {rc.succeeded}, lỗi {rc.errored}", flush=True)
        if time.monotonic() - bat_dau > tran_giay:
            return False
        ngu(nghi)


def ghi_bao_cao(cham: list, goc: Path, batch_id: str, chi_phi: float, ngay: str) -> tuple[Path, Path]:
    thu_muc = goc / "EBM-Dashboards" / "derivatives"
    thu_muc.mkdir(parents=True, exist_ok=True)
    md, js = thu_muc / f"QUET-LAC-CHU-DE_{ngay}.md", thu_muc / f"QUET-LAC-CHU-DE_{ngay}.json"
    ok = [c for c in cham if c["status"] == "ok"]
    loi = [c for c in cham if c["status"] != "ok"]
    co_viec = [c for c in ok if c["off_topic"] or c["uncertain"]]
    n_lac = sum(len(c["off_topic"]) for c in ok)
    n_kc = sum(len(c["uncertain"]) for c in ok)
    d = [f"# Quét lạc chủ đề toàn kho — {ngay}", "",
         f"Bản mới nhất của mỗi chủ đề: **{len(cham)} dashboard**, {sum(c['so_muc'] for c in cham):,} mục · "
         f"chấm được {len(ok)} · không chấm được {len(loi)} · batch `{batch_id}` · chi phí thật ~{chi_phi:.2f} USD.", "",
         f"**{n_lac} mục NGHI LẠC CHỦ ĐỀ** và **{n_kc} mục KHÔNG CHẮC** trên {len(co_viec)} dashboard.", "",
         "> LLM (Claude Sonnet 5.5) chấm từ tiêu đề + hành động của mục — có sai số. Đây là danh sách ĐỂ BÁC SĨ RÀ:",
         "> không mục nào bị gỡ, không dashboard nào bị sửa. Cần bác sĩ kiểm chứng.", ""]
    for c in sorted(co_viec, key=lambda x: (-len(x["off_topic"]), -len(x["uncertain"]), x["tep"])):
        d += [f"## {c['tep']}", f"Chủ đề khai báo: *{c['chu_de']}* · {c['so_muc']} mục", "",
              "| Mức | ID | Tiêu đề | Lý do (LLM) |", "|---|---|---|---|"]
        for muc, nhan in (("off_topic", "🔴 lạc"), ("uncertain", "🟡 không chắc")):
            for x in c[muc]:
                t = x["title"].replace("|", "/")[:140]
                r = x["reason"].replace("|", "/")[:160]
                d.append(f"| {nhan} | {x['id']} | {t} | {r} |")
        d.append("")
    if loi:
        d += ["## Không chấm được", ""] + [f"- {c['tep']}: {c['ly_do']}" for c in loi] + [""]
    md.write_text("\n".join(d), encoding="utf-8", newline="\n")
    js.write_text(json.dumps({"ngay": ngay, "batch_id": batch_id, "chi_phi_usd": chi_phi, "model": MODEL,
                              "ket_qua": cham}, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return md, js


NGUON_NHAT_KY = "quet_lac_chu_de_kho"


def ghi_suc_khoe(trang_thai: str, ly_do: str = "", so_muc: int = 0) -> None:
    """Ghi sức khoẻ lượt gọi cho giác quan hòm việc (17/11/2026) — qua `tools/nhat_ky_api_claude.py`, nguồn
    `quet_lac_chu_de_kho`. Thiếu mô-đun ghi (cây cũ) thì bỏ qua: nhật ký không bao giờ được làm vỡ lượt quét."""
    try:
        spec = importlib.util.spec_from_file_location("_nhat_ky_api_claude", Path(__file__).resolve().parent /
                                                      "nhat_ky_api_claude.py")
        nk = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nk)
    except (OSError, ImportError, AttributeError):
        return
    nk.ghi(trang_thai, ly_do, so_muc, NGUON_NHAT_KY)


def main(argv: list[str] | None = None, client=None, ngu=time.sleep) -> int:
    ap = argparse.ArgumentParser(description="Quét lạc chủ đề toàn kho dashboard (Batch API)")
    ap.add_argument("--ap-dung", action="store_true", help="gửi batch thật (TỐN TIỀN — chạy khô trước)")
    ap.add_argument("--tiep", default=None, help="lấy kết quả batch đã gửi (không gửi lại)")
    ap.add_argument("--goc", default=None, help="thư mục gốc (mặc định: repo này)")
    ap.add_argument("--nghi", type=float, default=30.0, help="giây giữa hai lần hỏi trạng thái batch")
    a = ap.parse_args(argv)
    goc = Path(a.goc).resolve() if a.goc else REPO
    kho = goc / "EBM-Dashboards"
    if not kho.is_dir() or not (goc / CTR_REL).exists():
        print(f"⛔ Thiếu {kho.as_posix()} hoặc {CTR_REL.as_posix()} — không có gì để quét.")
        return 2
    C = nap_cong(goc)
    yeu_cau = [y for y in (dung_yeu_cau(C, f) for f in chon_ban_moi_nhat(kho)) if y]
    so_muc = sum(len(y["muc"]) for y in yeu_cau)
    uoc = (so_muc * TOKEN_MUC["vao"] * GIA_BATCH["vao"] + so_muc * TOKEN_MUC["ra"] * GIA_BATCH["ra"]) / 1e6
    print(f"QUÉT LẠC CHỦ ĐỀ TOÀN KHO — {len(yeu_cau)} dashboard (bản mới nhất mỗi chủ đề), {so_muc:,} mục · "
          f"ước ~{uoc:.2f} USD qua Batch API")
    if not (a.ap_dung or a.tiep):
        print("Chạy khô — chưa gọi API. Gửi thật: --ap-dung. Cần bác sĩ kiểm chứng.")
        return 0
    ma_theo_id = {f"d{i:03d}": y for i, y in enumerate(yeu_cau, 1)}
    trang_thai = goc / "state" / "quet-lac-chu-de.json"
    if client is None:
        # Kiểm khoá TRƯỚC, nhập SDK SAU và trong try — CI 17/11: máy không cài SDK thì `import anthropic` đứng trước
        # văng ModuleNotFoundError thay vì dừng gọn (máy bác sĩ có SDK nên chốt cục bộ không thấy).
        khoa = os.getenv("ANTHROPIC_API_KEY", "") or C._khoa_tu_kho()
        if not khoa:
            print("⛔ Thiếu ANTHROPIC_API_KEY (biến môi trường lẫn kho bí mật).")
            ghi_suc_khoe("skipped", "Thiếu ANTHROPIC_API_KEY (biến môi trường lẫn kho bí mật)")
            return 2
        try:
            import anthropic
        except ImportError:
            print("⛔ Chưa cài SDK: pip install anthropic")
            return 2
        client = anthropic.Anthropic(api_key=khoa)
    if a.tiep:
        batch_id = a.tiep
        try:
            luu = json.loads(trang_thai.read_text(encoding="utf-8"))
            if luu.get("batch_id") == batch_id:
                ma_theo_id = {k: next((y for y in yeu_cau if y["tep"] == v), None) for k, v in luu["tep_theo_id"].items()}
                ma_theo_id = {k: y for k, y in ma_theo_id.items() if y}
        except (OSError, ValueError, KeyError):
            pass
    else:
        try:
            b = client.messages.batches.create(requests=[{"custom_id": k, "params": tham_so(C, y["prompt"])}
                                                         for k, y in ma_theo_id.items()])
        except Exception as e:  # noqa: BLE001 — 401/403/429/mạng: dừng gọn, ghi cho hòm việc, không văng traceback
            return _dung_loi_api("gửi batch", e)
        batch_id = b.id
        trang_thai.parent.mkdir(parents=True, exist_ok=True)
        trang_thai.write_text(json.dumps({"batch_id": batch_id, "luc": _dt.datetime.now().isoformat(timespec="seconds"),
                                          "tep_theo_id": {k: y["tep"] for k, y in ma_theo_id.items()}},
                                         ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        print(f"  Đã gửi batch {batch_id} ({len(ma_theo_id)} yêu cầu). Gián đoạn thì chạy lại: --tiep {batch_id}")
    try:
        xong = cho_xong(client, batch_id, nghi=a.nghi, ngu=ngu)
        ket = doc_ket_qua(client, batch_id) if xong else {}
    except Exception as e:  # noqa: BLE001 — cùng lý do: lỗi kênh API giữa chừng; batch đã gửi thì --tiep lấy lại
        return _dung_loi_api(f"theo dõi batch {batch_id} (chạy lại: --tiep {batch_id})", e)
    if not xong:
        print(f"⛔ Batch chưa xong sau trần chờ — chạy lại sau: --tiep {batch_id}")
        return 2
    if any(k.get("loai") == "succeeded" for k in ket.values()):
        ghi_suc_khoe("ok", "", sum(len(y["muc"]) for y in ma_theo_id.values()))
    else:
        loai_loi = sorted({str(k.get("loi") or k.get("loai") or "?") for k in ket.values()}) or ["không có kết quả"]
        ghi_suc_khoe("error", "Batch không có yêu cầu nào thành công: " + ", ".join(loai_loi))
    cham = [cham_mot(C, y, ket.get(k, {"loai": "khong_co_ket_qua"})) for k, y in ma_theo_id.items()]
    chi_phi = sum(k.get("vao", 0) * GIA_BATCH["vao"] + k.get("ra", 0) * GIA_BATCH["ra"] for k in ket.values()) / 1e6
    md, _ = ghi_bao_cao(cham, goc, batch_id, chi_phi, _dt.date.today().strftime("%Y%m%d"))
    loi = sum(1 for c in cham if c["status"] != "ok")
    n_lac = sum(len(c.get("off_topic", [])) for c in cham)
    n_kc = sum(len(c.get("uncertain", [])) for c in cham)
    print(f"  Xong: {len(cham) - loi}/{len(cham)} chấm được · {n_lac} mục nghi lạc · {n_kc} mục không chắc · "
          f"chi phí thật ~{chi_phi:.2f} USD")
    print(f"  Báo cáo: {md.as_posix()}")
    print("Cần bác sĩ kiểm chứng.")
    return 1 if loi else 0


def _dung_loi_api(buoc: str, e: Exception) -> int:
    ly_do = f"Gọi Batch API thất bại khi {buoc}: {type(e).__name__}: {str(e)[:150]}"
    print(f"⛔ {ly_do}")
    ghi_suc_khoe("error", ly_do)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
