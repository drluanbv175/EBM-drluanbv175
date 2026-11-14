#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy bộ canh lịch nền qua email (14/11/2026).

Vì sao: lượt lịch hỏng (kỳ lỡ, lệnh chưa được phép) chỉ lộ khi bác sĩ mở Claude — đo 28/10/2026 gói tuần chết 4 lượt liền
rồi lỡ hẳn kỳ 26/10 trước khi có người thấy. Kiểm HÀNH VI: chỉ lỗi đỏ mới gửi; MỘT email; chống lặp 24 giờ theo NỘI DUNG;
kênh chưa bật/gửi lỗi ⇒ mã 2, không giả đã gửi, không ghi sổ; không giá trị cấu hình nào lọt ra stdout/sổ/log; launchd mặc
định chạy khô. Offline: SMTP/notify GIẢ (gói `app` giả trong tmp), không gửi thật, không đọc ~/.ebm-secrets."""
from __future__ import annotations

import importlib.util as _ilu
import json
import plistlib
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = _ilu.spec_from_file_location("canh_lich_email", REPO / "tools" / "canh_lich_nen_email.py")
cle = _ilu.module_from_spec(_spec)
sys.modules["canh_lich_email"] = cle
_spec.loader.exec_module(cle)

# Giá trị cấu hình GIẢ — đủ đặc trưng để dò rò rỉ ở stdout/stderr/sổ/log.
MK_GIA = "MATKHAU-GIA-zq81"
DIA_CHI_GIA = "bacsi-gia@vd.test"
MAY_CHU_GIA = "smtp.may-chu-gia.test"
BI_MAT = (MK_GIA, DIA_CHI_GIA, MAY_CHU_GIA)


def _lich(do=(), phu=(), do_duoc=True):
    return {"do_duoc": do_duoc, "do": list(do), "phu": list(phu)}


# ---- cảm biến: gọi hàm kiem(), phân loại đúng ngữ nghĩa của từng cảm biến ------------------------------------------------
def test_do_lich_chi_uu_toi_da_1_la_do():
    kq = {"phat_hien": [
        {"id": "a", "ky": "2026-11-01 18:30", "muc": "lo", "uu": 0, "thong_diep": "«a» kỳ 01/11: KHÔNG có dấu vết nào"},
        {"id": "b", "ky": "2026-11-03 18:00", "muc": "tre", "uu": 1, "thong_diep": "«b» kỳ 03/11: có lượt chạy TRỄ"},
        {"id": "c", "ky": "2026-10-04 18:30", "muc": "lo", "uu": 2, "thong_diep": "«c» kỳ cũ đã lỡ, kỳ sau đã chạy"}],
        "khong_do_duoc": ["x: chưa khai dấu vết"], "ok": 1}
    r = cle.do_lich(lambda: kq)
    assert r["do"] == ["🔴 «a» kỳ 01/11: KHÔNG có dấu vết nào", "🟠 «b» kỳ 03/11: có lượt chạy TRỄ"]
    assert r["phu"] == ["x: chưa khai dấu vết"] and r["do_duoc"] is True


def test_do_lich_khong_tac_vu_nao_do_duoc_la_trang_khong_phai_xanh():
    r = cle.do_lich(lambda: {"phat_hien": [], "khong_do_duoc": ["thiếu log"], "ok": 0})
    assert r["do_duoc"] is False and r["do"] == []


def test_cam_bien_sap_la_khong_do_duoc_khong_sap_cong_cu():
    def hong():
        raise KeyError("cron")
    for ham in (cle.do_lich, cle.do_quyen):
        r = ham(hong)
        assert r["do_duoc"] is False and r["do"] == [] and "KeyError" in r["phu"][0]


def test_do_quyen_thieu_khai_va_thieu_may_la_do_va_rut_duong_dan_nguoi_dung():
    tuyet_doi = "//" + str(REPO).lstrip("/")
    kq = {"khong_do": [], "thieu_khai": [("goi-duyet-tuan-ebm", "python3 tools/moi.py")],
          "thieu_may": ["Bash(python3 tools/a.py)", f"Edit({tuyet_doi}/queue/**)"]}
    r = cle.do_quyen(lambda: kq)
    assert len(r["do"]) == 3 and r["do_duoc"] is True
    assert "goi-duyet-tuan-ebm" in r["do"][0] and "python3 tools/moi.py" in r["do"][0]
    assert r["do"][2] == "🔴 máy chưa áp quy tắc: Edit(<gốc-repo>/queue/**)"
    assert not any(str(REPO) in x for x in r["do"]), "email không được mang đường dẫn thư mục người dùng"


def test_do_quyen_chi_co_khong_do_la_trang():
    r = cle.do_quyen(lambda: {"khong_do": ["máy này là linux"], "thieu_khai": [], "thieu_may": []})
    assert r == {"do_duoc": False, "do": [], "phu": ["máy này là linux"]}


def test_hai_cam_bien_that_chay_duoc_va_dung_dang():
    """Import THẬT hai cảm biến (không đọc chuỗi in). Trên bản sao trần thường ra ⚪ — chỉ kiểm không sập và đúng dạng."""
    for r in (cle.do_lich(), cle.do_quyen()):
        assert set(r) == {"do_duoc", "do", "phu"} and isinstance(r["do"], list)
        assert not any("lỗi (" in x and "không đo được" in x for x in r["phu"]), r["phu"]


# ---- vân tay + sổ chống lặp ----------------------------------------------------------------------------------------------
def test_van_tay_khong_phu_thuoc_thu_tu_nhung_theo_noi_dung():
    assert cle.van_tay(["a", "b"]) == cle.van_tay(["b", "a"])
    assert cle.van_tay(["a", "b"]) != cle.van_tay(["a", "c"])


def test_chong_lap_24_gio_va_don_van_tay_cu():
    st = cle.ghi_da_gui({}, "vt1", 1_000_000.0)
    assert cle.lan_gui_gan(st, "vt1", 1_000_000.0 + 23 * 3600) == 1_000_000.0
    assert cle.lan_gui_gan(st, "vt1", 1_000_000.0 + 24 * 3600) is None
    assert cle.lan_gui_gan(st, "vt-khac", 1_000_000.0 + 60) is None
    st2 = cle.ghi_da_gui(st, "vt2", 1_000_000.0 + 15 * 86400)
    assert set(st2["da_gui"]) == {"vt2"}, "vân tay > 14 ngày phải được dọn"


@pytest.mark.parametrize("st", [{}, {"da_gui": []}, {"da_gui": {"vt": "hỏng"}}, {"da_gui": None}])
def test_so_hong_thi_duoc_gui_lai_khong_sap(st):
    assert cle.lan_gui_gan(st, "vt", 1000.0) is None
    assert cle.ghi_da_gui(st, "vt", 1000.0)["da_gui"] == {"vt": 1000.0}


def test_state_hong_doc_rong_va_ghi_nguyen_tu(tmp_path):
    p = tmp_path / "state" / "s.json"
    for noi_dung in ("", "{hỏng", "[]"):
        p.parent.mkdir(exist_ok=True)
        p.write_text(noi_dung, encoding="utf-8")
        assert cle.doc_state(p) == {}
    cle.ghi_state({"da_gui": {"x": 1.0}}, p)
    assert cle.doc_state(p) == {"da_gui": {"x": 1.0}} and list(p.parent.glob("*.tmp*")) == []


def test_so_nam_trong_state_va_state_khong_vao_git():
    assert cle.TEP_STATE.parent == REPO / "state"
    dong = [x.strip() for x in (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()]
    assert "/*" in dong and not any(x.rstrip("/") == "!/state" for x in dong), ".gitignore phải loại state/"


# ---- soạn email ------------------------------------------------------------------------------------------------------
def test_email_mot_ban_tom_tat_co_viec_can_lam_va_tran_muc():
    import datetime as dt
    quyen = _lich(do=[f"🔴 máy chưa áp quy tắc: Bash(python3 tools/t{i}.py)" for i in range(20)])
    tieu_de, than = cle.soan_email(_lich(do=["🔴 «a» kỳ 01/11: KHÔNG có dấu vết nào"]), quyen, dt.datetime(2026, 11, 14, 9))
    assert tieu_de == "[EBM] Lịch nền hỏng — 21 lỗi đỏ (14/11/2026)"
    assert "«a» kỳ 01/11" in than and "list_scheduled_tasks" in than and "quyen_lich_nen.py --ap-dung" in than
    assert "… và 5 mục nữa" in than and "t19.py" not in than


# ---- luồng chính với kênh GIẢ ------------------------------------------------------------------------------------------
class _KenhGia:
    def __init__(self, gui=None, trang_thai=None):
        self.goi: list[tuple[str, dict]] = []
        self._gui = gui or {"status": "sent", "thieu": []}
        self._tt = trang_thai or {"bat": True, "thieu": []}

    def __call__(self, che_do, payload, mea, python=None):
        self.goi.append((che_do, payload))
        return dict(self._gui if che_do == "gui" else self._tt)


def _chay(monkeypatch, tmp_path, lich, quyen, kenh, argv=(), mea="co", bay_gio=1_000_000.0):
    monkeypatch.setattr(cle, "TEP_STATE", tmp_path / "state" / "canh.json")
    monkeypatch.setattr(cle, "do_lich", lambda: lich)
    monkeypatch.setattr(cle, "do_quyen", lambda: quyen)
    monkeypatch.setattr(cle, "repo_y_khoa", lambda: (tmp_path / "mea") if mea else None)
    monkeypatch.setattr(cle, "chay_con", kenh)
    monkeypatch.setattr(cle.time, "time", lambda: bay_gio)
    return cle.main(list(argv))


DO = _lich(do=["🔴 «cap-nhat-thang-ebm» kỳ 01/11/2026 18:30: KHÔNG có dấu vết nào"])


def test_do_gui_mot_email_ghi_so_roi_chong_lap_24_gio(monkeypatch, tmp_path, capsys):
    kenh = _KenhGia()
    assert _chay(monkeypatch, tmp_path, DO, _lich(), kenh) == 1
    assert [c for c, _ in kenh.goi] == ["gui"], "đúng MỘT lần gửi"
    assert kenh.goi[0][1]["subject"].startswith("[EBM] Lịch nền hỏng — 1 lỗi đỏ")
    assert "đã gửi MỘT email" in capsys.readouterr().out
    assert cle.doc_state()["lan_chay_cuoi"]["ket_qua"] == "da_gui"
    # 23 giờ sau, cùng nội dung ⇒ KHÔNG gửi lại
    assert _chay(monkeypatch, tmp_path, DO, _lich(), kenh, bay_gio=1_000_000.0 + 23 * 3600) == 1
    assert len(kenh.goi) == 1 and "chống lặp 24 giờ" in capsys.readouterr().out
    # 25 giờ sau ⇒ gửi lại (lỗi còn nguyên thì nhắc mỗi ngày một lần)
    assert _chay(monkeypatch, tmp_path, DO, _lich(), kenh, bay_gio=1_000_000.0 + 25 * 3600) == 1
    assert len(kenh.goi) == 2


def test_noi_dung_moi_trong_24_gio_van_gui(monkeypatch, tmp_path):
    kenh = _KenhGia()
    _chay(monkeypatch, tmp_path, DO, _lich(), kenh)
    them = _lich(do=DO["do"] + ["🔴 «kiem-rut-bai-kho-thang» kỳ 04/11/2026 18:30: KHÔNG có dấu vết nào"])
    assert _chay(monkeypatch, tmp_path, them, _lich(), kenh, bay_gio=1_000_000.0 + 3600) == 1
    assert len(kenh.goi) == 2


@pytest.mark.parametrize("ket_qua,chuoi", [
    ({"status": "skipped", "reason": "email_not_configured", "thieu": ["ENABLE_EMAIL_ALERTS"]}, "⚪ kênh email chưa bật"),
    ({"status": "skipped", "reason": "missing_app_password", "thieu": ["SMTP_PASSWORD"]}, "thiếu khoá: SMTP_PASSWORD"),
    ({"status": "error", "loai_loi": "ket_noi"}, "KHÔNG thành công"),
    ({"status": "khong_nap_duoc", "loai_loi": "ModuleNotFoundError", "module": "sqlalchemy"}, "không nạp được"),
    ({"status": "la"}, "coi như CHƯA gửi"),
])
def test_kenh_khong_gui_duoc_la_ma_2_khong_gia_da_gui_khong_ghi_so(monkeypatch, tmp_path, capsys, ket_qua, chuoi):
    kenh = _KenhGia(gui=ket_qua)
    assert _chay(monkeypatch, tmp_path, DO, _lich(), kenh) == 2
    out = capsys.readouterr().out
    assert chuoi in out and "✉" not in out and "đã gửi MỘT email" not in out
    assert "da_gui" not in cle.doc_state(), "không gửi được thì KHÔNG ghi sổ chống lặp"
    assert _chay(monkeypatch, tmp_path, DO, _lich(), kenh, bay_gio=1_000_000.0 + 60) == 2
    assert len(kenh.goi) == 2, "lượt sau phải thử gửi lại"


def test_khong_thay_repo_y_khoa_la_ma_2_khong_gui(monkeypatch, tmp_path, capsys):
    kenh = _KenhGia()
    assert _chay(monkeypatch, tmp_path, DO, _lich(), kenh, mea=None) == 2
    assert kenh.goi == [] and "KHÔNG được gửi" in capsys.readouterr().out


def test_xanh_va_kenh_san_sang_la_0_im_lang(monkeypatch, tmp_path, capsys):
    kenh = _KenhGia()
    assert _chay(monkeypatch, tmp_path, _lich(), _lich(), kenh, argv=["--im-khi-on"]) == 0
    assert capsys.readouterr().out == "" and [c for c, _ in kenh.goi] == ["trang-thai"]


def test_xanh_nhung_kenh_chua_bat_la_ma_2_noi_ro(monkeypatch, tmp_path, capsys):
    kenh = _KenhGia(trang_thai={"bat": False, "thieu": ["SMTP_PASSWORD"]})
    assert _chay(monkeypatch, tmp_path, _lich(), _lich(), kenh, argv=["--im-khi-on"]) == 2
    out = capsys.readouterr().out
    assert "⚪ kênh email chưa bật (thiếu khoá: SMTP_PASSWORD)" in out
    assert [c for c, _ in kenh.goi] == ["trang-thai"], "lịch xanh không bao giờ gửi email"


def test_xanh_khong_thay_repo_y_khoa_la_ma_2_khong_goi_kenh(monkeypatch, tmp_path, capsys):
    """Duyệt PR #338 (đột biến A): không thấy repo y khoa ⇒ không đo được kênh ⇒ KHÔNG được ra 0 «kênh sẵn sàng»."""
    kenh = _KenhGia()
    assert _chay(monkeypatch, tmp_path, _lich(), _lich(), kenh, mea=None) == 2
    out = capsys.readouterr().out
    assert "không thấy repo y khoa" in out and "kênh email sẵn sàng" not in out
    assert kenh.goi == [], "không có repo thì không có kênh để gọi"
    assert cle.doc_state()["lan_chay_cuoi"]["ket_qua"] == "khong_thay_repo"


@pytest.mark.parametrize("trang_thai,chuoi", [
    ({"status": "error", "loai_loi": "ket_noi"}, "không đo được trạng thái kênh email (loại: ket_noi"),
    ({"status": "error", "loai_loi": "het_gio_tien_trinh_con"}, "loại: het_gio_tien_trinh_con"),
    ({"status": "khong_nap_duoc", "loai_loi": "ModuleNotFoundError", "module": "sqlalchemy"},
     "không nạp được kênh notify của repo y khoa (ModuleNotFoundError: sqlalchemy)"),
    ({"status": "skipped", "reason": "pytest_khong_goi_kenh_that"}, "loại: skipped"),
])
def test_xanh_kenh_khong_do_duoc_la_ma_2_khong_bao_san_sang(monkeypatch, tmp_path, capsys, trang_thai, chuoi):
    """Duyệt PR #338 (đột biến D): phép đo kênh lỗi/không nạp được ⇒ ⚪ mã 2 — chỉ `bat is True` mới là sẵn sàng. Chưa thử
    gửi gì nên cũng không được nói «gửi email KHÔNG thành công»."""
    kenh = _KenhGia(trang_thai=trang_thai)
    assert _chay(monkeypatch, tmp_path, _lich(), _lich(), kenh, argv=["--im-khi-on"]) == 2
    out = capsys.readouterr().out
    assert chuoi in out and "kênh email sẵn sàng" not in out and "gửi email KHÔNG thành công" not in out
    assert [c for c, _ in kenh.goi] == ["trang-thai"], "lịch xanh không bao giờ gửi email"
    assert cle.doc_state()["lan_chay_cuoi"]["ket_qua"] == "kenh_khong_do_duoc"


def test_khong_do_duoc_trong_la_ma_2_khong_goi_kenh(monkeypatch, tmp_path, capsys):
    kenh = _KenhGia()
    assert _chay(monkeypatch, tmp_path, _lich(do_duoc=False, phu=["thiếu log"]), _lich(), kenh) == 2
    assert kenh.goi == [] and "KHÔNG đo được trọn" in capsys.readouterr().out


def test_xem_truoc_khong_gui_khong_ghi_so(monkeypatch, tmp_path, capsys):
    kenh = _KenhGia()
    assert _chay(monkeypatch, tmp_path, DO, _lich(), kenh, argv=["--xem-truoc"]) == 1
    assert kenh.goi == [] and not cle.TEP_STATE.exists()
    assert "XEM TRƯỚC" in capsys.readouterr().out


# ---- tiến trình con THẬT với gói `app` GIẢ (không SMTP, không secrets) ---------------------------------------------------
def _dung_app_gia(goc: Path, mat_khau: str = MK_GIA, ket_qua: str = "{'status': 'sent', 'to': DIA_CHI}",
                  bat: bool = True) -> Path:
    mea = goc / "mea-gia"
    (mea / "app" / "services").mkdir(parents=True)
    (mea / "app" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (mea / "app" / "services" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (mea / "app" / "config.py").write_text(textwrap.dedent(f"""
        class _S:
            enable_email_alerts = {bat!r}
            smtp_host = {MAY_CHU_GIA!r}
            smtp_from = {DIA_CHI_GIA!r}
            smtp_password = {mat_khau!r}
            alert_email_to = {DIA_CHI_GIA!r}
        settings = _S()
        """), encoding="utf-8", newline="\n")
    (mea / "app" / "services" / "notify.py").write_text(textwrap.dedent(f"""
        import json, logging, os, sys
        from pathlib import Path
        DIA_CHI = {DIA_CHI_GIA!r}
        logging.basicConfig(filename=str(Path(__file__).with_name("app.log")), level=logging.INFO)
        logger = logging.getLogger("app.services.notify")
        def send_email(subject, body_md, body_html=None, attachments=None):
            logger.info("Đã gửi email cảnh báo tới %s", DIA_CHI)
            print("dòng lạc ra stdout của engine", DIA_CHI)
            print("log lạc ra stderr", DIA_CHI, file=sys.stderr)
            with open(Path(__file__).with_name("da_goi.json"), "a", encoding="utf-8") as f:
                f.write(json.dumps({{"subject": subject, "body": body_md}}, ensure_ascii=False) + "\\n")
            return {ket_qua}
        """), encoding="utf-8", newline="\n")
    return mea


def test_tien_trinh_con_goi_notify_that_va_chi_tra_khoa_danh_sach_trang(tmp_path):
    mea = _dung_app_gia(tmp_path)
    kq = cle.chay_con("gui", {"subject": "[EBM] thử", "body": "thân"}, mea, python=sys.executable)
    assert kq == {"status": "sent", "thieu": []}, kq
    goi = [json.loads(x) for x in (mea / "app" / "services" / "da_goi.json").read_text(encoding="utf-8").splitlines()]
    assert goi == [{"subject": "[EBM] thử", "body": "thân"}], "notify.send_email phải được gọi đúng MỘT lần"
    log = mea / "app" / "services" / "app.log"
    assert not log.exists() or DIA_CHI_GIA not in log.read_text(encoding="utf-8"), "log engine phải bị tắt"


def test_tien_trinh_con_bao_kenh_chua_bat_bang_ten_khoa(tmp_path):
    mea = _dung_app_gia(tmp_path, mat_khau="", ket_qua="{'status': 'skipped', 'reason': 'missing_app_password'}")
    kq = cle.chay_con("gui", {"subject": "s", "body": "b"}, mea, python=sys.executable)
    assert kq == {"status": "skipped", "reason": "missing_app_password", "thieu": ["SMTP_PASSWORD"]}
    assert cle.chay_con("trang-thai", {}, mea, python=sys.executable) == {"bat": False, "thieu": ["SMTP_PASSWORD"]}


def test_tien_trinh_con_trang_thai_cong_tac_tat_la_chua_bat(tmp_path):
    """Duyệt PR #338 (đột biến E): `trang-thai` phải dùng ĐÚNG điều kiện của notify.send_email — đủ SMTP mà
    ENABLE_EMAIL_ALERTS tắt thì notify trả 'skipped' ⇒ kênh CHƯA bật, tên khoá công tắc phải hiện trong `thieu`."""
    mea = _dung_app_gia(tmp_path, bat=False)
    assert cle.chay_con("trang-thai", {}, mea, python=sys.executable) == {"bat": False, "thieu": ["ENABLE_EMAIL_ALERTS"]}


def test_khoa_cau_hinh_khop_dieu_kien_cua_notify_send_email():
    """Danh sách khoá phải trùng đúng năm thuộc tính mà notify.send_email đòi trước khi gửi (đối chiếu 14/11/2026 với
    nhánh nền y khoa: enable_email_alerts · smtp_host · alert_email_to · smtp_from · smtp_password)."""
    assert {k.lower() for k in cle.KHOA_CAU_HINH} == {
        "enable_email_alerts", "smtp_host", "alert_email_to", "smtp_from", "smtp_password"}


def test_tien_trinh_con_loi_smtp_chi_tra_nhan_khong_tra_chuoi_loi(tmp_path):
    loi = "{'status': 'error', 'error': \"(535, b'Username and Password not accepted for \" + DIA_CHI + \"')\"}"
    mea = _dung_app_gia(tmp_path, ket_qua=loi)
    kq = cle.chay_con("gui", {"subject": "s", "body": "b"}, mea, python=sys.executable)
    assert kq == {"status": "error", "thieu": [], "loai_loi": "xac_thuc"}


def test_chay_con_danh_sach_trang_cha_loc_khoa_la_du_tien_trinh_con_tra_gi(monkeypatch, tmp_path):
    """Lớp lọc THỨ HAI ở tiến trình cha: tiến trình con (hoặc engine đổi API) có trả thêm khoá — địa chỉ, chuỗi lỗi, lý do
    lạ, tên khoá lạ — thì cha vẫn chỉ giữ khoá trong danh sách trắng."""
    dong = cle.DAU_KET_QUA + json.dumps({"status": "sent", "to": DIA_CHI_GIA, "error": MK_GIA, "reason": MAY_CHU_GIA,
                                         "thieu": ["SMTP_PASSWORD", DIA_CHI_GIA]})

    class _R:
        returncode, stdout, stderr = 0, "dòng lạc " + DIA_CHI_GIA + "\n" + dong + "\n", MK_GIA
    monkeypatch.setattr(cle.subprocess, "run", lambda *a, **k: _R())
    kq = cle.chay_con("gui", {}, tmp_path, python=sys.executable)
    assert kq == {"status": "sent", "thieu": ["SMTP_PASSWORD"]}, kq

    class _RKhong:
        returncode, stdout, stderr = 1, "Traceback … " + DIA_CHI_GIA, ""
    monkeypatch.setattr(cle.subprocess, "run", lambda *a, **k: _RKhong())
    kq = cle.chay_con("gui", {}, tmp_path, python=sys.executable)
    assert kq["status"] == "error" and DIA_CHI_GIA not in json.dumps(kq, ensure_ascii=False)


def test_tien_trinh_con_khong_co_app_la_khong_nap_duoc(tmp_path):
    (tmp_path / "rong").mkdir()
    kq = cle.chay_con("gui", {"subject": "s", "body": "b"}, tmp_path / "rong", python=sys.executable)
    assert kq["status"] == "khong_nap_duoc" and kq["loai_loi"] == "ModuleNotFoundError"


def test_dau_cuoi_khong_gia_tri_cau_hinh_nao_lot_ra_stdout_hay_so(monkeypatch, tmp_path, capsys):
    mea = _dung_app_gia(tmp_path)
    monkeypatch.setattr(cle, "TEP_STATE", tmp_path / "state" / "canh.json")
    monkeypatch.setattr(cle, "do_lich", lambda: DO)
    monkeypatch.setattr(cle, "do_quyen", lambda: _lich())
    monkeypatch.setattr(cle, "repo_y_khoa", lambda: mea)
    monkeypatch.setattr(cle, "python_engine", lambda: sys.executable)
    assert cle.main([]) == 1
    cap = capsys.readouterr()
    so = cle.TEP_STATE.read_text(encoding="utf-8")
    for bi_mat in BI_MAT:
        assert bi_mat not in cap.out and bi_mat not in cap.err and bi_mat not in so, bi_mat


def test_ran_pytest_khong_cham_kenh_that():
    """Phòng thủ chiều sâu: dưới pytest, chay_con từ chối repo y khoa THẬT (không spawn, không đọc cấu hình)."""
    for mea in (REPO / "medical-ebm-automation", REPO.parent / "medical-ebm-automation"):
        assert cle.chay_con("gui", {"subject": "s", "body": "b"}, mea)["reason"] == "pytest_khong_goi_kenh_that"


# ---- bộ canh tự hỏng không được im lặng (duyệt PR #338): --thong-bao + --suc-khoe ----------------------------------------
def _bat_thong_bao(monkeypatch):
    goi: list[str] = []
    monkeypatch.setattr(cle, "thong_bao_he_thong", lambda nd: goi.append(nd) or True)
    return goi


@pytest.mark.parametrize("lich,kenh,mea,nhan", [
    (_lich(), _KenhGia(trang_thai={"bat": False, "thieu": ["SMTP_PASSWORD"]}), "co", "kênh email chưa bật"),
    (_lich(), _KenhGia(trang_thai={"status": "error", "loai_loi": "ket_noi"}), "co", "không đo được kênh email"),
    (_lich(), _KenhGia(), None, "không thấy repo y khoa"),
    (DO, _KenhGia(gui={"status": "error", "loai_loi": "xac_thuc"}), "co", "email KHÔNG gửi được (error)"),
    (DO, _KenhGia(), None, "không thấy repo y khoa"),
    (_lich(do_duoc=False, phu=["thiếu log"]), _KenhGia(), "co", "không đo được trọn"),
])
def test_thong_bao_he_thong_khi_canh_bao_khong_toi_email(monkeypatch, tmp_path, lich, kenh, mea, nhan):
    goi = _bat_thong_bao(monkeypatch)
    assert _chay(monkeypatch, tmp_path, lich, _lich(), kenh, argv=["--im-khi-on", "--thong-bao"], mea=mea) == 2
    assert len(goi) == 1 and nhan in goi[0], goi
    for bi_mat in BI_MAT:
        assert bi_mat not in goi[0]
    assert cle.doc_state()["thong_bao_luc"] == 1_000_000
    # 1 giờ sau ⇒ không báo lại; 21 giờ sau (lượt hằng ngày) ⇒ báo lại
    _chay(monkeypatch, tmp_path, lich, _lich(), kenh, argv=["--im-khi-on", "--thong-bao"], mea=mea,
          bay_gio=1_000_000.0 + 3600)
    assert len(goi) == 1
    _chay(monkeypatch, tmp_path, lich, _lich(), kenh, argv=["--im-khi-on", "--thong-bao"], mea=mea,
          bay_gio=1_000_000.0 + 21 * 3600)
    assert len(goi) == 2


def test_thong_bao_khong_bat_khi_canh_bao_da_toi_email_hoac_khong_xin(monkeypatch, tmp_path):
    goi = _bat_thong_bao(monkeypatch)
    assert _chay(monkeypatch, tmp_path, _lich(), _lich(), _KenhGia(), argv=["--thong-bao"]) == 0
    assert _chay(monkeypatch, tmp_path, DO, _lich(), _KenhGia(), argv=["--thong-bao"]) == 1
    assert _chay(monkeypatch, tmp_path, DO, _lich(), _KenhGia(gui={"status": "error"}), bay_gio=2_000_000.0) == 2
    assert goi == [], "mã 0/1 không báo; thiếu --thong-bao thì không báo"
    assert "thong_bao_luc" not in cle.doc_state()


def test_thong_bao_that_bai_khong_ghi_moc_lan_sau_thu_lai(monkeypatch, tmp_path):
    monkeypatch.setattr(cle, "thong_bao_he_thong", lambda nd: False)
    kenh = _KenhGia(trang_thai={"bat": False, "thieu": []})
    assert _chay(monkeypatch, tmp_path, _lich(), _lich(), kenh, argv=["--thong-bao"]) == 2
    assert "thong_bao_luc" not in cle.doc_state()


def test_thong_bao_he_thong_ngoai_macos_khong_gia_da_bao(monkeypatch):
    monkeypatch.setattr(cle.sys, "platform", "linux")
    monkeypatch.setattr(cle.subprocess, "run", lambda *a, **k: pytest.fail("không được gọi osascript"))
    assert cle.thong_bao_he_thong("x") is False


def _so(ket_qua, luc=1_000_000):
    return {"lan_chay_cuoi": {"luc": luc, "ket_qua": ket_qua, "so_loi_do": 0}}


@pytest.mark.parametrize("ket_qua", ["kenh_chua_bat", "kenh_khong_do_duoc", "khong_thay_repo", "khong_do_duoc",
                                     "khong_gui_error", "khong_gui_skipped", "nhan_la"])
@pytest.mark.parametrize("da_cai", [True, None])
def test_suc_khoe_luot_cuoi_khong_toi_kenh_la_vang(ket_qua, da_cai):
    ma, dong = cle.suc_khoe(_so(ket_qua), 1_000_000.0 + 3600, da_cai)
    assert ma == 1 and dong.startswith("🟡") and "KHÔNG đưa được cảnh báo tới email" in dong


@pytest.mark.parametrize("ket_qua", sorted(cle.KET_QUA_TOI_KENH))
def test_suc_khoe_luot_cuoi_toi_kenh_va_moi_la_xanh(ket_qua):
    ma, dong = cle.suc_khoe(_so(ket_qua), 1_000_000.0 + 47 * 3600, True)
    assert ma == 0 and dong.startswith("🟢")


def test_suc_khoe_da_cai_ma_cu_hon_48_gio_la_vang_chua_biet_cai_thi_bo_phep_cu():
    ma, dong = cle.suc_khoe(_so("xanh"), 1_000_000.0 + 49 * 3600, True)
    assert ma == 1 and "49 giờ không có lượt mới" in dong
    assert cle.suc_khoe(_so("xanh"), 1_000_000.0 + 49 * 3600, None)[0] == 0, "Windows: lượt chạy tay cũ không báo giả"


def test_suc_khoe_chua_cai_va_so_trong_hong():
    assert cle.suc_khoe(_so("kenh_chua_bat"), 1_000_000.0, False)[0] == 3, "chưa cài = bác sĩ chưa chọn, không nhắc"
    ma, dong = cle.suc_khoe({}, 1_000_000.0, True)
    assert ma == 1 and "chưa có lượt chạy nào" in dong
    assert cle.suc_khoe({}, 1_000_000.0, None)[0] == 3
    assert cle.suc_khoe({"lan_chay_cuoi": {"ket_qua": "xanh"}}, 1_000_000.0, True)[0] == 1
    assert cle.suc_khoe({"lan_chay_cuoi": "hỏng"}, 1_000_000.0, True)[0] == 1


def test_suc_khoe_doc_dung_so_do_luong_chinh_ghi(monkeypatch, tmp_path, capsys):
    """Đầu–cuối: lượt chính ghi nhãn ⇒ `--suc-khoe` đọc lại đúng sổ; chỉ đọc, không đo lại, không ghi sổ."""
    kenh = _KenhGia(trang_thai={"bat": False, "thieu": ["SMTP_PASSWORD"]})
    _chay(monkeypatch, tmp_path, _lich(), _lich(), kenh, argv=["--im-khi-on"])
    capsys.readouterr()
    truoc = cle.TEP_STATE.read_bytes()
    monkeypatch.setattr(cle, "da_cai_launchd", lambda: True)
    monkeypatch.setattr(cle, "do_lich", lambda: pytest.fail("--suc-khoe không được đo lại"))
    assert cle.main(["--suc-khoe", "--im-khi-on"]) == 1
    assert "kênh email chưa bật" in capsys.readouterr().out
    assert cle.TEP_STATE.read_bytes() == truoc and len(kenh.goi) == 1


def test_suc_khoe_im_khi_on_im_lang_khi_xanh_va_chua_cai(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cle, "TEP_STATE", tmp_path / "s.json")
    monkeypatch.setattr(cle.time, "time", lambda: 1_000_000.0 + 60)
    cle.ghi_state(_so("xanh"))
    for da_cai, ma in ((True, 0), (False, 3)):
        monkeypatch.setattr(cle, "da_cai_launchd", lambda d=da_cai: d)
        assert cle.main(["--suc-khoe", "--im-khi-on"]) == ma
        assert capsys.readouterr().out == ""
        assert cle.main(["--suc-khoe"]) == ma and capsys.readouterr().out.strip()


# ---- launchd ----------------------------------------------------------------------------------------------------------
def test_plist_moi_ngay_mot_lan_khong_chay_luc_nap():
    tep = Path("/x/tools/canh_lich_nen_email.py")
    d = plistlib.loads(cle.tao_plist("/usr/bin/python3", tep))
    assert d["Label"] == cle.NHAN_LAUNCHD and d["StartCalendarInterval"] == {"Hour": 9, "Minute": 0}
    assert d["RunAtLoad"] is False
    # Đầu ra vào /dev/null ⇒ --thong-bao là đường lùi duy nhất để bộ canh hỏng tự lộ ra (duyệt PR #338).
    assert d["ProgramArguments"] == ["/usr/bin/python3", str(tep), "--im-khi-on", "--thong-bao"]
    assert not any(k in d for k in ("KeepAlive", "WatchPaths", "StartInterval"))


def test_cai_launchd_mac_dinh_chay_kho_khong_ghi_khong_goi_launchctl(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cle.sys, "platform", "darwin")
    monkeypatch.setattr(cle.os, "getuid", lambda: 501, raising=False)
    monkeypatch.setattr(cle.Path, "home", classmethod(lambda c: tmp_path))
    chay = []
    monkeypatch.setattr(cle.subprocess, "run", lambda *a, **k: chay.append(a))
    assert cle.main(["--cai-launchd"]) == 0 and cle.main(["--go-launchd"]) == 0
    assert chay == [] and not (tmp_path / "Library").exists(), "chạy khô không được ghi/gọi launchctl"
    out = capsys.readouterr().out
    assert "CHẠY KHÔ" in out and "StartCalendarInterval" in out


def test_cai_launchd_ap_dung_ghi_plist_va_nap(monkeypatch, tmp_path):
    monkeypatch.setattr(cle.sys, "platform", "darwin")
    monkeypatch.setattr(cle.os, "getuid", lambda: 501, raising=False)
    monkeypatch.setattr(cle.Path, "home", classmethod(lambda c: tmp_path))
    chay = []

    class _R:
        returncode, stderr = 0, ""
    monkeypatch.setattr(cle.subprocess, "run", lambda lenh, **k: chay.append(lenh) or _R())
    assert cle.cai_launchd(True, False) == 0
    plist = tmp_path / "Library" / "LaunchAgents" / f"{cle.NHAN_LAUNCHD}.plist"
    assert plistlib.loads(plist.read_bytes())["Label"] == cle.NHAN_LAUNCHD
    assert ["launchctl", "bootstrap", "gui/501", str(plist)] in chay


def test_cai_launchd_windows_chi_in_huong_dan_task_scheduler(monkeypatch, capsys):
    monkeypatch.setattr(cle.sys, "platform", "win32")
    chay = []
    monkeypatch.setattr(cle.subprocess, "run", lambda *a, **k: chay.append(a))
    assert cle.cai_launchd(True, False) == 3 and chay == []
    out = capsys.readouterr().out
    assert "Task Scheduler" in out and "schtasks /Create /SC DAILY" in out


def test_cai_launchd_thieu_getuid_thi_tu_choi(monkeypatch, capsys):
    monkeypatch.setattr(cle.sys, "platform", "darwin")
    monkeypatch.delattr(cle.os, "getuid", raising=False)
    assert cle.cai_launchd(True, False) == 3 and "uid" in capsys.readouterr().out
