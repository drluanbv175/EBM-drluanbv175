"""
inject_self_check.py — Thêm BƯỚC TỰ KIỂM vào 46 agent files chưa có

Chạy từ thư mục gốc Claude AI/:
    python tools/inject_self_check.py             # preview
    python tools/inject_self_check.py --apply     # áp dụng thật
    python tools/inject_self_check.py --check     # kiểm tra mà không sửa

Mục đích: sau khi _TU-CHINH-SUA-PROTOCOL.md §4 đặt chuẩn, script này
tự thêm BƯỚC TỰ KIỂM vào từng agent file trước <!-- EBM-MANDATORY-FINAL-GUARDRAIL -->.
"""

import argparse
import re
from pathlib import Path

AGENTS_DIR = Path(__file__).parent.parent / ".claude" / "agents"
GUARDRAIL_MARKER = "<!-- EBM-MANDATORY-FINAL-GUARDRAIL -->"

# Marker để tránh inject trùng lặp
SELF_CHECK_MARKER = "BƯỚC TỰ KIỂM"

SELF_CHECK_BLOCK = """
## BƯỚC TỰ KIỂM — trước khi trả đầu ra

Trước khi trả bất kỳ đầu ra cuối nào, thực hiện nhanh:
1. Đối chiếu với **TIÊU CHÍ HOÀN THÀNH / QUA CỔNG** của agent này
2. Thiếu sót tự giải được → sửa ngay trong lần trả này
3. Thiếu sót phụ thuộc input thật (IRB/data/SAP lock) → gắn `[CẦN BỔ SUNG]`
4. Chỉ trả khi self-check PASS; còn 🔴 → áp vòng tự sửa (`_TU-CHINH-SUA-PROTOCOL.md` §4)

```
✦ SELF-CHECK [agent-name] — Cổng G__:
  ĐÃ ĐẠT: [liệt kê tiêu chí đã đáp ứng]
  CÒN THIẾU: [liệt kê hoặc "không có"]
  KẾT: ĐẠT TỰ KIỂM / CÒN 🔴 → [hành động cụ thể]
```

"""


def is_infrastructure_file(path: Path) -> bool:
    """Bỏ qua file hạ tầng _*.md và README."""
    name = path.name
    return name.startswith("_") or name == "README.md"


def already_has_self_check(content: str) -> bool:
    return SELF_CHECK_MARKER in content


def inject_self_check(content: str, agent_name: str) -> tuple[str, bool]:
    """
    Thêm BƯỚC TỰ KIỂM trước <!-- EBM-MANDATORY-FINAL-GUARDRAIL -->.
    Trả về (new_content, changed).
    """
    if already_has_self_check(content):
        return content, False
    if GUARDRAIL_MARKER not in content:
        return content, False

    # Điền tên agent thật vào template
    block = SELF_CHECK_BLOCK.replace("[agent-name]", agent_name)

    # Chèn block trước guardrail marker
    new_content = content.replace(GUARDRAIL_MARKER, block + GUARDRAIL_MARKER)
    return new_content, True


def get_agent_name(path: Path) -> str:
    """Lấy tên agent từ frontmatter name: hoặc tên file."""
    content = path.read_text(encoding="utf-8")
    m = re.search(r'^name:\s*(\S+)', content, re.MULTILINE)
    return m.group(1) if m else path.stem


def main():
    parser = argparse.ArgumentParser(description="Inject BƯỚC TỰ KIỂM vào agent files")
    parser.add_argument("--apply", action="store_true", help="Ghi file thật (mặc định: chỉ preview)")
    parser.add_argument("--check", action="store_true", help="Chỉ kiểm tra, không sửa")
    args = parser.parse_args()

    dry_run = not args.apply
    check_only = args.check

    if not AGENTS_DIR.exists():
        print(f"❌ Không tìm thấy thư mục agents: {AGENTS_DIR}")
        return

    agent_files = sorted(AGENTS_DIR.glob("*.md"))
    agent_files = [f for f in agent_files if not is_infrastructure_file(f)]

    total = len(agent_files)
    already_ok = 0
    will_inject = 0
    no_marker = 0
    injected = 0
    errors = 0

    changed_list = []
    skipped_list = []

    print(f"{'='*60}")
    print(f"BƯỚC TỰ KIỂM INJECTION — {'DRY RUN (preview)' if dry_run else 'APPLY'}")
    print(f"Thư mục agents: {AGENTS_DIR}")
    print(f"Tổng agent files (không hạ tầng): {total}")
    print(f"{'='*60}\n")

    for f in agent_files:
        try:
            content = f.read_text(encoding="utf-8")
            agent_name = get_agent_name(f)

            if already_has_self_check(content):
                already_ok += 1
                skipped_list.append(f"✅ (đã có) {f.name}")
                continue

            if GUARDRAIL_MARKER not in content:
                no_marker += 1
                skipped_list.append(f"⚠️  (no guardrail marker) {f.name}")
                continue

            new_content, changed = inject_self_check(content, agent_name)
            if changed:
                will_inject += 1
                changed_list.append(f.name)
                if not dry_run and not check_only:
                    f.write_text(new_content, encoding="utf-8")
                    injected += 1

        except Exception as e:
            errors += 1
            print(f"  ❌ LỖI {f.name}: {e}")

    # Báo cáo
    print("FILE SẼ ĐƯỢC INJECT:")
    for name in changed_list:
        print(f"  🔧 {name}")

    print("\nBỎ QUA:")
    for msg in skipped_list[:10]:
        print(f"  {msg}")
    if len(skipped_list) > 10:
        print(f"  ... và {len(skipped_list)-10} file khác")

    print(f"\n{'='*60}")
    print(f"KẾT QUẢ:")
    print(f"  Đã có SELF-CHECK: {already_ok}")
    print(f"  Cần inject:       {will_inject}")
    print(f"  Không có marker:  {no_marker}")
    print(f"  Lỗi:              {errors}")
    if not dry_run and not check_only:
        print(f"  ✅ Đã inject:   {injected}")
    elif dry_run:
        print(f"\n[DRY RUN] Chạy lại với --apply để áp dụng thật.")
    print(f"{'='*60}")

    return {"total": total, "already_ok": already_ok, "injected": injected or will_inject,
            "no_marker": no_marker, "errors": errors}


if __name__ == "__main__":
    main()
