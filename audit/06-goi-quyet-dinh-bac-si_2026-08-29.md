# Gói quyết định cho bác sĩ — 5 vấn đề chưa hoàn thiện (29/08/2026)

> Soạn theo yêu cầu «đưa đề xuất và giải quyết từng vấn đề» sau khi dừng vòng lặp canh.
> Mọi mục y khoa trong tài liệu này là **ĐỀ XUẤT** — chỉ có hiệu lực sau khi bác sĩ chuẩn y
> (Cổng A). Mọi PMID/DOI dưới đây **đã tra sống PubMed ngày 29/08/2026** (metadata khớp,
> không mục nào mang nhãn Retracted Publication ở bản hiện hành). Cần bác sĩ kiểm chứng.

---

## Vấn đề 1 — Duyệt 7 khối cờ đỏ `de_xuat` trong `clinical_runtime/safety_net_templates.json`

Bảy hội chứng được Claude điền 28/08/2026 từ nguồn đã tra PubMed, đang mang nhãn
`de_xuat` (chưa chuẩn y). Tóm tắt để duyệt:

| Hội chứng | Công cụ / phạm vi | Nguồn (đã tra) | Giới hạn phải nhớ |
|---|---|---|---|
| Đau ngực | Marburg Heart Score — LOẠI TRỪ mạch vành ở chăm sóc ban đầu, ≥3 điểm = cần đánh giá thêm | PMID 20603345 · doi:10.1503/cmaj.100212 | KHÔNG sàng lọc bóc tách ĐMC/thuyên tắc phổi/tràn khí |
| Khó thở | Ngưỡng NẶNG NHẤT (3 điểm/thông số) của NEWS2 | NEWS2 — Royal College of Physicians 2017 | Chuẩn NỘI TRÚ, chưa kiểm định phân loại ngoại trú; caveat Pimentel (PMID 30287355) |
| Đau bụng | HẸP CÓ CHỦ Ý: khó tiêu kéo dài (nội soi ≥60 tuổi) — KHÔNG phủ bụng cấp | ACG/CAG 2017 — PMID 28631728 · doi:10.1038/ajg.2017.154 | Alarm features chi tiết nằm ở toàn văn |
| Sốt | qSOFA ≥2/3 → nguy cơ diễn tiến nặng | Sepsis-3 — PMID 26903335 · doi:10.1001/jama.2016.0288 | Dấu NHẮC, không phải tiêu chuẩn chẩn đoán sepsis |
| Đau thắt lưng | Nhóm cờ đỏ CÓ giá trị thông tin cho gãy xương/ác tính (kèm xác suất hậu nghiệm) | Downie BMJ 2013 — PMID 24335669 · doi:10.1136/bmj.f7095 | KTC rất rộng; nhiều cờ đỏ guideline khác không có giá trị |
| Chóng mặt | HAI LỚP: nhận diện bệnh cảnh tiền đình cấp + nguy cơ đột quỵ (P1) ≠ ba dấu khám HINTS (H1–H3, người được huấn luyện) | Kattah Stroke 2009 — PMID 19762709 · doi:10.1161/STROKEAHA.109.551234 | Độ chính xác không tự chuyển sang người chưa huấn luyện; MRI sớm âm giả 12% |
| Sụt cân | Sụt cân không chủ ý ở >65 tuổi — ghi nhận bằng CÂN, theo dõi có hẹn | Gaddey AFP 2021 — PMID 34264616 (PubMed không ghi DOI) | Tóm tắt KHÔNG nêu ngưỡng ≥5% — cần toàn văn mới ghi thành tiêu chí |

**Cách duyệt:** bác sĩ xác nhận (một câu trong chat là đủ) → nhãn `de_xuat` được đổi thành
`da_duyet` kèm ngày và người duyệt; nội dung tiêu chí GIỮ NGUYÊN, chỉ đổi trạng thái chuẩn y.
Duyệt từng hội chứng riêng cũng được — nêu tên hội chứng muốn giữ lại xem thêm.

---

## Vấn đề 2 — BẢN NHÁP lời dặn bệnh nhân (0/8 → 8 bản nháp chờ duyệt)

Doctrine cấm máy sinh lời dặn THAY bác sĩ, nên các bản nháp dưới đây **chưa được ghi vào
JSON** — JSON vẫn 0/8 trung thực. Mỗi câu đều truy về đúng tiêu chí đã có nguồn của khối
cờ đỏ tương ứng; chỗ nguồn hiện có KHÔNG phủ được thì ghi rõ `[CẦN BÁC SĨ CHỌN NGUỒN]`,
tuyệt đối không bịa thêm ngưỡng. Sau khi bác sĩ duyệt/sửa, nội dung sẽ được ghi vào
`dan_benh_nhan_quay_lai` với `trang_thai: "co-nguon"` kèm ghi chú người duyệt.

### 2.1 Đau đầu (mọi câu truy về SNNOOP10 — PMID 30587518)
QUAY LẠI KHÁM NGAY hoặc đi cấp cứu nếu:
- Đau đầu khởi phát **đột ngột, dữ dội** (O1)
- Đau đầu **kèm sốt** (S)
- Kèm **yếu tay chân, nói khó, nhìn mờ/nhìn đôi, lú lẫn** (N2)
- Đau đầu **sau ngã hoặc va đập đầu** (P8)
- Đau đầu **kiểu mới khác hẳn trước đây** hoặc **ngày càng nặng dần** (P1, P5)
- Đang **mang thai hoặc mới sinh** mà xuất hiện đau đầu mới (P6)

### 2.2 Đau ngực (Marburg không sinh được tiêu chí cấp cứu — nháp tối thiểu)
- Đau ngực **xuất hiện hoặc tăng khi gắng sức** → đi khám sớm (M4)
- Các mốc "gọi cấp cứu ngay" (đau kéo dài, kèm khó thở/vã mồ hôi/lan tay-hàm):
  `[CẦN BÁC SĨ CHỌN NGUỒN — gợi ý: guideline đau ngực cấp hiện hành; Marburg không phủ]`

### 2.3 Khó thở (mọi ngưỡng truy về NEWS2 mức 3 điểm — RCP 2017)
QUAY LẠI NGAY/cấp cứu nếu (người nhà đo được):
- **SpO₂ ≤91%** trên máy đo kẹp ngón tại nhà (N2)
- **Thở ≥25 lần/phút** — người nhà đếm trọn 1 phút (N1)
- **Mới lú lẫn hoặc khó đánh thức** (N5)
- Lưu ý: người COPD dùng ngưỡng SpO₂ riêng theo chỉ định của bác sĩ (Scale 2)

### 2.4 Đau bụng (ACG/CAG 2017 — phạm vi khó tiêu)
- **≥60 tuổi mới xuất hiện khó tiêu** → đi khám để cân nhắc nội soi (D1)
- Dấu cấp cứu (nôn ra máu, đi ngoài phân đen, đau dữ dội đột ngột):
  `[CẦN BÁC SĨ CHỌN NGUỒN — alarm features nằm trong toàn văn guideline]`

### 2.5 Sốt (mọi câu truy về qSOFA — PMID 26903335)
QUAY LẠI NGAY/cấp cứu nếu sốt kèm:
- **Lơ mơ, nói lẫn, khó đánh thức** (Q3)
- **Thở nhanh ≥22 lần/phút** (Q1)
- Nếu nhà có máy đo huyết áp: **HA tâm thu ≤100 mmHg** (Q2)

### 2.6 Đau thắt lưng (mọi câu truy về Downie BMJ 2013 — PMID 24335669)
ĐI KHÁM SỚM nếu đau lưng kèm một trong:
- **Sau chấn thương đáng kể** (F2) · thấy **bầm tím/trầy xước vùng đau** (F3)
- Đang dùng **corticoid kéo dài** (F1) · có **tiền sử ung thư** (C1)
- Dấu chèn ép thần kinh (yếu chân, bí tiểu, tê vùng yên ngựa):
  `[CẦN BÁC SĨ CHỌN NGUỒN — không nằm trong phạm vi bài Downie (chỉ gãy xương/ác tính)]`

### 2.7 Chóng mặt (truy về quần thể nghiên cứu Kattah 2009 — PMID 19762709)
- **Chóng mặt liên tục không dứt + đi đứng không vững**, nhất là khi có tăng huyết áp/
  đái tháo đường/rung nhĩ/hút thuốc → đi khám NGAY (P1)
- Dấu đột quỵ khác (nói khó, nhìn đôi, yếu nửa người):
  `[CẦN BÁC SĨ CHỌN NGUỒN — gợi ý bộ dấu hiệu đột quỵ chuẩn (FAST); HINTS không phủ]`

### 2.8 Sụt cân (mọi câu truy về Gaddey AFP 2021 — PMID 34264616)
- **Tự cân mỗi tuần** cùng một cân, cùng điều kiện, ghi lại số (W1)
- Cân **tiếp tục giảm giữa hai lần khám** → quay lại TRƯỚC hẹn (W1)
- **Giữ đúng hẹn theo dõi 3–6 tháng** kể cả khi thấy khỏe (W2)

`moc_thoi_gian` của cả 8 hội chứng: `[CẦN BÁC SĨ ĐIỀN]` — chọn mốc tái khám là thẩm quyền
lâm sàng, bản nháp không đề xuất số.

---

## Vấn đề 3 — Merge nhánh về `master`

- Nhánh `claude/medical-research-system-phggdf`: 7 commit, CI xanh cả 4 lane trên đầu nhánh
  `ba598c4` (run #94), cây sạch, không xung đột với `origin/master` (master không có commit
  mới từ 28/08).
- **Đề xuất:** merge `--no-ff` (giữ mốc lịch sử đợt rà 28/08) rồi push `master`.
  Chỉ thực hiện khi bác sĩ xác nhận tường minh — quy tắc «không đẩy nhánh khác khi chưa
  được phép» vẫn giữ.

---

## Vấn đề 4 — 6 mục chứng cứ chờ neo phân hạng / đối chiếu (dashboard nằm trên OneDrive,
## KHÔNG sửa được từ phiên cloud — đây là hồ sơ quyết định để áp trên máy thật)

Theo PubMed (tra sống 29/08/2026):

### 4a. Ba mục CKD (`BenhThanMan_BenhKem_DoiTuongDacBiet`) — DAPA-CKD (PMID 32970396 ·
[doi:10.1056/NEJMoa2024816](https://doi.org/10.1056/NEJMoa2024816)) · FIDELIO-DKD (PMID 33264825 ·
[doi:10.1056/NEJMoa2025845](https://doi.org/10.1056/NEJMoa2025845)) · EMPA-KIDNEY (PMID 36331190 ·
[doi:10.1056/NEJMoa2204233](https://doi.org/10.1056/NEJMoa2204233))
- **Neo đề xuất: KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management
  of CKD** — PMID 38490803 · [doi:10.1016/j.kint.2023.10.018](https://doi.org/10.1016/j.kint.2023.10.018),
  Kidney Int 2024;105(4S):S117-S314, loại Practice Guideline. Bản tóm tắt điều hành
  (PMID 38519239 · [doi:10.1016/j.kint.2023.10.016](https://doi.org/10.1016/j.kint.2023.10.016))
  xác nhận nguyên văn: khuyến cáo xây dựng theo **GRADE** — đủ điều kiện «tổ chức CÓ chấm».
- ⚠️ ĐÍNH CHÍNH so với ghi chú cũ: PMID 41485807 mà `kiem_chung_cu_vuot_qua` từng bắt được
  là **KDIGO 2026 về THIẾU MÁU trong CKD** ([doi:10.1016/j.kint.2025.06.005](https://doi.org/10.1016/j.kint.2025.06.005))
  — KHÔNG phải neo cho 3 mục SGLT2i/finerenone; nó thuộc dashboard thiếu máu.
- **Việc trên máy thật:** mở toàn văn KDIGO 2024, chép ĐÚNG mức khuyến cáo nguyên bản
  (số/chữ của chính KDIGO) cho SGLT2i và finerenone vào `gradeSource` + `gradeBy: "KDIGO 2024"`,
  rồi mới nâng `decision`. KHÔNG chép «RCT chất lượng cao» tự chấm (đúng lỗi đã hạ 13/08).

### 4b. Hai mục RA (`RA_TimMachChuyenHoaNoiTiet` ITEM-01 và mục cùng PMID) — PMID 27697765
- Bài neo hiện tại: **EULAR recommendations for CVD risk management in RA — 2015/2016
  update**, Ann Rheum Dis 2017 ([doi:10.1136/annrheumdis-2016-209775](https://doi.org/10.1136/annrheumdis-2016-209775)).
  Tra PubMed theo đúng tiêu đề chỉ có MỘT bản — chưa có bản thay cùng dòng tiêu đề.
- **Việc trên máy thật:** chép mức LoE/SoR nguyên bản của từng khuyến cáo từ toàn văn
  EULAR vào `gradeBy: "EULAR LoE/SoR"`. Lưu ý EULAR 2025 về quản lý DMARD (PMID 41826212 ·
  [doi:10.1016/j.ard.2026.01.023](https://doi.org/10.1016/j.ard.2026.01.023)) là dòng
  KHÁC (điều trị, không phải nguy cơ tim mạch) — không dùng thay.

### 4c. ViemGanB ITEM-05 — bài rút-và-thay (PMID 30267080)
- **Đối chiếu đã làm xong ở mức tóm tắt:** bản HIỆN HÀNH trên PubMed của PMID 30267080
  (Choi và cs., JAMA Oncol — [doi:10.1001/jamaoncol.2018.4070](https://doi.org/10.1001/jamaoncol.2018.4070),
  tức bản ĐÃ THAY sau Notice of Retraction and Replacement PMID 31021386 ·
  [doi:10.1001/jamaoncol.2019.0576](https://doi.org/10.1001/jamaoncol.2019.0576)) **vẫn kết
  luận TDF gắn với nguy cơ HCC thấp hơn entecavir**. Số liệu bản-đã-sửa, nguyên văn tóm tắt:
  HR HCC **0,61 (KTC 95% 0,54–0,70)** ở đoàn hệ quốc gia; HR **0,62 (0,54–0,70)** sau ghép
  điểm xu hướng; HR **0,68 (0,46–0,99)** ở đoàn hệ bệnh viện; tử vong/ghép gan HR 0,77
  (0,65–0,92).
- **Đề xuất:** GIỮ chiều kết luận của ITEM-05; trên máy thật đối chiếu con số đang ghi
  trong dashboard với các HR trên — nếu dashboard còn mang số của bản TRƯỚC-sửa thì thay
  bằng số đã sửa, thêm ghi chú «retract-and-replace 2019, đã đối chiếu bản thay» vào
  `gradeSource`, và bỏ cờ đỏ rút bài cho mục này (cơ chế cờ đọc trạng thái từ sổ, sẽ tự
  tắt khi sổ ghi nhận đã đối chiếu).

---

## Vấn đề 5 — Kiểm trên máy thật (không làm được từ phiên cloud)

Bản chất: 36 chốt cần cây OneDrive; phiên cloud chỉ có git trần nên chúng ⚪ có khai báo.
**Một khối lệnh duy nhất trên Mac/Windows sau khi nhánh về máy** (chi tiết: `HANDOVER.md` mục 9):

```bash
git fetch origin && git checkout claude/medical-research-system-phggdf \
  && git config core.hooksPath .githooks && chmod +x .githooks/pre-commit
python3 tools/sync_safety_check.py            # làn ① — 🔴 thì DỪNG
python3 tools/chot_hoi_quy_bai_hoc.py         # BH01–BH83 với ĐẦY ĐỦ nguyên liệu
python3 tools/dong_bo_tat_ca.py --ap-dung     # 8 làn đồng bộ hai máy
```

Mốc xác nhận hoàn tất: bộ chốt **0 tái phát với 0 mục ⚪** (mọi chốt chạy trên nguyên liệu
thật) trên CẢ HAI máy.

---

---

## ✍️ QUYẾT ĐỊNH BÁC SĨ 29/08/2026 (trả lời trong phiên Claude Code) + thi hành

1. **Cờ đỏ:** «Duyệt cả 7» → 7 khối `de_xuat` đã đổi thành `da_duyet` kèm ngày; nội dung
   tiêu chí giữ nguyên. (`safety_net_templates.json` v2.2.0)
2. **Lời dặn:** «Bổ sung nguồn cho chính xác giúp tôi» → 8 khối lời dặn đã ghi vào JSON,
   MỖI CÂU truy về nguồn tra sống PubMed 29/08/2026; các nguồn BỔ SUNG so với bản nháp:
   - Chùm đuôi ngựa (đau lưng): Dionne 2019, tổng quan hệ thống — PMID 31132655 ·
     [doi:10.1016/j.msksp.2019.05.004](https://doi.org/10.1016/j.msksp.2019.05.004)
     (+ Corrigendum 2021 — PMID 33722511); tóm tắt nêu đích danh tê yên ngựa, bí tiểu,
     tiểu/đại tiện không tự chủ; giới hạn: đặc hiệu hơn nhạy (Se gộp 0,19–0,43).
   - Dấu đột quỵ (chóng mặt): BE-FAST — Aroor, Stroke 2017 — PMID 28082668 ·
     [doi:10.1161/STROKEAHA.116.015169](https://doi.org/10.1161/STROKEAHA.116.015169)
     (thêm Thăng bằng + Mắt giảm bỏ sót 14,1%→4,4%; hồi cứu một trung tâm).
   - Dấu báo động tiêu hoá: Odeghe 2019 — PMID 31762930 ·
     [doi:10.11604/pamj.2019.34.66.18848](https://doi.org/10.11604/pamj.2019.34.66.18848)
     (nôn máu/nôn dai dẳng/nuốt đau → nội soi sớm; hồi cứu một trung tâm, Se 65%/Sp 49%).
   - Mốc cấp cứu đau ngực: TÓM TẮT AHA/ACC 2021 (PMID 34709879 ·
     [doi:10.1161/CIR.0000000000001029](https://doi.org/10.1161/CIR.0000000000001029))
     không nêu ngưỡng cụ thể → ô này GIỮ `[CẦN BÁC SĨ ĐIỀN]`, chỉ ghi nguồn đề xuất —
     không bịa ngưỡng.
   ⚠️ Câu chữ cuối của lời dặn vẫn mang nhãn `de_xuat` — chỉ in cho bệnh nhân sau khi
   bác sĩ chuẩn y câu chữ (Cổng A). `moc_thoi_gian` 8/8 vẫn `[CẦN BÁC SĨ ĐIỀN]`.
3. **Merge:** «Merge và push master» → thi hành trong cùng phiên (merge `--no-ff`).
4. **Chứng cứ:** «Đồng ý hướng neo» → hồ sơ neo ở mục 4 là quyết định hiện hành; việc áp
   vào dashboard làm trên máy thật (chép mức nguyên bản KDIGO 2024/EULAR từ toàn văn
   TRƯỚC, rồi mới nâng `decision`; ITEM-05 giữ chiều, đối chiếu HR 0,61 bản đã thay).

*Tài liệu do Claude soạn 29/08/2026; nguồn tra qua PubMed cùng ngày. Cần bác sĩ kiểm chứng.*
