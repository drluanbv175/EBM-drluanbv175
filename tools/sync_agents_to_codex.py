#!/usr/bin/env python3
"""Dong bo bo agent Claude sang hai thu muc agent Codex.

Nguon su that hien tai la `.claude/agents/*.md`. Script nay:
- chuyen moi agent Markdown frontmatter sang TOML cho Codex;
- copy README.md va cac so ha tang `_* .md` sang Codex;
- doi duong dan tham chieu `.claude/agents` thanh thu muc dich;
- kiem tra so luong, ten file, TOML hop le va cac agent loi.

Mac dinh ghi vao ca `.Codex/agents` va `.codex/agents` de hai cach dat ten
thu muc deu dung duoc trong cac runtime khac nhau.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11 tren mot so may.
    try:
        # SUA: tren Python < 3.11 (vd 3.9 trong ~/.ebm-venv), khong co tomllib
        # stdlib nen roi ve SIMPLE_TOML_RE (regex tu viet) trong
        # parse_generated_toml(). Regex do dung `(?:#.*\n)*` + `.*` voi
        # re.DOTALL tren noi dung TOML sinh ra (~30-40KB/file, nhung dung
        # developer_instructions ba dau nhay don gian). Da do bang faulthandler:
        # 1 file mat ~1s de match (rat cham cho 1 lan match regex don), nhan
        # voi 48 agent x 2 thu muc dich (.Codex/ + .codex/) = ~96 lan goi
        # trong `sync_agents_to_codex.py --check` -> tich luy thanh treo
        # nhieu phut, tuong nhu vo han. tomli (ban backport chinh thuc cua
        # tomllib, cung API) da co san trong venv du an -> dung thay the,
        # nhanh + dung chuan TOML that thay vi regex tu che.
        import tomli as tomllib  # type: ignore[assignment,no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / ".claude" / "agents"
TARGETS = (
    (ROOT / ".Codex" / "agents", ".Codex/agents"),
    (ROOT / ".codex" / "agents", ".codex/agents"),
)

REQUIRED_AGENTS = {
    "dieu-phoi-lam-sang",
    "dieu-phoi-nghien-cuu",
    "tham-dinh-dau-ra",
    "pico-lam-sang",
    "chan-doan-xac-suat",
    "thu-thu-tai-lieu",
    "tong-quan-y-van",
    "viet-ban-thao",
    "binh-duyet",
}

REQUIRED_INFRA = {
    "README.md",
    "_BAN-DO-KET-NOI.md",
    "_HIEN-PHAP-LIEM-CHINH.md",
    "_KIEM-DUYET-DOC-LAP.md",
    "_CHUAN-CHAT-LUONG-MEDPALM.md",
    "_NGUYEN-TAC-TRUNG-THUC-BAO-MAT-PHAP-LY-LIEM-CHINH.md",
    "_SO-TRANG-THAI-CHECKPOINT.md",
    "_KIEM-TOAN-DAY-DU-NGHIEN-CUU.md",
    "_PLUGIN-ROUTING-CONTRACT.md",
}

FRONTMATTER_RE = re.compile(r"\A---\n(?P<meta>.*?)\n---\n?(?P<body>.*)\Z", re.DOTALL)
SIMPLE_TOML_RE = re.compile(
    r'\A(?:#.*\n)*'
    r'name = (?P<name>"(?:\\.|[^"\\])*")\n'
    r'description = (?P<description>"(?:\\.|[^"\\])*")\n'
    r"developer_instructions = '''\n(?P<body>.*)'''\n?\Z",
    re.DOTALL,
)


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    body: str
    source_path: Path


def parse_frontmatter(path: Path) -> AgentSpec:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path} khong co YAML frontmatter")

    meta: dict[str, str] = {}
    for raw_line in match.group("meta").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path}: dong frontmatter khong hop le: {raw_line!r}")
        key, value = line.split(":", 1)
        value = value.strip()
        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]
        meta[key.strip()] = value

    name = meta.get("name", "").strip()
    description = meta.get("description", "").strip()
    if not name or not description:
        raise ValueError(f"{path}: thieu name hoac description")
    if path.stem != name:
        raise ValueError(f"{path}: filename != name ({path.stem!r} != {name!r})")
    return AgentSpec(
        name=name,
        description=description,
        body=match.group("body").rstrip() + "\n",
        source_path=path,
    )


def source_agent_paths() -> list[Path]:
    return sorted(
        path
        for path in SOURCE_DIR.glob("*.md")
        if path.name != "README.md" and not path.name.startswith("_")
    )


def source_infra_paths() -> list[Path]:
    return sorted(
        path
        for path in SOURCE_DIR.glob("*.md")
        if path.name == "README.md" or path.name.startswith("_")
    )


_CASE_INSENSITIVE_FS_CACHE: bool | None = None


def _case_insensitive_fs() -> bool:
    """Phat hien (mot lan, co cache) filesystem chua ROOT co phan biet
    hoa/thuong hay khong.

    Dung `ROOT / "tools"` (thu muc chua chinh script nay, nen CHAC CHAN da
    ton tai) lam vat tham do, roi thu doi ten hoa/thuong va kiem samefile —
    KHONG dua vao Path.exists() cua .Codex/.codex nhu truoc, vi trong mot
    git worktree moi (ca hai deu gitignored, chua tung chay script) ca hai
    thu muc do deu chua ton tai tai thoi diem kiem tra dedup dau tien, khien
    heuristic cu coi chung la KHONG trung nhau va ghi doc lap. Tren filesystem
    case-insensitive (vd APFS mac dinh), hai lan ghi do thuc chat ghi de len
    CUNG mot thu muc vat ly -> lan ghi sau (nhan ".codex/agents") de len lan
    ghi truoc (nhan ".Codex/agents"), lam moi file mang nhan sai va bao drift
    hang loat khi chay lai --check sau khi ca hai thu muc da ton tai.
    """
    global _CASE_INSENSITIVE_FS_CACHE
    if _CASE_INSENSITIVE_FS_CACHE is not None:
        return _CASE_INSENSITIVE_FS_CACHE

    probe_dir = ROOT / "tools"
    flipped = probe_dir.parent / probe_dir.name.upper()
    result = False
    try:
        if flipped.exists() and flipped.samefile(probe_dir):
            result = True
    except OSError:
        result = False

    _CASE_INSENSITIVE_FS_CACHE = result
    return result


def active_targets() -> list[tuple[Path, str]]:
    """Loai bo target trung nhau tren filesystem khong phan biet hoa/thuong.

    So sanh ten duong dan (khong phan biet hoa/thuong) CHI KHI da xac dinh
    filesystem la case-insensitive (xem _case_insensitive_fs) — khong con
    phu thuoc vao .Codex/.codex da ton tai tren dia hay chua, nen dedup dung
    ngay tu lan goi dau tien ke ca khi ca hai thu muc dich deu chua duoc tao.
    Tren filesystem case-sensitive (vd Linux/CI), tra ve nguyen TARGETS —
    ca hai thu muc PHAI duoc ghi doc lap dung nhu thiet ke goc.
    """
    if not _case_insensitive_fs():
        return list(TARGETS)

    active: list[tuple[Path, str]] = []
    for target_dir, target_label in TARGETS:
        duplicate_of: str | None = None
        for seen_dir, seen_label in active:
            if str(target_dir).lower() == str(seen_dir).lower():
                duplicate_of = seen_label
                break
        if duplicate_of:
            print(
                f"Note: {target_label} points to the same directory as {duplicate_of}; "
                f"using {duplicate_of} as canonical."
            )
            continue
        active.append((target_dir, target_label))
    return active


def toml_quote(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\b", "\\b")
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'


def rewrite_paths(text: str, target_label: str) -> str:
    return (
        text.replace(".claude/agents", target_label)
        .replace("`.claude/agents", f"`{target_label}")
        .replace(" .claude/agents", f" {target_label}")
    )


def render_agent(spec: AgentSpec, target_label: str) -> str:
    body = rewrite_paths(spec.body, target_label)
    return (
        "# Generated by tools/sync_agents_to_codex.py. Edit .claude/agents/*.md, then rerun.\n"
        f"name = {toml_quote(spec.name)}\n"
        f"description = {toml_quote(spec.description)}\n"
        "developer_instructions = '''\n"
        f"{body}"
        "'''\n"
    )


def render_infra(path: Path, target_label: str) -> str:
    text = path.read_text(encoding="utf-8")
    text = rewrite_paths(text, target_label)
    if path.name == "README.md":
        text = text.replace(
            f"`{target_label}/*.md` là bản biên tập chính",
            "`.claude/agents/*.md` là bản biên tập chính",
        )
        text = text.replace(
            f"sửa/thêm agent ở `{target_label}`",
            "sửa/thêm agent ở `.claude/agents`",
        )
    return (
        "<!-- Generated by tools/sync_agents_to_codex.py. "
        "Edit .claude/agents/*.md, then rerun. -->\n"
        f"{text.rstrip()}\n"
    )


def expected_files(target_label: str) -> dict[str, str]:
    specs = [parse_frontmatter(path) for path in source_agent_paths()]
    files: dict[str, str] = {}
    for spec in specs:
        files[f"{spec.name}.toml"] = render_agent(spec, target_label)
    for path in source_infra_paths():
        files[path.name] = render_infra(path, target_label)
    return files


def write_target(target_dir: Path, target_label: str) -> list[str]:
    target_dir.mkdir(parents=True, exist_ok=True)
    changed: list[str] = []
    for filename, content in expected_files(target_label).items():
        target_path = target_dir / filename
        old = target_path.read_text(encoding="utf-8") if target_path.exists() else None
        if old != content:
            target_path.write_text(content, encoding="utf-8")
            changed.append(str(target_path.relative_to(ROOT)))
    return changed


def check_target(target_dir: Path, target_label: str) -> list[str]:
    errors: list[str] = []
    expected = expected_files(target_label)

    if not target_dir.exists():
        return [f"thieu thu muc {target_dir.relative_to(ROOT)}"]

    for filename, content in expected.items():
        target_path = target_dir / filename
        if not target_path.exists():
            errors.append(f"thieu {target_path.relative_to(ROOT)}")
            continue
        current = target_path.read_text(encoding="utf-8")
        if current != content:
            errors.append(f"drift {target_path.relative_to(ROOT)}")

    source_agents = {path.stem for path in source_agent_paths()}
    target_agents = {path.stem for path in target_dir.glob("*.toml")}
    missing = sorted(source_agents - target_agents)
    extra = sorted(target_agents - source_agents)
    if missing:
        errors.append(f"{target_label}: thieu agent {', '.join(missing)}")
    if extra:
        errors.append(f"{target_label}: agent thua {', '.join(extra)}")

    missing_required = sorted(REQUIRED_AGENTS - target_agents)
    if missing_required:
        errors.append(f"{target_label}: thieu agent loi {', '.join(missing_required)}")

    for infra in sorted(REQUIRED_INFRA):
        if not (target_dir / infra).exists():
            errors.append(f"{target_label}: thieu so ha tang {infra}")

    for toml_path in sorted(target_dir.glob("*.toml")):
        try:
            data = parse_generated_toml(toml_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{toml_path.relative_to(ROOT)}: TOML loi: {exc}")
            continue
        if data.get("name") != toml_path.stem:
            errors.append(
                f"{toml_path.relative_to(ROOT)}: name != filename "
                f"({data.get('name')!r} != {toml_path.stem!r})"
            )
        if not data.get("description"):
            errors.append(f"{toml_path.relative_to(ROOT)}: thieu description")
        if not data.get("developer_instructions"):
            errors.append(f"{toml_path.relative_to(ROOT)}: thieu developer_instructions")

    return errors


def parse_generated_toml(text: str) -> dict[str, str]:
    if tomllib is not None:
        return tomllib.loads(text)

    match = SIMPLE_TOML_RE.match(text)
    if not match:
        raise ValueError("khong khop schema TOML generated")
    return {
        "name": json.loads(match.group("name")),
        "description": json.loads(match.group("description")),
        "developer_instructions": match.group("body"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dong bo .claude/agents sang .Codex/agents va .codex/agents."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Chi kiem tra drift, khong ghi file.",
    )
    args = parser.parse_args()

    if not SOURCE_DIR.exists():
        print(f"ERROR: khong thay {SOURCE_DIR}", file=sys.stderr)
        return 2

    if args.check:
        errors: list[str] = []
        for target_dir, target_label in active_targets():
            errors.extend(check_target(target_dir, target_label))
        if errors:
            print("Agent sync check: FAIL")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Agent sync check: PASS")
        print(f"- source agents: {len(source_agent_paths())}")
        for target_dir, _ in TARGETS:
            print(f"- {target_dir.relative_to(ROOT)}: {len(list(target_dir.glob('*.toml')))} TOML")
        return 0

    all_changed: list[str] = []
    for target_dir, target_label in active_targets():
        all_changed.extend(write_target(target_dir, target_label))

    print("Agent sync: done")
    print(f"- source agents: {len(source_agent_paths())}")
    print(f"- changed files: {len(all_changed)}")
    for changed in all_changed:
        print(f"  {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
