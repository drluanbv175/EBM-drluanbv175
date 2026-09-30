# -*- coding: utf-8 -*-
"""`kiem_nguon_that.kiem_mang()` đo HAI tầng: DNS rồi bắt tay TCP cổng 443 — 30/09/2026 (BH135).

Ca thật trên máy Windows 30/09: bản cũ chỉ gọi `gethostbyname` nên «phân giải được» bị coi là «tới được». Đo bằng tay:
  • api.crossref.org có lúc phân giải được mà cổng 443 KHÔNG thông 10/10 lần trong 2,5 phút ⇒ chốt ① của chu trình chứng
    cứ báo 🟢 «4/4 nguồn phân giải được» trong khi Crossref không tới được (xanh giả);
  • DNS nội bộ trả lời sau 7–12 s hoặc hết hạn, DNS công cộng trả lời trong ~45 ms ⇒ «không phân giải được» lúc đó là lỗi
    của máy chủ DNS đang dùng, không phải nguồn sập.
Test khoá: phân giải được mà không nối được ⇒ 🟡 với lý do «đường truyền, không phải DNS»; một nhịp rớt không báo động;
DNS của máy hỏng thì đối chiếu DNS công cộng và nói đúng chỗ hỏng; không hỏi được DNS công cộng ⇒ không kết luận thêm;
mạng không bao giờ là 🔴; đi qua proxy (phiên Cloud) thì KHÔNG thử nối trực tiếp; gói DNS dựng/đọc đúng RFC 1035.
Ngoại tuyến hoàn toàn: `_phan_giai`, `_noi_duoc`, `_hoi_dns_cong_cong` đều giả.
"""
from __future__ import annotations

import importlib.util
import struct
from pathlib import Path

import pytest

_DUONG = Path(__file__).resolve().parent / "kiem_nguon_that.py"
_sp = importlib.util.spec_from_file_location("_knt_mang_hai_tang", _DUONG)
K = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(K)

CROSSREF = "api.crossref.org"
IP_CR = "18.234.0.150"


@pytest.fixture(autouse=True)
def _khong_proxy(monkeypatch):
    for k in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.delenv(k, raising=False)


def _gia(monkeypatch, dns: dict | None = None, noi: dict | None = None, cong_cong: dict | None = None):
    """`dns[host]` = danh sách (ip|None, giây) theo lượt gọi (hết thì lặp phần tử cuối); `noi[ip]` = danh sách bool theo
    lượt; `cong_cong[host]` = ip|None. Nguồn không khai ⇒ DNS nhanh + nối được."""
    dem_dns: dict[str, int] = {}
    goi_noi: list[str] = []
    goi_cc: list[tuple[str, str]] = []

    def phan_giai(host):
        i = dem_dns.get(host, 0)
        dem_dns[host] = i + 1
        ds = (dns or {}).get(host, [("9.9.9.9", 0.01)])
        return ds[min(i, len(ds) - 1)]

    def noi_duoc(ip, cong=443, han=5.0):
        goi_noi.append(ip)
        ds = (noi or {}).get(ip, [True])
        return ds[min(goi_noi.count(ip) - 1, len(ds) - 1)]

    def hoi_cc(host, may_chu, han=3.0):
        goi_cc.append((host, may_chu))
        return (cong_cong or {}).get(host)

    monkeypatch.setattr(K, "_phan_giai", phan_giai)
    monkeypatch.setattr(K, "_noi_duoc", noi_duoc)
    monkeypatch.setattr(K, "_hoi_dns_cong_cong", hoi_cc)
    return goi_noi, goi_cc


def test_moi_nguon_phan_giai_va_noi_duoc_la_xanh(monkeypatch):
    goi_noi, goi_cc = _gia(monkeypatch)
    assert K.kiem_mang() == ("xanh", [])
    assert len(goi_noi) == len(K.HOST_NGUON) and goi_cc == []      # có thử nối THẬT từng nguồn, không hỏi DNS ngoài


def test_phan_giai_duoc_ma_khong_noi_duoc_khong_con_la_xanh(monkeypatch):
    """Đúng ca Crossref 30/09: có địa chỉ mà cổng 443 không thông — trước đây là 🟢 «phân giải được»."""
    goi_noi, _ = _gia(monkeypatch, dns={CROSSREF: [(IP_CR, 0.2)]}, noi={IP_CR: [False, False]})
    muc, tin = K.kiem_mang()
    assert muc == "vang" and len(tin) == 1
    assert "Crossref" in tin[0] and "KHÔNG nối được cổng 443" in tin[0] and "KHÔNG phải DNS" in tin[0]
    assert goi_noi.count(IP_CR) == 2                               # thử lại đúng một lần rồi mới kết luận


def test_mot_nhip_rot_khi_noi_khong_bao_dong(monkeypatch):
    _gia(monkeypatch, dns={CROSSREF: [(IP_CR, 0.2)]}, noi={IP_CR: [False, True]})
    assert K.kiem_mang() == ("xanh", [])


def test_dns_cua_may_hong_ma_dns_cong_cong_duoc_thi_noi_dung_cho_hong(monkeypatch):
    _gia(monkeypatch, dns={CROSSREF: [(None, 12.0)]}, cong_cong={CROSSREF: IP_CR})
    muc, tin = K.kiem_mang()
    assert muc == "vang" and len(tin) == 1
    assert "DNS của mạng này KHÔNG phân giải được" in tin[0] and "DNS công cộng phân giải được" in tin[0]
    assert "không phải nguồn sập" in tin[0]
    assert "đường truyền/tường lửa" not in tin[0]                  # nối thẳng IP thông ⇒ chỉ DNS hỏng


def test_dns_cua_may_hong_va_duong_truyen_cung_vuong(monkeypatch):
    _gia(monkeypatch, dns={CROSSREF: [(None, 12.0)]}, cong_cong={CROSSREF: IP_CR}, noi={IP_CR: [False]})
    _muc, tin = K.kiem_mang()
    assert "DNS công cộng phân giải được" in tin[0] and f"nối thẳng {IP_CR}:443 cũng KHÔNG thông" in tin[0]


def test_dns_cong_cong_cung_khong_hoi_duoc_thi_khong_ket_luan_them(monkeypatch):
    _goi_noi, goi_cc = _gia(monkeypatch, dns={CROSSREF: [(None, 12.0)]}, cong_cong={})
    muc, tin = K.kiem_mang()
    assert muc == "vang"
    assert "KHÔNG phân giải được" in tin[0] and "mất mạng hoặc mạng chặn DNS ra ngoài" in tin[0]
    assert "máy chủ DNS đang dùng" not in tin[0]                   # không đổ lỗi cho DNS nội bộ khi chưa có bằng chứng
    assert [m for _h, m in goi_cc] == list(K.DNS_CONG_CONG)        # đã hỏi đủ các DNS công cộng trước khi bỏ cuộc


def test_dns_chap_chon_va_dns_cham_deu_lo_ra(monkeypatch):
    _gia(monkeypatch, dns={CROSSREF: [(None, 12.0), (IP_CR, 9.0), (IP_CR, 0.01)],
                           "eutils.ncbi.nlm.nih.gov": [("34.107.134.59", 8.0)]})
    muc, tin = K.kiem_mang()
    assert muc == "vang" and len(tin) == 2
    assert any("DNS chỉ 2/3 lần" in t and CROSSREF in t for t in tin)
    assert any("DNS chậm 8 s" in t and "eutils.ncbi.nlm.nih.gov" in t for t in tin)


def test_mang_hong_toan_phan_van_chi_la_vang(monkeypatch):
    """Mạng hỏng làm KHÔNG LẤY ĐƯỢC dữ liệu chứ không làm dữ liệu SAI ⇒ tối đa 🟡 (🔴 dành cho dữ liệu giả)."""
    ten = [h for h, _ in K.HOST_NGUON]
    _gia(monkeypatch, dns={h: [(None, 12.0)] for h in ten}, cong_cong={})
    muc, tin = K.kiem_mang()
    assert muc == "vang" and len(tin) == len(ten)


def test_di_qua_proxy_thi_khong_thu_noi_truc_tiep(monkeypatch):
    """Phiên Cloud: tiến trình không tự nối thẳng được (mọi thứ qua proxy) ⇒ thử bắt tay trực tiếp chỉ sinh báo động giả."""
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:1")
    goi_noi, goi_cc = _gia(monkeypatch, noi={"9.9.9.9": [False]})
    assert K.kiem_mang() == ("xanh", [])
    assert goi_noi == [] and goi_cc == []


def test_di_qua_proxy_ma_dns_hong_van_bao_nhu_cu(monkeypatch):
    monkeypatch.setenv("https_proxy", "http://127.0.0.1:1")
    _goi_noi, goi_cc = _gia(monkeypatch, dns={CROSSREF: [(None, 12.0)]}, cong_cong={CROSSREF: IP_CR})
    muc, tin = K.kiem_mang()
    assert muc == "vang" and "KHÔNG phân giải được" in tin[0] and goi_cc == []


# ---------- gói DNS (RFC 1035) ----------

def _tra_loi(ma: int, co: int, ban_ghi: list[tuple[int, bytes]]) -> bytes:
    hoi = b"\x03api\x08crossref\x03org\x00" + struct.pack(">HH", 1, 1)
    goi = struct.pack(">HHHHHH", ma, co, 1, len(ban_ghi), 0, 0) + hoi
    for loai, du_lieu in ban_ghi:
        goi += b"\xc0\x0c" + struct.pack(">HHIH", loai, 1, 60, len(du_lieu)) + du_lieu      # tên = con trỏ nén về câu hỏi
    return goi


def test_goi_hoi_dns_dung_dinh_dang():
    goi = K._goi_hoi_dns("api.crossref.org", 0x1234)
    assert goi[:12] == struct.pack(">HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
    assert goi[12:] == b"\x03api\x08crossref\x03org\x00" + struct.pack(">HH", 1, 1)


def test_doc_tra_loi_dns_bo_qua_cname_lay_ban_ghi_a():
    goi = _tra_loi(0x1234, 0x8180, [(5, b"\x03cdn\xc0\x10"), (1, bytes([18, 234, 0, 150]))])
    assert K._doc_tra_loi_dns(goi, 0x1234) == IP_CR


@pytest.mark.parametrize("goi", [
    _tra_loi(0x9999, 0x8180, [(1, bytes([1, 2, 3, 4]))]),          # sai mã truy vấn ⇒ không phải trả lời của mình
    _tra_loi(0x1234, 0x8183, [(1, bytes([1, 2, 3, 4]))]),          # RCODE=3 (NXDOMAIN)
    _tra_loi(0x1234, 0x8180, []),                                  # không có bản ghi trả lời
    _tra_loi(0x1234, 0x8180, [(5, b"\x03cdn\xc0\x10")]),           # chỉ có CNAME, không có A
    _tra_loi(0x1234, 0x8180, [(1, bytes([1, 2, 3, 4]))])[:20],     # gói bị cắt
    b"",
])
def test_doc_tra_loi_dns_khong_doan(goi):
    assert K._doc_tra_loi_dns(goi, 0x1234) is None
