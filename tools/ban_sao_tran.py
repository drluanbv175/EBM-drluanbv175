#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MỘT định nghĩa DUY NHẤT cho «bản sao git trần» — dùng chung cho mọi chốt/verifier.

VÌ SAO CÓ (28/08/2026, vòng 4 — bình duyệt đối kháng trên chính diff của phiên):
trong MỘT PR, năm bản sao của phép thử «có phải bản sao trần không» đã tự phân kỳ
thành HAI ngữ nghĩa — bộ chốt bài học + conftest đòi cả BA gốc dữ liệu vắng mặt,
còn ba verifier trong hook pre-commit chỉ kiểm MỘT gốc (medical-ebm-automation/).
Hệ quả đo được: trên máy thật còn EBM-Dashboards/ + EBM_MASTER/ nhưng thiếu riêng
repo y khoa (đúng kiểu sự cố OneDrive đã gặp — thư mục bị conflict-rename, selective
sync, máy mới đồng bộ dở), cả ba cổng hook thoát 0 ⇒ commit đi qua mà KHÔNG một phép
đối chiếu chéo repo nào chạy — fail-open đúng nghĩa. Nhân bản một phép thử là nhân
bản chỗ cho nó phân kỳ; từ nay chỉ MỘT nơi định nghĩa.

Ngữ nghĩa: bản sao trần = KHÔNG MỘT gốc dữ liệu ngoài-git nào có mặt. Còn ≥1 gốc
nghĩa là đây là máy thật (hoặc máy thật đang hỏng dở) — mọi thiếu hụt phải ĐỎ như cũ.
Mất cả ba gốc cùng lúc trên máy thật là sự cố cây OneDrive — việc của
sync_safety_check (làn ①), không phải của các chốt dùng helper này.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Ba gốc dữ liệu nằm ngoài git (kiến trúc code→GitHub · dữ liệu→OneDrive).
GOC_DU_LIEU_NGOAI_GIT = ("EBM-Dashboards", "medical-ebm-automation", "EBM_MASTER")


def ban_sao_git_tran(repo: Path = REPO) -> bool:
    """True CHỈ khi cả BA gốc dữ liệu ngoài-git đều vắng mặt (clone tươi/CI/cloud)."""
    return not any((repo / goc).exists() for goc in GOC_DU_LIEU_NGOAI_GIT)
