"""Cửa vào định tuyến ba câu «hội đồng cổng» mà README §Ma trận định tuyến đã khai. 14/10/2026.

Trước bản vá cả ba câu (trừ khi tình cờ chứa «đề tài») ra `unknown`. Cụm cố ý HẸP; cờ đỏ / mô tả ca lâm sàng vẫn thắng.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from intent import CLINICAL_ORCHESTRATOR, RESEARCH_ORCHESTRATOR, route  # noqa: E402

CAU_README = [
    "Họp hội đồng cổng G2",
    "tranh biện trước khi kết luận cổng G4",
    "đánh giá chéo đầu ra các agent cổng G1",
    "hop hoi dong cong G0",                       # gõ không dấu
    "danh gia cheo dau ra cac agent",
]


@pytest.mark.parametrize("cau", CAU_README)
def test_cau_hoi_dong_cong_vao_nhac_truong_nghien_cuu(cau):
    r = route(cau)
    assert (r.kind, r.target) == ("research_topic", RESEARCH_ORCHESTRATOR), (cau, r.as_dict())


def test_hoi_dong_dao_duc_tran_khong_bi_cum_moi_bat():
    """«hội đồng» trần (Hội đồng Đạo đức) KHÔNG được khớp qua cụm mới."""
    for cau in ("Hội đồng Đạo đức hẹn lịch khi nào", "hoi dong dao duc hen lich khi nao"):
        assert route(cau).kind != "research_topic", (cau, route(cau).as_dict())


def test_co_do_van_thang_cum_hoi_dong_cong():
    r = route("bệnh nhân nữ 60 tuổi đau ngực dữ dội vã mồ hôi, họp hội đồng cổng sau")
    assert (r.kind, r.target) == ("clinical_case", CLINICAL_ORCHESTRATOR), r.as_dict()
