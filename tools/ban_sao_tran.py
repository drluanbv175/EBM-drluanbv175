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

VÁ 07/09/2026 — SIBLING CHECKOUT TRÊN PHIÊN CLOUD KHÔNG ĐƯỢC NHẬN DIỆN (mục #105
còn treo từ đợt audit 148 mục). Bản đầu chỉ kiểm `repo / goc` (LỒNG bên trong repo)
— trên phiên cloud, `add_repo` dựng các repo ở CÙNG một thư mục cha dưới dạng ANH EM
(sibling), không lồng vào nhau. Đo trực tiếp trên chính phiên phát hiện lỗi này:
`/home/user/EBM-drluanbv175` (repo gốc) và `/home/user/medical-ebm-automation`
(clone thật, `git remote` xác nhận `drluanbv175/medical-ebm-automation`, cây làm
việc sạch, đã đồng bộ `origin`) là HAI THƯ MỤC ANH EM dưới `/home/user/` — kiểm
`repo / "medical-ebm-automation"` mãi mãi rỗng dù dữ liệu thật đang nằm ngay cạnh.
Hệ quả: `ban_sao_git_tran()` báo "bản trần" SAI trên một phiên có đủ dữ liệu thật,
khiến hàng loạt verifier (qua `upgrade_verify.py` bước 9-24) tự hạ xuống ⚪ NGOÀI
PHẠM VI thay vì chạy kiểm thật — chiều SAI của BH08 (biến "có dữ liệu" thành "coi
như không biết"), không phải chiều báo-động-giả nhưng vẫn làm mù mọi cổng phụ
thuộc. Đã vá: kiểm CẢ `repo / goc` (lồng) LẪN `repo.parent / goc` (anh em cùng
thư mục cha) — chỉ THÊM một đường phát hiện, không bớt đường cũ, nên không làm
yếu lại phép thử "vắng cả ba gốc" mà BH82/BH83 đã khoá.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Ba gốc dữ liệu nằm ngoài git (kiến trúc code→GitHub · dữ liệu→OneDrive).
GOC_DU_LIEU_NGOAI_GIT = ("EBM-Dashboards", "medical-ebm-automation", "EBM_MASTER")


def ban_sao_git_tran(repo: Path = REPO) -> bool:
    """True CHỈ khi cả BA gốc dữ liệu ngoài-git đều vắng mặt (clone tươi/CI/cloud).

    Kiểm cả vị trí LỒNG (`repo/goc` — máy thật, kiến trúc OneDrive cây chung) lẫn
    vị trí ANH EM (`repo.parent/goc` — phiên cloud, các repo được `add_repo` dựng
    cạnh nhau dưới cùng một thư mục cha) — xem "VÁ 07/09/2026" ở docstring module.
    """
    return all(duong_goc(goc, repo) is None for goc in GOC_DU_LIEU_NGOAI_GIT)


def duong_cong_cu_pipeline(ten_file: str, repo: Path = REPO) -> Path | None:
    """Đường dẫn THẬT của một tool trong dây chuyền dashboard (verify_dashboard.py,
    build_library.py, make_derivatives.py, surveillance_scan.py…).

    VÁ 08/09/2026 — CRITICAL: `tools/xuat_goi_cap_nhat.py` (lệnh «một cửa» CLAUDE.md
    dạy bác sĩ chạy) và canary `tools/thu_dau_cuoi_chung_cu.py` chỉ từng tìm các tool
    này ở ĐÚNG MỘT nơi — `EBM-Dashboards/tools/` (doctrine-canonical, đồng bộ qua
    OneDrive, KHÔNG BAO GIỜ có trong bất kỳ git checkout nào) — nên trên phiên cloud
    (hay bất kỳ clone git-only nào) cả hai đều dừng ngay ở bước ĐẦU TIÊN dù các bản
    VENDOR QUA GIT của CHÍNH những tool đó (`sync/skills/cap-nhat-chung-cu-y-khoa/
    tools/`, giữ đồng bộ bằng `dong_bo_scanner_giam_sat.py`) chạy TỐT trên máy này.

    Ưu tiên bản doctrine-canonical (máy thật); vắng mặt thì lùi về bản git-vendor
    (LUÔN có trên mọi checkout kể cả cloud/CI). `None` nếu không có ở đâu — một số
    tool (vd `build_dashboard_docx.py`) chưa từng được vendor qua git, xem
    CLAUDE.md/audit về khoảng trống đó; gọi nơi cần dùng phải tự báo rõ, không giả
    định resolver này luôn trả về một đường dẫn.
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


def duong_goc(ten: str, repo: Path = REPO) -> Path | None:
    """Đường dẫn THẬT của một gốc dữ liệu ngoài-git (`ten` ∈ GOC_DU_LIEU_NGOAI_GIT).

    Ưu tiên vị trí LỒNG (`repo/ten`), rồi tới vị trí ANH EM (`repo.parent/ten`);
    `None` nếu không có ở đâu. MỘT nơi giải quyết đường dẫn — mọi chốt/verifier
    cần mở file bên trong `medical-ebm-automation`/`EBM-Dashboards`/`EBM_MASTER`
    PHẢI gọi hàm này thay vì tự ghép `repo / "medical-ebm-automation"` (đúng lỗi
    đã gây fail-open/fail-closed-sai được vá 07/09/2026 — xem docstring module).
    """
    for base in (repo, repo.parent):
        candidate = base / ten
        if candidate.exists():
            return candidate
    return None
