#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đồng bộ skill tự động giữa nguồn git, Claude Code, Codex và Cowork.

Nguồn duy nhất là ``sync/skills``. Claude Code và Codex dùng liên kết trực tiếp,
nên sửa file hiện có có hiệu lực ngay. Skill mới được nối ở SessionStart hoặc
watcher nền. Runtime Cowork được cập nhật bằng công cụ fail-closed hiện có.

CHẠY ĐƯỢC TRÊN CẢ HAI MÁY từ 21/08/2026. Trước đó bản này tự chặn Windows ngay ở
dòng đầu ``main()`` (``if os.name == "nt": return 1``) nên «một lệnh đồng bộ» chỉ
tồn tại trên Mac; Windows phải chạy tay ``link-skills.ps1`` và **không có đường nào
nối Codex**. Nay việc tạo liên kết giao cho ``tools/lien_ket_da_nen.py`` — symlink
trên macOS, junction trên Windows (``os.symlink`` ném WinError 1314 khi máy chưa bật
Developer Mode, đã đo trên chính máy Windows này 17/08/2026).

BA BƯỚC PHỤ KHÔNG ĐƯỢC GIẾT CẢ LỆNH (vá 21/08). Ba nhánh dưới đây từng trả mã lỗi
làm hỏng toàn bộ lượt chạy vì trỏ vào thứ KHÔNG có trong repo:
  · ``rebuild_router``/``package_router`` → ``sync/skills/plugin-router-chatgpt``
  · ``sync_plugins``   → ``tools/dong_bo_plugin_claude_codex.py`` (nay đã có)
  · ``sync_cowork``    → cờ ``--nguon-la-chuan`` chưa từng tồn tại trong
    ``dong_bo_skill.py`` (đã bổ sung đúng hợp đồng ghi ở AGENTS.md)
Việc CHÍNH của lệnh này là nối skill vào hai runtime; một bước phụ thiếu nguyên
liệu phải được BÁO RÕ chứ không được biến lượt nối skill thành công thành thất bại.
Riêng bước phụ HỎNG (chạy nhưng trả lỗi) vẫn fail-closed như cũ.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lien_ket_da_nen as LK           # noqa: E402  (cần sau khi chỉnh sys.path)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def _resolve_repo_root(start_dir: Path | None = None) -> Path:
    """Tìm gốc repo CHÍNH, không phải nơi file này đang nằm.

    Nếu phiên đang chạy TRONG một git worktree phụ (``.claude/worktrees/<tên>``
    — Claude Code tự dựng khi cô lập một phiên/agent), ``Path(__file__).resolve()``
    trỏ vào worktree đó, không phải repo chính. Trước bản vá này, "gốc repo" được
    suy trực tiếp từ vị trí file (``parents[1]``) — nghĩa là chạy lệnh đồng bộ
    TRONG một worktree phụ sẽ lấy ``sync/skills`` của CHÍNH worktree đó (một bản
    sao độc lập, có thể cũ hơn nhánh chính) rồi nối nó vào ``~/.claude/skills`` và
    ``~/.codex/skills`` — hai đường dẫn DÙNG CHUNG cho MỌI phiên trên máy. Kết quả
    đo được thật (08/09/2026): 2 skill hoàn toàn vắng mặt khỏi danh sách được chào
    ra ở một phiên KHÁC, vì runtime bị một phiên worktree ghi đè sang bản cũ của
    chính nó — đúng nguyên nhân "mỗi lần một kiểu" bác sĩ báo.

    ``git rev-parse --git-common-dir`` luôn trả về đường dẫn ``.git`` của repo
    CHÍNH dù gọi từ worktree nào (khác ``--git-dir``, vốn trả về thư mục quản trị
    RIÊNG của từng worktree) — dùng nó để luôn quy về đúng một gốc, bất kể phiên
    đang đứng ở worktree nào. Git không gọi được (thiếu binary, không phải repo
    git) thì lùi về cách cũ, không làm chết lệnh.
    """
    here = start_dir if start_dir is not None else Path(__file__).resolve().parent
    try:
        result = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=10, check=True,
            encoding="utf-8", errors="replace",
        )
        git_common_dir = Path(result.stdout.strip())
        if git_common_dir.is_dir():
            return git_common_dir.parent
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return here.parent


REPO = _resolve_repo_root()
DEFAULT_SOURCE = REPO / "sync/skills"
ROUTER_NAME = "plugin-router-chatgpt"
SO_KHAI = REPO / "sync/plugin-manifest.json"


@dataclass(frozen=True)
class LinkResult:
    """Kết quả của một liên kết skill."""

    runtime: str
    skill: str
    status: str
    detail: str = ""


def skill_sources(source: Path) -> list[Path]:
    """Liệt kê các skill nguồn hợp lệ theo thứ tự ổn định."""

    if not source.is_dir():
        raise RuntimeError(f"Không tìm thấy nguồn skill: {source}")
    return sorted(
        (item for item in source.iterdir() if item.is_dir() and (item / "SKILL.md").is_file()),
        key=lambda item: item.name.casefold(),
    )


def backup_path(destination: Path, name: str) -> Path:
    """Tạo đường dẫn sao lưu nằm ngoài thư mục skill đang được quét."""

    root = destination.parent / f"{destination.name}-backup"
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}.bak-{stamp}"


def ensure_link(source: Path, destination: Path, apply: bool) -> LinkResult:
    """Nối một skill vào một runtime; thư mục thật được sao lưu trước khi thay.

    Dùng ``LK.la_lien_ket`` chứ KHÔNG dùng ``Path.is_symlink()``: trên Windows
    junction không phải symlink nên ``is_symlink()`` trả False, và bản cũ vì thế
    coi junction đã nối là «thư mục thật» → sao lưu rồi nối lại ở MỌI lượt chạy.
    Với hook ``SessionStart`` thì đó là một bản .bak mỗi phiên mở máy.

    Liên kết đã có nhưng TRỎ SAI/TREO (dangling) tự phục hồi khi ``apply=True``:
    gỡ điểm nối cũ bằng ``LK.go`` (không đụng dữ liệu đích, chỉ tháo liên kết) rồi
    tạo lại bằng ``LK.tao``. Thiếu nhánh này thì hook ``SessionStart`` kẹt vĩnh
    viễn ở ``XUNG_DOT`` (mã thoát 2) mỗi lần mở máy nếu liên kết từng lệch một lần
    — dời chỗ clone repo, OneDrive ghi đè, cài tay — vì bản thân hook không có
    cách nào khác để tự sửa.
    """

    target = destination / source.name
    label = destination.parent.name
    if LK.la_lien_ket(target):
        if LK.tro_dung(target, source):
            return LinkResult(label, source.name, "KHOP")
        if not apply:
            return LinkResult(label, source.name, "XUNG_DOT",
                              f"{LK.kieu()} đang trỏ nơi khác: {target}")
        truoc = LK.dich_cua(target)
        LK.go(target)
        LK.tao(source, target)
        return LinkResult(label, source.name, "DA_NOI",
                          f"đã sửa {LK.kieu()} trỏ sai (trước trỏ: {truoc})")
    if target.exists():
        if not apply:
            return LinkResult(label, source.name, "CAN_NOI", "đang là thư mục/file thật")
        backup = backup_path(destination, source.name)
        backup.parent.mkdir(parents=True, exist_ok=True)
        LK.sao_luu_ra_ngoai(target, backup.parent, backup.name.split(".bak-", 1)[1])
        LK.tao(source, target)
        return LinkResult(label, source.name, "DA_NOI", f"đã sao lưu tại {backup}")
    if not apply:
        return LinkResult(label, source.name, "CAN_NOI", "chưa tồn tại")
    LK.tao(source, target)
    return LinkResult(label, source.name, "DA_NOI")


def co_codex_tren_may() -> bool:
    """Máy này có Codex để hỏi «plugin nào đang cài» không (cùng ứng viên build_catalog dùng).

    KHÔNG suy từ thông điệp lỗi của build_catalog (BH82: khai báo tường minh, không đoán
    qua chuỗi) — hỏi thẳng sự có mặt của binary hoặc cấu hình dự phòng.
    """
    ung_vien = (
        os.environ.get("EBM_CODEX_BIN"),
        __import__("shutil").which("codex"),
        "/Applications/ChatGPT.app/Contents/Resources/codex",
        str(Path.home() / ".local/bin/codex"),
    )
    if any(u and Path(u).is_file() for u in ung_vien):
        return True
    return (Path.home() / ".codex/config.toml").is_file()


def co_the_dung_cache_claude_code() -> bool:
    """Máy này có cache Claude Code để build_catalog.py dùng làm TẦNG BA dự phòng không
    (thêm 05/09/2026, cùng lúc build_catalog.py học cách đọc thẳng cache này).

    Chỉ hỏi NGUYÊN LIỆU tối thiểu (installed_plugins.json tồn tại) — không tự đoán nó
    còn ĐỦ plugin hay không, việc đó để build_catalog.py tự fail-closed nếu thiếu.
    """
    return (Path.home() / ".claude/plugins/installed_plugins.json").is_file()


def _ten_may() -> str:
    """'Mac' | 'Windows' | 'Cloud' | … — MỘT nguồn duy nhất là tools/nhan_dien_may.py (cùng sổ khai plugin)."""
    import nhan_dien_may as NM             # cùng thư mục tools/ (sys.path đã chỉnh ở đầu tệp)
    return NM.ten_may()


def plugin_id_router(script: Path) -> tuple[str, ...]:
    """Danh sách plugin mà build_catalog.py đòi — đọc TĨNH hằng ``PLUGIN_IDS`` bằng ``ast``, không chạy mã của nó.

    Trả ``()`` khi không đọc được: không biết ≠ không thiếu — nơi gọi coi ``()`` là «không quyết được»
    và KHÔNG bỏ qua gì (build_catalog.py vẫn chạy và tự fail-closed).
    """
    try:
        cay = ast.parse(script.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return ()
    for nut in cay.body:
        if isinstance(nut, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PLUGIN_IDS" for t in nut.targets):
            try:
                gia_tri = ast.literal_eval(nut.value)
            except ValueError:
                return ()
            if isinstance(gia_tri, (tuple, list)) and all(isinstance(x, str) for x in gia_tri):
                return tuple(gia_tri)
    return ()


def plugin_thieu_tren_may(ids: tuple[str, ...]) -> list[str] | None:
    """Trong ``ids``, plugin nào máy này KHÔNG có trong cache Claude Code (không có mục, hoặc ``installPath`` không
    phải thư mục). Đọc CÙNG nguồn với build_catalog.py tầng ba: ``~/.claude/plugins/installed_plugins.json``.

    ``None`` = không đọc được tệp (không biết) — nơi gọi KHÔNG được bỏ qua dựa trên ``None``.
    """
    tep = Path.home() / ".claude/plugins/installed_plugins.json"
    try:
        payload = json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    bang = payload.get("plugins") if isinstance(payload, dict) else None
    if not isinstance(bang, dict):
        return None
    thieu: list[str] = []
    for pid in ids:
        muc = bang.get(pid)
        entry = muc[0] if isinstance(muc, list) and muc else None
        duong = entry.get("installPath") if isinstance(entry, dict) else None
        if not duong or not Path(str(duong)).is_dir():
            thieu.append(pid)
    return thieu


def plugin_thieu_ma_may_nay_khong_can(script: Path) -> list[str]:
    """Plugin router thiếu trên máy này mà sổ khai ``sync/plugin-manifest.json`` xác nhận máy này KHÔNG cần.

    Chỉ trả danh sách khác rỗng khi MỌI plugin thiếu đều như vậy. ``[]`` = không bỏ qua được — một trong:
    không thiếu gì · có plugin thiếu mà máy này ĐƯỢC KHAI là cần (mất thật) · plugin không có trong sổ khai
    (chưa ai khai ý định) · ``can_o_may`` rỗng/không đọc được · không đọc được danh sách/cache/sổ khai.
    Mọi trường hợp «không biết» đều rơi về ``[]`` ⇒ build_catalog.py vẫn chạy và tự fail-closed như trước.
    """
    ids = plugin_id_router(script)
    if not ids:
        return []
    thieu = plugin_thieu_tren_may(ids)
    if not thieu:
        return []
    try:
        muc_khai = (json.loads(SO_KHAI.read_text(encoding="utf-8")) or {}).get("plugin") or {}
    except (OSError, UnicodeDecodeError, ValueError, AttributeError):
        return []
    may = _ten_may()
    for pid in thieu:
        muc = muc_khai.get(pid)
        can = muc.get("can_o_may") if isinstance(muc, dict) else None
        if not (isinstance(can, list) and can and may not in can):
            return []
    return thieu


def rebuild_router(source_root: Path, quiet: bool) -> int:
    """Dựng lại catalog từ trạng thái plugin thật — Codex trước, cache Claude Code sau."""

    script = source_root / ROUTER_NAME / "scripts/build_catalog.py"
    if script.is_file() and not co_codex_tren_may() and not co_the_dung_cache_claude_code():
        # Máy không có CẢ Codex LẪN cache Claude Code (installed_plugins.json) thì
        # build_catalog.py chắc chắn không dựng được gì — bản catalog đã commit là
        # nguyên liệu đúng để đóng gói. Trước 05/09/2026, nhánh này bỏ qua bất cứ khi nào
        # KHÔNG có Codex, kể cả khi máy hoàn toàn có thể tự dựng qua cache Claude Code
        # (build_catalog.py lúc đó chưa biết đọc cache này) — nghĩa là mọi phiên cloud
        # đều giữ nguyên bản catalog đã commit dù kho thật đã đổi khác, và không ai biết.
        # Đo được cùng ngày: catalog cam kết 828 skill trong khi cloud đo thật 842, lệch
        # ở academic-research-skills (17→4, đã cắt từ trước) và pubmed-search (31→10,
        # đã cắt từ trước) — hai lần cắt tỉa THẬT chưa từng tới catalog. Nay: có cache
        # Claude Code thì vẫn GỌI build_catalog.py (nó tự chọn tầng đọc phù hợp); chỉ khi
        # THIẾU CẢ HAI mới giữ nguyên bản đã commit như cũ.
        if not quiet:
            print("⚠ Máy này không có Codex lẫn cache Claude Code — giữ catalog router đã "
                  "commit, không dựng lại.")
        return 0
    if not script.is_file():
        # THIẾU NGUYÊN LIỆU ≠ HỎNG. Nguồn router hiện chỉ có trên máy Mac và chưa
        # được commit, nên trên mọi máy khác nhánh này luôn thiếu. Trả 0 kèm lời
        # nhắc: biến lượt nối skill THÀNH CÔNG thành thất bại chỉ vì làn ChatGPT
        # chưa có nguyên liệu là đúng kiểu báo động giả làm người ta quen bỏ qua
        # màu đỏ. Bước phụ CHẠY MÀ LỖI thì vẫn fail-closed (bên dưới).
        if not quiet:
            print(f"⚠ Bỏ qua làn ChatGPT: chưa có {ROUTER_NAME} trong sync/skills/ "
                  f"(cần commit bản nguồn từ máy Mac vào repo).")
        return 0
    khong_can = plugin_thieu_ma_may_nay_khong_can(script)
    if khong_can:
        # THIẾU PLUGIN MÀ SỔ KHAI NÓI MÁY NÀY KHÔNG CẦN ≠ HỎNG (01/10/2026). Catalog router cần đủ 9 plugin; máy Windows
        # chỉ được khai 4 (sync/plugin-manifest.json: codex · humanizer · openmed-skills · meta-pipe · pubmed-search
        # là `can_o_may: [Mac, Cloud]`). build_catalog.py ở đó LUÔN ném «Plugin thiếu trong cache» ⇒ mã 1 ⇒ hook
        # SessionStart in «⚠ Đồng bộ Claude–Codex còn lỗi» ở MỌI phiên dù nối skill 50×2 đạt, agent khớp 50/50 —
        # đúng kiểu báo động giả làm người ta quen bỏ qua màu đỏ (nhánh `not script.is_file()` ở trên đã nói thế).
        # Dựng bản thiếu còn tệ hơn: nó GHI ĐÈ catalog đầy đủ đã commit từ Mac bằng bản 4 plugin. Nên giữ catalog đã
        # commit và trả 0. Chỉ bỏ qua khi MỌI plugin thiếu đều được sổ khai xác nhận không cần ở máy này; thiếu một
        # plugin máy này ĐƯỢC KHAI là cần (mất thật, vd 12 plugin biến mất im lặng 05/08) thì vẫn chạy và fail-closed.
        if not quiet:
            print(f"⚪ Bỏ qua dựng catalog router: máy {_ten_may()} không cài {len(khong_can)} plugin router "
                  f"({', '.join(khong_can)}) và sổ khai sync/plugin-manifest.json xác nhận máy này KHÔNG cần chúng — "
                  "giữ catalog đã commit, không dựng bản thiếu đè lên.")
        return 0
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=script.parent.parent,
        check=False,
        capture_output=quiet,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0 and quiet:
        print((proc.stderr or proc.stdout or "dựng catalog thất bại").strip(), file=sys.stderr)
    return proc.returncode


def newest_mtime(root: Path) -> float:
    """Lấy mtime mới nhất của nội dung skill, bỏ file tạm Python."""

    values = [
        path.stat().st_mtime
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    return max(values, default=0.0)


def package_router(source_root: Path) -> bool:
    """Cập nhật ZIP phân phối chỉ khi nguồn router mới hơn gói."""

    source = source_root / ROUTER_NAME
    if not source.is_dir():
        return False
    output = REPO / "CHATGPT_SKILLS/dist/plugin-router-chatgpt.zip"
    if output.exists() and output.stat().st_mtime >= newest_mtime(source):
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            arcname = Path(ROUTER_NAME) / path.relative_to(source)
            archive.write(path, arcname.as_posix())
    os.replace(temporary, output)
    return True


def co_runtime_cowork() -> bool:
    """Máy này có runtime Cowork không. Hỏi chính ``dong_bo_skill.py`` thay vì
    viết lại đường dẫn ``~/Library/...`` lần thứ hai — hai bản đường dẫn là hai
    thứ sẽ lệch nhau khi Claude đổi chỗ lưu."""
    try:
        import dong_bo_skill                       # cùng thư mục tools/
        return dong_bo_skill.tim_runtime() is not None
    except Exception:
        return False


def sync_cowork(quiet: bool) -> int:
    """Đẩy bản nguồn sang runtime Cowork bằng luật chống mất nội dung hiện có."""

    command = [
        sys.executable,
        str(REPO / "tools/dong_bo_skill.py"),
        "--ap-dung",
        "--nguon-la-chuan",
    ]
    if quiet:
        command.append("--im-khi-on")
    proc = subprocess.run(command, cwd=REPO, check=False, timeout=300)
    return proc.returncode


def sync_plugins(apply: bool, quiet: bool) -> int:
    """Giữ plugin Codex không cũ hơn registry Claude."""

    cong_cu = REPO / "tools/dong_bo_plugin_claude_codex.py"
    if not cong_cu.is_file():
        print(f"⚠ Bỏ qua kiểm plugin: thiếu {cong_cu.name} trong tools/.", file=sys.stderr)
        return 0
    command = [sys.executable, str(cong_cu)]
    if apply:
        command.append("--ap-dung")
    if quiet:
        command.append("--im-khi-on")
    proc = subprocess.run(command, cwd=REPO, check=False, timeout=1200)
    return proc.returncode


def parse_args() -> argparse.Namespace:
    """Nhận chế độ kiểm hoặc áp dụng và cho phép test bằng thư mục tạm."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ap-dung", action="store_true", help="tạo liên kết và cập nhật runtime")
    parser.add_argument("--dong-bo-plugin", action="store_true", help="kiểm/nâng plugin Claude → Codex")
    parser.add_argument("--im-khi-on", action="store_true", help="im lặng khi hệ thống đã khớp")
    parser.add_argument("--bo-qua-runtime", action="store_true", help="không đẩy sang Cowork runtime")
    parser.add_argument("--bo-qua-dong-goi", action="store_true", help="không dựng catalog/ZIP router")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--claude-skills", type=Path, default=Path.home() / ".claude/skills")
    parser.add_argument("--codex-skills", type=Path, default=Path.home() / ".codex/skills")
    return parser.parse_args()


def main() -> int:
    """Điều phối đồng bộ và trả mã lỗi fail-closed."""

    args = parse_args()
    try:
        sources = skill_sources(args.source)
        results = [
            ensure_link(source, destination, args.ap_dung)
            for destination in (args.claude_skills, args.codex_skills)
            for source in sources
        ]
    except (OSError, RuntimeError) as exc:
        print(f"LỖI đồng bộ skill: {exc}", file=sys.stderr)
        return 1

    conflicts = [item for item in results if item.status == "XUNG_DOT"]
    pending = [item for item in results if item.status == "CAN_NOI"]
    changed = [item for item in results if item.status == "DA_NOI"]
    if changed and not args.im_khi_on:
        print(f"✓ Đã liên kết {len(changed)} skill vào Claude/Codex")
    for item in conflicts:
        print(f"✗ {item.runtime}/{item.skill}: {item.detail}", file=sys.stderr)

    codes: list[int] = [2 if conflicts else (1 if pending else 0)]
    # Chỉ kể tên bước ĐÃ THỰC SỰ CHẠY. Dòng kết cũ luôn nói "Cowork và plugin đã
    # kiểm" kể cả khi cả hai vừa bị bỏ qua vì thiếu nguyên liệu — một câu tổng kết
    # khẳng định thứ nó không đo là đúng họ lỗi mà doctrine gọi tên: người đọc tin
    # là đã kiểm, trong khi chưa có bước nào chạm tới.
    da_chay: list[str] = []
    if args.dong_bo_plugin:
        codes.append(sync_plugins(args.ap_dung, args.im_khi_on))
        if (REPO / "tools/dong_bo_plugin_claude_codex.py").is_file():
            da_chay.append("plugin")
    if args.ap_dung and not args.bo_qua_dong_goi:
        codes.append(rebuild_router(args.source, args.im_khi_on))
        try:
            packaged = package_router(args.source)
            if packaged and not args.im_khi_on:
                print("✓ Đã cập nhật gói plugin-router-chatgpt.zip")
            if (args.source / ROUTER_NAME).is_dir():
                da_chay.append("làn ChatGPT")
        except OSError as exc:
            print(f"LỖI đóng gói router: {exc}", file=sys.stderr)
            codes.append(1)
    if args.ap_dung and not args.bo_qua_runtime:
        codes.append(sync_cowork(args.im_khi_on))
        if co_runtime_cowork():
            da_chay.append("Cowork")

    final = 2 if 2 in codes else (1 if any(code != 0 for code in codes) else 0)
    if final == 0 and not args.im_khi_on:
        them = f"; đã chạy thêm: {', '.join(da_chay)}" if da_chay else ""
        print(f"✓ Nối skill đạt: {len(sources)} skill × 2 runtime bằng {LK.kieu()}{them}")
    elif not args.ap_dung and pending:
        print(f"⚠ Còn {len(pending)} liên kết cần tạo; chạy lại với --ap-dung.")
    return final


if __name__ == "__main__":
    raise SystemExit(main())
