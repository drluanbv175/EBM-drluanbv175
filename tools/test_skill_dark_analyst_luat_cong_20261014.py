"""Skill `dark-analyst` phải mang ĐỦ luật cổng như `cap-nhat-chung-cu-y-khoa` — hai skill cùng mô tả kích hoạt.

14/10/2026. VÌ SAO. Hai SKILL.md có frontmatter `description` giống hệt (chỉ khác `name`/`version`), cùng nối vào
`~/.claude/skills`, và dùng chung `tools/verify_dashboard.py` trùng byte — model có thể chọn BẤT KỲ skill nào. Rà
đồng bộ 14/10: ba commit (4087a14 BH156 · 6307e5c + f27be3e BH161) sửa CẢ HAI bản cổng nhưng chỉ dạy luật mới ở
SKILL.md của cap-nhat; luật «cổng chặn nguồn đã rút» (14/08) cũng vắng; 15/10 thấy thêm: thiếu cả lệnh bộ năm
`xuat_goi_cap_nhat.py` cùng bước ⑦ toàn văn (làn Chrome) và ⑧ EndNote; dark-analyst còn dạy TỰ chạy
`EBM_MASTER/tools/sync_all.py` trái quyết định 05/08 của bác sĩ. Cổng vẫn chặn, nhưng agent không biết luật thì
dựng gói rồi bị chặn mà không hiểu vì sao (CLAUDE.md §6.4: thêm luật ở cổng phải DẠY AGENT cùng lúc).
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "sync" / "skills"
HAI_SKILL = ("cap-nhat-chung-cu-y-khoa", "dark-analyst")
# Mỗi cụm là tiêu đề của một khối luật cổng — có ở skill này thì phải có ở skill kia.
LUAT_CONG = (
    "CẶP PMID–DOI PHẢI CÙNG MỘT BÀI",
    "CỔNG NAY CHẶN NGUỒN ĐÃ BỊ RÚT",
    "BẢO ĐẢM ĐỌC TOÀN VĂN",
    "hai định danh phải trỏ CÙNG một bài",
    # Dây chuyền bộ năm + ⑦ toàn văn (làn Chrome/Unpaywall) + ⑧ EndNote (15/10/2026: dark-analyst thiếu cả khối này)
    "xuat_goi_cap_nhat.py <dashboard>.html --online",
    "toan_van_theo_chu_de.py --moi-trich-dan",
    "nap_endnote_chu_de.py",
)


def _doc(ten: str) -> str:
    return (SKILLS / ten / "SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("cum", LUAT_CONG)
def test_luat_cong_co_o_ca_hai_skill(cum):
    thieu = [ten for ten in HAI_SKILL if cum not in _doc(ten)]
    assert not thieu, f"luật cổng «{cum}» vắng ở {thieu} — port nguyên khối từ skill kia"


@pytest.mark.parametrize("ten", HAI_SKILL)
def test_khong_day_tu_chay_sync_all(ten):
    """Mọi dòng nhắc sync_all.py phải là dòng CẤM tự chạy (quyết định 05/08 của bác sĩ)."""
    sai = [d.strip()[:160] for d in _doc(ten).splitlines() if "sync_all.py" in d and "KHÔNG" not in d]
    assert not sai, f"{ten}/SKILL.md còn dạy chạy sync_all.py mà không kèm «KHÔNG»:\n  " + "\n  ".join(sai)
