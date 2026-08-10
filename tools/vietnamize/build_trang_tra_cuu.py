#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_trang_tra_cuu.py — Sinh 2 thứ bác sĩ dùng để TÌM công cụ:

  1. TRA-CUU-CONG-CU.html  (gốc "Claude AI")  — trang tra bằng MẮT: gõ tiếng Việt
     có dấu hay không dấu đều ra, lọc theo loại/máy, bấm là copy lệnh. Mở bằng chuột,
     KHÔNG cần Claude đang chạy, tự đồng bộ OneDrive sang máy kia.

  2. INDEX-CONG-CU.md  (cùng thư mục này)     — bản GỌN cho lệnh `/cong-cu-gi` đọc.
     DANH-MUC-CONG-CU.md đầy đủ nặng ~530 KB (~150k token) — nạp trọn vào ngữ cảnh
     mỗi lần hỏi là phí và chậm. Index chỉ giữ tên + một dòng mô tả, đủ để chọn ra
     vài ứng viên; cần chi tiết thì mở danh mục đầy đủ.

KHỬ TRÙNG LẶP — lý do chính khiến danh sách công cụ khó dùng:
  Một kho plugin hay được đóng gói thành nhiều "cửa vào" theo chủ đề, mỗi cửa chứa
  Y HỆT một bộ skill (bộ medsci-skills: 9 plugin × 58 skill = 522 mục cho 58 skill
  thật — đã so md5, byte-identical). Trang này gom các mục trùng (cùng loại + cùng
  tên + cùng mô tả) thành MỘT dòng, và ghi mọi cách gọi của nó.

Chạy lại sau mỗi lần cập nhật plugin:
    python tools/vietnamize/extract_catalog.py      # quét máy này
    python tools/vietnamize/build_danh_muc.py       # danh mục đầy đủ
    python tools/vietnamize/build_trang_tra_cuu.py  # trang tra + index gọn
"""
from __future__ import annotations

# --- Ép stdout sang UTF-8 (vá 05/08/2026) ---------------------------------
# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt làm script chết giữa
# chừng bằng UnicodeEncodeError, trong khi phần việc chính đã chạy xong.
import sys as _sys

for _luong in (_sys.stdout, _sys.stderr):
    if _luong is not None and (getattr(_luong, "encoding", "") or "").lower().replace("-", "") != "utf8":
        try:
            _luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
# --------------------------------------------------------------------------

import html
import json
import pathlib
import re
from collections import defaultdict

from bo_dau import bo_dau        # cùng thư mục — dùng chung cách bỏ dấu tiếng Việt

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
SNAP_DIR = HERE / "catalog_may"
VIEC_HAY_LAM = HERE / "viec-hay-lam.json"
VI_DESC = HERE / "vi_descriptions.json"
OUT_HTML = REPO / "TRA-CUU-CONG-CU.html"
OUT_INDEX = HERE / "INDEX-CONG-CU.md"

TEN_LOAI = {"skill": "kỹ năng", "command": "lệnh", "agent": "agent"}
# Thứ tự ưu tiên khi một mục có nhiều cách gọi: agent EBM của bác sĩ trước, rồi
# lệnh tiếng Việt, rồi plugin. Cách gọi đầu tiên là cách trang này khuyên dùng.
UU_TIEN_NGUON = ("ebm-agents", "user-commands", "user-skills", "cowork")


def nap_lop_phu_vi() -> dict[str, str]:
    """Bản dịch tiếng Việt dạng LỚP PHỦ, khoá theo `id` trong catalog.

    VÌ SAO CÓ (sửa 2026-08-10): trước đây tiếng Việt chỉ hiện ra nhờ `apply_vi.py`
    GHI ĐÈ trường `description:` vào chính file SKILL.md của plugin. Với plugin cài
    kiểu thư mục từ một repo git (aipoch trỏ vào ~/Documents/GitHub/medical-research-skills),
    mỗi lần `git pull` hoặc mỗi lần Claude Code tự đồng bộ lại cache là bản dịch bị
    XOÁ SẠCH. Sự cố này ĐÃ XẢY RA và không ai phát hiện: bản chụp ngày 05/08 có
    605/605 mô tả aipoch tiếng Việt, tới 10/08 trên đĩa còn 0/605.

    Lớp phủ đọc lúc dựng trang nên KHÔNG đụng vào bất kỳ file plugin nào ⇒ cập nhật
    plugin không bao giờ làm mất tiếng Việt nữa, và Việt hoá không bao giờ gây xung
    đột `git pull` trong repo nguồn của plugin.
    """
    if not VI_DESC.exists():
        return {}
    ra: dict[str, str] = {}
    for khoa, v in json.loads(VI_DESC.read_text(encoding="utf-8")).items():
        if khoa.startswith("_"):          # _ghi_chu… là chú thích, không phải bản dịch
            continue
        s = v.get("vi") if isinstance(v, dict) else v
        if isinstance(s, str) and s.strip():
            ra[khoa] = s.strip()
    return ra


def nap_ban_chup() -> tuple[list[dict], dict[str, str]]:
    """Gộp bản chụp của mọi máy. Trả (danh sách mục, ngày quét theo máy).

    Mỗi mục được gắn thêm khoá 'may' = tập máy gọi được — nhãn này là thứ cho bác
    sĩ biết "mục này có gọi được trên máy đang ngồi không", tránh cảnh gõ một lệnh
    chỉ tồn tại ở máy kia.
    """
    lop_phu = nap_lop_phu_vi()
    gom: dict[str, dict] = {}
    ngay: dict[str, str] = {}
    for f in sorted(SNAP_DIR.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        may = d.get("may") or f.stem
        ngay[may] = d.get("ngay_quet", "?")
        for m in d.get("muc", []):
            khoa = m.get("id") or f"{m.get('kind')}:{m.get('plugin')}:{m.get('name')}"
            # Lớp phủ THẮNG mô tả đọc từ file: file có thể vừa bị bản cập nhật của
            # plugin trả về tiếng Anh, còn lớp phủ là bản dịch bác sĩ đã duyệt.
            vi = lop_phu.get(khoa)
            cu = gom.get(khoa)
            if cu is None:
                gom[khoa] = {**m, "may": {may}, **({"desc_en": vi} if vi else {})}
            else:
                cu["may"].add(may)
                if vi:
                    cu["desc_en"] = vi
    return list(gom.values()), ngay


def gom_trung(muc: list[dict]) -> list[dict]:
    """Gom các mục TRÙNG NỘI DUNG thành một dòng.

    Khoá gom = (loại, tên, 120 ký tự đầu của mô tả). Cố ý KHÔNG gom chỉ theo tên:
    hai plugin khác nhau có thể cùng đặt tên `peer-review` cho hai thứ khác nhau —
    gom nhầm sẽ giấu mất một công cụ thật.
    """
    nhom: dict[tuple, list[dict]] = defaultdict(list)
    for m in muc:
        mo_ta = (m.get("desc_en") or "").strip()
        nhom[(m.get("kind"), m.get("name"), bo_dau(mo_ta[:120]).lower())].append(m)

    ra = []
    for (kind, ten, _), ds in nhom.items():
        # Cách gọi ĐƯỢC KHUYÊN phải là cách CHẠY ĐƯỢC ở nhiều máy nhất — nếu không,
        # trang sẽ khuyên gõ một lệnh thuộc plugin đã tắt. Đúng lỗi lộ ra ngày
        # 05/08/2026: sau khi tắt 8 plugin medsci-* trên Windows, bản chụp Mac (chưa
        # dọn) vẫn còn `/medsci-analysis:*`, và nó thắng chỉ vì đứng trước theo bảng
        # chữ cái. Xếp theo SỐ MÁY thay vì viết cứng tên plugin nào được ưu ái.
        ds.sort(key=lambda x: (-len(x.get("may") or ()),
                               UU_TIEN_NGUON.index(x["source"])
                               if x.get("source") in UU_TIEN_NGUON else 99,
                               x.get("invoke", "")))
        chinh = ds[0]
        may = set()
        for x in ds:
            may |= set(x.get("may") or ())

        # "Gọi được cả:" chỉ đáng hiện khi công cụ đến từ HAI KHO KHÁC NHAU (vd một
        # skill có cả bản cá nhân lẫn bản plugin — bác sĩ cần biết mình đang gọi bản
        # nào). Nhiều cửa vào của CÙNG một kho thì không: bộ medsci-skills đẻ ra 8
        # dòng "gọi được cả" y hệt dưới mỗi skill, che lấp chính phần mô tả.
        kho_chinh = (chinh.get("source") or "").partition("@")[2]
        goi_khac = [x["invoke"] for x in ds[1:]
                    if x.get("invoke") and (x.get("source") or "").partition("@")[2] != kho_chinh]

        ra.append({
            "ten": ten,
            "loai": TEN_LOAI.get(kind, kind),
            "nhom": chinh.get("plugin") or chinh.get("source") or "khác",
            "mo_ta": (chinh.get("desc_en") or "").strip(),
            "goi": chinh.get("invoke") or "",
            "goi_khac": goi_khac,
            "tang": min(int(x.get("tier_guess") or 3) for x in ds),
            "may": "".join(sorted({"Windows": "W", "Mac": "M"}.get(v, v[:1]) for v in may)),
        })
    ra.sort(key=lambda x: (x["tang"], x["nhom"], x["ten"]))
    return ra


def rut_gon(s: str, n: int = 300) -> str:
    """Rút mô tả cho vừa một dòng đọc lướt, cắt ở ranh giới câu nếu có."""
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cat = s[:n]
    for dau in (". ", "; ", " — ", ", "):
        i = cat.rfind(dau)
        if i > n * 0.6:
            return cat[:i] + "…"
    return cat.rstrip() + "…"


def nap_viec_hay_lam() -> list[dict]:
    """Bảng 'việc cần làm → gọi cái gì'. Bác sĩ SỬA ĐƯỢC bằng tay ở
    viec-hay-lam.json — đây là phần duy nhất của trang không sinh từ máy quét."""
    if VIEC_HAY_LAM.exists():
        return json.loads(VIEC_HAY_LAM.read_text(encoding="utf-8")).get("viec", [])
    return []


# ---------------------------------------------------------------- HTML ----

CSS = """
*{box-sizing:border-box}
:root{
  --nen:#f7f8fa; --the:#fff; --chu:#1a1d21; --mo:#5b6470; --vien:#e3e6ea;
  --nhan:#0b5fff; --nhan-nen:#e8f0ff; --xanh:#0a7d4b; --xanh-nen:#e6f5ee;
  --cam:#a35a00; --cam-nen:#fdf0e0; --ma-nen:#f0f2f5;
}
@media (prefers-color-scheme:dark){:root{
  --nen:#14171a; --the:#1c2024; --chu:#e8eaed; --mo:#9aa4b0; --vien:#2c3238;
  --nhan:#6ea8ff; --nhan-nen:#1a2740; --xanh:#5fd3a0; --xanh-nen:#12301f;
  --cam:#f0a95a; --cam-nen:#33240f; --ma-nen:#252a30;
}}
html,body{margin:0;padding:0}
body{background:var(--nen);color:var(--chu);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.boc{max-width:1180px;margin:0 auto;padding:20px 18px 60px}
h1{font-size:22px;margin:0 0 4px}
.phu{color:var(--mo);font-size:13px;margin:0 0 18px}
.dinh{position:sticky;top:0;z-index:9;background:var(--nen);padding-top:12px;
  border-bottom:1px solid var(--vien);margin-bottom:16px}
#o-tim{width:100%;padding:13px 15px;font-size:16px;border:2px solid var(--vien);
  border-radius:10px;background:var(--the);color:var(--chu);outline:none}
#o-tim:focus{border-color:var(--nhan)}
.loc{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.chip{padding:5px 12px;border:1px solid var(--vien);border-radius:999px;background:var(--the);
  color:var(--mo);cursor:pointer;font-size:13px;user-select:none}
.chip:hover{border-color:var(--nhan)}
.chip.chon{background:var(--nhan-nen);border-color:var(--nhan);color:var(--nhan);font-weight:600}
.dem{color:var(--mo);font-size:13px;padding:6px 0 10px}
.viec{display:grid;grid-template-columns:repeat(auto-fill,minmax(265px,1fr));gap:8px;margin-bottom:22px}
.the-viec{background:var(--the);border:1px solid var(--vien);border-radius:9px;padding:10px 12px;
  cursor:pointer;transition:.12s}
.the-viec:hover{border-color:var(--nhan);transform:translateY(-1px)}
.the-viec b{display:block;font-size:13.5px;font-weight:600;margin-bottom:3px}
.the-viec span{color:var(--nhan);font-size:12px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
h2.nhom{font-size:13px;text-transform:uppercase;letter-spacing:.5px;color:var(--mo);
  margin:22px 0 8px;padding-bottom:5px;border-bottom:1px solid var(--vien)}
.muc{background:var(--the);border:1px solid var(--vien);border-radius:9px;padding:11px 13px;margin-bottom:7px}
.dau{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:4px}
.ma{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;
  background:var(--ma-nen);padding:3px 8px;border-radius:6px;cursor:pointer;border:1px solid transparent}
.ma:hover{border-color:var(--nhan);color:var(--nhan)}
.ma.xong{background:var(--xanh-nen);color:var(--xanh);border-color:var(--xanh)}
.nhan{font-size:11px;padding:2px 7px;border-radius:5px;background:var(--ma-nen);color:var(--mo)}
.nhan.agent{background:var(--xanh-nen);color:var(--xanh)}
.nhan.may{background:var(--cam-nen);color:var(--cam)}
.mota{color:var(--mo);font-size:13.5px;margin:0}
.them{font-size:12px;color:var(--mo);margin-top:4px}
.trong{text-align:center;color:var(--mo);padding:40px 0}
kbd{background:var(--ma-nen);border:1px solid var(--vien);border-radius:4px;padding:1px 5px;font-size:12px}
.chan{margin-top:34px;padding-top:14px;border-top:1px solid var(--vien);color:var(--mo);font-size:12px}
"""

JS = """
const DATA = __DATA__;
const oTim = document.getElementById('o-tim');
const khungKq = document.getElementById('kq');
const oDem = document.getElementById('dem');
let locLoai = 'tat-ca', locMay = 'tat-ca';

// Bỏ dấu ngay trong trình duyệt: bác sĩ gõ "co mau" phải ra "cỡ mẫu".
// đ/Đ không phải d + dấu tổ hợp nên NFD không tách được — xử lý riêng.
function boDau(s){
  return (s||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')
                .replace(/đ/g,'d').replace(/Đ/g,'D').toLowerCase();
}
DATA.forEach(m => {
  m._ten  = boDau(m.ten);
  m._goi  = boDau(m.goi);
  m._mota = boDau(m.mo_ta);
  m._tim  = [m._ten, m._mota, m._goi, boDau(m.nhom), boDau(m.loai)].join(' ');
});

// Nguồn do chính bác sĩ dựng — ưu tiên hơn plugin ngoài khi điểm ngang nhau:
// agent EBM có cổng an toàn, buộc ghi PMID/DOI, không PII.
const NGUON_NHA = ['ebm-agents','user-commands','user-skills','cowork'];

// XẾP HẠNG. Không có nó thì gõ "co mau" trả về synthesis_agent trước
// co-mau-nghien-cuu (lỗi lộ ra khi thử ngày 05/08/2026): lọc đúng nhưng thứ tự
// vô nghĩa thì vẫn không tìm ra được. Khớp ở TÊN đáng giá hơn hẳn khớp trong mô tả.
function diem(m, tu){
  let d = 0;
  for (const t of tu){
    if (m._ten === t)                d += 100;
    else if (m._ten.startsWith(t))   d += 60;
    else if (m._ten.includes(t))     d += 40;
    else if (m._goi.includes(t))     d += 22;
    else if (m._mota.startsWith(t))  d += 10;
    else if (m._mota.includes(t))    d += 5;
  }
  if (m.loai === 'agent')            d += 14;
  if (NGUON_NHA.includes(m.nhom))    d += 10;
  return d;
}

function loc(){
  const q = boDau(oTim.value.trim());
  const tu = q ? q.split(/\\s+/) : [];
  const ds = DATA.filter(m => {
    if (locLoai !== 'tat-ca' && m.loai !== locLoai) return false;
    if (locMay !== 'tat-ca' && !m.may.includes(locMay)) return false;
    return tu.every(t => m._tim.includes(t));   // mọi từ đều phải khớp
  });
  if (tu.length) ds.forEach(m => m._d = diem(m, tu));
  return {ds, coTim: tu.length > 0};
}

function veMuc(m){
  const nhanMay = m.may === 'MW' ? '' : '<span class="nhan may">chỉ ' + (m.may==='W'?'Windows':'Mac') + '</span>';
  const khac = m.goi_khac && m.goi_khac.length
    ? '<div class="them">Gọi được cả: ' + m.goi_khac.map(x=>'<code>'+x+'</code>').join(' · ') + '</div>' : '';
  return '<div class="muc"><div class="dau">'
       + '<span class="ma" data-goi="' + m.goi + '">' + m.goi + '</span>'
       + '<span class="nhan ' + (m.loai==='agent'?'agent':'') + '">' + m.loai + '</span>'
       + nhanMay + '<span class="nhan">' + m.nhom + '</span></div>'
       + '<p class="mota">' + m.mo_ta + '</p>' + khac + '</div>';
}

function ve(){
  const {ds, coTim} = loc();
  oDem.textContent = ds.length + ' mục' + (coTim ? ' khớp "'+oTim.value.trim()+'"' : '');
  // Bảng "Việc hay làm" chiếm trọn màn hình đầu — để nguyên khi đang tìm thì kết
  // quả bị đẩy xuống dưới màn hình, bác sĩ tưởng không có gì. Ẩn khi đang gõ.
  document.getElementById('khoi-viec').style.display = coTim ? 'none' : '';
  if (!ds.length){
    khungKq.innerHTML = '<div class="trong">Không có mục nào khớp.<br>Thử ít từ hơn, hoặc bỏ bộ lọc.</div>';
    return;
  }
  // ĐANG TÌM → một danh sách phẳng xếp theo độ sát, cái cần tìm nằm ngay dòng đầu.
  // KHÔNG tìm → gom theo nhóm để bác sĩ duyệt xem hệ thống có sẵn những gì.
  if (coTim){
    ds.sort((a,b) => b._d - a._d || a.ten.localeCompare(b.ten));
    khungKq.innerHTML = '<h2 class="nhom">Sát nhất với "' + oTim.value.trim() + '"</h2>'
                      + ds.slice(0,60).map(veMuc).join('')
                      + (ds.length > 60 ? '<p class="them">…còn ' + (ds.length-60)
                         + ' mục nữa — gõ thêm từ để thu hẹp.</p>' : '');
    return;
  }
  const nhom = {};
  ds.forEach(m => (nhom[m.nhom] = nhom[m.nhom] || []).push(m));
  khungKq.innerHTML = Object.keys(nhom).sort().map(g =>
    '<h2 class="nhom">' + g + ' — ' + nhom[g].length + ' mục</h2>' + nhom[g].map(veMuc).join('')
  ).join('');
}

// Bấm vào lệnh = chép vào bộ nhớ tạm, dán thẳng vào Claude Code.
khungKq.addEventListener('click', e => {
  const el = e.target.closest('.ma'); if (!el) return;
  navigator.clipboard.writeText(el.dataset.goi).then(() => {
    const cu = el.textContent;
    el.classList.add('xong'); el.textContent = '✓ đã chép';
    setTimeout(() => { el.classList.remove('xong'); el.textContent = cu; }, 1100);
  });
});

document.querySelectorAll('.the-viec').forEach(t => t.addEventListener('click', () => {
  oTim.value = t.dataset.tim; ve(); oTim.focus();
}));

document.querySelectorAll('.chip').forEach(c => c.addEventListener('click', () => {
  const loai = c.dataset.loc;
  document.querySelectorAll('.chip[data-loc="' + loai + '"]').forEach(x => x.classList.remove('chon'));
  c.classList.add('chon');
  if (loai === 'loai') locLoai = c.dataset.gt; else locMay = c.dataset.gt;
  ve();
}));

oTim.addEventListener('input', ve);
document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== oTim){ e.preventDefault(); oTim.focus(); }
  if (e.key === 'Escape'){ oTim.value = ''; ve(); oTim.blur(); }
});
ve(); oTim.focus();
"""


def sinh_html(muc: list[dict], viec: list[dict], ngay: dict[str, str]) -> str:
    data = [{k: m[k] for k in ("ten", "loai", "nhom", "goi", "goi_khac", "may")}
            | {"mo_ta": rut_gon(m["mo_ta"])} for m in muc]

    the_viec = "".join(
        f'<div class="the-viec" data-tim="{html.escape(v["tim"])}">'
        f'<b>{html.escape(v["viec"])}</b><span>{html.escape(v["goi"])}</span></div>'
        for v in viec)

    quet = " · ".join(f"{m}: {n}" for m, n in sorted(ngay.items()))
    js = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False))

    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tra cứu công cụ — Claude Code</title>
<style>{CSS}</style></head><body><div class="boc">

<h1>Tra cứu công cụ</h1>
<p class="phu">{len(muc)} công cụ (đã gộp các bản trùng) · quét ngày {quet} ·
sinh bằng <code>tools/vietnamize/build_trang_tra_cuu.py</code> — không sửa tay file này</p>

<div class="dinh">
  <input id="o-tim" placeholder="Gõ việc cần làm — có dấu hay không dấu đều được (vd: co mau, tram cam, ICD, viet ban thao)" autocomplete="off">
  <div class="loc">
    <span class="chip chon" data-loc="loai" data-gt="tat-ca">Tất cả</span>
    <span class="chip" data-loc="loai" data-gt="agent">agent</span>
    <span class="chip" data-loc="loai" data-gt="kỹ năng">kỹ năng</span>
    <span class="chip" data-loc="loai" data-gt="lệnh">lệnh</span>
    <span style="width:14px"></span>
    <span class="chip chon" data-loc="may" data-gt="tat-ca">Máy nào cũng được</span>
    <span class="chip" data-loc="may" data-gt="W">Chạy được trên Windows</span>
    <span class="chip" data-loc="may" data-gt="M">Chạy được trên Mac</span>
  </div>
  <div class="dem" id="dem"></div>
</div>

<div id="khoi-viec">
  <h2 class="nhom">Việc hay làm — bấm để lọc</h2>
  <div class="viec">{the_viec}</div>
</div>

<div id="kq"></div>

<p class="chan">Bấm vào tên lệnh để chép, rồi dán vào Claude Code.
Phím <kbd>/</kbd> nhảy tới ô tìm, <kbd>Esc</kbd> xoá.
Trang này chỉ TRA CỨU — mọi kết quả y khoa do công cụ sinh ra vẫn cần bác sĩ kiểm chứng.</p>

</div><script>{js}</script></body></html>
"""


# Những nhóm bác sĩ chạm tới hằng ngày → liệt kê ĐẦY ĐỦ trong index.
# Phần còn lại chỉ tóm tắt, vì nạp cả 1170 mục vào ngữ cảnh mỗi lần hỏi vừa chậm
# vừa lấn chỗ của chính câu hỏi — mà `/cong-cu-gi` chỉ cần chọn ra vài ứng viên.
NHOM_LIET_KE_DU = {"ebm-agents", "user-commands", "user-skills"}


def sinh_index(muc: list[dict], viec: list[dict]) -> str:
    """Index GỌN cho `/cong-cu-gi`.

    Thiết kế CÓ CHỦ Ý không liệt kê hết: bản đầy đủ 1170 mục nặng ~213 KB (~60k
    token) — nạp trước mỗi câu hỏi là phí, trong khi phần lớn câu hỏi chỉ chạm tới
    agent EBM và mấy lệnh tiếng Việt. Nhóm hay dùng liệt kê đủ; nhóm còn lại ghi
    tóm tắt + vài tên tiêu biểu, tra sâu bằng `grep` trên DANH-MUC-CONG-CU.md
    (lấy đúng dòng khớp, không nạp cả file).
    """
    nhom: dict[str, list[dict]] = defaultdict(list)
    for m in muc:
        nhom[m["nhom"]].append(m)

    ra = [
        "# Index công cụ — bản GỌN cho `/cong-cu-gi`",
        "",
        "> Sinh tự động bằng `tools/vietnamize/build_trang_tra_cuu.py`. KHÔNG sửa tay.",
        "",
        f"**{len(muc)} công cụ** (đã gộp bản trùng giữa các plugin cùng nội dung).",
        "Nhãn máy: **[W]** chỉ Windows · **[M]** chỉ Mac · không ghi = chạy được cả hai.",
        "",
        "## Cách dùng index này",
        "",
        "1. Xem bảng **Việc hay làm** — phần lớn câu hỏi dừng ở đây.",
        "2. Chưa thấy thì đọc 3 mục liệt kê đầy đủ bên dưới (agent EBM · lệnh · kỹ năng).",
        "3. Vẫn chưa thấy thì **grep** trên danh mục đầy đủ, ĐỪNG đọc cả file (~530 KB):",
        "   `grep -i -A2 '<từ khoá>' tools/vietnamize/DANH-MUC-CONG-CU.md`",
        "   — thử cả từ khoá tiếng Anh (tên skill hầu hết là tiếng Anh).",
        "4. Không có công cụ nào hợp thì nói thẳng, đừng gợi ý gượng ép.",
        "",
        "## Việc hay làm",
        "",
        "| Cần làm gì | Gọi cái gì |",
        "|---|---|",
    ]
    ra += [f'| {v["viec"]} | `{v["goi"]}` |' for v in viec]
    ra.append("")

    for g in sorted(nhom, key=lambda x: (x not in NHOM_LIET_KE_DU, x)):
        if g not in NHOM_LIET_KE_DU:
            continue
        ra += [f"## {g}  ({len(nhom[g])} mục — liệt kê đủ)", ""]
        for m in sorted(nhom[g], key=lambda x: x["ten"]):
            may = "" if m["may"] == "MW" else f' [{m["may"]}]'
            ra.append(f'- `{m["goi"]}`{may} — {rut_gon(m["mo_ta"], 130)}')
        ra.append("")

    con_lai = {g: ds for g, ds in nhom.items() if g not in NHOM_LIET_KE_DU}
    ra += [
        f"## Các nhóm còn lại ({sum(len(v) for v in con_lai.values())} mục)",
        "",
        "Không liệt kê đủ ở đây — dùng `grep` trên `DANH-MUC-CONG-CU.md` như hướng dẫn trên.",
        "",
        "| Nhóm | Số mục | Vài tên tiêu biểu |",
        "|---|---|---|",
    ]
    for g in sorted(con_lai, key=lambda x: -len(con_lai[x])):
        ten = " · ".join(sorted(m["ten"] for m in con_lai[g])[:6])
        ra.append(f"| `{g}` | {len(con_lai[g])} | {ten} |")
    ra.append("")
    return "\n".join(ra)


def main() -> int:
    muc_tho, ngay = nap_ban_chup()
    muc = gom_trung(muc_tho)
    viec = nap_viec_hay_lam()

    OUT_HTML.write_text(sinh_html(muc, viec, ngay), encoding="utf-8")
    OUT_INDEX.write_text(sinh_index(muc, viec), encoding="utf-8")

    print(f"Mục thô (gộp 2 máy)   : {len(muc_tho)}")
    print(f"Sau khi gộp bản trùng : {len(muc)}   (bớt {len(muc_tho) - len(muc)} dòng trùng)")
    print(f"→ {OUT_HTML}  ({OUT_HTML.stat().st_size // 1024} KB)")
    print(f"→ {OUT_INDEX}  ({OUT_INDEX.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
