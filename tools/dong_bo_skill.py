#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đồng bộ skill từ NGUỒN biên tập sang nơi Claude THẬT SỰ CHẠY.

VÌ SAO CÓ (13/08/2026)
======================
Bác sĩ sửa skill ở `sync/skills/` (nguồn biên tập, có git). Nhưng lệnh
`/anthropic-skills:<tên>` chạy một bản KHÁC nằm ở

    ~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/
        <uuid>/<uuid>/skills/<tên>/

và **không có cơ chế nào tự đẩy** từ nguồn sang đó. Hậu quả đo được ngày
13/08/2026: **20/22 skill riêng của bác sĩ đang chạy bản khác với nguồn**, chỉ 2
khớp. `cap-nhat-chung-cu-y-khoa` chạy v1.12.0 trong khi nguồn đã v1.15.0 —
tức toàn bộ bản vá cổng nguồn, bài học "73 mục bị che" và tài liệu source
universe đều CHƯA tới nơi bác sĩ thật sự gọi.

Điều này giải thích một lớp bực bội lặp lại: gọi skill và nhận hành vi cũ,
trong khi tài liệu nói về bản mới.

QUYẾT ĐỊNH CHIỀU: THEO NỘI DUNG, KHÔNG THEO mtime
==================================================
Cạm bẫy đã đo: 6 skill có mtime runtime MỚI HƠN nguồn (đều đúng mốc
`21/06 18:12`) — nhưng đó là dấu thời gian DỰNG LẠI HÀNG LOẠT, không phải nội
dung mới. Kiểm theo nội dung thì `tham-dinh-chung-cu-grade-nnt` runtime có **0
dòng riêng** trong khi nguồn nhiều hơn 1388 byte. Tin mtime sẽ chặn nhầm, hoặc
tệ hơn nếu đảo chiều thì ghi đè mất bản đầy đủ.

Nên luật là:
  • runtime KHÔNG có dòng nào riêng  → nguồn là bản bao trùm → ĐẨY (an toàn)
  • runtime CÓ dòng riêng            → phân kỳ hai chiều → CHẶN, chờ người xem
Không bao giờ tự hợp nhất hai chiều: mất nội dung y khoa nguy hiểm hơn nhiều
so với việc phải xem tay vài file.

Dùng:
    python3 tools/dong_bo_skill.py              # xem trước, KHÔNG ghi gì
    python3 tools/dong_bo_skill.py --ap-dung    # thật sự đẩy (có sao lưu)
    python3 tools/dong_bo_skill.py --im-khi-on  # chỉ nói khi lệch (dùng cho hook)

Mã thoát: 0 = mọi skill khớp · 1 = có skill lệch · 2 = có skill phân kỳ hai chiều.

🔴 TRẦN KIẾN TRÚC ĐÃ XÁC NHẬN BẰNG TÀI LIỆU CHÍNH THỨC (16/09/2026) — nhánh
COWORK CỦA CÔNG CỤ NÀY CHỈ ĐẨY ĐƯỢC, KHÔNG GIỮ ĐƯỢC.
=====================================================
Đo trực tiếp: 18:08:00 (đúng đỉnh chu kỳ 20 phút) app xoá "25 orphans cleaned"
— quét sạch mọi skill vừa được lệnh này đẩy vào phút trước, chỉ chừa lại đúng
những skill ĐÃ CÓ SẴN trong `manifest.json` của app (`creatorType:"user"`).
Đọc thẳng mã ứng dụng (`app.asar`, hàm nội bộ lấy "N enabled skills") xác nhận
danh sách đó tới từ gọi API thật:
`GET /api/organizations/{org}/skills/list-skills?...&entrypoint=local-agent` —
TỨC LÀ danh sách **Custom Skills đã đăng ký ở tài khoản claude.ai**
(Customize → Skills), KHÔNG PHẢI file trên đĩa. Tài liệu chính thức xác nhận
đúng điều này: *"Cowork loads the ones enabled for your claude.ai account,
synced at session start, and doesn't read the Claude Code CLI's ~/.claude
directory on your machine. To use a skill or plugin that exists only in
~/.claude, add it in Customize."* — https://claude.com/docs/cowork/overview.md

**Hệ quả: mọi skill được `--ap-dung` đẩy vào nơi chạy Cowork mà KHÔNG có mặt
trong danh sách tài khoản chỉ tồn tại tới lượt đồng bộ định kỳ kế tiếp**
(`skillsSyncIntervalMs`, mặc định 1.200.000 ms = 20 phút, đo qua log
`[SkillsPlugin] Starting periodic sync`). Đây KHÔNG phải lỗi phân kỳ nội dung
để sửa bằng cách so sánh kỹ hơn — sao lưu đúng chỗ, lọc đúng file, đẩy đúng
nội dung đều không đổi kết quả, vì app coi thư mục này là TẤM GƯƠNG của tài
khoản, không phải nơi ghi tự do. Việc dời `*.bak-*` ra ngoài
(`doi_sao_luu_ra_ngoai`) vẫn đúng và nên giữ — nó chỉ không giải quyết được
trần kiến trúc này.

**Đường CHÍNH THỐNG để một skill riêng sống sót qua mọi chu kỳ Cowork** —
không cái nào tự động hoá được thẳng từ `sync/skills/` bằng CLI/API: tài liệu
nói rõ *"Custom Skills do not sync across surfaces"* và *"Skills uploaded
through the API are not available on claude.ai"* —
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
  (a) tải tay từng skill dạng ZIP ở **Customize → Skills** trên claude.ai/
      Desktop (https://support.claude.com/en/articles/12512180-use-skills-in-claude)
      — cho đúng `/anthropic-skills:<tên>`, nhưng KHÔNG API/CLI để tự đẩy lại
      sau mỗi lần sửa `sync/skills/`, phải tải lại tay;
  (b) gói CẢ BỘ thành một plugin trong repo Git, thêm bằng **Customize →
      Plugins → Add marketplace** (owner/repo) — gần mô hình "một nguồn Git,
      cập nhật bằng git push" hơn, và đường plugin CÓ cảnh báo trước khi ghi
      đè sửa cục bộ (đường skill-sync KHÔNG có) —
      https://claude.com/docs/cowork/guide/plugins.md — nhưng CHƯA xác nhận
      marketplace tự thêm có theo được sang máy khác hay phải thêm lại từng máy;
  (c) tài khoản Team/Enterprise: admin cấp phát skill/plugin tổ chức, tới
      được cả Cowork —
      https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization

**Kênh KHÔNG bị ảnh hưởng, đã đo còn nguyên:** `~/.claude/skills/` (Claude Code
CLI/tab Code) là symlink trỏ thẳng `sync/skills/` — cơ chế hoàn toàn khác, do
`dong_bo_skill_claude_codex.py` phụ trách; tài liệu xác nhận Cowork "doesn't
read... ~/.claude" còn Code tab đọc thư mục đó "for local sessions". Giới hạn
ở trên CHỈ áp cho nhánh Cowork của chính file này — không đổi hành vi/luật
ĐẨY-hay-CHẶN đã có, chỉ đổi mức kỳ vọng: một skill "CẦN ĐẨY" thành công vẫn
CẦN ĐẨY LẠI mỗi khi hết hạn khung ≤20 phút, trừ khi cũng được đăng ký ở một
trong ba đường trên. Xem chốt BH104 (`chot_hoi_quy_bai_hoc.py`).
"""
from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def goc_repo_chinh(tu: Path | None = None) -> Path:
    """Gốc repo CHÍNH — không phải git worktree phụ đang chứa file này.

    `git rev-parse --git-common-dir` trả `.git` của repo chính dù gọi từ worktree
    nào; git không gọi được (thiếu binary, không phải repo) thì lùi về thư mục cha
    của `tu`. Cùng cách với `dong_bo_skill_claude_codex._resolve_repo_root` (08/09).

    VÌ SAO CÔNG CỤ NÀY CŨNG CẦN (16/09/2026): nơi chạy Cowork DÙNG CHUNG cho mọi phiên
    trên máy, nhưng mỗi phiên mở trong `.claude/worktrees/<tên>` chạy bản
    `tools/*.py` CỦA worktree đó. Bản vá 08/09 chỉ đưa đường `sync_cowork` về repo
    chính; đường `tu_sua_chua.py` → `dong_bo_skill.py` vẫn chạy mã + nguồn của
    worktree. Ca thật 16/09 17:09:12: worktree HEAD `0ec62fc` (trước bản vá 13/09)
    chép đè bản cũ lên nơi chạy và để lại 23 thư mục `.bak` ngay trong đó."""
    here = tu if tu is not None else Path(__file__).resolve().parent
    try:
        r = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=10, check=True,
            encoding="utf-8", errors="replace",
        )
        common = Path(r.stdout.strip())
        if common.is_dir():
            return common.parent
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return here.parent


REPO = Path(__file__).resolve().parents[1]      # cây chứa CHÍNH file mã đang chạy
GOC_CHINH = goc_repo_chinh()
# Nguồn đẩy sang nơi chạy dùng chung = `sync/skills` của repo CHÍNH — cùng nguồn mà
# `~/.claude/skills`/`~/.codex/skills` đang trỏ tới. Nguồn lấy theo worktree thì hai
# phiên ở hai cây khác nhau có thể thay nhau đẩy hai phiên bản (dấu hiệu đo được:
# `dark-analyst` có 8 bản sao lưu trong 14–16/09, hai bản cách nhau 8 giây lúc 17:14).
# Repo chính không có `sync/skills` (clone trần…) thì lùi về cây của chính file.
NGUON = (GOC_CHINH / "sync/skills") if (GOC_CHINH / "sync/skills").is_dir() else (REPO / "sync/skills")
GOC_RUNTIME = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"


def cong_cu_dong_bo_cowork() -> Path:
    """Bản `dong_bo_skill.py` được phép GHI nơi chạy Cowork: bản trong repo CHÍNH.

    `tu_sua_chua.py` gọi hàm này thay vì tự trỏ `tools/dong_bo_skill.py` của cây
    mình, để một worktree lạc hậu không thể chạy MÃ cũ lên nơi chạy dùng chung (đúng
    ca 16/09 17:09:12). Repo chính không có công cụ thì trả chính file này."""
    ung_vien = GOC_CHINH / "tools" / "dong_bo_skill.py"
    return ung_vien if ung_vien.is_file() else Path(__file__).resolve()

BO_QUA = {".DS_Store", "__pycache__", ".claude"}

# VÁ 14/08/2026 — BỎ QUA THEO MẪU TÊN, không chỉ theo thành phần đường dẫn.
# `BO_QUA` so trên `f.parts` nên không bao giờ bắt được một TÊN FILE như
# `verify_dashboard.py.bak-20260814-005720`. Hệ quả đo được: **8 file sao lưu do
# CHÍNH quy trình đồng bộ này tạo ra đã bị đẩy vào thư mục skill ĐANG CHẠY**, nằm
# ngay cạnh bản sống. Không gây lỗi chạy (đuôi `.bak-*` không import được), nhưng
# kho sẽ phình mãi và một bản CŨ của công cụ an toàn nằm cạnh bản mới là thứ gây
# hiểu nhầm cho bất kỳ ai mở thư mục đó ra xem.
BO_QUA_MAU = ("*.bak-*", "*.orig", "*.rej", "*~")


def _bi_bo_qua(f: Path, goc: Path) -> bool:
    """VÁ 16/09/2026 — so `BO_QUA` trên đường dẫn TƯƠNG ĐỐI với `goc`, không trên
    đường dẫn tuyệt đối. Bản cũ nhận `goc` mà không dùng; `.claude` nằm trong
    `BO_QUA` (để bỏ thư mục `.claude/` riêng của một skill) nên khớp luôn đoạn
    `.claude/worktrees/` của MỌI worktree ⇒ chạy từ worktree thì 505/505 file nguồn
    bị lọc, cả 50 skill báo «KHOP» trên phép so rỗng (BH09 xanh giả), còn nhánh đẩy
    trọn thì chép không qua lọc."""
    import fnmatch
    try:
        phan = f.relative_to(goc).parts
    except ValueError:
        phan = f.parts
    if any(x in phan for x in BO_QUA):
        return True
    return any(fnmatch.fnmatch(f.name, m) for m in BO_QUA_MAU)


def tim_runtime() -> Path | None:
    """Tìm thư mục skills đang chạy. Đường dẫn có 2 tầng UUID do Claude sinh ra,
    nên dò thay vì viết cứng — UUID đổi khi bác sĩ nạp lại bộ skill."""
    if not GOC_RUNTIME.is_dir():
        return None
    ung_vien = sorted(GOC_RUNTIME.glob("*/*/skills"),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    return ung_vien[0] if ung_vien else None


def duong_dan_sao_luu(runtime: Path, ten_skill: str, stamp: str) -> Path:
    """Đường dẫn sao lưu NẰM NGOÀI thư mục skill mà Claude Desktop quét — cùng
    khuôn `dong_bo_skill_claude_codex.py::backup_path()` đã dùng cho đường
    symlink `~/.claude/skills`/`~/.codex/skills` (docstring hàm đó: "Tạo đường
    dẫn sao lưu nằm ngoài thư mục skill đang được quét").

    VÌ SAO CÓ (13/08/2026 tạo bug, vá 13/09/2026): trước bản vá này, `--ap-dung`
    gọi `shutil.copytree(dst, dst.parent / f"{k}.bak-{stamp}", ...)` — sao lưu
    NGAY TRONG `runtime` (chính thư mục Claude Desktop coi mỗi thư mục con là
    MỘT skill ứng viên). Mỗi lần đẩy tạo thêm một "skill" rác tên
    `<ten_skill>.bak-<stamp>` (Claude hiển thị thành
    `<ten_skill>-bak-<stamp>` trong danh sách skill gọi được, dấu chấm đổi
    thành gạch ngang) — đo thật 13/09/2026: 3 mục rác
    (`cap-nhat-chung-cu-y-khoa.bak-20260913-174830` và 2 mục khác) lọt vào danh
    sách skill của phiên model, gây nhầm lẫn cho cả bác sĩ lẫn Claude. Bug này
    ĐÃ được vá cho đường symlink (`ensure_link`/`backup_path`) từ trước nhưng bị
    bỏ sót ở đường Cowork runtime — cùng họ lỗi «vá một nơi, quên nơi kia» đã
    lặp lại nhiều lần trong repo này.

    Thư mục sao lưu là SIBLING của `runtime` (`<runtime>-backup`, không phải
    `<runtime>/...`), nên KHÔNG khớp glob `*/*/skills` mà `tim_runtime()` dùng
    và KHÔNG nằm trong `runtime.iterdir()` mà Claude Desktop quét làm skill."""
    thu_muc = runtime.parent / f"{runtime.name}-backup"
    thu_muc.mkdir(parents=True, exist_ok=True)
    return thu_muc / f"{ten_skill}.bak-{stamp}"


def muc_sao_luu_sai_cho(runtime: Path) -> list[Path]:
    """Mọi mục tên `*.bak-*` — THƯ MỤC lẫn FILE — đang nằm TRONG nơi chạy (BH22).

    Chỉ trả mục «gốc»: con của một mục đã liệt kê thì bỏ, vì dời thư mục cha là
    dời luôn con.

    VÌ SAO PHẢI ĐẾM CẢ THƯ MỤC (16/09/2026): BH22 cũ chỉ lọc `is_file()`, nên nó
    XANH trong khi 23 thư mục `<tên>.bak-20260916-170912` nằm ngay trong nơi chạy
    và Claude chào ra 23 skill trùng `anthropic-skills:<tên>-bak-20260916-170912`.
    Thư mục sao lưu mới là thứ app nạp nhầm thành skill — bỏ sót nó là bỏ sót
    đúng loại gây hại."""
    goc: list[Path] = []
    for p in sorted(runtime.rglob("*.bak-*"), key=lambda x: (len(x.parts), str(x))):
        if any(q in p.parents for q in goc):
            continue
        goc.append(p)
    return goc


def doi_sao_luu_ra_ngoai(runtime: Path) -> list[tuple[Path, Path]]:
    """DỜI (không xoá) mọi mục `*.bak-*` sai chỗ sang `<runtime>-backup/`, giữ
    nguyên đường dẫn tương đối — đúng thư mục `duong_dan_sao_luu` ghi vào.

    VÌ SAO TỰ LÀM Ở `--ap-dung`, VÀ VÌ SAO DỜI CHỨ KHÔNG XOÁ (16/09/2026):
    • Mục sai chỗ không chỉ đến từ mã cũ của CHÍNH cây này. Mọi git worktree dựng
      TRƯỚC bản vá 13/09 vẫn mang `dong_bo_skill.py` cũ, và hook SessionStart của
      phiên mở trong worktree đó chạy công cụ CỦA worktree. Ca thật 16/09 17:09:12:
      phiên resume ở worktree HEAD `0ec62fc` → `tu_sua_chua.py` → `dong_bo_skill.py`
      cũ → 23 thư mục `.bak` ngay trong nơi chạy. Từ đây không sửa được mã của cây
      khác, nên bản mới phải tự dọn hậu quả mỗi lần được gọi.
    • Ứng dụng Claude tự xoá mọi thư mục KHÔNG có trong manifest của nó, định kỳ
      20 phút (`[SkillsPlugin] ... orphans cleaned` — đo 16/09 17:28:00: 48 mục =
      23 `.bak` + 25 skill riêng). Bản sao lưu để trong nơi chạy vì vậy mất trong
      ≤20 phút, tức nó CHƯA BAO GIỜ thực sự là bản sao lưu; dời ra ngoài mới giữ
      được nội dung.
    Trùng tên ở đích thì thêm hậu tố `.trung-N` — không bao giờ ghi đè."""
    kho = runtime.parent / f"{runtime.name}-backup"
    da_doi: list[tuple[Path, Path]] = []
    for p in muc_sao_luu_sai_cho(runtime):
        dich = kho / p.relative_to(runtime)
        n = 1
        while dich.exists() or dich.is_symlink():
            dich = dich.with_name(f"{p.name}.trung-{n}")
            n += 1
        dich.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dich))
        da_doi.append((p, dich))
    return da_doi


def don_bak(runtime: Path) -> int:
    """`--don-bak`: đưa mọi mục `*.bak-*` (BH22) ra khỏi thư mục skill đang chạy.

    Từ 16/09/2026 hàm này DỜI sang `<runtime>-backup/` (qua `doi_sao_luu_ra_ngoai`)
    thay vì `rmtree`: thư mục sao lưu là bản DUY NHẤT của nội dung runtime trước
    một lượt đẩy — xoá nó là xoá dữ liệu, còn dời thì vừa sạch danh sách skill vừa
    giữ nội dung.

    Lịch sử giữ lại vì nó giải thích BH75: bản gốc chỉ biết `.unlink()`; gặp THƯ MỤC
    `.bak-*` (do bản CŨ của `--ap-dung` trước 13/09 sao lưu bằng
    `shutil.copytree(dst, dst.parent / f"{k}.bak-{stamp}", ...)`) thì macOS ném
    `PermissionError` — dễ đọc nhầm thành lỗi quyền hệ thống — và cả lượt dọn chết
    giữa chừng (vá 25/08/2026; đo được 17 mục rác tồn đọng từ 13/08).
    `shutil.move` xử lý được cả thư mục lẫn file. Trả về số mục đã dời."""
    return len(doi_sao_luu_ra_ngoai(runtime))


def _bam(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _dong_rieng(a: Path, b: Path) -> tuple[int, int]:
    """Trả (số dòng CHỈ có ở a, số dòng CHỈ có ở b). So theo TẬP DÒNG nên không
    bị ảnh hưởng bởi việc di chuyển đoạn — điều duy nhất cần biết ở đây là
    'có nội dung nào sẽ MẤT nếu ghi đè không'."""
    try:
        ta = set(a.read_text(encoding="utf-8", errors="replace").splitlines())
        tb = set(b.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return (0, 0)
    return (len(ta - tb), len(tb - ta))


def _doc_ver(p: Path) -> tuple[int, ...] | None:
    """Đọc `version:` trong frontmatter SKILL.md, trả tuple so sánh được."""
    import re
    try:
        t = p.read_text(encoding="utf-8", errors="replace")[:3000]
    except OSError:
        return None
    m = re.search(r'^\s*version:\s*"?(\d+(?:\.\d+)*)', t, re.M)
    if not m:
        return None
    return tuple(int(x) for x in m.group(1).split("."))


def nguon_moi_hon_theo_ver(nguon: Path, runtime: Path) -> bool:
    """Nguồn có số phiên bản CAO HƠN runtime không?

    VÌ SAO CẦN LUẬT NÀY: khi nguồn là bản nâng cấp (1.12.0 → 1.15.0), câu chữ cũ
    của runtime đương nhiên là "dòng riêng" — nhưng đó là nội dung ĐÃ ĐƯỢC VIẾT
    LẠI, không phải nội dung sẽ mất. Nếu chỉ đếm dòng riêng thì mọi lần nâng cấp
    đều bị chặn oan, và skill sẽ mãi không bao giờ được cập nhật.

    Một lần tăng số phiên bản là lời tuyên bố "bản này thay bản kia". Tôn trọng
    tuyên bố đó, NHƯNG vẫn sao lưu trước khi ghi — để nếu sai còn lấy lại được.
    Không có số phiên bản ở một trong hai bên → không suy đoán, giữ nguyên chặn.
    """
    vn, vr = _doc_ver(nguon / "SKILL.md"), _doc_ver(runtime / "SKILL.md")
    return bool(vn and vr and vn > vr)


def so_mot_skill(nguon: Path, runtime: Path) -> dict:
    """So một skill. Trả trạng thái + danh sách file cần đẩy."""
    can_day: list[Path] = []
    phan_ky: list[tuple[Path, int]] = []      # (file, số dòng runtime sẽ mất)
    for f in sorted(nguon.rglob("*")):
        if not f.is_file() or _bi_bo_qua(f, nguon):
            continue
        rel = f.relative_to(nguon)
        dich = runtime / rel
        if not dich.exists():
            can_day.append(rel)
            continue
        if filecmp.cmp(f, dich, shallow=False):
            continue
        _, rieng_runtime = _dong_rieng(f, dich)
        if rieng_runtime > 0:
            phan_ky.append((rel, rieng_runtime))
        else:
            can_day.append(rel)
    if phan_ky:
        # Nguồn là bản NÂNG CẤP có tuyên bố rõ → câu chữ cũ của runtime là nội
        # dung đã được viết lại, không phải nội dung bị mất. Đẩy cả, có sao lưu.
        if nguon_moi_hon_theo_ver(nguon, runtime):
            return {"trang_thai": "CAN_DAY_NANG_CAP",
                    "day": can_day + [r for r, _ in phan_ky], "phan_ky": []}
        return {"trang_thai": "PHAN_KY", "day": can_day, "phan_ky": phan_ky}
    if can_day:
        return {"trang_thai": "CAN_DAY", "day": can_day, "phan_ky": []}
    return {"trang_thai": "KHOP", "day": [], "phan_ky": []}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ skill nguồn → nơi chạy")
    ap.add_argument("--ap-dung", action="store_true",
                    help="thật sự ghi (mặc định chỉ xem trước)")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi mọi skill đã khớp (dùng cho hook)")
    ap.add_argument("--don-bak", action="store_true",
                    help="dời *.bak-* còn sót trong NƠI CHẠY sang <runtime>-backup/ "
                         "(BH22: app nạp nhầm thành skill; KHÔNG xoá)")
    ap.add_argument("--nguon-la-chuan", action="store_true",
                    help="phân kỳ hai chiều thì NGUỒN thắng (vẫn sao lưu trước khi "
                         "ghi). Mặc định KHÔNG bật: chạy riêng thì phân kỳ phải chặn "
                         "để bác sĩ xem. Chỉ bộ hợp nhất dong_bo_skill_claude_codex.py "
                         "mới truyền cờ này — đúng hợp đồng đã ghi ở AGENTS.md §Đồng bộ "
                         "skill/plugin: «nguồn OneDrive thắng runtime Cowork nhưng bản "
                         "cũ luôn được sao lưu».")
    a = ap.parse_args(argv)

    runtime = tim_runtime()
    if a.don_bak and runtime:
        n = don_bak(runtime)
        print(f"✓ dời {n} mục .bak khỏi nơi chạy sang {runtime.name}-backup/ (BH22, không xoá)")
        if not a.ap_dung:
            return 0
    if runtime is None:
        if not a.im_khi_on:
            print("⚠ Không tìm thấy thư mục skill đang chạy — bỏ qua.")
        return 0

    sai_cho = muc_sao_luu_sai_cho(runtime)
    ket: dict[str, dict] = {}
    for d in sorted(NGUON.iterdir()):
        if not d.is_dir() or not (d / "SKILL.md").exists():
            continue
        rt = runtime / d.name
        if not rt.is_dir():
            ket[d.name] = {"trang_thai": "THIEU_HAN", "day": [], "phan_ky": []}
            continue
        ket[d.name] = so_mot_skill(d, rt)

    khop = [k for k, v in ket.items() if v["trang_thai"] == "KHOP"]
    can_day = [k for k, v in ket.items() if v["trang_thai"] in ("CAN_DAY", "CAN_DAY_NANG_CAP", "THIEU_HAN")]
    phan_ky = [k for k, v in ket.items() if v["trang_thai"] == "PHAN_KY"]

    if a.im_khi_on and not can_day and not phan_ky and not sai_cho:
        return 0

    tu_repo_chinh = GOC_CHINH != REPO and NGUON == GOC_CHINH / "sync/skills"
    print(f"ĐỒNG BỘ SKILL — nguồn: sync/skills{' (repo chính)' if tu_repo_chinh else ''}"
          f" · nơi chạy: …/{runtime.parent.name[:8]}/skills")
    print(f"  khớp {len(khop)} · cần đẩy {len(can_day)} · phân kỳ hai chiều {len(phan_ky)}"
          + (f" · sao lưu nằm sai chỗ {len(sai_cho)}" if sai_cho else ""))

    if sai_cho:
        print(f"\n▸ {len(sai_cho)} MỤC SAO LƯU nằm TRONG nơi chạy (BH22) — app nạp nhầm "
              "thành skill «…-bak-…»; --ap-dung sẽ DỜI (không xoá) sang "
              f"{runtime.name}-backup/:")
        for p in sai_cho[:5]:
            print(f"   {p.relative_to(runtime)}")
        if len(sai_cho) > 5:
            print(f"   … và {len(sai_cho) - 5} mục khác")

    if can_day:
        print("\n▸ CẦN ĐẨY (nguồn bao trùm, runtime không có nội dung riêng):")
        for k in can_day:
            n = len(ket[k]["day"]) or "toàn bộ"
            print(f"   {k:44s} {n} file")

    if phan_ky:
        if a.nguon_la_chuan:
            print("\n▸ PHÂN KỲ HAI CHIỀU — nguồn được chọn làm chuẩn, sao lưu trước khi ghi:")
        else:
            print("\n⚠ PHÂN KỲ HAI CHIỀU — KHÔNG tự đẩy, cần bác sĩ xem:")
        for k in phan_ky:
            for rel, mat in ket[k]["phan_ky"]:
                print(f"   {k}/{rel}: runtime có {mat} dòng sẽ MẤT nếu ghi đè")

    if not a.ap_dung:
        if can_day or phan_ky or sai_cho:
            print("\n(Chưa ghi gì. Thêm --ap-dung để đẩy nhóm an toàn và dời sao lưu sai chỗ.)")
        return 2 if phan_ky else (1 if (can_day or sai_cho) else 0)

    # --- Ghi thật, có sao lưu ---
    # Dời sao lưu sai chỗ TRƯỚC khi đẩy: copytree sao lưu một skill không được cuốn
    # theo `.bak-*` con đang nằm lẫn trong nó.
    da_doi = doi_sao_luu_ra_ngoai(runtime)
    if da_doi:
        print(f"\n✓ Đã dời {len(da_doi)} mục sao lưu khỏi nơi chạy sang "
              f"{runtime.name}-backup/ (không xoá).")
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    da_day = 0
    # Skill phân kỳ chỉ vào danh sách ghi khi bác sĩ (hoặc bộ hợp nhất) đã chọn
    # nguồn làm chuẩn. Chúng được đẩy TRỌN nguồn: danh sách "day" của một skill
    # phân kỳ chỉ là phần giao, đẩy phần giao thì runtime vẫn giữ dòng riêng và
    # lần chạy sau lại báo phân kỳ y như cũ.
    if a.nguon_la_chuan:
        for k in phan_ky:
            ket[k]["day"] = []
        can_day = can_day + phan_ky
    for k in can_day:
        src, dst = NGUON / k, runtime / k
        if dst.exists():
            shutil.copytree(dst, duong_dan_sao_luu(runtime, k, stamp), dirs_exist_ok=True)
        # Nhánh đẩy TRỌN skill (thiếu hẳn ở nơi chạy, hoặc phân kỳ + --nguon-la-chuan)
        # PHẢI đi qua CÙNG bộ lọc `_bi_bo_qua` với `so_mot_skill` — trước 16/09/2026
        # nhánh này chép thẳng `src.rglob("*")`, nên một file `*.bak-*`/`__pycache__`
        # nằm trong nguồn vẫn bị đẩy vào nơi chạy: đúng lỗi gốc BH22 (14/08), chỉ là
        # đi đường vòng qua nhánh không ai canh.
        toan_bo = [p.relative_to(src) for p in src.rglob("*")
                   if p.is_file() and not _bi_bo_qua(p, src)]
        for rel in (ket[k]["day"] or toan_bo):
            f, d = src / rel, dst / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)
            da_day += 1
    if can_day:
        print(f"\n✓ Đã đẩy {da_day} file cho {len(can_day)} skill "
              f"(sao lưu ở {runtime.name}-backup/*.bak-{stamp}, KHÔNG nằm trong "
              "thư mục skill đang chạy).")
    if phan_ky and not a.nguon_la_chuan:
        print(f"⚠ Bỏ qua {len(phan_ky)} skill phân kỳ hai chiều — chưa đụng tới.")
        return 2
    if phan_ky:
        print(f"  Trong đó {len(phan_ky)} skill phân kỳ đã bị nguồn ghi đè theo "
              f"--nguon-la-chuan; bản runtime cũ nằm ở {runtime.name}-backup/*.bak-{stamp}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
