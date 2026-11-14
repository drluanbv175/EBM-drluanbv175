"""Dọn mức thấp hòm việc + chốt doctrine tác vụ lịch (14/11/2026, việc P — bác sĩ «Tiếp tục» ~17:00, sau thẩm định #356/#348).

Ba khe đo được trên mã sống (master c248fbb):
  (1) `tu_de_xuat_viec` chỉ đọc `phat_hien` của cảm biến người chết lịch nền ⇒ mọi mục `khong_do_duoc` (kể cả trạng thái ⚪ mới
      «KẾT THÚC không đọc được mã» của #356) biến mất khỏi bảng tự đề xuất lẫn hòm việc — im lặng như xanh.
  (2) Bảng in «🟢 KHÔNG CÒN VIỆC NÀO» và hòm in «🟢 không có việc nào chờ bác sĩ» dù còn mục ⚪ của giác quan còn sống ⇒ nay
      «không có việc đỏ, còn N mục chưa đo được».
  (3) Chốt `doctrine_tac_vu_lich` còn âm tính giả với «lúc/vào», giờ «7h/7 giờ», ngoặc «(thứ Hai)», «(lịch)», gạch «—» xen giữa
      «tác vụ …» và tên — mở rộng CÓ KIỂM SOÁT, kèm câu dương tính (không được bắt) để chốt chặn commit không báo oan.
Không gọi mạng, không đọc log/settings/state thật (thư mục tạm, phép đo giả).
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import socket
import sys
import urllib.request
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T = _nap("_hvtd_tdxv", "tu_de_xuat_viec.py")
HV = _nap("_hvtd_hv", "hom_viec_mot_cua.py")
K = _nap("_hvtd_kln", "kiem_lich_nen.py")
sys.path.insert(0, str(REPO / "tools"))
import verify_claude_code_repo_alignment as V  # noqa: E402

KHONG_RO = ("tv: kỳ 04/11/2026 18:30 có KẾT THÚC 04/11 19:06 trong hạn nhưng không đọc được mã (không có «(mã N)»/«tổng "
            "thể=…») — không tính đúng hẹn, cũng không phải lỡ")


@pytest.fixture()
def _sach():
    for ds in (T._GIAC_QUAN_CHET, T._CHUA_DO, T._THONG_TIN):
        ds.clear()
    T._SO_GIAC_QUAN["chay"] = 0
    yield
    for ds in (T._GIAC_QUAN_CHET, T._CHUA_DO, T._THONG_TIN):
        ds.clear()


# ── (1) khong_do_duoc của cảm biến lịch nền ⇒ dòng ⚪ ─────────────────────────────────────────────────────────────────────

def test_muc_chua_do_moi_muc_mot_dong():
    ra = T.muc_chua_do_lich_nen([KHONG_RO, "cap-nhat-thang-ebm: dấu vết log chỉ có từ kỳ 03/12/2026"])
    assert len(ra) == 2 and all(x.startswith("lịch nền — ") for x in ra)
    assert "không đọc được mã" in ra[0] and "03/12/2026" in ra[1]
    assert T.muc_chua_do_lich_nen([]) == []


@pytest.mark.parametrize("sai", [None, "một chuỗi", {"a": 1}, 3])
def test_muc_chua_do_sai_kieu_la_trang_khong_phai_rong(sai):
    ra = T.muc_chua_do_lich_nen(sai)
    assert len(ra) == 1 and "sai kiểu" in ra[0], "khong_do_duoc hỏng không được đọc thành «không còn gì chưa đo»"


def test_giac_quan_ket_thuc_khong_doc_duoc_ma_thanh_dong_trang(_sach):
    ra = T.giac_quan_nguoi_chet_lich_nen(lambda: {"phat_hien": [], "khong_do_duoc": [KHONG_RO], "ok": 2})
    assert ra == [], "⚪ không phải việc 🛎 (không lệnh nào làm nó hết ⚪ ngay)"
    assert len(T._CHUA_DO) == 1 and "không đọc được mã" in T._CHUA_DO[0]
    assert T._GIAC_QUAN_CHET == [], "giác quan vẫn SỐNG — mục ⚪ không được tính là giác quan chết"
    assert T._SO_GIAC_QUAN["chay"] == 1


def test_giac_quan_van_phan_loai_phat_hien_nhu_cu(_sach):
    kq = {"phat_hien": [{"uu": 0, "thong_diep": "«tv» kỳ 04/11: KHÔNG có dấu vết nào"},
                        {"uu": 2, "thong_diep": "«tv» kỳ 04/10: cũ"}],
          "khong_do_duoc": [], "ok": 0}
    ra = T.giac_quan_nguoi_chet_lich_nen(lambda: kq)
    assert [(u, ai) for u, ai, _v, _l in ra] == [(0, "🛎")] and "KHÔNG có dấu vết" in ra[0][2]
    assert len(T._THONG_TIN) == 1 and T._CHUA_DO == []


def test_giac_quan_cong_cu_hong_la_giac_quan_chet(_sach):
    def hong():
        raise OSError("x")
    assert T.giac_quan_nguoi_chet_lich_nen(hong) == []
    assert len(T._GIAC_QUAN_CHET) == 1 and "OSError" in T._GIAC_QUAN_CHET[0] and T._CHUA_DO == []


def test_giac_quan_ket_qua_thieu_khoa_khong_ghi_nua_chung(_sach):
    """Thiếu `khong_do_duoc` ⇒ giác quan chết; ⓘ của `phat_hien` không được ghi trước rồi bỏ dở."""
    kq = {"phat_hien": [{"uu": 2, "thong_diep": "cũ"}], "ok": 0}
    assert T.giac_quan_nguoi_chet_lich_nen(lambda: kq) == []
    assert len(T._GIAC_QUAN_CHET) == 1 and "KeyError" in T._GIAC_QUAN_CHET[0]
    assert T._THONG_TIN == [] and T._CHUA_DO == []


SO_THANG = {"cua_so_ngay": 40, "tac_vu": [{"id": "tv", "cron": "30 18 4 * *", "tu_ngay": "2026-09-01", "grace_gio": 30,
                                           "dau_vet": {"loai": "log-ket-thuc", "path": "state/tv.log"}}]}
XET = dt.datetime(2026, 11, 6, 9, 0)


def test_cam_bien_that_ket_thuc_khong_ma_toi_duoc_bang(_sach, tmp_path):
    """Đầu–cuối trên `kiem_lich_nen.kiem()` THẬT (log tạm): dòng KẾT THÚC thiếu mã ⇒ ⚪ trong bảng, không im."""
    log = tmp_path / "state" / "tv.log"
    log.parent.mkdir(parents=True)
    log.write_text("===== 2026-10-04 19:00:00 : KẾT THÚC tv (mã 0)\n===== 2026-11-04 19:06:01 : KẾT THÚC tv\n",
                   encoding="utf-8", newline="\n")
    ra = T.giac_quan_nguoi_chet_lich_nen(lambda: K.kiem(XET, SO_THANG, tmp_path))
    assert ra == [] and len(T._CHUA_DO) == 1 and "không đọc được mã" in T._CHUA_DO[0], T._CHUA_DO


def test_main_goi_giac_quan_va_dua_trang_vao_bang_json(monkeypatch, tmp_path, capsys, _sach):
    """Nối dây: main() thật gọi giác quan, in dòng ⚪ và ghi khoá `chua_do` cho hòm việc."""
    goc = T.giac_quan_nguoi_chet_lich_nen
    goi: list[int] = []

    def gia():
        goi.append(1)
        return goc(lambda: {"phat_hien": [], "khong_do_duoc": ["MỐC-TRẮNG-20261114"], "ok": 1})

    def cam_mang(*a, **k):
        raise AssertionError("test không được gọi mạng")

    monkeypatch.setattr(T, "giac_quan_nguoi_chet_lich_nen", gia)
    monkeypatch.setattr(T, "_chay", lambda lenh, giay=120, cwd=None: "")
    # CI (gh/urlopen tới api.github.com) là đường mạng duy nhất không đi qua `_chay` ⇒ thay bằng kết quả giả + cấm urlopen.
    monkeypatch.setattr(T, "doc_ci_mot_repo", lambda *a, **k: ("success", "master"))
    monkeypatch.setattr(urllib.request, "urlopen", cam_mang)
    monkeypatch.setattr(socket.socket, "connect", cam_mang)
    monkeypatch.setattr(T, "DASH", tmp_path / "EBM-Dashboards-khong-ton-tai")
    tep = tmp_path / "hom-viec.json"
    monkeypatch.setattr(sys, "argv", ["tu_de_xuat_viec.py", "--gon", "--json", str(tep)])
    try:
        T.main()
    except SystemExit:
        pass
    assert goi, "main() không gọi giac_quan_nguoi_chet_lich_nen"
    assert tep.exists(), "main() không chạy tới bước ghi bảng — phép thử không đo được"
    assert any("MỐC-TRẮNG-20261114" in x for x in json.loads(tep.read_text(encoding="utf-8"))["chua_do"])
    ra = capsys.readouterr().out
    assert "⚪ chưa đo được: lịch nền — MỐC-TRẮNG-20261114" in ra
    assert "🟢 KHÔNG CÒN VIỆC" not in ra


# ── (2) không in «🟢 không còn việc» khi còn ⚪ ─────────────────────────────────────────────────────────────────────────────

def test_tom_tat_bang_chi_xanh_khi_khong_con_gi_chua_do():
    assert "🟢 KHÔNG CÒN VIỆC NÀO" in T.dong_tom_tat(0, 0, 0)[0]
    chi_trang = " ".join(T.dong_tom_tat(0, 0, 1))
    assert "🟢" not in chi_trang and "không có việc đỏ, còn 1 mục chưa đo được" in chi_trang.lower()
    assert "còn 3 mục chưa đo được" in " ".join(T.dong_tom_tat(0, 2, 1))
    assert "🟢" not in " ".join(T.dong_tom_tat(0, 1, 0)), "giác quan chết vẫn chặn dòng xanh như cũ"
    assert T.dong_tom_tat(4, 0, 1) == [], "có việc ⇒ bảng tự liệt kê, không có dòng tóm tắt"


def _bang(viec=(), chet=(), **them):
    d = {"sinh_luc": "2026-11-14T07:00:00", "chet": list(chet), "viec": list(viec)}
    d.update(them)
    return d


GIO = dt.datetime(2026, 11, 14, 8)


def test_hom_khong_xanh_khi_con_muc_chua_do():
    cuoi = HV.dong_hom(_bang(chua_do=["lịch nền — " + KHONG_RO]), GIO)[-1]
    assert "🟢" not in cuoi
    assert "không có việc đỏ chờ bác sĩ, còn 1 mục chưa đo được" in cuoi and "⚪ 1 mục chưa đo được" in cuoi
    assert "lịch nền" in cuoi, "phải nói mục ⚪ là gì, không chỉ đếm"


def test_hom_cong_ca_giac_quan_chet_va_muc_chua_do():
    cuoi = HV.dong_hom(_bang(chet=["x (y)"], chua_do=["lịch nền — a"]), GIO)[-1]
    assert "còn 2 mục chưa đo được" in cuoi and "⚪ 1 giác quan không đo được" in cuoi and "🟢" not in cuoi


def test_hom_bang_cu_khong_co_khoa_van_xanh():
    """Tương thích ngược: bảng sinh trước 14/11 không có `chua_do` — không có gì chưa đo ⇒ vẫn xanh như cũ."""
    assert "🟢 không có việc nào chờ bác sĩ" in HV.dong_hom(_bang(), GIO)[-1]


@pytest.mark.parametrize("sai", ["một chuỗi", {"a": 1}, 7])
def test_hom_khoa_chua_do_sai_kieu_khong_xanh(sai):
    cuoi = HV.dong_hom(_bang(chua_do=sai), GIO)[-1]
    assert "🟢" not in cuoi and "sai kiểu" in cuoi


def test_hom_co_viec_bac_si_van_neu_muc_chua_do():
    cuoi = HV.dong_hom(_bang(viec=[{"uu": 1, "ai": "👤", "viec": "ký G2", "lenh": "x"}], chua_do=["lịch nền — a"]), GIO)[-1]
    assert "⚪ 1 mục chưa đo được" in cuoi and "không có việc đỏ" not in cuoi


def test_vong_tron_ghi_json_toi_hom(tmp_path):
    tep = tmp_path / "state" / "hv.json"
    T.ghi_json([(2, "🤖", "máy", "lệnh")], [], tep, 9, ["lịch nền — " + KHONG_RO])
    d = HV.doc(tep)
    assert d is not None and d["chua_do"] == ["lịch nền — " + KHONG_RO]
    cuoi = HV.dong_hom(d, dt.datetime.now())[-1]
    assert "🟢" not in cuoi and "còn 1 mục chưa đo được" in cuoi
    T.ghi_json([], [], tep, 9)
    assert json.loads(tep.read_text(encoding="utf-8"))["chua_do"] == [], "gọi kiểu cũ (4 tham số) vẫn ghi khoá rỗng"


# ── (3) chốt doctrine_tac_vu_lich: mở rộng có kiểm soát ──────────────────────────────────────────────────────────────────

def _kiem_doctrine(tmp_path: Path, noi_dung: str) -> dict:
    tl = tmp_path / "CLAUDE.md"
    tl.write_text(noi_dung, encoding="utf-8", newline="\n")
    tm = tmp_path / "scheduled-tasks"
    for ten in ("cap-nhat-thang-ebm", "goi-duyet-tuan-ebm"):
        (tm / ten).mkdir(parents=True)
        (tm / ten / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8", newline="\n")
    so = tmp_path / "lich-nen-ky-vong.json"
    so.write_text(json.dumps({"tac_vu": [{"id": "cap-nhat-thang-ebm"}]}), encoding="utf-8", newline="\n")
    return V.check_tac_vu_lich_trong_doctrine({"CLAUDE.md": tl}, tm, so)


AM_TINH_GIA = (  # câu GỌI `tên` là tác vụ lịch — chốt PHẢI bắt (thẩm định #356 đo được 4 câu đầu lọt)
    "Gói nằm sẵn (tác vụ lịch tuần thứ 2 lúc 07:00 `goi-duyet-tuan-ebm`).",
    "Gói nằm sẵn (tác vụ lịch tuần vào thứ Hai `goi-duyet-tuan-ebm`).",
    "Gói nằm sẵn (tác vụ lịch hằng tuần (thứ Hai) `goi-duyet-tuan-ebm`).",
    "Gói nằm sẵn — tác vụ mới — `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ (lịch) `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ mới – `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ mới - `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ lịch lúc 7h `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ lịch lúc 7 giờ 30 `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ lịch 18g30 `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ mùng 4 `goi-duyet-tuan-ebm`.",
    "Chạy bởi tác vụ lịch (thứ Hai, 18:00) `goi-duyet-tuan-ebm`.",
)


@pytest.mark.parametrize("cau", AM_TINH_GIA)
def test_doctrine_bat_cau_tung_lot(tmp_path, cau):
    kq = _kiem_doctrine(tmp_path, cau + "\n")
    assert kq["status"] == "FAIL" and any("goi-duyet-tuan-ebm" in e and "ĐÃ BỎ" in e for e in kq["errors"]), (cau, kq)


DUONG_TINH = (  # câu KHÔNG nói `tên` là tác vụ lịch — chốt chặn commit nên KHÔNG được bắt
    "(c) gói duyệt thuộc tác vụ tháng `cap-nhat-thang-ebm` (quy trình `goi-duyet-tuan-ebm`).",
    "Gói thuộc tác vụ tháng (quy trình `goi-duyet-tuan-ebm`).",
    "Tác vụ lịch (app Claude trên Mac): đo sống bằng `list_scheduled_tasks` + `goi-duyet-tuan-ebm`.",
    "Tác vụ tháng — gọi agent `goi-duyet-tuan-ebm` khi cần.",
    "Tác vụ (agent) `goi-duyet-tuan-ebm`.",
    "Tác vụ (lịch tuần, quy trình) `goi-duyet-tuan-ebm`.",
    "Tác vụ 2 gói `goi-duyet-tuan-ebm`.",
    "Tác vụ tháng vào repo `goi-duyet-tuan-ebm`.",
    "Tác vụ tháng đọc quy trình `goi-duyet-tuan-ebm` lúc 18:00.",
)


@pytest.mark.parametrize("cau", DUONG_TINH)
def test_doctrine_khong_bao_oan_quy_trinh(tmp_path, cau):
    kq = _kiem_doctrine(tmp_path, cau + "\n")
    assert kq["status"] == "PASS", (cau, kq)


def test_doctrine_tai_lieu_that_van_dat():
    """CLAUDE.md + AGENTS.md đang track (gồm §1(c) gọi `goi-duyet-tuan-ebm` đúng là QUY TRÌNH) vẫn qua chốt sau khi mở rộng."""
    kq = V.check_tac_vu_lich_trong_doctrine()
    assert kq["status"] == "PASS", kq
