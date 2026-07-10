---
name: ke-don-an-toan-benh-man
description: Sử dụng skill này khi cần KÊ ĐƠN / RÀ ĐƠN AN TOÀN cho bệnh nhân bệnh mạn ngoại trú (mọi lứa tuổi, không chỉ người cao tuổi). Kích hoạt với "đơn này có an toàn không", "thuốc có đánh nhau không/tương tác", "hiệu chỉnh liều theo thận/gan", "cần theo dõi xét nghiệm gì khi dùng thuốc này", "có nên bớt thuốc/ngưng thuốc không", "mục tiêu HbA1c/huyết áp cho bệnh nhân này". Quy trình: đối chiếu thuốc · kiểm tương tác · hiệu chỉnh theo eGFR/gan · lịch theo dõi · cá thể hóa mục tiêu · cân nhắc giảm/ngưng. Liều/ngưỡng CHỈ nêu khi nguồn xác minh; KHÔNG bịa; KHÔNG lưu PII.
metadata:
  version: 1.0.0
---

# Skill: Kê đơn an toàn cho bệnh mạn (ngoại trú)

## 1. Phạm vi
Rà soát/kê đơn an toàn cho bệnh nhân bệnh mạn (THA, ĐTĐ, suy tim, CKD, COPD, rối loạn lipid, kháng đông…). Bao trùm mọi lứa tuổi. Người cao tuổi/đa thuốc → ưu tiên dùng cùng `nguoi-cao-tuoi-da-benh-da-thuoc` (Beers/STOPP-START).

## 2. Nguyên tắc bất biến
- **Liều, ngưỡng eGFR, mục tiêu điều trị CHỈ nêu khi nguồn chính thống xác minh** (guideline/label/SR). Không nhớ mơ hồ → ghi `[CẦN TRA NGUỒN]` và nối `cap-nhat-chung-cu-y-khoa`/`clinical-evidence-rag`.
- Không bịa cặp tương tác/độ mạnh. Bảng dưới chỉ NHẮC cặp hay gặp, phải đối chiếu trình kiểm tương tác chính thức.
- Cá thể hóa theo kỳ vọng sống, gánh nặng điều trị, ưu tiên của bệnh nhân.

## 3. Quy trình 6 bước
1. **Đối chiếu thuốc (reconciliation):** liệt kê TẤT CẢ thuốc đang dùng (kể cả OTC, đông dược, thực phẩm chức năng). Phát hiện trùng nhóm, thuốc không còn chỉ định.
2. **Chỉ định & phù hợp:** mỗi thuốc còn lý do dùng? đúng bệnh, đúng nhóm bệnh nhân?
3. **Tương tác:** rà cặp nguy hiểm (mục 4) + đối chiếu công cụ chính thức; chú ý thuốc khoảng QT, kháng đông, thuốc hạ kali/tăng kali.
4. **Hiệu chỉnh theo cơ quan:** kiểm eGFR (thuốc thải thận) & chức năng gan; nêu cần giảm liều/tránh — chỉ với con số khi nguồn xác minh.
5. **Theo dõi (monitoring):** xét nghiệm nền + định kỳ theo nhóm thuốc (mục 5).
6. **Cá thể hóa mục tiêu + deprescribing:** mục tiêu HbA1c/HA/LDL theo bệnh đồng mắc & kỳ vọng sống; cân nhắc giảm/ngưng thuốc hết lợi ích (nối Beers/STOPP).

## 4. Cặp tương tác / tình huống hay gặp (NHẮC — phải đối chiếu công cụ chính thức)
- **Tăng kali máu:** ACEi/ARB + spironolactone/finerenone + (NSAID/trimethoprim) → theo dõi kali.
- **Chảy máu:** kháng đông/kháng kết tập tiểu cầu + NSAID; warfarin + nhiều kháng sinh/azole.
- **Suy thận/AKI "bộ ba":** ACEi-ARB + lợi tiểu + NSAID.
- **Hạ đường huyết:** sulfonylurea + (suy thận/bỏ ăn/người cao tuổi); phối hợp insulin.
- **Kéo dài QT:** một số chống loạn nhịp + macrolide/fluoroquinolone + chống nôn + chống loạn thần.
- **Statin:** + một số azole/macrolide/fibrate → tăng độc cơ.
- **Đông dược/bổ sung:** St. John's wort (cảm ứng men), kali, cam thảo.

## 5. Theo dõi theo nhóm thuốc (khung — xác nhận chi tiết tại nguồn/đơn vị)
- **ACEi/ARB, lợi tiểu, MRA, finerenone:** creatinin/eGFR + kali (nền & sau khởi trị/chỉnh liều).
- **SGLT2i:** chức năng thận; nguy cơ nhiễm nấm sinh dục, hiếm DKA.
- **Metformin:** eGFR (ngưỡng tránh theo guideline).
- **Statin:** lipid; men gan/CK khi có triệu chứng.
- **Kháng đông (warfarin/DOAC):** INR (warfarin) / chức năng thận (DOAC), dấu chảy máu.
- **Lợi tiểu/thuốc hạ HA:** điện giải, HA tư thế (té ngã ở người cao tuổi).
- **Amiodarone, methotrexate, ức chế miễn dịch:** theo dõi cơ quan đích chuyên biệt.

## 6. Đầu ra mặc định
1. **Đánh giá đơn:** vấn đề an toàn phát hiện (tương tác/hiệu chỉnh/trùng lặp).
2. **Khuyến nghị cụ thể:** giữ/đổi/giảm/ngưng từng thuốc + lý do.
3. **Hiệu chỉnh theo thận/gan** (kèm nguồn nếu nêu số).
4. **Lịch theo dõi** (xét nghiệm nào, khi nào).
5. **Mục tiêu cá thể hóa** + cờ đỏ ngộ độc/tác dụng phụ cần đến khám ngay.
6. `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` cho danh mục/sẵn có thuốc & BHYT.

## 7. Checklist
- Đã đối chiếu toàn bộ thuốc (gồm OTC/đông dược)? · Mỗi thuốc còn chỉ định? · Đã rà tương tác nguy hiểm? · Hiệu chỉnh thận/gan (số có nguồn)? · Lịch theo dõi rõ? · Mục tiêu cá thể hóa? · Cân nhắc deprescribing? · Disclaimer + không PII?

## 7b. Chốt kiểm đầu ra 2 LỚP (trước khi trả lời)
Tự áp như agent `tham-dinh-dau-ra` (skill chạy độc lập): **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn PMID/DOI hoặc nhãn thiếu · KHÔNG PII · không tự đổi đơn/dừng Cổng A · không tự gán mức · tách 2 trục · nhãn `[CẦN…]` · disclaimer) + **Lớp 2 CHẤT LƯỢNG Med-PaLM** Q1–Q7 (dễ đọc · đúng đắn · **Q3 đầy đủ-an toàn** [CCĐ/tương tác/chỉnh liều thận-gan-người già] · thiên kiến · **Q5 nguy cơ hại** · cập nhật · thẩm quyền nguồn; `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`). Còn 🔴 → sửa trước khi trả; **Q2/Q5 đỏ → cờ chuyển bác sĩ**. Tự-kiểm cùng phiên — rào cứng cuối vẫn là bác sĩ.

## 8. Liên hệ skill
`nguoi-cao-tuoi-da-benh-da-thuoc` (Beers/STOPP-START) · `cap-nhat-chung-cu-y-khoa` & `clinical-evidence-rag` (tra liều/ngưỡng có nguồn) · `tuan-thu-dieu-tri` (đơn giản hóa phác đồ → tăng tuân thủ) · `tiep-can-chan-doan-co-do-chuyen-tuyen` (nếu triệu chứng mới nghi do thuốc) · `pyhealth` (2026-07-04: tra/đối chiếu mã ATC↔NDC↔RxNorm khi cần chuẩn hóa định danh thuốc ở Bước 1 đối chiếu thuốc — CHỈ tra mã, KHÔNG dùng làm nguồn mức độ tương tác/liều, vẫn phải đối chiếu công cụ chính thức theo mục 2).
