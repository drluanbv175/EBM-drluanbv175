"""Unit test cho tools/verify_hard_gate_count_consistency.py::scan().

Thêm 2026-07-16 sau audit đối kháng vòng 2 — phát hiện: tool tự sinh ra để bắt
lớp lỗi "thêm 1 cổng cứng mới, quên cập nhật hết doctrine" (vụ G8, lọt lưới
16+ ngày) chưa từng được TEST bằng fixture cố tình sai — "bằng chứng" duy nhất
trước đây là nó chạy trên corpus thật và in ra ✅, không chứng minh được khả
năng phát hiện DƯƠNG TÍNH thật khi có lỗi. File này dùng fixture thư mục giả
lập (tmp_path) — không đụng .claude/agents/ thật — để chứng minh scan() thật
sự bắt được đúng loại lỗi nó tồn tại để chặn."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_hard_gate_count_consistency as V  # noqa: E402

GATE_SET = ["G2", "G4", "G8", "G9"]


def _write(d: Path, name: str, content: str) -> Path:
    p = d / name
    p.write_text(content, encoding="utf-8")
    return p


def test_scan_detects_line_missing_one_gate(tmp_path):
    """Đúng kịch bản đã xảy ra thật: liệt kê cổng cứng G2/G4/G9, THIẾU G8."""
    _write(tmp_path, "doctrine.md", "Cổng cứng: G2/G4/G9 không được vượt qua.\n")
    findings = V.scan(agents_dir=tmp_path, gate_set=GATE_SET)
    assert len(findings) == 1
    assert findings[0]["missing"] == ["G8"]
    assert findings[0]["line_no"] == 1


def test_scan_detects_synonym_diem_dung_cung(tmp_path):
    """Hồi quy đúng: "điểm dừng cứng" (đồng nghĩa THẬT đã lọt lưới bản đầu,
    _KHUNG-DANH-GIA-KHA-THI.md) phải được nhận diện, không chỉ "cổng cứng"."""
    _write(tmp_path, "doctrine.md", "4 điểm dừng cứng nghiên cứu (G2/G4/liêm chính) nguyên vẹn.\n")
    findings = V.scan(agents_dir=tmp_path, gate_set=GATE_SET)
    assert len(findings) == 1
    assert set(findings[0]["missing"]) == {"G8", "G9"}


def test_scan_passes_when_all_gates_present(tmp_path):
    """Không dương tính giả khi dòng liệt kê ĐỦ cả 4 gate."""
    _write(tmp_path, "doctrine.md", "Cổng cứng: G2 · G4 · G8 · G9 đều phải đóng.\n")
    findings = V.scan(agents_dir=tmp_path, gate_set=GATE_SET)
    assert findings == []


def test_scan_ignores_line_mentioning_only_one_gate(tmp_path):
    """Dòng chỉ nhắc 1 gate (không đủ dấu hiệu đang LIỆT KÊ cổng cứng) — không
    báo lệch dù thiếu 3 gate còn lại (đúng ngưỡng "≥2 gate" trong docstring)."""
    _write(tmp_path, "doctrine.md", "Cổng cứng quan trọng nhất là G2 (đạo đức).\n")
    findings = V.scan(agents_dir=tmp_path, gate_set=GATE_SET)
    assert findings == []


def test_scan_ignores_lines_without_hard_gate_phrase(tmp_path):
    """Dòng liệt kê G2/G4/G9 nhưng KHÔNG có cụm "cổng cứng"/"điểm dừng cứng"/
    "hard gate" nào — không phải mục tiêu của tool này (vd bảng crosswalk kỹ
    thuật khác), không báo lệch."""
    _write(tmp_path, "doctrine.md", "Trục đánh số: G2=đạo đức, G4=SAP, G9=liêm chính.\n")
    findings = V.scan(agents_dir=tmp_path, gate_set=GATE_SET)
    assert findings == []


def test_scan_scans_multiple_files_and_reports_correct_filename(tmp_path):
    """Quét đúng NHIỀU file, gán đúng tên file cho từng finding. Lưu ý: câu
    KHÔNG được nhắc chữ "G4" ở BẤT KỲ đâu (kể cả trong ngoặc mô tả) — nếu không
    _gates_mentioned_on_line sẽ vô tình khớp và làm "missing" thành rỗng."""
    _write(tmp_path, "a.md", "không liên quan\n")
    _write(tmp_path, "b.md", "Cổng cứng: G2, G8, G9 phải cùng đóng trước khi nghiệm thu.\n")
    findings = V.scan(agents_dir=tmp_path, gate_set=GATE_SET)
    assert len(findings) == 1
    assert findings[0]["file"].endswith("b.md")
    assert findings[0]["missing"] == ["G4"]


def test_scan_case_insensitive_hard_gate_phrase(tmp_path):
    """_HARD_GATE_PHRASE dùng re.IGNORECASE — "Hard Gate" hoa/thường vẫn khớp."""
    _write(tmp_path, "doctrine.md", "Hard Gate: G2, G4, G9.\n")
    findings = V.scan(agents_dir=tmp_path, gate_set=GATE_SET)
    assert len(findings) == 1
    assert findings[0]["missing"] == ["G8"]


def test_scan_on_empty_directory_returns_no_findings(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert V.scan(agents_dir=empty, gate_set=GATE_SET) == []


def test_scan_default_call_uses_real_agents_dir_and_gate_set():
    """Xác nhận scan() gọi KHÔNG tham số vẫn hoạt động đúng trên corpus thật
    (đây là cách main()/pre-commit hook thật sự gọi nó) — không phải chỉ hoạt
    động qua đường test fixture."""
    findings = V.scan()
    assert isinstance(findings, list)
    for f in findings:
        assert set(f.keys()) == {"file", "line_no", "line", "missing"}


def test_gate_set_matches_gate_contract_source_of_truth():
    """GATE_SET của tool phải LUÔN đúng bằng _GATE_REQUIRED_STAKEHOLDERS thật —
    nếu ai thêm cổng cứng mới vào gate_contract.py mà quên tool này tự đọc lại,
    test sẽ đỏ (dù trên thực tế tool đọc trực tiếp từ gate_contract.py nên
    không thể lệch — test này khóa lại bất biến đó, không phải dò lệch thủ công)."""
    assert V.GATE_SET == sorted(V.GC._GATE_REQUIRED_STAKEHOLDERS.keys())
