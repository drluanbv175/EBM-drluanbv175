#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANARY ĐẦU–CUỐI: gài lỗi ĐÃ BIẾT vào một gói giả, đòi dây chuyền phải bắt được.

VÌ SAO CÓ (14/08/2026)
======================
Mọi chốt hồi quy hiện có (BH01–BH42) kiểm **chữ trong file**: luật có mặt chưa, doctrine
nhắc chưa, ba bản khớp chưa. **Không chốt nào chứng minh dây chuyền THẬT SỰ BẮT ĐƯỢC một
lỗi khi chạy.** Khoảng cách đó không phải lý thuyết — riêng ngày 14/08 đã tìm được ba ca
mà luật CÓ MẶT nhưng KHÔNG BAO GIỜ chạy tới:

  • `verify_dashboard.py` `return` sớm khi thiếu `DATA.standards` ⇒ toàn bộ luật an toàn
    cấp item chưa từng chạy trên 47 dashboard (che 73 mục nguy hiểm).
  • Bộ lọc `[ptyp]` ở khâu tìm ⇒ 22 chủ đề báo "0 ứng viên" trong khi thực có chứng cứ mới.
  • 8 công cụ chứng cứ tồn tại mà 0 agent gọi ⇒ với dây chuyền hằng ngày chúng không tồn tại.

Canary này gài lỗi vào một gói GIẢ rồi đòi dây chuyền phải bắt. Lỗi nào không bị bắt là
một lỗ hổng THẬT ở đúng chỗ đó — không phải chuyện câu chữ.

GIỚI HẠN CÓ CHỦ Ý — đọc kỹ để không nói quá
============================================
Canary kiểm **dây chuyền CÔNG CỤ**, KHÔNG kiểm hành vi của agent LLM lúc chạy thật. Nó
chứng minh "cổng bắt được lỗi nếu gói đi qua cổng", KHÔNG chứng minh "agent đã gọi cổng".
Vế sau chỉ chứng minh được bằng cách quan sát phiên thật, và doctrine + BH39/40/41 là thứ
làm cho vế sau khả dĩ — không thay thế được nhau.

Dữ liệu hoàn toàn GIẢ, không PII, không đụng kho thật (chạy trong thư mục tạm).

Dùng:
    python tools/thu_dau_cuoi_chung_cu.py
    python tools/thu_dau_cuoi_chung_cu.py --chi-tiet

Mã thoát: 0 = mọi lỗi gài đều bị bắt · 1 = có lỗ hổng thật.
"""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"

# PMID 30267080 — Choi và cs., JAMA Oncology. Đáp án BIẾT TRƯỚC: đã rút (retract-and-replace),
# và đáng giá làm ca thử vì CẢ PubMed LẪN Europe PMC đều trả 'ok'; chỉ nền Retraction Watch
# ngoại tuyến bắt được. Nếu canary này xanh bằng đường mạng thì nó chưa kiểm đúng thứ cần kiểm.
PMID_DA_RUT = "30267080"

_KHUNG = """<!doctype html><html><body><script>
const DATA = {{{standards}
  meta: {{ question: "Gói CANARY — dữ liệu giả để thử dây chuyền", updated: "2026-08-14" }},
  summary: {{ conclusion: [], doNow: [], dontDo: [], redFlags: [] }},
  items: [
{items}
  ]
}};
</script>
<p>Cần bác sĩ kiểm chứng</p>
</body></html>"""

_STANDARDS_TRONG = ("\n  standards: { provenanceUnknown: true, "
                    'provenanceUnknownLyDo: "gói canary, không có provenance thật" },')


def _item(iid, pmid, design, grade, decision, gs="nguồn thử", extra=""):
    return (f'    {{ id: "{iid}", title: "Mục thử {iid}", source: "Canary", '
            f'dateVersion: "2026", pmid: "{pmid}", design: "{design}", '
            f'gradeLevel: "{grade}", decision: "{decision}", gradeSource: "{gs}"{extra}, '
            f'action: "Không áp dụng — dữ liệu giả", vn: "Không áp dụng" }},')


def _nap(duong_dan: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m          # bắt buộc trước exec — xem BH40/_nap
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description="Canary đầu-cuối cho dây chuyền chứng cứ")
    ap.add_argument("--chi-tiet", action="store_true", help="in thông điệp cổng trả về")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi mọi lỗi gài đều bị bắt (dùng cho hook)")
    a = ap.parse_args()

    vd = _nap(DASH / "tools" / "verify_dashboard.py", "vd_canary")
    dk = _nap(REPO / "tools" / "dang_ky_chu_de.py", "dk_canary")
    ss = _nap(DASH / "tools" / "surveillance_scan.py", "ss_canary")

    tmp = Path(tempfile.mkdtemp(prefix="canary-chungcu-"))
    ket: list[tuple[str, bool, str]] = []
    try:
        # ── Gói A: gài 3 lỗi cổng ────────────────────────────────────────────────
        items_a = "\n".join([
            # (1a) apply + gradeLevel='na' trên nghiên cứu THƯỜNG (RCT) → chặn, và thông
            #      điệp đúng phải là "hạ xuống consider", KHÔNG phải "thiếu normativeBasis"
            #      (RCT không phải văn bản quy phạm nên không có đường miễn trừ nào).
            _item("ITEM-01", "11111111", "RCT", "na", "apply"),
            # (1b) apply + 'na' trên GUIDELINE, chưa khai normativeBasis → chặn ĐÚNG bằng
            #      thông điệp thiếu normativeBasis. Hai nhánh này dễ lẫn: bản đầu của chính
            #      canary đã kỳ vọng nhầm nhánh, và cổng mới là bên đúng.
            _item("ITEM-04", "44444444", "Guideline", "na", "apply"),
            # (2) apply chỉ dựa Consensus → phải CHẶN
            _item("ITEM-02", "22222222", "Consensus", "high", "apply", extra=', gradeBy: "X"'),
            # (3) gradeLevel khác 'na' mà KHÔNG khai gradeBy → phải CẢNH BÁO
            _item("ITEM-03", "33333333", "RCT", "high", "consider"),
        ])
        a_path = tmp / "WebDashboard_EBM_VanDeCuThe_Canary_20260101.html"
        a_path.write_text(_KHUNG.format(standards=_STANDARDS_TRONG, items=items_a),
                          encoding="utf-8")

        # ── Gói B: cùng chủ đề, NGƯỢC quyết định trên cùng PMID → phải phát hiện ──
        items_b = "\n".join([_item("ITEM-01", "11111111", "RCT", "high", "notyet",
                                   extra=', gradeBy: "Cochrane (GRADE)"')])
        b_path = tmp / "WebDashboard_EBM_VanDeCuThe_Canary_20260202.html"
        b_path.write_text(_KHUNG.format(standards=_STANDARDS_TRONG, items=items_b),
                          encoding="utf-8")

        # ── Chạy cổng thật trên gói A ────────────────────────────────────────────
        blk = vd.extract_data_block(a_path.read_text(encoding="utf-8"))
        errors, warns, _oks = vd.strict_source_checks(blk, vd.split_items(blk))
        gop_e, gop_w = " | ".join(errors), " | ".join(warns)

        ket.append(("apply + 'na' trên RCT → CHẶN, thông điệp 'hạ xuống consider'",
                    "ITEM-01" in gop_e and "hạ xuống" in gop_e, gop_e[:130]))
        ket.append(("apply + 'na' trên GUIDELINE chưa khai basis → CHẶN đúng 'normativeBasis'",
                    "ITEM-04" in gop_e and "normativeBasis" in gop_e, gop_e[:130]))
        ket.append(("apply chỉ dựa Consensus → CHẶN",
                    "ITEM-02" in gop_e and "Consensus" in gop_e, gop_e[:110]))
        ket.append(("gradeLevel khác 'na' không khai gradeBy → CẢNH BÁO",
                    "ITEM-03" in gop_w and "gradeBy" in gop_w, gop_w[:110]))
        # Luật an toàn cấp item VẪN phải chạy dù gói khai provenanceUnknown (BH35)
        ket.append(("khai provenanceUnknown KHÔNG tắt luật an toàn cấp item",
                    "ITEM-01" in gop_e, "miễn trừ provenance đã nuốt luật item"))

        # ── Dò mâu thuẫn giữa hai bản cùng chủ đề ────────────────────────────────
        v, _lat, theo_goc = dk.quet_kho(tmp)
        mt, _ = dk.tim_mau_thuan(v, theo_goc)
        so_mt = sum(len(m["khac"]) for m in mt)
        ket.append(("hai bản cùng chủ đề nói ngược nhau → PHÁT HIỆN",
                    so_mt >= 1, f"bắt được {so_mt} mục"))

        # ── Rút bài NGAY LÚC NHẬN (offline, không cần mạng) ──────────────────────
        uv = [ss.Candidate(pmid=PMID_DA_RUT, publication_date="2019",
                           title="ca thử đã rút", url="u")]
        gan = ss.gan_do_tin_cay(uv)
        tt = gan[0].rut_bai if gan else "?"
        ket.append((f"ứng viên PMID {PMID_DA_RUT} (đã rút) → BẮT ở khâu nhận",
                    tt in ("retracted", "expression_of_concern"), f"trạng thái={tt}"))
        # ── HỢP ĐỒNG ITEM (LÔ 2): máy tự APPROVED / tự gán mức / số không nguồn ─────
        hd = _nap(REPO / "tools" / "kiem_hop_dong_item.py", "hd_canary")
        xau = {"id": "EBM-2026-9999", "topic": "t", "status": "APPROVED",
               "decision": "apply",
               "source": {"type": "RCT", "title": "x", "year": 2026, "pmid": "1",
                          "resolved": True},
               "certainty": {"reported_by_source": False, "level": "high"}}
        vi_pham = hd.kiem(xau)
        ket.append(("hợp đồng item: máy tự APPROVED + tự gán mức → BẮT",
                    sum(1 for v in vi_pham if "I4" in v or "I2" in v) >= 2,
                    " | ".join(vi_pham)[:110]))

        # ── KHOÁ GHI (LÔ 1): giành lần 2 phải FAIL, không lặng lẽ chạy chồng ───────
        ok1, _ = ss.gianh_khoa()
        ok2, _ly = ss.gianh_khoa()
        ss.tra_khoa()
        ket.append(("khoá quét: tiến trình thứ hai bị chặn rõ ràng",
                    ok1 and not ok2, f"lần1={ok1} lần2={ok2}"))

        # và KHÔNG được mặc định 'ok' cho PMID không tra được
        gan2 = ss.gan_do_tin_cay([ss.Candidate(pmid="99999999", publication_date="2026",
                                               title="không tồn tại", url="u")])
        ket.append(("PMID không tra được → 'chua_kiem', KHÔNG mặc định 'ok'",
                    bool(gan2) and gan2[0].rut_bai != "ok", f"trạng thái={gan2[0].rut_bai if gan2 else '?'}"))

        # ── MỞ RỘNG TẦNG-1 (16/08, bác sĩ duyệt): 2 làn mới + phân xử + ed1 ──────
        # (11) làn preprint (fetch_json TIÊM — offline) phải TỰ KHAI chưa-bình-duyệt
        pp = ss.search_preprint_lane("x", 45, 5, fetch_json=lambda _u: {
            "resultList": {"result": [{"id": "PPR1", "doi": "10.1101/x",
                                       "title": "preprint thử", "journalTitle": "medRxiv",
                                       "firstPublicationDate": "2026-08-01"}]}})
        ket.append(("làn preprint → chua_binh_duyet=True + tầng riêng",
                    bool(pp) and pp[0].chua_binh_duyet
                    and pp[0].tang == "preprint_chua_binh_duyet",
                    f"tang={pp[0].tang if pp else '?'}"))
        # (12) ứng viên NCT trong BÁO CÁO không được nhận chú «mới vào PubMed»
        #      (bản ghi ngoài PubMed) và không in «PMID <rỗng>»
        tr = ss.search_trials_lane("x", 45, 5, fetch_json=lambda _u: {"studies": [{
            "protocolSection": {"identificationModule": {"nctId": "NCT99999999",
                                                         "briefTitle": "thử"},
                                "statusModule": {"overallStatus": "RECRUITING",
                                                 "lastUpdatePostDateStruct":
                                                     {"date": "2099-01-01"}}},
            "hasResults": False}]})
        bao = ss.markdown_report({"status": "PASS", "started_at": "", "finished_at": "",
                                  "days": 45, "max_results_per_topic": 5,
                                  "topic_count": 1, "successful_topics": 1,
                                  "failed_topics": 0, "candidate_count": 1,
                                  "topics": [{"topic": "t", "query": "q", "status": "PASS",
                                              "error": "",
                                              "candidates": [ss.asdict(tr[0])] if tr else []}],
                                  "disclaimer": "x"})
        ket.append(("ứng viên NCT trong báo cáo: không «mới vào PubMed», không PMID-rỗng",
                    bool(tr) and "mới vào PubMed" not in bao and "(không PMID" in bao,
                    bao[bao.find("NCT"):bao.find("NCT") + 80] if "NCT" in bao else "?"))
        # (13) phân xử rút-và-thay: item khai ĐỦ → CẢNH BÁO (không chặn);
        #      thiếu decision='notyet' → vẫn CHẶN (chống lách)
        rr = [{"loai": "pmid", "gia_tri": "30267080", "tinh_trang": "retracted",
               "rut_va_thay": True, "tieu_de": "ca thử", "kiem_luc": "2026-08-15",
               "nguon": "canary", "thong_bao": "31021386"}]
        du_path = tmp / "WebDashboard_EBM_VanDeCuThe_CanaryRR_20260101.html"
        du_path.write_text(_KHUNG.format(standards=_STANDARDS_TRONG, items=_item(
            "ITEM-05", "", "Cohort", "low", "notyet",
            extra=(', replacesPmid: "30267080", replacementNoticePmid: "31021386", '
                   'dateVersion: "2019 (bản thay thế)", '
                   'effectText: "số liệu của bản thay thế"'))),
            encoding="utf-8")
        e_rr, w_rr = [], []
        vd.kiem_nguon_da_rut(du_path, e_rr, w_rr, [], tra_cuu=lambda _t: list(rr))
        thieu_path = tmp / "WebDashboard_EBM_VanDeCuThe_CanaryRR_20260102.html"
        thieu_path.write_text(_KHUNG.format(standards=_STANDARDS_TRONG, items=_item(
            "ITEM-05", "", "Cohort", "low", "apply",
            extra=', replacesPmid: "30267080", replacementNoticePmid: "31021386"')),
            encoding="utf-8")
        e_rr2, w_rr2 = [], []
        vd.kiem_nguon_da_rut(thieu_path, e_rr2, w_rr2, [], tra_cuu=lambda _t: list(rr))
        ket.append(("rút-và-thay khai ĐỦ → cảnh báo; khai THIẾU (apply) → vẫn chặn",
                    not e_rr and any("RÚT" in w for w in w_rr) and bool(e_rr2),
                    f"đủ: e={len(e_rr)}/w={len(w_rr)} · thiếu: e={len(e_rr2)}"))
        # (14) vòng ed1: ký bằng khoá riêng tạm → xác minh CHỈ bằng khoá công;
        #      thiếu cryptography (python3 hệ thống) → bỏ qua CÓ KHAI BÁO (lượt venv
        #      của bộ chốt vẫn kiểm thật — không phải lượt nào cũng mù).
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            from cryptography.hazmat.primitives.serialization import (
                Encoding, NoEncryption, PrivateFormat, PublicFormat,
            )
            gc_mod = _nap(REPO / "medical-ebm-automation" / "tools" / "gate_contract.py",
                          "gc_canary")
            priv = Ed25519PrivateKey.generate()
            (tmp / "priv").mkdir()
            (tmp / "pub").mkdir()
            grp = gc_mod.role_group_for("IRB_ETHICS_COMMITTEE")
            (tmp / "priv" / f"gate_ed25519_{grp}.key").write_bytes(
                priv.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
            (tmp / "pub" / f"{grp}.pub").write_bytes(priv.public_key().public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
            gc_mod._ED_PRIVATE_DIR = tmp / "priv"
            gc_mod._ED_PUBLIC_DIR = tmp / "pub"
            sig = gc_mod.sign_approval_ed25519(
                "G2", "CANARY-ED", "a" * 64, "2026-08-16T00:00:00+00:00",
                reviewer_role="IRB_ETHICS_COMMITTEE", reviewer_ref="REF-CANARY",
                decision="APPROVED")
            (tmp / "priv" / f"gate_ed25519_{grp}.key").unlink()  # ĐỘC LẬP: xoá khoá riêng
            rec = {"gate_id": "G2", "reviewer_role": "IRB_ETHICS_COMMITTEE",
                   "reviewer_identity_reference": "REF-CANARY", "decision": "APPROVED",
                   "evidence_hash": "a" * 64,
                   "timestamp_utc": "2026-08-16T00:00:00+00:00",
                   "is_synthetic": False, "prev_hash": "", "approver_signature": sig}
            ok_ed = (bool(sig) and sig.startswith("ed1:role:")
                     and gc_mod.verify_approval_signature(rec, "CANARY-ED")
                     and not gc_mod.verify_approval_signature(
                         dict(rec, decision="REJECTED"), "CANARY-ED"))
            ket.append(("ed1: ký khoá riêng tạm → verify CHỈ bằng khoá công; sửa nội dung → trượt",
                        ok_ed, (sig or "?")[:40]))
        except ImportError:
            ket.append(("ed1: vòng ký-xác minh",
                        True, "bỏ qua CÓ KHAI BÁO — thiếu cryptography ở trình "
                              "thông dịch này; lượt venv của bộ chốt kiểm thật"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    do = [k for k in ket if not k[1]]
    if a.im_khi_on and not do:
        return 0
    print("=" * 70)
    print("  CANARY ĐẦU–CUỐI — gài lỗi đã biết, đòi dây chuyền bắt được")
    print("=" * 70)
    for ten, ok, ct in ket:
        print(f"  {'✓' if ok else '✗'} {ten}")
        if a.chi_tiet or not ok:
            print(f"      → {ct}")
    print("-" * 70)
    if do:
        print(f"🔴 {len(do)}/{len(ket)} lỗi gài KHÔNG bị bắt — đây là lỗ hổng THẬT, không phải")
        print("   chuyện câu chữ. Sửa đúng chỗ đó trước khi tin dây chuyền.")
        return 1
    print(f"🟢 {len(ket)}/{len(ket)} lỗi gài đều bị bắt.")
    print("   Canary kiểm DÂY CHUYỀN CÔNG CỤ — KHÔNG chứng minh agent đã GỌI cổng lúc chạy")
    print("   thật. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
