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

VÒNG 6 (16/09/2026) — `Path(__file__).resolve().parents[1]` SAI khi `__file__` nằm
trong một GIT WORKTREE PHỤ (`git worktree add`, ví dụ `.claude/worktrees/<tên>/`).
Worktree chỉ có bản checkout riêng của các file GIT-TRACKED; ba gốc dữ liệu ngoài-git
(`EBM-Dashboards`/`EBM_MASTER`/`medical-ebm-automation`) chỉ tồn tại bên cạnh
CHECKOUT CHÍNH trên đĩa, không bên cạnh thư mục worktree. Đo được khi vá template
Dark Analyst từ một worktree: cả ba gốc đều "vắng mặt" theo `ROOT` của worktree dù
máy thật có đủ cả ba — `ban_sao_git_tran()` (nhánh máy-thật) và mọi verifier tính
ROOT rồi cộng thẳng tên ba gốc đều báo SAI SỰ THẬT.

`checkout_chinh()` dò checkout chính bằng CHÍNH cơ chế git dùng cho worktree
(`.git` là FILE trỏ `gitdir:`, rồi đọc `commondir` bên trong) — không suy đoán từ
tên thư mục. `ban_sao_git_tran()` nay kiểm ba gốc CẢ ở `repo` LẪN ở checkout chính
(khi khác `repo`) trước khi kết luận "bản sao trần"; `duong_goc()`/
`duong_cong_cu_pipeline()` KHÔNG đổi (đã có phương án lùi riêng, không nằm trong lỗi
báo cáo lần này).
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


def checkout_chinh(repo: Path = REPO) -> Path | None:
    """Thư mục checkout CHÍNH khi `repo` đang là một git WORKTREE PHỤ.

    VÌ SAO CÓ (16/09/2026, vòng 6) — xem docstring module. Trả về `repo` KHÔNG ĐỔI
    khi `.git` ở gốc là một THƯ MỤC bình thường (repo đã LÀ checkout chính, không
    phải worktree). Khi `.git` là một FILE dạng `gitdir: <path>/.git/worktrees/
    <tên>` — dấu hiệu DUY NHẤT của git cho một worktree phụ — đọc file `commondir`
    bên trong thư mục đó (thường ghi tương đối, kiểu `../..`) để suy ra `.git`
    CHUNG, rồi lấy cha của nó làm checkout chính.

    Trả về `None` khi KHÔNG xác định được (file `.git` dị dạng, `commondir` thiếu
    hoặc trỏ tới nơi không còn tồn tại) — KHÔNG đoán liều (BH08): nơi gọi phải tự
    quyết định cách xử lý "chưa biết", không được coi `None` là "không phải
    worktree" hay ngầm định repo đã là checkout chính.
    """
    git_marker = repo / ".git"
    if git_marker.is_dir():
        return repo
    if not git_marker.is_file():
        return None
    try:
        noi_dung = git_marker.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    tien_to = "gitdir:"
    if not noi_dung.startswith(tien_to):
        return None
    duong_gitdir_worktree = Path(noi_dung[len(tien_to):].strip())
    if not duong_gitdir_worktree.is_absolute():
        duong_gitdir_worktree = (repo / duong_gitdir_worktree).resolve()
    commondir_file = duong_gitdir_worktree / "commondir"
    if not commondir_file.is_file():
        return None
    try:
        commondir_raw = commondir_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not commondir_raw:
        return None
    duong_git_chung = Path(commondir_raw)
    if not duong_git_chung.is_absolute():
        duong_git_chung = (duong_gitdir_worktree / duong_git_chung).resolve()
    if not duong_git_chung.is_dir():
        return None
    ket_qua = duong_git_chung.parent
    return ket_qua if ket_qua.is_dir() else None


def ban_sao_git_tran(repo: Path = REPO) -> bool:
    """True khi bản sao KHÔNG có hạ tầng chỉ-sống-trong-OneDrive (clone tươi/CI/cloud).

    Trên cloud: chỉ đòi EBM-Dashboards + EBM_MASTER vắng mặt — medical-ebm-automation
    NẰM TRONG repo là chuyện BÌNH THƯỜNG trên cloud (đúng kiến trúc lồng nhau thật),
    không phải dấu hiệu máy thật hỏng OneDrive. Nơi khác (CI/máy thật ngoài cloud):
    giữ NGUYÊN đòi CẢ BA gốc vắng — xem "VÒNG 5" trong docstring module.

    VÒNG 6 — khi `repo` là một worktree phụ, ba gốc chỉ tồn tại bên cạnh checkout
    CHÍNH (`checkout_chinh(repo)`), không bên cạnh `repo`. Kiểm CẢ HAI nơi trước
    khi kết luận "bản sao trần", để không báo nhầm một worktree của máy thật thành
    bản sao trần chỉ vì `repo` tự nó không lồng sẵn ba gốc.
    """
    goc_chinh = checkout_chinh(repo)
    thu_muc_kiem = (repo,) if goc_chinh is None or goc_chinh == repo else (repo, goc_chinh)
    if _la_phien_cloud():
        goc_can_kiem = _GOC_LUON_NGOAI_GIT_TREN_CLOUD
    else:
        goc_can_kiem = GOC_DU_LIEU_NGOAI_GIT
    return not any((base / goc).exists() for base in thu_muc_kiem for goc in goc_can_kiem)


def duong_goc(ten: str, repo: Path = REPO) -> Path | None:
    """Đường dẫn THẬT của một gốc dữ liệu ngoài-git (`ten` ∈ GOC_DU_LIEU_NGOAI_GIT).

    Thứ tự ưu tiên: `repo/ten` (lồng theo cây đang chạy — kiến trúc OneDrive cây
    chung của máy thật) → `checkout_chinh(repo)/ten` (VÒNG 6, 16/09/2026 — chỉ
    khác `repo` khi đang ở một git worktree phụ; ba gốc ngoài-git chỉ tồn tại bên
    cạnh checkout CHÍNH, không bên cạnh worktree) → `repo.parent/ten` (anh em —
    một số phiên dựng các repo cạnh nhau dưới cùng một thư mục cha); `None` nếu
    không có ở đâu.
    """
    goc_chinh = checkout_chinh(repo)
    ung_vien: list[Path] = [repo]
    if goc_chinh is not None and goc_chinh != repo:
        ung_vien.append(goc_chinh)
    ung_vien.append(repo.parent)
    for base in ung_vien:
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
