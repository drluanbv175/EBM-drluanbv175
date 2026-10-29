"""Kết luận «đã cập nhật» (`da_cap_nhat`) của sổ bác sĩ đã xét — 29/10/2026.

Lỗi đo thật: 7 mục nhóm U của phiếu sàng lọc 25/10 đã được cập nhật bằng PHIÊN BẢN NỐI TIẾP (mục cũ giữ `apply` +
`flag` sang mục mới `consider`), nhưng sổ chỉ có `can_cap_nhat` — loại không đóng, chỉ rời danh sách khi PMID đang dùng
đổi. Cách cập nhật nối tiếp cố ý KHÔNG đổi PMID cũ ⇒ 7 mục nằm mãi trong hòm việc dù bác sĩ đã xét và gói đã cập nhật.
Vá: thêm `da_cap_nhat` (đóng), và `ghi_vuot_qua_da_xet.py` chỉ nhận khi bản dashboard HIỆN HÀNH dùng PMID đó chứa nguồn
mới đã xét.
Ngoại tuyến; chỉ ghi trong tmp_path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import dat_canh_chung_cu_moi as DC  # noqa: E402
import ghi_vuot_qua_da_xet as G  # noqa: E402


def _dash(tmp_path: Path, tep: dict[str, str]) -> Path:
    d = tmp_path / "EBM-Dashboards"
    d.mkdir()
    for ten, noi_dung in tep.items():
        (d / ten).write_text(noi_dung, encoding="utf-8", newline="\n")
    return d


def _ghi(so: Path, dash: Path, pmid_moi: str = "901,902") -> int:
    return G.main(["--pmid", "111", "--ket-luan", "da_cap_nhat", "--pmid-moi", pmid_moi, "--loi", "đồng ý ghi cả 7",
                   "--so", str(so), "--dash", str(dash), "--ghi"])


def test_da_cap_nhat_la_ket_luan_dong_va_nguon_moi_thi_mo_lai():
    so = {"111": {"pmid_moi_da_xet": ["901", "902"], "ket_luan": "da_cap_nhat"},
          "222": {"pmid_moi_da_xet": ["903"], "ket_luan": "can_cap_nhat"}}
    assert DC.da_xet_het("111", [{"pmid": "901"}, {"pmid": "902"}], so) is True
    assert DC.da_xet_het("111", [{"pmid": "901"}, {"pmid": "999"}], so) is False, "nguồn MỚI chưa xét ⇒ mở lại"
    assert DC.da_xet_het("222", [{"pmid": "903"}], so) is False, "can_cap_nhat vẫn không đóng"


def test_ghi_khi_ban_hien_hanh_da_co_nguon_moi(tmp_path):
    dash = _dash(tmp_path, {"WebDashboard_EBM_VanDeCuThe_Gia_20261025.html":
                            "{id:'ITEM-03',pmid:'111',decision:'apply',flag:'xem ITEM-30'},{id:'ITEM-30',pmid:'901'}"})
    so = tmp_path / "vuot-qua-da-xet.json"
    assert _ghi(so, dash) == 0
    m = json.loads(so.read_text(encoding="utf-8"))["muc"]["111"]
    assert m["ket_luan"] == "da_cap_nhat" and m["pmid_moi_da_xet"] == ["901", "902"]
    assert "WebDashboard_EBM_VanDeCuThe_Gia_20261025.html" in m["de_xuat_tu"], "ghi kèm bằng chứng gói đã cập nhật"


def test_tu_choi_khi_goi_chua_cap_nhat(tmp_path):
    dash = _dash(tmp_path, {"WebDashboard_EBM_VanDeCuThe_Gia_20261025.html": "{id:'ITEM-03',pmid:'111'}"})
    so = tmp_path / "vuot-qua-da-xet.json"
    assert _ghi(so, dash) == 2
    assert not so.exists(), "gói chưa cập nhật ⇒ không ghi gì"


def test_ban_cu_da_bi_ban_noi_tiep_thay_khong_duoc_tinh(tmp_path):
    dash = _dash(tmp_path, {
        "WebDashboard_EBM_VanDeCuThe_Gia_20261018.html": "{pmid:'111'},{pmid:'901'}",
        "WebDashboard_EBM_VanDeCuThe_Gia_20261025.html": "{pmid:'111'}",
    })
    so = tmp_path / "vuot-qua-da-xet.json"
    assert _ghi(so, dash) == 2, "nguồn mới chỉ nằm ở bản đã bị thay ⇒ bản đang dùng chưa cập nhật"
    assert not so.exists()


def test_nguon_moi_o_goi_khac_khong_tinh(tmp_path):
    dash = _dash(tmp_path, {
        "WebDashboard_EBM_VanDeCuThe_Gia_20261025.html": "{pmid:'111'}",
        "WebDashboard_EBM_VanDeCuThe_Khac_20261025.html": "{pmid:'901'}",
    })
    assert _ghi(tmp_path / "vuot-qua-da-xet.json", dash) == 2, "PMID đang dùng và nguồn mới phải ở CÙNG một gói"


def test_khong_khop_nham_chuoi_con_cua_nguon_moi(tmp_path):
    dash = _dash(tmp_path, {"WebDashboard_EBM_VanDeCuThe_Gia_20261025.html": "{pmid:'111'},{pmid:'9010'}"})
    assert _ghi(tmp_path / "vuot-qua-da-xet.json", dash) == 2, "9010 không phải nguồn mới 901"


def test_khong_khop_nham_chuoi_con_cua_pmid_dang_dung(tmp_path):
    dash = _dash(tmp_path, {"WebDashboard_EBM_VanDeCuThe_Gia_20261025.html": "{pmid:'1111'},{pmid:'901'}"})
    assert _ghi(tmp_path / "vuot-qua-da-xet.json", dash) == 2, "1111 không phải PMID đang dùng 111"


def test_cac_ket_luan_khac_khong_doi_hanh_vi(tmp_path):
    so = tmp_path / "vuot-qua-da-xet.json"
    assert G.main(["--pmid", "222", "--ket-luan", "can_cap_nhat", "--pmid-moi", "903", "--loi", "cần cập nhật",
                   "--so", str(so), "--dash", str(tmp_path / "vang"), "--ghi"]) == 0, "can_cap_nhat không đo gói"
    assert json.loads(so.read_text(encoding="utf-8"))["muc"]["222"]["ket_luan"] == "can_cap_nhat"
