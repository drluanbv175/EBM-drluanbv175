"""Test verify_agent_routing.py — kiểm chứng đồ thị định tuyến agent (S1/S2).

Gồm test bằng FIXTURE giả lập (khóa logic lọc dương-tính-giả) + 1 test TÍCH HỢP chạy
trên hệ .claude/agents/ THẬT (cổng "lần chạy sạch đầu tiên" — nếu fail, đó là TÍN
HIỆU THẬT cần sửa .md hoặc vá bộ lọc, KHÔNG phải test cần bỏ qua).

Chạy: `pytest tools/test_verify_agent_routing.py` hoặc `python tools/test_verify_agent_routing.py`.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_agent_routing as V  # noqa: E402


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_classify_token_agent_infra_artifact_skill_dangling():
    agents = {"agent-one", "agent-two-here"}
    assert V.classify_token("agent-one", agents) == "agent"
    assert V.classify_token("_INFRA-FILE.md", agents) == "infra_or_script"
    assert V.classify_token("run_script.py --flag", agents) == "infra_or_script"
    assert V.classify_token("A13b", agents) == "artifact_id"
    assert V.classify_token("G10", agents) == "artifact_id"
    assert V.classify_token("nghien-cuu-y-khoa-chuan-quoc-te", agents) == "skill"
    assert V.classify_token("agent-does-not-exist", agents) == "dangling_candidate"
    assert V.classify_token("bash", agents) == "other"  # từ đơn, không gạch nối
    assert V.classify_token("ghi", agents) == "other"


def test_extract_references_fixture_orphan_and_dangling():
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        agents_dir = base / ".claude" / "agents"
        _write(agents_dir / "agent-one.md", "---\nname: agent-one\n---\nnội dung")
        _write(agents_dir / "agent-two-here.md", "---\nname: agent-two-here\n---\nnội dung")
        _write(agents_dir / "agent-three-orphan.md", "---\nname: agent-three-orphan\n---\nnội dung")
        _write(agents_dir / "_INFRA.md", "hạ tầng, không phải agent")
        orch = base / "orch.md"
        _write(orch, (
            "Gọi `agent-one` rồi `agent-two-here`. "
            "Tham chiếu treo: `agent-four-does-not-exist`. "
            "Không phải agent: `some-script.py --flag`, `_INFRA.md`, `A13`."
        ))

        # extract_references() nhận `agents` làm tham số, KHÔNG đọc AGENTS_DIR toàn
        # cục — nên fixture gọi trực tiếp, không cần trỏ lại đường dẫn thật.
        r = V.extract_references(orch, {"agent-one", "agent-two-here", "agent-three-orphan"})
        assert r["agent"] == {"agent-one", "agent-two-here"}
        assert r["dangling"] == {"agent-four-does-not-exist"}
        assert "_INFRA.md" not in r["agent"] and "_INFRA.md" not in r["dangling"]
        _ = agents_dir  # thư mục agent giả chỉ cần TỒN TẠI cho tính đầy đủ fixture


def test_fenced_code_block_not_scanned_for_dangling():
    text = "Trước.\n```bash\npython some.py --flag\n```\nSau: `agent-one`."
    stripped = V._FENCED_BLOCK.sub(" ", text)
    assert "some.py" not in stripped
    assert "`agent-one`" in stripped


def test_real_system_clean_run_no_dangling_references():
    """CỔNG 'lần chạy sạch': trên hệ .claude/agents/ THẬT, không được có tham chiếu
    treo. Nếu fail — đây là TÍN HIỆU THẬT (agent bị xóa/gõ sai trong nhạc trưởng
    hoặc bộ lọc cần vá thêm), KHÔNG phải flaky test để bỏ qua."""
    rep = V.audit_routing()
    assert rep["dangling_references"] == [], (
        f"Tham chiếu treo thật trong nhạc trưởng: {rep['dangling_references']}")
    assert rep["total_agents"] >= 40  # sanity: đội agent không rỗng/vỡ


def test_real_system_title_counts_fresh():
    """CỔNG 'tiêu đề không lỗi thời': _BAN-DO-KET-NOI.md/README.md phải ghi ĐÚNG
    tổng agent thật. Bắt lớp bug đã xảy ra ≥2 lần (48→49→50, 2026-07-04/05) mà
    audit cấu trúc khác (dangling/orphan) không bắt được — tiêu đề trôi âm thầm
    sau mỗi lần thêm/bớt agent nếu không có công cụ đối chiếu lại."""
    rep = V.audit_routing()
    assert rep["title_count_mismatches"] == [], (
        f"Tiêu đề ghi số agent cũ, cần cập nhật: {rep['title_count_mismatches']}")


def test_check_title_counts_fresh_detects_stale_title():
    """Fixture: tiêu đề cố ý ghi số SAI → phải bị bắt (chứng minh detector THẬT
    hoạt động, không phải luôn trả rỗng)."""
    with tempfile.TemporaryDirectory() as d:
        agents_dir = Path(d) / ".claude" / "agents"
        _write(agents_dir / "_BAN-DO-KET-NOI.md",
               "# BẢN ĐỒ KẾT NỐI ĐỘI AGENT EBM (48 agent: 19 lâm sàng + 28 nghiên cứu + 1 guardrail)\n")
        old_dir = V.AGENTS_DIR
        try:
            V.AGENTS_DIR = agents_dir
            mismatches = V.check_title_counts_fresh(total_agents=50)
        finally:
            V.AGENTS_DIR = old_dir
        assert mismatches == [{"file": "_BAN-DO-KET-NOI.md", "claimed": 48, "actual": 50}]


def test_check_title_counts_fresh_passes_when_matching():
    with tempfile.TemporaryDirectory() as d:
        agents_dir = Path(d) / ".claude" / "agents"
        _write(agents_dir / "_BAN-DO-KET-NOI.md",
               "# BẢN ĐỒ KẾT NỐI ĐỘI AGENT EBM (50 agent: 21 lâm sàng + 28 nghiên cứu + 1 guardrail)\n")
        old_dir = V.AGENTS_DIR
        try:
            V.AGENTS_DIR = agents_dir
            mismatches = V.check_title_counts_fresh(total_agents=50)
        finally:
            V.AGENTS_DIR = old_dir
        assert mismatches == []


def _run_all():
    fns = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"  FAIL {fn.__name__}: {e}")
    print(f"\n{ok}/{len(fns)} passed")
    return ok == len(fns)


if __name__ == "__main__":
    raise SystemExit(0 if _run_all() else 1)
