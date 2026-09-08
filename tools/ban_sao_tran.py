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


def duong_goc(ten: str, repo: Path = REPO) -> Path | None:
    """Đường dẫn THẬT của một gốc dữ liệu ngoài-git (`ten` ∈ GOC_DU_LIEU_NGOAI_GIT).

    Ưu tiên vị trí LỒNG (`repo/ten` — kiến trúc OneDrive cây chung của máy thật),
    rồi tới vị trí ANH EM (`repo.parent/ten` — một số phiên dựng các repo cạnh
    nhau dưới cùng một thư mục cha); `None` nếu không có ở đâu.
    """
    for base in (repo, repo.parent):
        candidate = base / ten
        if candidate.exists():
            return candidate
    return None


def duong_cong_cu_pipeline(ten_file: str, repo: Path = REPO) -> Path | None:
    """Đường dẫn THẬT của một tool trong dây chuyền dashboard (verify_dashboard.py,
    build_dashboard_docx.py, build_library.py, make_derivatives.py…).

    VÁ 08/09/2026 — `tools/xuat_goi_cap_nhat.py` (lệnh «một cửa» CLAUDE.md dạy bác
    sĩ chạy) chỉ từng tìm các tool này ở ĐÚNG MỘT nơi — `EBM-Dashboards/tools/`
    (doctrine-canonical, đồng bộ qua OneDrive, KHÔNG BAO GIỜ có trong một checkout
    thuần git) — nên trên checkout git-only (worktree không lồng cây OneDrive,
    clone tươi, CI, phiên cloud) lệnh này dừng ngay ở bước ĐẦU TIÊN dù các bản
    VENDOR QUA GIT của CHÍNH những tool đó (`sync/skills/cap-nhat-chung-cu-y-khoa/
    tools/`) chạy tốt.

    Ưu tiên bản doctrine-canonical (máy thật); vắng mặt thì lùi về bản git-vendor
    (LUÔN có trên mọi checkout kể cả cloud/CI). `None` nếu không có ở đâu — gọi
    nơi cần dùng phải tự báo rõ, không giả định resolver này luôn trả về một
    đường dẫn.
    """
    goc = duong_goc("EBM-Dashboards", repo)
    if goc is not None:
        ung_vien = goc / "tools" / ten_file
        if ung_vien.exists():
            return ung_vien
    vendor = repo / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / ten_file
    if vendor.exists():
        return vendor
    return None
