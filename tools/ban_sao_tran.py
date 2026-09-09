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

VÒNG 5 (09/09/2026) — «medical-ebm-automation» không còn là tín hiệu đáng tin trên
CLOUD. Trước đó, phiên cloud clone `medical-ebm-automation` như SIBLING (không lồng
trong EBM-drluanbv175) nên gốc này vắng mặt trên MỌI phiên cloud — đúng ngẫu nhiên
với ngữ nghĩa ba-gốc. Sau khi kiến trúc lồng nhau thật được nối đúng trên một phiên
cloud (medical-ebm-automation NẰM TRONG EBM-drluanbv175/, đúng bố cục Mac/Windows —
CẦN THIẾT để nhiều verifier khác chẩn đoán đúng), gốc này LUÔN có mặt trên phiên đó,
trong khi EBM-Dashboards/EBM_MASTER vẫn LUÔN vắng — hai gốc đó CHỈ sống trong
OneDrive, không bao giờ đi qua git dù trên máy nào. Kết quả đo: ~8 verifier báo ĐỎ
một cách hệ thống trên MỌI phiên cloud tương lai kể từ đó, dù không có gì hỏng thật
— đúng loại «bức tường đỏ giả» BH08 cảnh báo.

Trên CLOUD (`la_phien_cloud()` — tín hiệu MÔI TRƯỜNG qua `CLAUDE_CODE_REMOTE`, không
suy từ cấu trúc thư mục, cùng nguồn nhận diện máy mà BH86 đã dùng để cài đủ plugin
trên cloud), chỉ đòi EBM-Dashboards + EBM_MASTER vắng mặt — medical-ebm-automation
có mặt hay không không còn là tín hiệu đáng tin ở đây. Trên máy KHÔNG PHẢI cloud
(CI/Mac/Windows thật), giữ NGUYÊN ngữ nghĩa ba-gốc cũ không nới lỏng — đây vẫn là
nơi duy nhất bắt được máy thật đang hỏng dở cây OneDrive (sự cố gốc mà vòng 4 vá).
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Ba gốc dữ liệu nằm ngoài git (kiến trúc code→GitHub · dữ liệu→OneDrive).
GOC_DU_LIEU_NGOAI_GIT = ("EBM-Dashboards", "medical-ebm-automation", "EBM_MASTER")

# Trên CLOUD: chỉ hai gốc này VĨNH VIỄN không đi qua git ở bất kỳ máy nào — xem
# docstring module, "VÒNG 5". medical-ebm-automation bị loại khỏi danh sách này
# CHỈ trên nhánh cloud của ban_sao_git_tran(); nhánh máy-thật vẫn dùng đủ ba gốc.
_GOC_LUON_NGOAI_GIT_TREN_CLOUD = ("EBM-Dashboards", "EBM_MASTER")


def _la_phien_cloud() -> bool:
    """Nạp tools/nhan_dien_may.py CÙNG THƯ MỤC bằng đường dẫn file — không phụ thuộc
    sys.path của nơi gọi. ban_sao_tran.py tự nó được ~9 nơi nạp bằng
    importlib.util.spec_from_file_location (không phải `import` thường), nên không
    thể giả định `tools/` đã có sẵn trong sys.path lúc module này chạy; nạp kiểu
    tương đối-theo-__file__ giữ ban_sao_tran.py tự-chứa, đúng khuôn các module khác
    trong tools/ đã dùng khi nạp lẫn nhau."""
    import importlib.util
    duong = Path(__file__).resolve().parent / "nhan_dien_may.py"
    if not duong.is_file():
        return False  # thiếu nguyên liệu ⇒ không suy đoán, giữ nhánh máy-thật (BH08)
    spec = importlib.util.spec_from_file_location("_bst_nhan_dien_may", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return bool(mod.la_phien_cloud())


def ban_sao_git_tran(repo: Path = REPO) -> bool:
    """True khi bản sao KHÔNG có hạ tầng chỉ-sống-trong-OneDrive (clone tươi/CI/cloud).

    Trên cloud: chỉ đòi EBM-Dashboards + EBM_MASTER vắng mặt — medical-ebm-automation
    NẰM TRONG repo là chuyện BÌNH THƯỜNG trên cloud (đúng kiến trúc lồng nhau thật),
    không phải dấu hiệu máy thật hỏng OneDrive. Nơi khác (CI/máy thật ngoài cloud):
    giữ NGUYÊN đòi CẢ BA gốc vắng — xem "VÒNG 5" trong docstring module.
    """
    if _la_phien_cloud():
        return not any((repo / goc).exists() for goc in _GOC_LUON_NGOAI_GIT_TREN_CLOUD)
    return not any((repo / goc).exists() for goc in GOC_DU_LIEU_NGOAI_GIT)
