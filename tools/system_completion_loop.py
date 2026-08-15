#!/usr/bin/env python3
"""Điểm vào chính cho vòng lặp kiểm tra–hoàn thiện toàn hệ EBM.

Logic được giữ tại ``clinical_production_loop.py`` để tương thích với các lịch và
lệnh cũ. File này chỉ là bí danh mỏng, không tạo thêm một owner điều phối.
"""

from clinical_production_loop import main


if __name__ == "__main__":
    raise SystemExit(main())
