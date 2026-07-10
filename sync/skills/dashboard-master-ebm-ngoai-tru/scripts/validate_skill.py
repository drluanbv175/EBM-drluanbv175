"""Kiểm định cấu trúc skill Dashboard Master EBM trước khi đóng gói/upload.

Kiểm tra:
- SKILL.md tồn tại, name khớp tên thư mục, có description và <= 200 ký tự.
- Đủ các file phụ trợ đang được SKILL.md tham chiếu.
- File Excel mẫu có đủ 9 sheet nghiệp vụ bắt buộc (bỏ qua nếu thiếu openpyxl).
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
skill = root / "SKILL.md"

required = [
    root / "README_HUONG_DAN_SU_DUNG.md",
    root / "assets" / "EBM_Dashboard_Master_Template.xlsx",
    root / "references" / "01_cau_truc_dashboard_va_quy_tac_du_lieu.md",
    root / "references" / "02_xac_minh_nguon_va_phan_loai_chung_cu.md",
    root / "workflows" / "01_cap_nhat_dashboard_tu_tasks.md",
    root / "workflows" / "02_tong_hop_thang_va_loai_trung.md",
    root / "workflows" / "03_tao_file_dashboard_master.md",
    root / "prompts" / "01_prompt_bo_sung_cho_5_tasks.md",
    root / "quality" / "01_checklist_kiem_dinh.md",
    root / "templates" / "01_goi_cap_nhat_dashboard.md",
]

required_sheets = [
    "Dashboard_Summary", "Change_Log", "Action_Register", "Evidence_Register",
    "Medication_Safety", "Clinical_Tools", "Not_For_Change", "Task_Run_Log",
    "Lists_Validation",
]

errors = []
warnings = []

if not skill.exists():
    errors.append("Thiếu SKILL.md")
else:
    txt = skill.read_text(encoding="utf-8")
    m_name = re.search(r"^name:\s*(.+)$", txt, re.M)
    m_desc = re.search(r"^description:\s*(.+)$", txt, re.M)
    if not m_name or m_name.group(1).strip() != root.name:
        errors.append("name không khớp tên thư mục")
    if not m_desc:
        errors.append("Thiếu description")
    elif len(m_desc.group(1).strip()) > 200:
        errors.append(f"description vượt 200 ký tự ({len(m_desc.group(1).strip())})")

for f in required:
    if not f.exists():
        errors.append(f"Thiếu file: {f.relative_to(root)}")

xlsx = root / "assets" / "EBM_Dashboard_Master_Template.xlsx"
if xlsx.exists():
    try:
        import openpyxl
        wb = openpyxl.load_workbook(xlsx, read_only=True)
        missing = [s for s in required_sheets if s not in wb.sheetnames]
        if missing:
            errors.append("File Excel thiếu sheet bắt buộc: " + ", ".join(missing))
    except ImportError:
        warnings.append("Bỏ qua kiểm tra sheet Excel (chưa cài openpyxl).")
    except Exception as e:  # noqa: BLE001
        warnings.append(f"Không đọc được file Excel để kiểm tra sheet: {e}")

for w in warnings:
    print("CẢNH BÁO:", w)

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("PASS: cấu trúc skill Dashboard Master EBM hợp lệ.")
