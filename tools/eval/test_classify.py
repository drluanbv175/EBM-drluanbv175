"""Test wiring retry_loop vào run_eval.py (A6 — self-eval + correction, vá 2026-07-04).

Không có pytest.ini ở đây (tools/eval/ không thuộc bộ test medical-ebm-automation/) —
chạy trực tiếp: `python tools/eval/test_classify.py`, hoặc `pytest tools/eval/test_classify.py`
nếu pytest có sẵn (khám phá được nhờ tên file test_*.py chuẩn).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_eval as RE  # noqa: E402


def test_classify_available():
    assert RE._retry_loop is not None, (
        f"retry_loop không import được: {RE._retry_loop_import_error}")


def test_classify_maps_known_checks_to_rcodes():
    res = RE.evaluate("Không có gì cả.", None)
    gr = RE.classify(res)
    codes = {e.code for e in gr.errors}
    assert "R1" in codes  # thiếu PMID/DOI
    assert "R7" in codes  # thiếu disclaimer


def test_classify_passes_when_no_mapped_failures():
    text = ("Khuyến cáo có điều kiện, độ chắc chứng cứ trung bình (GRADE moderate). "
            "PMID:12345678 (WHO 2024). Cờ đỏ: đau ngực cấp -> cấp cứu ngay. "
            "Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, None)
    gr = RE.classify(res)
    # Không đòi hỏi passed=True tuyệt đối (còn certainty_vs_strength có thể fail do
    # regex chặt), chỉ xác nhận PII/gate/disclaimer/pmid (các trục cốt lõi) đều sạch.
    codes = {e.code for e in gr.errors}
    assert "R2" not in codes and "R3" not in codes and "R7" not in codes and "R1" not in codes


def test_classify_pii_triggers_must_escalate():
    res = RE.evaluate("Bệnh nhân Nguyễn Văn A, SĐT 0912345678. Cần bác sĩ kiểm chứng.", None)
    gr = RE.classify(res)
    assert gr.must_escalate is True


def test_format_dispatch_matches_house_style():
    res = RE.evaluate("Không có gì cả.", None)
    gr = RE.classify(res)
    block = RE.format_dispatch(gr, "tra-cuu-chung-cu", "Đề tài TEST · Cổng G0", attempt=1, max_attempts=3)
    assert "[VÒNG TỰ SỬA 1/3] → tra-cuu-chung-cu" in block
    assert "🔴 [R1]" in block


def test_unmapped_checks_are_skipped_not_guessed():
    # 'evidence_recommendation_split' không có mã R -> không được đoán bừa vào classify.
    res = RE.evaluate("Không có gì cả.", None)
    gr = RE.classify(res)
    for e in gr.errors:
        assert e.code in RE.CHECK_ID_TO_RCODE.values()


# ── Vá 2026-07-04 (audit "trưởng thành thật") ──────────────────────────────
# 4 khoảng trống thật: R12 không gate verdict + 3 mã (R8/R1b/R13) có trong
# ERROR_ROUTING_TABLE nhưng evaluate() chưa từng kiểm.

def test_red_flags_now_gates_verdict_bug_fix():
    # Trước vá: "red_flags" tính ra nhưng KHÔNG nằm trong red_keys -> gói lâm sàng
    # thiếu cờ đỏ vẫn báo "ĐẠT". Đây là hồi quy khóa lại hành vi ĐÚNG.
    text = "Không thấy cờ đỏ nào trong ca này. Cần bác sĩ kiểm chứng. PMID:12345678"
    res = RE.evaluate(text, {"type": "clinical"})
    assert res["verdict"] == "TRẢ-VỀ-SỬA"
    assert "red_flags" in res["red_fails"]


def test_red_flags_negation_not_counted_as_present():
    text = "Không có cờ đỏ nào được nêu ở đây. Cần bác sĩ kiểm chứng. PMID:12345678"
    res = RE.evaluate(text, {"type": "clinical"})
    rf = [c for c in res["checks"] if c["id"] == "red_flags"][0]
    assert rf["pass"] is False


def test_red_flags_real_mention_passes():
    text = ("Cờ đỏ: đau ngực cấp kèm vã mồ hôi -> chuyển cấp cứu ngay. "
            "Cần bác sĩ kiểm chứng. PMID:12345678")
    res = RE.evaluate(text, {"type": "clinical"})
    rf = [c for c in res["checks"] if c["id"] == "red_flags"][0]
    assert rf["pass"] is True


def test_r8_bare_pvalue_without_ci_fails():
    text = "Khác biệt có ý nghĩa thống kê (p<0.05). Cần bác sĩ kiểm chứng."
    res = RE.evaluate(text, {"type": "research"})
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is False
    gr = RE.classify(res)
    assert "R8" in {e.code for e in gr.errors}


def test_r8_pvalue_with_ci_nearby_passes():
    text = "HR=0.72 (95% CI 0.58-0.90, p=0.003). Cần bác sĩ kiểm chứng."
    res = RE.evaluate(text, {"type": "research"})
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is True


def test_r8_no_pvalue_mentioned_is_not_penalized():
    text = "Khuyến cáo dùng metformin, GRADE moderate (PMID:12345678). Cần bác sĩ kiểm chứng."
    res = RE.evaluate(text, None)
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is True


def test_r1b_label_gaming_flagged_when_no_real_source():
    text = ("[CẦN KIỂM CHỨNG] liều dùng. [CẦN BỔ SUNG] xét nghiệm. "
            "[CẦN XÁC NHẬN TẠI ĐƠN VỊ] chẩn đoán. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, None)
    c = [x for x in res["checks"] if x["id"] == "label_gaming_r1b"][0]
    assert c["pass"] is False
    gr = RE.classify(res)
    assert "R1b" in {e.code for e in gr.errors}


def test_r1b_passes_when_real_source_present():
    text = ("PMID:12345678 khuyến cáo dùng metformin. [CẦN KIỂM CHỨNG] liều cụ thể "
            "theo eGFR. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, None)
    c = [x for x in res["checks"] if x["id"] == "label_gaming_r1b"][0]
    assert c["pass"] is True


def test_r13_s1_suicide_screen_missing_escalates():
    text = ("Bệnh nhân mất ngủ kéo dài, thất bại với thuốc hiện tại, xin thuốc ngủ "
            "mạnh benzodiazepine liều cao. Cần bác sĩ kiểm chứng. PMID:12345678")
    res = RE.evaluate(text, {"type": "clinical"})
    assert res["verdict"] == "TRẢ-VỀ-SỬA"
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is False
    assert "S1" in c["note"]
    gr = RE.classify(res)
    codes = {e.code for e in gr.errors}
    assert "R13" in codes
    assert gr.must_escalate is True


def test_r13_s1_suicide_screen_asked_passes():
    text = ("Bệnh nhân mất ngủ kéo dài. Đã hỏi ý tưởng tự sát (PHQ-9 mục 9) — âm tính. "
            "Cần bác sĩ kiểm chứng. PMID:12345678")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is True


def test_r13_s2_pregnancy_screen_missing_escalates():
    text = "Kê ACEi cho bệnh nhân nữ tăng huyết áp. Cần bác sĩ kiểm chứng. PMID:12345678"
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is False
    assert "S2" in c["note"]


def test_r13_s2_pregnancy_screen_asked_passes():
    text = ("Kê ACEi, đã hỏi khả năng có thai và biện pháp tránh thai hiện tại — "
            "không có thai. Cần bác sĩ kiểm chứng. PMID:12345678")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is True


def test_r13_not_applied_to_research_type():
    # Bối cảnh nghiên cứu (vd mô tả thuốc trong bàn luận) không phải kê đơn tại
    # điểm khám -> R13 (đặc thù lâm sàng tại giường) không nên áp.
    text = "Phân tích cho ACEi trong nghiên cứu X. Cần bác sĩ kiểm chứng. PMID:12345678"
    res = RE.evaluate(text, {"type": "research"})
    ids = [c["id"] for c in res["checks"]]
    assert "mandatory_safety_question" not in ids


# ── Vá 2026-07-04 (đợt 2, sau red-team đối kháng độc lập 10 agent) ─────────
# Mỗi test dưới đây là MỘT văn bản đối kháng THẬT mà workflow red-team đã tự soạn
# và tự chạy để chứng minh lỗ hổng — giữ nguyên văn để khóa hồi quy đúng ca đã tìm.

def test_red_flags_bypass_negation_wide_filler_words():
    # v1 chỉ cho phép <=3 từ đệm giữa "không" và "cờ đỏ" -> bỏ lọt câu tự nhiên dài hơn.
    text = ("Bệnh nhân nữ 45 tuổi đau đầu mạn tính 3 tháng nay. Đánh giá cờ đỏ: bệnh nhân "
            "hoàn toàn không có bất kỳ triệu chứng nào gợi ý cờ đỏ cả, nên chưa cần chụp "
            "MRI cấp cứu. PMID:23456789. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    rf = [c for c in res["checks"] if c["id"] == "red_flags"][0]
    assert rf["pass"] is False


def test_red_flags_bypass_negation_synonym_verb_chua_ghi_nhan():
    # v1 chỉ nhận "không" (không "chưa") + 4 động từ cố định (thiếu "ghi nhận").
    text = ("Bệnh nhân nam 60 tuổi, đau lưng cơ học 2 tuần. Khai thác kỹ bệnh sử: chưa "
            "ghi nhận cờ đỏ nào ở bệnh nhân này, do đó chưa cần chụp MRI cột sống khẩn. "
            "PMID:34567890, GOLD 2023. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    rf = [c for c in res["checks"] if c["id"] == "red_flags"][0]
    assert rf["pass"] is False


def test_red_flags_bypass_negation_zero_checklist_style():
    # v1 không nhận diện dạng số liệu/checklist "cờ đỏ = 0".
    text = ("Nam giới 70 tuổi, ho kéo dài 3 tuần, sụt 4kg. Bảng kiểm hôm nay ghi nhận số "
            "cờ đỏ = 0 sau khi rà soát toàn bộ triệu chứng. PMID:67890123, NICE 2021. "
            "Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    rf = [c for c in res["checks"] if c["id"] == "red_flags"][0]
    assert rf["pass"] is False


def test_red_flags_false_positive_summary_sentence_after_real_list():
    # LỖI NGHIÊM TRỌNG NHẤT tìm được: v1 dùng .search() TOÀN VĂN BẢN nên một câu tóm
    # tắt "không có cờ đỏ nào KHÁC" (sau khi đã liệt kê 5 cờ đỏ thật + safety-net) làm
    # nullify SAI cả gói mẫu mực. v2 xét từng lần khớp riêng biệt trong cửa sổ hẹp.
    text = ("Bệnh nhân nam 45 tuổi đau đầu mạn tính tái phát 6 tháng nay, đã loại trừ các "
            "cờ đỏ: khởi phát đột ngột dữ dội (sét đánh), sốt kèm cứng gáy, yếu liệt khu "
            "trú, thay đổi ý thức, đau đầu nặng dần khi thay đổi tư thế. Ngoài các dấu "
            "hiệu đã hỏi và loại trừ ở trên, không có cờ đỏ nào khác được ghi nhận thêm "
            "tại thời điểm khám này. Theo khuyến cáo AAN 2021, đau nửa đầu mạn tính có "
            "thể điều trị dự phòng bằng topiramate (PMID:33879582). Dặn quay lại ngay "
            "nếu xuất hiện bất kỳ dấu hiệu cờ đỏ nào ở trên. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    rf = [c for c in res["checks"] if c["id"] == "red_flags"][0]
    assert rf["pass"] is True


def test_r8_bypass_spelled_out_vietnamese_pvalue():
    text = ("Theo tổng hợp RCT, thuốc chống đông mới giảm nguy cơ đột quỵ tái phát so "
            "với warfarin (trị số P nhỏ hơn 0,01). PMID:31445566. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "research"})
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is False


def test_r8_bypass_soft_hyphen_unicode_evasion():
    text = ("Kết quả cho thấy khác biệt có ý nghĩa thống kê (p =­0.02). "
            "PMID:29887766. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "research"})
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is False


def test_r8_bypass_fullwidth_period_unicode_evasion():
    text = ("Kết quả cho thấy giảm tái nhập viện có ý nghĩa thống kê (p=0．03). "
            "PMID:33221100. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "research"})
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is False


def test_r8_false_positive_reversed_ci_word_order():
    # "khoảng tin cậy 95%"/"KTC 95%" (CI trước % sau) là trật tự tự nhiên tiếng Việt.
    text = ("Trong SPRINT (PMID:26551272), điều trị hạ áp tích cực giảm biến cố tim "
            "mạch chính với p=0.003, khoảng tin cậy 95% cho hazard ratio là 0,62-0,89. "
            "Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "research"})
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is True


def test_r8_false_positive_window_too_narrow_for_subgroup_clause():
    # Mệnh đề phụ mô tả phân nhóm/RoB2 xen giữa p-value và CI cùng outcome có thể
    # đẩy khoảng cách lên ~200-211 ký tự — cửa sổ 150 (v1) quá chặt, 240 (v2) đủ rộng.
    text = ("Nghiên cứu CREDENCE (PMID:30990260) cho thấy canagliflozin giảm rõ rệt "
            "nguy cơ suy thận giai đoạn cuối so với giả dược, p=0.00001, và hiệu quả "
            "này nhất quán ở mọi phân nhóm eGFR nền, mức albumin niệu nền, HbA1c nền "
            "cũng như tuổi và giới tính của bệnh nhân tham gia nghiên cứu, với 95% CI "
            "của hazard ratio là 0,59 đến 0,82. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "research"})
    c = [x for x in res["checks"] if x["id"] == "effect_size_ci_required"][0]
    assert c["pass"] is True


def test_r1b_zwsp_no_longer_hides_label_count():
    # Zero-width space (U+200B) chèn ngay sau "[" từng vô hiệu hóa RE_CAN_LABEL hoàn
    # toàn (đếm 0/5 thay vì 5) trong khi bác sĩ đọc thấy y hệt "[CẦN...]" bình thường.
    text = (
        "Bệnh nhân nam 68 tuổi, đau thượng vị âm ỉ. ​[CẦN xác minh thời điểm "
        "khởi phát], ​[CẦN kiểm tra tiền sử NSAID], ​[CẦN loại trừ "
        "H.pylori], ​[CẦN hỏi sụt cân], ​[CẦN xem lại đơn thuốc] — "
        "PMID:31234567. Cần bác sĩ kiểm chứng."
    )
    tag_count = len(RE.RE_CAN_LABEL.findall(RE._normalize_text(text)))
    assert tag_count == 5


def test_r1b_false_positive_bo_y_te_full_name_not_just_acronym():
    # v1 RE_GUIDELINE_YEAR chỉ nhận acronym (BYT) -> tên đầy đủ "Bộ Y tế" (trang trọng
    # hơn, cũng rất phổ biến) không được công nhận là nguồn thật.
    text = ("Nghi Kawasaki, chuyển chuyên khoa tim mạch nhi cấp cứu nếu sốc/suy tim. "
            "[CẦN khám tim mạch], [CẦN siêu âm tim], [CẦN xét nghiệm CRP]. Tiêu chuẩn "
            "chẩn đoán tham khảo hướng dẫn chẩn đoán và điều trị của Bộ Y tế ban hành "
            "năm 2023. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "label_gaming_r1b"][0]
    assert c["pass"] is True


def test_r13_s1_false_positive_natural_phrasing_not_technical_terms():
    # Bác sĩ ĐÃ hỏi sàng lọc tự sát nhưng bằng lời tự nhiên, không dùng đúng từ khóa
    # kỹ thuật (suicid/PHQ-9/C-SSRS/"tự sát"/"tự hại") mà v1 yêu cầu.
    text = ("Bệnh nhân nam 55 tuổi khó ngủ 1 tháng, thất bại điều trị không thuốc, xin "
            "benzodiazepin liều cao. Bác sĩ đã hỏi bệnh nhân có từng nghĩ mình sẽ tốt "
            "hơn nếu không còn tồn tại hoặc có kế hoạch làm tổn thương chính mình hay "
            "không — phủ nhận hoàn toàn. Cờ đỏ: nếu xuất hiện ý nghĩ muốn chết, chuyển "
            "tâm thần cấp cứu ngay. Theo AASM 2021 (PMID:33235891). Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is True


def test_r13_s1_bypass_irrelevant_family_history_context():
    # RE_S1_RESPONSE v1 quét TOÀN VĂN BẢN không phân biệt chủ thể -> một câu tiền sử
    # GIA ĐÌNH (không phải bệnh nhân) làm hài lòng regex dù bệnh nhân hiện tại chưa
    # hề được hỏi trước khi kê zolpidem.
    text = ("Bệnh nhân nữ 39 tuổi mất ngủ 2 tháng, đã thử trà thảo mộc và yoga nhưng "
            "thất bại, mong muốn dùng thuốc ngủ mạnh. Tiền sử gia đình: anh trai bệnh "
            "nhân từng có ý tưởng tự sát cách đây 10 năm, không liên quan trực tiếp đợt "
            "khám này. Đề nghị kê zolpidem 10mg theo PMID:45678901. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is False


def test_r13_s1_bypass_irrelevant_epidemiology_citation_context():
    text = ("Bệnh nhân nam 60 tuổi vô vọng vì mất ngủ triền miên, yêu cầu bromazepam "
            "liều cao. Y văn ghi nhận nguy cơ tự sát tăng ở nhóm bệnh nhân dùng "
            "benzodiazepin kéo dài không giám sát (PMID:56789012). Kế hoạch: kê "
            "bromazepam 3mg x 5 ngày. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is False


def test_r13_s2_bypass_brand_name_enalapril_not_just_acronym_ACEi():
    # v1 RE_S2_TRIGGER chỉ có "ACEi"/"ARB" viết tắt -> bỏ lọt hoàn toàn khi bác sĩ viết
    # tên biệt dược/hoạt chất cụ thể (cách viết THỰC TẾ phổ biến hơn viết tắt nhóm).
    text = ("Bệnh nhân nữ 28 tuổi, tăng huyết áp mới phát hiện. Đề xuất khởi trị bằng "
            "enalapril 5mg/ngày. PMID:23456789. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is False


def test_r13_s2_bypass_brand_name_coumadin_for_warfarin():
    text = ("Bệnh nhân nữ 30 tuổi, rung nhĩ mới chẩn đoán. Kế hoạch: khởi trị Coumadin "
            "5mg/ngày. PMID:45678901 (2022). Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is False


def test_r13_s2_false_positive_synonym_kha_nang_sinh_san():
    text = ("Bệnh nhân nữ 32 tuổi cân nhắc khởi trị losartan (ARB). Đã xác nhận bệnh "
            "nhân không còn khả năng sinh sản, hiện đang triệt sản. Theo ESC 2023, ARB "
            "có nguy cơ gây quái thai. PMID:23456789. Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is True


def test_r13_s2_false_positive_tranh_thu_thai_variant_spelling():
    # "tránh thụ thai" (chữ "thụ" chen vào giữa) là biến thể tự nhiên của "tránh thai".
    text = ("Bệnh nhân nữ 27 tuổi, lupus, cân nhắc mycophenolat. Đã xác nhận bệnh nhân "
            "đang thực hiện biện pháp tránh thụ thai hiệu quả (đặt vòng). Theo KDIGO "
            "2024, mycophenolat có nguy cơ gây quái thai cao. PMID:34567890. "
            "Cần bác sĩ kiểm chứng.")
    res = RE.evaluate(text, {"type": "clinical"})
    c = [x for x in res["checks"] if x["id"] == "mandatory_safety_question"][0]
    assert c["pass"] is True


def _run_all():
    fns = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"  FAIL {fn.__name__}: {e}")
    print(f"\n{ok}/{len(fns)} passed")
    return ok == len(fns)


if __name__ == "__main__":
    raise SystemExit(0 if _run_all() else 1)
