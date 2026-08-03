# Lộ trình làm trọn một đề tài nghiên cứu

> Gọi lần lượt từ trên xuống. Mỗi dòng là một lệnh gõ được ngay sau dấu `/`.
> Xem mình đang ở đâu: `/lo-trinh-de-tai <mã đề tài>`

Có **hai lộ trình**, chọn theo loại đề tài:
- **A — Nghiên cứu gốc** (quan sát, can thiệp, chẩn đoán, tiên lượng): có thu thập dữ liệu bệnh nhân
- **B — Tổng quan hệ thống / phân tích gộp**: tổng hợp từ y văn đã công bố

Cách nhanh nhất cho cả hai: gọi **`/lam-nghien-cuu <tên đề tài>`** — nhạc trưởng
`dieu-phoi-nghien-cuu` tự chạy tuần tự và tự dừng đúng ở các cổng. Lộ trình dưới đây là
bản chi tiết để bác sĩ tự đi từng bước, hoặc để biết nhạc trưởng đang làm gì.

---

## Điều quan trọng nhất: 6 cổng cần NGƯỜI ký

Sáu cổng này **không phần mềm nào vượt qua thay bác sĩ được**. Chúng là ranh giới giữa
"máy soạn giúp" và "người chịu trách nhiệm":

| Cổng | Nội dung | Ai ký |
|---|---|---|
| **G2** | Đạo đức + đăng ký nghiên cứu | Hội đồng Đạo đức |
| **G4** | Khoá kế hoạch phân tích (SAP) | Thống kê viên hoặc chủ nhiệm |
| **G5** | Khoá cơ sở dữ liệu | Chủ nhiệm / quản lý dữ liệu |
| **G8** | Bình duyệt độc lập | Người phản biện ngoài nhóm |
| **G9** | Liêm chính tác giả, COI | Chủ nhiệm |
| **G10** | Khoá gói nộp | Chủ nhiệm |

Ký bằng `python tools/approve_gate.py --gate <G> …` trong `medical-ebm-automation/`.
Sau khi ký, sổ cái được niêm phong — sửa tay file sổ cái sẽ làm **mọi cổng của đề tài bị chặn**.

---

## A — Nghiên cứu gốc

### Giai đoạn 1: Đặt vấn đề (trước khi chạm dữ liệu)

| # | Việc | Gọi | Xong khi có |
|---|---|---|---|
| 1 | Tìm khoảng trống, biện minh tính mới | `/tim-khoang-trong` | Câu trả lời "y văn còn thiếu gì" |
| 2 | **Cổng G0** — chuyển thành câu hỏi PICO/PECO | `/dat-cau-hoi-nghien-cuu` | PICO rõ + kết cục chính/phụ + chấm FINER |
| 3 | Tổng quan y văn nền | `/tong-quan-y-van` | Phần tổng quan có PMID/DOI |
| 4 | **Cổng G1** — chọn thiết kế, kiểm soát sai lệch | `/thiet-ke-de-tai` | Thiết kế + khung phân tích |
| 5 | **Cổng G3** — tính cỡ mẫu | `/tinh-co-mau` | N kèm NGUỒN effect size |
| 6 | Đặc tả biến số, dựng CRF | `/dat-bien-so` | Bộ biến xuất được sang REDCap |

> Bước 5 hay bị bỏ qua nguồn effect size. Không có nguồn thì cổng G3 sẽ chặn — đúng như thiết kế.

### Giai đoạn 2: Hồ sơ pháp lý — **cổng ký G2**

| # | Việc | Gọi |
|---|---|---|
| 7 | Hồ sơ Hội đồng Đạo đức, phiếu đồng thuận, đăng ký nghiên cứu, kế hoạch dữ liệu | `/lam-ho-so-dao-duc` |
| 8 | **Nộp hội đồng và chờ phê duyệt thật** | (ngoài hệ thống) |
| 9 | Ký cổng G2 sau khi có quyết định | `approve_gate.py --gate G2` |

**Không thu thập dữ liệu trước khi G2 được ký.**

### Giai đoạn 3: Dữ liệu — **cổng ký G4, G5**

| # | Việc | Gọi |
|---|---|---|
| 10 | Khoá kế hoạch phân tích trước khi nhìn dữ liệu | `/thiet-ke-de-tai` → ký **G4** |
| 11 | Sinh từ điển dữ liệu ngay khi nhận dữ liệu | `/tu-dien-du-lieu` |
| 12 | Làm sạch, có bác sĩ duyệt từng quyết định | `/lam-sach-du-lieu` |
| 13 | Khử định danh trước khi phân tích | `/khu-dinh-danh` |
| 14 | Khoá cơ sở dữ liệu | `/khoa-du-lieu` → ký **G5** |

> Khoá SAP **trước** khi xem dữ liệu là điều phân biệt nghiên cứu với việc dò tìm kết quả đẹp.

### Giai đoạn 4: Phân tích và diễn giải

| # | Việc | Gọi |
|---|---|---|
| 15 | **Cổng G6** — chạy đúng SAP đã khoá | `/chay-thong-ke` |
| 16 | Dựng Bảng 1 (đặc điểm nền) | `/lam-bang-mot` |
| 17 | Vẽ hình đạt chuẩn đăng bài | `/ve-hinh-bai-bao` |
| 18 | Chuyển con số thành ý nghĩa lâm sàng | `/dien-giai-so-lieu` |

### Giai đoạn 5: Bản thảo

| # | Việc | Gọi |
|---|---|---|
| 19 | **Cổng G7** — viết IMRAD bám chuẩn báo cáo | `/viet-bai-bao` |
| 20 | Đối chiếu 47 chuẩn báo cáo | `/kiem-chuan-bao-cao` |
| 21 | Xác minh mọi PMID/DOI, tra bài bị rút | `/kiem-trich-dan` |
| 22 | Gọt tiếng Anh học thuật | `/got-tieng-anh` |
| 23 | Xoá dấu vết văn phong máy | `/xoa-dau-vet-ai` |
| 24 | Tự rà bằng con mắt phản biện | `/tu-ra-bai` |

### Giai đoạn 6: Bình duyệt và nộp — **cổng ký G8, G9, G10**

| # | Việc | Gọi |
|---|---|---|
| 25 | Thử phản biện nội bộ | `/nho-phan-bien` |
| 26 | **Gửi người phản biện thật ngoài nhóm** → ký **G8** | (ngoài hệ thống) |
| 27 | Chọn tạp chí đích | `/chon-tap-chi` |
| 28 | Khai tác giả, COI, khai dùng AI → ký **G9** | `/nop-bai` |
| 29 | Đóng gói nộp → ký **G10** | `/nop-bai` |
| 30 | Khi có góp ý: soạn thư phản hồi từng điểm | `/tra-loi-phan-bien` |

---

## B — Tổng quan hệ thống / phân tích gộp

| # | Việc | Gọi |
|---|---|---|
| 1 | Tìm và gọt chủ đề | `/tim-chu-de-gop` |
| 2 | Chuyển thành câu hỏi PICO | `/dat-cau-hoi-nghien-cuu` |
| 3 | **Đăng ký PROSPERO trước khi sàng lọc** | `/dang-ky-tong-quan` |
| 4 | Tìm y văn, khử trùng lặp | `/tong-quan-y-van` |
| 5 | Sàng lọc + đánh giá nguy cơ sai lệch | `/sang-loc-nghien-cuu` |
| 6 | Trích xuất dữ liệu | `/gop-tron-goi` (chặng 5) |
| 7 | Chạy gộp: hiệu ứng, I², sai lệch công bố | `/phan-tich-gop` |
| 8 | Kiểm PRISMA/MOOSE, GRADE SoF | `/kiem-prisma` |
| 9 | Viết bản thảo | `/viet-bai-bao` |
| 10 | Từ bước 20 của lộ trình A trở đi | như trên |

> Chạy trọn một mạch: `/gop-tron-goi <chủ đề>`. Nhưng dây chuyền meta-pipe **không có
> cổng G0–G10**; đề tài định nộp tạp chí nên đi lộ trình có cổng.

---

## Ba việc luôn đúng, ở mọi bước

1. **Không PII** — không ghi họ tên, ngày sinh, số hồ sơ vào bất kỳ đâu.
2. **Mọi khẳng định y khoa kèm PMID/DOI** và dòng "Cần bác sĩ kiểm chứng".
3. **Cổng ký là người, không phải phần mềm** — máy soạn hồ sơ, bác sĩ và hội đồng chịu trách nhiệm.

## Xem mình đang ở đâu

```bash
python tools/study_readiness.py --study <mã đề tài>
```

Nó đếm việc **chưa làm** từ chính tài liệu của đề tài, nêu quyết định còn treo, và chỉ ghi
"ĐÃ KÝ" khi sổ cái xác nhận thật — cố ý bi quan, không bao giờ tự kết luận "sẵn sàng".
