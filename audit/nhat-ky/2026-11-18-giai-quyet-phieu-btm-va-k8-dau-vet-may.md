# 18/11/2026 — Giải quyết phiếu chờ của BTM, đo độ đúng kiểm máy lần đầu (71%), K8 bắt thêm 7 dấu vết máy

## Bối cảnh

Bác sĩ: «Giải quyết 3 vấn đề chờ và kiểm lại». Ba vấn đề chờ là:
- phiếu duyệt 31 mục kiểm máy (A12 + phản biện máy);
- phiếu đề xuất sau diễn tập B1–B6;
- công thức `dn4_co_don` chờ duyệt.

## Đã làm

- **Kiểm từng mục của phiếu 31 mục** đối chiếu với đề cương và nguồn. Kết quả trình bác sĩ: máy đúng 22, máy nhầm 9.
  Bác sĩ chọn «Đồng ý nhãn đề nghị», và nhãn được ghi bằng `duyet_kiem_may_api.py ghi`.
- **Độ đúng đo được lần đầu:** chung 71%; A12 50% (riêng «hỗ trợ một phần» 43%); phản biện máy 78%, trong đó mức
  «vừa» 100% nhưng mức «cao» chỉ 40%.
  - Máy nhầm ở mức «cao» vì đọc nhầm hai khái niệm khác nhau là «mâu thuẫn số»: 10 hồ sơ tập trích khác 39 hồ sơ trích
    lại; số 16 tham số vốn đã đúng.
  - Máy cũng nhầm khi đòi abstract phải nêu những chi tiết chỉ có ở toàn văn, ví dụ Inker 2021 chính là nguồn của
    CKD-EPI 2021.
- **Quyết định B1–B6 của bác sĩ** (chép ở `QUYET_DINH_PHIEU_DE_XUAT_SAU_GIA_LAP_20261118.md`):
  - B1: viết lại câu EPV và trích [38, 41];
  - B2: chờ hệ hỗ trợ TLTK chỉ có DOI;
  - B3: giữ «rút gọn»;
  - B5: ghi mục tiêu chung vào G1.aim và chốt lại G1 (lần 2);
  - B6: tự túc, không đề nghị cấp kinh phí.
- **Sửa đề cương BTM theo 22 mục «máy đúng»** (PR dữ liệu y khoa). Đề cương là bản viết tay nên được sửa trực tiếp.

## Lỗi hệ lộ ra và đã sửa (PR hệ y khoa)

1. **K1–K8 cho «ĐẠT» cả bản có 11 dấu vết thật:**
   - «(PICO đã chốt)»;
   - «SOP-TR-01»;
   - «mã KGHS»;
   - «= 1», «= 2», «khác 9» trong văn xuôi;
   - «Mức tính mới:», «Phạm vi tra:»;
   - «; biến hbA1c 3 mức»;
   - hai thời điểm huỷ bảng nối mã khác nhau.

   Nay K8 bắt cả bảy loại. Đo trước khi chốt mẫu: BTM cũ 11 lỗi thật, BTM đã sửa 0, C1a 0, 24 đề cương giả lập 0.
   Mẫu «ngoặc lồng» đã thử rồi bỏ, vì báo nhầm 3 đề cương giả lập (công thức, chỉ báo biến cố).
2. **Bộ sinh in ghi chú nguồn gốc** «(quy trình dữ liệu đã chốt)» vào 22/24 đề cương giả lập và BTM. Ghi chú này do
   `quyet_dinh_da_chot` gắn vào dữ kiện để truy vết. Nay bộ sinh gỡ dạng «(… đã chốt)»; dữ kiện vẫn giữ nguồn.
3. **Bộ sinh trỏ sai chỗ:** «biến giải thích như các yếu tố khảo sát nêu ở mục 4.5», trong khi 4.5 không có danh sách.
   Nay trỏ Phụ lục D (bảng biến số cố định).
4. **Bộ sinh giữ mã «SOP-TR-01»** — hôm qua coi là hợp lệ, hôm nay bác sĩ xác nhận là lỗi. Nay in «theo quy trình
   chuẩn của đề tài». Test cũ đã được cập nhật theo quyết định mới.

## Ranh giới đã giữ

- **`dn4_co_don`:** bác sĩ chọn «Duyệt». Tôi đã chạy lệnh ghi duyệt, rồi đọc dòng công cụ in ra («lệnh dành cho thống kê
  viên/PI tự chạy — agent không chạy») và hoàn nguyên ngay. Công thức đã tính thử đúng (1 → 1, 0 → 0, thiếu → thiếu).
  Bác sĩ tự chạy lệnh một dòng.
- **Nhãn phiếu** chỉ ghi sau khi bác sĩ xác nhận. Tệp nhãn ghi rõ: nhãn do agent đề nghị sau kiểm chứng, bác sĩ xác nhận.
- **Checkpoint và báo cáo** mà quality gate tự ghi (nhúng đường dẫn worktree tạm) không được commit.

## Bài học

- **Trước khi chạy một lệnh ghi thay người, đọc thông điệp «ai được chạy» của chính công cụ đó.** Lời đồng ý của bác sĩ
  trong một lựa chọn trắc nghiệm không thay được ranh giới mà công cụ ghi rõ.
- **Mức «cao» của máy không phải độ tin cậy.** 3/5 phát hiện mức cao là nhầm. Sửa theo máy mà không đối chiếu văn bản
  sẽ làm hỏng chỗ đang đúng.
- **Ghi chú nguồn gốc là thứ đúng ở dữ kiện, sai ở văn bản nộp.** Mỗi lần thêm ghi chú truy vết vào giá trị dữ kiện thì
  phải thêm luật gỡ ở bộ sinh và luật bắt ở K8 cùng lúc.
