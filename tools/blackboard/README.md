# tools/blackboard — Trình kiểm định schema sổ cái (validator)

> **Mục đích:** siết độ chặt cho hạng mục **1b "Blackboard"** — thực thi (enforce) SCHEMA bản ghi
> của `_SO-EBM-MASTER.md` và hub `EBM_MASTER/EBM_MASTER.json`. Phát hiện bản ghi thiếu trường,
> sai `verification_status`, thiếu nguồn, hoặc trùng khóa **trước khi** đưa vào sổ cái/hub.

## ⚠️ Trạng thái liêm chính — đọc trước
- `validate_ledger.py` là **trình kiểm định offline (lint)**, **KHÔNG** phải message bus cưỡng chế.
- Schema blackboard hiện vẫn là **QUY ƯỚC ở tầng file**: các agent *đồng ý* ghi theo schema; validator
  chỉ **phát hiện vi phạm SAU khi ghi**, không chặn được lúc ghi và không tự sửa dữ liệu.
- ⇒ Hạng mục **1b Blackboard vẫn ở mức MỘT PHẦN** — nay **"MỘT PHẦN chắc hơn"** vì đã có công cụ
  thực thi schema, nhưng chưa đạt mức bus tiến trình cưỡng chế (cần hạ tầng ngoài).
- Công cụ **KHÔNG bịa, KHÔNG tự sửa sổ cái**; mọi chỉnh sửa do bác sĩ duyệt (Cổng B).

## Cách dùng
```bash
python3 validate_ledger.py <ledger.json>        # kiểm 1 file, in báo cáo
python3 validate_ledger.py <ledger.json> --json # in JSON (cho CI/log)
python3 validate_ledger.py --demo               # chạy demo trên dữ liệu synthetic
```
Không cần thư viện ngoài (chỉ thư viện chuẩn Python 3). Quy ước thoát: `0` = không lỗi ĐỎ;
`1` = có ≥1 lỗi ĐỎ (dùng được trong git hook / CI).

## Đầu vào chấp nhận
1. **List** các bản ghi blackboard 8-trường: `[ {...}, {...} ]`
2. **Object** có khóa `records`: `{ "records": [ ... ] }`
3. **Hub** `EBM_MASTER.json` (object có `evidence_cards`) — tự **ánh xạ thẻ → 8 trường**
   (`topic→chu_de`, `date_added→ngay`, `source.{pmid,doi,url}→nguon`, `recommendation`≠rỗng→`loai`=khuyến cáo,
   `impact/decision→phan_loai`, `verification_status` giữ nguyên, `provenance→agent_ghi`).

## 8 trường bắt buộc (theo `_SO-EBM-MASTER.md`)
`id` · `ngay` · `chu_de` · `nguon` · `loai` · `verification_status` · `phan_loai` · `agent_ghi`

## Luật kiểm (tóm tắt)
| Kiểm | Mức | Quy tắc |
|---|---|---|
| Đủ 8 trường | ĐỎ nếu thiếu/rỗng | thiếu dữ liệu phải ghi nhãn `[CẦN BỔ SUNG]` (placeholder → CẢNH BÁO, không ĐỎ) |
| `id` duy nhất | ĐỎ nếu trùng | khóa duy nhất, không tái dùng |
| `verification_status` | ĐỎ nếu ngoài tập | `chưa xác minh` \| `đang xác minh` \| `đã xác minh` |
| `nguon` có nguồn | ĐỎ nếu vừa không PMID/DOI/URL vừa không `[CẦN KIỂM CHỨNG]` | chống bịa / nguồn trống; thiếu **năm** → CẢNH BÁO |
| `loai` / `phan_loai` | CẢNH BÁO nếu ngoài tập | `loai`∈{chứng cứ, khuyến cáo}; `phan_loai`∈{đáng đổi, theo dõi, không đổi} |
| `ngay` dạng | CẢNH BÁO | `YYYY-MM-DD` |
| Khóa dedup | CẢNH BÁO nếu trùng | `pmid \| doi \| chu_de (chuẩn hóa)`; theo schema: trùng → KHÔNG thêm bản ghi mới, chỉ nối bản ghi cập nhật trạng thái trỏ `id` cũ |

## Demo synthetic (đã chạy trong sandbox)
`python3 validate_ledger.py --demo` trên 7 bản ghi synthetic (KHÔNG phải dữ liệu thật):
3 bản ĐẠT · 4 lỗi ĐỎ (thiếu `agent_ghi`; `verification_status="đã duyệt"` sai; nguồn trống; trùng `id`)
· 2 CẢNH BÁO (placeholder `ngay`; khóa PMID trùng). Kết: **TRẢ-VỀ-SỬA**, exit `1`.

File mẫu kèm theo: `sample_synthetic.json` (toàn hợp lệ → PASS) và `sample_hub.json` (định dạng hub).

## Quan hệ với phần còn lại
- Schema gốc: `.claude/agents/_SO-EBM-MASTER.md` (mục "SCHEMA BẮT BUỘC CHO MỖI BẢN GHI").
- Hub nội dung: `EBM_MASTER/EBM_MASTER.json` (Cổng B — thẻ mới luôn `verification_status="chưa xác minh"`).
- Lộ trình & giới hạn: `.claude/agents/_LO-TRINH-HA-TANG.md` (mục blackboard / công cụ ngoài).

> **"Cần bác sĩ kiểm chứng."**
