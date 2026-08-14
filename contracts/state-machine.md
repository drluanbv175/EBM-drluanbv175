# MÁY TRẠNG THÁI MỤC CHỨNG CỨ (hình thức hoá 15/08/2026 — LÔ 2, bác sĩ duyệt LÔ 0)

> Hình thức hoá cái ĐANG CHẠY, không phát minh luồng mới. Cột "Hiện thân thật" là nơi mỗi
> trạng thái đã tồn tại từ trước — schema chỉ đặt tên thống nhất để kiểm toán được.

```
NEW ──► VERIFIED ──► APPRAISED ──► CANDIDATE ──(BÁC SĨ)──► APPROVED ──► APPLIED
 │          │                          │
 └► UNRESOLVED (nguồn không phân giải) └► DROPPED (nhiễu, kèm lý do)
```

| Trạng thái | Hiện thân thật trong hệ | Ai được đặt |
|---|---|---|
| `NEW` | Ứng viên từ `surveillance_scan` (đã mang nhãn rút bài · loại thiết kế · trùng kho ngay lúc nhận) | máy |
| `VERIFIED` | Có mặt trong `.so-xac-minh-nguon.json` **còn hạn** (tồn tại 180ng · rút bài 30ng) và không `da_rut` | máy |
| `APPRAISED` | Đã qua `tham-dinh-grade-nnt` (3 lớp tách: khuyến cáo nguồn · certainty · operational_assessment) | máy |
| `CANDIDATE` | Item trong dashboard đã PASS `verify_dashboard --online --strict-sources`; thẻ vào **hàng chờ duyệt** EBM_MASTER | máy |
| `APPROVED` | Bác sĩ duyệt (Cổng B / `quan-ly-cap-nhat-ebm` approve) | **CHỈ BÁC SĨ** |
| `APPLIED` | Bác sĩ xác nhận đã áp vào thực hành (Cổng A) | **CHỈ BÁC SĨ** |
| `UNRESOLVED` | PMID/DOI không phân giải được / cổng truy nguyên FAIL — **không vào dashboard** | máy |
| `DROPPED` | Loại có lý do ghi lại (nhiễu, lệch PICO, đã có trong kho) | máy |

## Chuyển tiếp CẤM (thi hành bằng `tools/kiem_hop_dong_item.py`, khoá BH46)

1. **Máy đặt `APPROVED`/`APPLIED`** — hai trạng thái này đòi `human_review.reviewed_by` khác
   null. Validator FAIL bất kỳ item nào `APPROVED|APPLIED` mà thiếu người duyệt (I4).
2. **Nhảy cóc vào `CANDIDATE`** khi `source.resolved != true` — chưa truy nguyên thì chưa
   là ứng viên (I1).
3. **`retracted=true` mà vẫn `CANDIDATE|APPROVED|APPLIED`** — phát hiện rút bài trên item đã
   APPLIED là **điều kiện dừng khẩn**: alert + trình bác sĩ, không tự gỡ (retract-and-replace
   cần đối chiếu bản đã thay, BH34).
4. **`certainty.reported_by_source=false` mà `level != 'na'`** — tự gán mức (I2/BH36).

## Điều kiện dừng khẩn (từ prompt §5, ánh xạ vào cơ chế thật)

| Điều kiện | Cơ chế bắt |
|---|---|
| Mất mạng khi cần `--online` | cổng fail-closed sẵn có; sổ xác minh không ghi thất bại thành công |
| `UNRESOLVED` > 20%/lô | báo trong tổng kết quét — `[CẦN BỔ SUNG]` ngưỡng máy tự chặn |
| Retraction ở item đã APPLIED | quét rút bài THÁNG (hạn 30ng) + `alerts/` |
| Schema drift | `kiem_hop_dong_item.py --self-test` trong canary |
| 2 máy cùng ghi | khoá `.quet.lock` (LÔ 1) — tiến trình sau FAIL rõ, exit 3 |

*Cần bác sĩ kiểm chứng.*
