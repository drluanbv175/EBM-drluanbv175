from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_lessons_rubric_alignment as V  # noqa: E402


def test_current_lessons_rubric_alignment_passes():
    report = V.build_report()

    assert report.overall_status == "PASS"
    assert "GUIDE-CONFLICT" in report.rubric_codes
    assert "GUIDE-CONFLICT" in report.taxonomy_codes
    assert "GAP-LABEL-WASH" in report.taxonomy_codes
    assert report.retry_loop_codes["R1b"] == "GAP-LABEL-WASH"
    assert report.retry_loop_codes["R6"] == "GAP-MISSING"
    assert report.r1b_r6_distinct is True
    assert report.missing_in_taxonomy == []
    assert report.missing_in_bridge == []
    assert report.retry_loop_codes_missing_in_taxonomy == []


def test_extracts_missing_rubric_code_from_synthetic_text():
    rubric = """
## 3. TIER 0
| 0.1 | `CIT-GHOST` | ok |
## 4. TIER 1
- [ ] `NEW-MISSING` — synthetic missing code
## 6. Bản ghi phán quyết
"""
    taxonomy = """
## 2. Taxonomy lỗi
| Mã | Tên | Rubric |
|---|---|---|
| `CIT-GHOST` | ok | 0.1 |
## 2b. Bảng đối chiếu mã R hiện hành
| Mã mới | Mã R |
|---|---|
| `CIT-GHOST` | R1 |
## 3. Schema
"""

    rubric_codes = V.rubric_controlled_codes(rubric)
    taxonomy_codes = V.taxonomy_table_codes(taxonomy)
    bridge_codes = V.taxonomy_bridge_codes(taxonomy)

    assert "NEW-MISSING" in rubric_codes
    assert rubric_codes - taxonomy_codes == {"NEW-MISSING"}
    assert rubric_codes - bridge_codes == {"NEW-MISSING"}
