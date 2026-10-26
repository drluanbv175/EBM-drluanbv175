# 26/10/2026 — Word ⑨: tiêu đề «nguy cơ sai lệch» cho AGREE II và màu ngược chiều cho AMSTAR-2

**Phát hiện.** Kiểm chéo độc lập PMID 42799440 (văn bản quan điểm FIGO/WHF, thẩm định bằng AGREE II) báo: mức miền «thấp» in dưới
tiêu đề mục «Thẩm định nguy cơ sai lệch — AGREE II» dễ bị đọc thành «nguy cơ sai lệch thấp», tức NGƯỢC nghĩa, vì AGREE II đo chất
lượng phương pháp (cao = tốt). Soát hàm tô màu `_mau_danh_gia` lộ thêm lỗi cùng họ: chỉ AGREE được đảo chiều màu, còn AMSTAR-2 (đo
ĐỘ TIN CẬY, cao = tốt) thì không, nên «Độ tin cậy thấp theo AMSTAR-2» bị tô xanh lá như «nguy cơ thấp». Thêm nữa, câu tổng thể hay
kể số đếm nghiên cứu gốc («22 thấp, 18 cao, 35 không rõ»; «51 nguy cơ thấp, 104 nguy cơ cao») nên màu nhãn TỔNG THỂ bị kéo lệch.
Ở PMID 37142273 màu chỉ tình cờ ra cam nhờ chữ «không rõ»; ở PMID 37696529 («CAO» + «thấp»/«cao» trong số đếm) nhãn ra màu navy
trung tính.

**Cách vá** (`tools/tom_tat_chung_cu_word.py`):
- `_do_chat_luong(cong_cu)`: AGREE II và AMSTAR-2 là công cụ đo chất lượng/độ tin cậy ⇒ đảo chiều màu. ROBIS, RoB, ROBINS, QUADAS
  giữ chiều cũ.
- Tiêu đề mục: AGREE II ⇒ «Thẩm định chất lượng phương pháp — AGREE II»; công cụ khác giữ «Thẩm định nguy cơ sai lệch — …».
- Màu nhãn TỔNG THỂ tính sau khi bỏ các cụm «<số> [nguy cơ] thấp/cao/không rõ» (`_bo_so_dem_nc_goc`).

**Kiểm hồi quy.** Test `test_agree_ii_tieu_de_chat_luong_va_amstar_dao_chieu_mau`: 3 đột biến (tiêu đề cũ · bỏ AMSTAR khỏi nhóm đảo
chiều · không lọc số đếm) đều đỏ đúng chỗ rồi xanh lại; 44 test của công cụ đạt; ruff sạch. Word đã dựng trước bản vá
(37696529, 37142273) chỉ khác màu nhãn TỔNG THỂ; nội dung không đổi.
