# GOLD SET & HARNESS ĐỐI KHÁNG — trạng thái 15/08/2026

Harness: `tools/thu_dau_cuoi_chung_cu.py` (canary, 2s, ngoại tuyến, tự chạy mỗi phiên qua
BH43) + 47 chốt hồi quy `chot_hoi_quy_bai_hoc.py` (mỗi chốt đã ĐỘT BIẾN kiểm).

## Ca đã có (10/20+)
1. apply+na trên RCT → chặn đúng thông điệp «hạ xuống consider»
2. apply+na trên GUIDELINE thiếu normativeBasis → chặn đúng thông điệp
3. apply chỉ dựa Consensus → chặn
4. gradeLevel khác na thiếu gradeBy → cảnh báo
5. provenanceUnknown KHÔNG tắt luật an toàn item (tái hiện lỗi return-sớm 12/08: đỏ 5/8)
6. hai bản cùng chủ đề nói ngược → phát hiện
7. **bài ĐÃ RÚT thật** (PMID 30267080 — PubMed & Europe PMC đều trả `ok`, chỉ nền
   Retraction Watch bắt được) → bắt ở khâu nhận
8. PMID không tra được → `chua_kiem`, không mặc định `ok`
9. hợp đồng item: máy tự APPROVED + tự gán mức → validator bắt (5 ca xấu trong self-test)
10. khoá quét: tiến trình thứ hai bị chặn rõ

## Còn thiếu `[CẦN BỔ SUNG]` (theo mục 8 prompt)
- guideline bị thay thế đầu-cuối (dữ kiện thật đã có: KDIGO 2024→2026, PMID 41485807 —
  cần seam tiêm dữ liệu cho `kiem_chung_cu_vuot_qua` để thử ngoại tuyến)
- SR chất lượng thấp (AMSTAR-2) · RCT outcome-switching — cần ca có đáp án biết trước
- ca người cao tuổi đa thuốc trọn dây chuyền A→B
