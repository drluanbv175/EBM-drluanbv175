from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
skill = root / "SKILL.md"
errors = []
warnings = []

if root.name != "nghien-cuu-y-khoa-chuan-quoc-te":
    errors.append("Tên thư mục gốc của skill không đúng")

if not skill.exists():
    errors.append("Thiếu SKILL.md")
else:
    text = skill.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append("SKILL.md thiếu YAML frontmatter hợp lệ")
    else:
        fm = m.group(1)
        name_match = re.search(r"^name:\s*(.+)\s*$", fm, re.M)
        desc_match = re.search(r"^description:\s*(.+)\s*$", fm, re.M)
        if not name_match or not desc_match:
            errors.append("Frontmatter phải có name và description")
        else:
            name = name_match.group(1).strip()
            desc = desc_match.group(1).strip()
            if len(name) > 64 or not re.fullmatch(r"[a-z0-9-]+", name):
                errors.append("name phải <=64 ký tự và chỉ có a-z, 0-9, dấu gạch ngang")
            if any(term in name for term in ("anthropic", "claude")):
                errors.append("name không được chứa từ dành riêng anthropic/claude")
            if not desc:
                errors.append("description không được rỗng")
            if len(desc) > 1024:
                errors.append(f"description dài {len(desc)} ký tự; giới hạn kỹ thuật là 1024")
            if not re.search(r"(?i)(d[uù]ng|s[uử] d[uụ]ng|k[ií]ch ho[aạ]t)[^.]*\bkhi\b", desc):
                warnings.append("description nên nêu rõ khi nào dùng skill")
    body = text.split("---", 2)[-1]
    approx_tokens = len(body) / 4
    if approx_tokens > 5000:
        warnings.append(f"SKILL.md ước tính {approx_tokens:.0f} token; nên rút gọn để progressive disclosure hiệu quả")
    referenced = re.findall(r"`((?:references|workflows|modules|templates|quality)/[^`]+\.(?:md|py))`", text)
    for ref in sorted(set(referenced)):
        if not (root / ref).exists():
            errors.append(f"Thiếu file tham chiếu: {ref}")

required_files = [
    "README_HUONG_DAN_SU_DUNG.md", "MANIFEST.md",
    "references/00_nguon_chinh_thuc_va_quy_tac_cap_nhat.md",
    "references/01_dao_duc_phap_ly_bao_mat_viet_nam.md",
    "references/02_ban_do_chuan_bao_cao.md",
    "references/04_liem_chinh_cong_bo_tac_gia_AI.md",
    "quality/01_bo_test_va_checklist_kiem_dinh.md",
    "quality/02_ca_kiem_thu_dau_ra.md",
    "workflows/08_bao_tri_skill_va_kiem_thu_sau_cap_nhat.md",
]
for ref in required_files:
    if not (root / ref).exists():
        errors.append(f"Thiếu tệp bắt buộc của bản 5.0: {ref}")

unsafe_extensions = {".sav", ".xlsx", ".csv", ".dta", ".rds", ".sas7bdat"}
for p in root.rglob("*"):
    if p.is_file() and p.suffix.lower() in unsafe_extensions:
        errors.append(f"Không đóng gói dữ liệu nghiên cứu trong skill: {p.relative_to(root)}")
    if p.is_file() and p.name.lower() in {".env", "credentials.json", "secrets.json"}:
        errors.append(f"Không đóng gói thông tin xác thực: {p.relative_to(root)}")

if errors:
    print("KHÔNG ĐẠT")
    for e in errors:
        print("-", e)
    if warnings:
        print("CẢNH BÁO")
        for w in warnings:
            print("-", w)
    sys.exit(1)

print("ĐẠT: cấu trúc skill và các tài liệu bắt buộc hợp lệ.")
for w in warnings:
    print("CẢNH BÁO:", w)
print("Lưu ý: kiểm tra kỹ thuật không thay thế kiểm thử hành vi của Claude hoặc thẩm định chuyên gia.")
