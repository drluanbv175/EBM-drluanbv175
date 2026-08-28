# `lam-sang/` — gói tiếp cận lâm sàng theo CHỦ ĐỀ (dừng ở Cổng A)

Thư mục này giữ các **gói tiếp cận lâm sàng theo chủ đề/hội chứng** do dây chuyền
`dieu-phoi-lam-sang` soạn: cờ đỏ → PICO → chứng cứ có nguồn → thẩm định → khuyến nghị
**có điều kiện**, và **dừng ở Cổng A** chờ bác sĩ duyệt.

## Khác gì với hai thư mục dễ nhầm

| Thư mục | Nội dung | Vị trí trong dây chuyền |
|---|---|---|
| `lam-sang/` (đây) | Tiếp cận một **hội chứng/chủ đề** (vd viêm đa khớp) | **TRƯỚC Cổng A** — mới là đề xuất |
| `implementation/` | Gói triển khai một **thẻ chứng cứ ĐÃ duyệt** (`EVID-*`) | **SAU Cổng B** — đã vào sổ cái |
| `vn-guidelines/` | Sổ đăng ký **nguồn guideline Việt Nam** | Nguyên liệu đầu vào |

Đặt nhầm gói chờ-duyệt vào `implementation/` sẽ khiến nó trông như đã qua Cổng B —
đúng họ lỗi "vượt cổng" mà R3 của `tham-dinh-dau-ra` sinh ra để chặn.

## Luật của thư mục

1. Mọi khẳng định lâm sàng kèm **PMID/DOI**; không tra được thì ghi `[CẦN KIỂM CHỨNG]`,
   **không bịa**.
2. **KHÔNG tự gán GRADE.** Ghi phân hạng **nguyên bản của nguồn**; nguồn không dùng thang
   phân hạng (tiêu chuẩn phân loại, nhãn thuốc) → ghi `na` + nêu `normativeBasis`.
3. Tách **độ chắc chứng cứ** khỏi **độ mạnh khuyến cáo** — hai trục, không gộp.
4. **KHÔNG PII.** Không tên, tuổi chính xác, số hồ sơ, ngày khám của người bệnh.
5. Mỗi gói kết bằng **"Cần bác sĩ kiểm chứng."** và một khối **Cổng A** còn để trống.
6. Sửa nội dung y khoa của gói đã duyệt = tạo bản mới có ngày, **không** sửa đè lịch sử.

> ⚠️ `.gitignore` của repo dùng lối `/*` (ignore tất cả rồi un-ignore từng mục). Thư mục
> này chỉ theo git được nhờ dòng `!/lam-sang/` — gỡ dòng đó thì mọi file ở đây biến mất
> khỏi git **trong im lặng** (bài học BH70).
