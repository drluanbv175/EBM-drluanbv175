"""Khoá chốt «doctrine không nhắc tác vụ lịch đã bỏ» (14/11/2026).

Lỗi có thật: 13/11 bác sĩ gộp lịch nội dung thành MỘT tác vụ tháng và bỏ tác vụ quý thang điểm,
nhưng CLAUDE.md vẫn ghi «tác vụ lịch `goi-duyet-tuan-ebm`» (§1(c)) và «tác vụ `kiem-thang-diem-quy`»
(§10) tới khi lượt kiểm tháng 14/11 đọc bằng mắt (#334, #336). Các test dưới đây kiểm HÀNH VI của
`check_tac_vu_lich_trong_doctrine()` trên tài liệu thật và trên tệp tạm — kể cả không dương tính
giả với `goi-duyet-tuan-ebm` khi nó được gọi đúng là QUY TRÌNH.
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS))
import verify_claude_code_repo_alignment as V  # noqa: E402

_GOC = _TOOLS.parent


def _moi_truong(tmp_path: Path, noi_dung: str, ky_vong: list[str] | None = None,
                thu_muc: tuple[str, ...] = ("cap-nhat-thang-ebm", "goi-duyet-tuan-ebm")):
    """Dựng bộ ba (tài liệu, thư mục nguồn tác vụ, sổ kỳ vọng) giả lập trong tmp_path."""
    tl = tmp_path / "CLAUDE.md"
    tl.write_text(noi_dung, encoding="utf-8", newline="\n")
    tm = tmp_path / "scheduled-tasks"
    for ten in thu_muc:
        (tm / ten).mkdir(parents=True)
        (tm / ten / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8", newline="\n")
    so = tmp_path / "lich-nen-ky-vong.json"
    so.write_text(json.dumps({"tac_vu": [{"id": i} for i in (ky_vong or ["cap-nhat-thang-ebm"])]}),
                  encoding="utf-8", newline="\n")
    return {"CLAUDE.md": tl}, tm, so


def _kiem(tmp_path: Path, noi_dung: str, **kw) -> dict:
    tai_lieu, tm, so = _moi_truong(tmp_path, noi_dung, **kw)
    return V.check_tac_vu_lich_trong_doctrine(tai_lieu, tm, so)


def test_doctrine_that_dat():
    """CLAUDE.md + AGENTS.md gốc đang track phải qua chốt — chạy trên tài liệu hiện tại."""
    kq = V.check_tac_vu_lich_trong_doctrine()
    assert kq["status"] == "PASS", kq


def test_cau_cu_par10_tac_vu_quy_da_bo_bi_chan(tmp_path):
    """Nguyên văn câu §10 trước #334 — tác vụ quý không còn ở dạng nào."""
    kq = _kiem(tmp_path, "- Kiểm rút bài + độ tươi 37 thang điểm (QUÝ, tác vụ `kiem-thang-diem-quy`): …\n")
    assert kq["status"] == "FAIL"
    assert any("kiem-thang-diem-quy" in e and "ĐÃ BỎ" in e for e in kq["errors"]), kq
    assert all(e.startswith("CLAUDE.md:1:") for e in kq["errors"]), "phải chỉ đúng dòng"


def test_goi_tac_vu_lich_cho_ten_chi_con_la_quy_trinh_bi_chan(tmp_path):
    """Nguyên văn §1(c) trước #336: thư mục goi-duyet-tuan-ebm CÒN (quy trình) nhưng lịch đã bỏ."""
    kq = _kiem(tmp_path, "(c) gói duyệt tuần tự nằm sẵn tối thứ Hai (tác vụ lịch `goi-duyet-tuan-ebm`).\n")
    assert kq["status"] == "FAIL"
    assert any("goi-duyet-tuan-ebm" in e and "ĐÃ BỎ" in e for e in kq["errors"]), kq


def test_goi_dung_la_quy_trinh_va_tac_vu_thang_con_song_khong_bi_chan(tmp_path):
    """Không dương tính giả: câu hiện hành §1(c) và đường dẫn tới tệp quy trình."""
    kq = _kiem(tmp_path,
               "(c) gói duyệt thuộc tác vụ tháng `cap-nhat-thang-ebm` (quy trình `goi-duyet-tuan-ebm`).\n"
               "Đọc `sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md`.\n"
               "Tác vụ lịch (app Claude trên Mac): đo sống bằng `list_scheduled_tasks`.\n")
    assert kq["status"] == "PASS", kq


def test_tac_vu_khong_ton_tai_bi_chan_du_khong_nam_trong_danh_sach_da_bo(tmp_path):
    """Lớp chung: tác vụ bị xoá mà quên ghi danh sách đã bỏ vẫn bị bắt."""
    kq = _kiem(tmp_path, "Chạy hằng ngày bởi tác vụ lịch `hoi-dong-c1a-hang-ngay`.\n")
    assert kq["status"] == "FAIL"
    assert any("hoi-dong-c1a-hang-ngay" in e and "không có trong" in e for e in kq["errors"]), kq


def test_nhieu_ten_sau_mot_cum_tac_vu_deu_duoc_xet(tmp_path):
    kq = _kiem(tmp_path, "Các tác vụ `cap-nhat-thang-ebm`, `tac-vu-ma` và `tac-vu-ma-hai` chạy tối.\n")
    assert kq["status"] == "FAIL"
    loi = " ".join(kq["errors"])
    assert "`tac-vu-ma`" in loi and "`tac-vu-ma-hai`" in loi and "cap-nhat-thang-ebm" not in loi


def test_duong_dan_toi_thu_muc_tac_vu_khong_co_bi_chan(tmp_path):
    kq = _kiem(tmp_path, "Định nghĩa ở `sync/scheduled-tasks/khong-con-nua/SKILL.md`.\n")
    assert kq["status"] == "FAIL"
    assert any("scheduled-tasks/khong-con-nua" in e for e in kq["errors"]), kq


def test_thu_muc_sot_khong_co_skill_khong_tinh_la_con_song(tmp_path):
    """Thư mục rỗng sót lại sau `git rm` (OneDrive hay để lại) không được làm tác vụ đã xoá «sống lại»."""
    tai_lieu, tm, so = _moi_truong(tmp_path, "Chạy bởi tác vụ lịch `tac-vu-da-xoa`.\n")
    (tm / "tac-vu-da-xoa").mkdir()
    kq = V.check_tac_vu_lich_trong_doctrine(tai_lieu, tm, so)
    assert kq["status"] == "FAIL" and any("tac-vu-da-xoa" in e for e in kq["errors"]), kq


def test_nhac_ten_da_bo_ngoai_ngu_canh_tac_vu_van_bi_chan(tmp_path):
    """Luật 3: tên đã bỏ hẳn, nhắc trần (không dấu huyền, không «tác vụ …») vẫn đỏ."""
    kq = _kiem(tmp_path, "Báo cáo giam-sat-acc-aha-quy nằm ở state/.\n")
    assert kq["status"] == "FAIL"
    assert any("giam-sat-acc-aha-quy" in e and "nhắc tác vụ lịch đã bỏ" in e for e in kq["errors"]), kq


def test_ten_dai_hon_chua_ten_da_bo_khong_bi_chan(tmp_path):
    """Ranh giới từ: `kiem-thang-diem-quy-moi` không phải `kiem-thang-diem-quy`."""
    kq = _kiem(tmp_path, "Công cụ `kiem-thang-diem-quy-moi` (chạy tay).\n")
    assert kq["status"] == "PASS", kq


def test_van_ban_nfd_van_bi_bat(tmp_path):
    """«tác vụ» gõ dạng tổ hợp (NFD, hay gặp khi dán từ macOS) không được lọt luật 1."""
    cau = unicodedata.normalize("NFD", "Chạy bởi tác vụ lịch `tac-vu-ma`.\n")
    assert "tác vụ" not in cau  # tiền đề: chuỗi thật sự ở dạng NFD
    kq = _kiem(tmp_path, cau)
    assert kq["status"] == "FAIL", kq


def test_ten_da_bo_ma_con_trong_so_ky_vong_la_lech(tmp_path):
    kq = _kiem(tmp_path, "Không nhắc gì.\n", ky_vong=["cap-nhat-thang-ebm", "kiem-thang-diem-quy"])
    assert kq["status"] == "FAIL"
    assert any("vừa nằm trong TAC_VU_LICH_DA_BO" in e for e in kq["errors"]), kq


def test_so_ky_vong_hong_la_fail_khong_phai_pass(tmp_path):
    tai_lieu, tm, so = _moi_truong(tmp_path, "Không nhắc gì.\n")
    so.write_text("{hỏng", encoding="utf-8", newline="\n")
    kq = V.check_tac_vu_lich_trong_doctrine(tai_lieu, tm, so)
    assert kq["status"] == "FAIL" and any("không đọc được sổ kỳ vọng" in e for e in kq["errors"])
    kq2 = V.check_tac_vu_lich_trong_doctrine(tai_lieu, tmp_path / "vang", so.with_name("vang.json"))
    assert kq2["status"] == "FAIL"


def test_moi_ten_da_bo_neo_vao_tep_nhat_ky_ghi_loi_bac_si():
    """Danh sách đã bỏ không được tự chế: mỗi tên phải có mặt trong đúng tệp nhật ký nó dẫn."""
    assert V.TAC_VU_LICH_DA_BO
    for ten, nguon in V.TAC_VU_LICH_DA_BO.items():
        tep = _GOC / nguon
        assert tep.is_file(), nguon
        assert ten in tep.read_text(encoding="utf-8"), (ten, nguon)
        assert not (_GOC / "sync" / "scheduled-tasks" / ten).exists() or ten == "goi-duyet-tuan-ebm", (
            f"{ten}: thư mục nguồn còn — chỉ goi-duyet-tuan-ebm được giữ làm quy trình")


def test_chot_duoc_noi_vao_run_verification():
    """Chốt không ai gọi thì không tồn tại — pre-commit chạy run_verification()."""
    assert "doctrine_tac_vu_lich" in [c["name"] for c in V.run_verification()["checks"]]
