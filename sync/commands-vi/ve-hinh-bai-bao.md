---
description: "Vẽ hình đạt chuẩn đăng bài: ROC, forest plot, sơ đồ CONSORT/STARD/PRISMA, Kaplan-Meier"
---

Hình cần vẽ: **$ARGUMENTS**

1. Xác định thiết kế, chạy `python3 medical-ebm-automation/tools/ve_bieu_do.py danh-muc --thiet-ke <thiết kế>` để lấy bộ hình bắt buộc theo chuẩn báo cáo.
2. Vẽ bằng đúng lệnh của bảy họ công cụ chủ (`bieu_do_gop`, `bieu_do_chan_doan`, `bieu_do_song_con`, `bieu_do_mo_ta`, `bieu_do_hoi_quy`, `bieu_do_do_luong`, `bieu_do_bao_cao`); thêm `--kiem-cheo-r` khi có R, `--ngon-ngu en` cho bản thảo quốc tế.
3. Kiểm: `python3 medical-ebm-automation/tools/ve_bieu_do.py kiem --thu-muc <thư mục hình> --thiet-ke <thiết kế>` phải mã 0.
Kỹ năng `make-figures` của plugin chỉ là phương án dự phòng cho loại hình các công cụ chủ chưa có.
