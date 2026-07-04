#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_antifacts_qv.py — Sinh BẢN QUICK VIEW GỌN của Antifacts để nhúng làm Live Artifact
trong app Claude (tính năng Artifacts). KHÁC Antifacts.html đầy đủ ở chỗ:
  - BỎ field `detail_html` nặng (~8.5KB/thang × 45) → nhẹ ~25KB thay vì ~600KB.
  - Thẻ cập nhật là THẺ THÔNG TIN (không link file, vì sandbox artifact không thấy OneDrive).
  - Bỏ modal (position:fixed không hợp artifact) — thang điểm hiện dạng chip tên + badge.
Đây là BẢN CHỤP (snapshot): không tự cập nhật. Bản sống đầy đủ vẫn là Antifacts.html + skill.

Chạy:  python tools/build_antifacts_qv.py   →  ghi _antifacts_qv.html (fragment cho show_widget)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Antifacts.html"
OUT = ROOT / "_antifacts_qv.html"


def load_data():
    c = SRC.read_text(encoding="utf-8")
    m = re.search(r"const DATA=(\{.*?\});</script>", c, re.S)
    if not m:
        sys.exit("Không tìm thấy khối DATA trong Antifacts.html")
    return json.loads(m.group(1))


def lean(data):
    ups = []
    for u in data.get("updates", []):
        ups.append({
            "title": u.get("title", ""), "date": u.get("date", ""),
            "specialty": u.get("specialty", ""),
            "apply": u.get("apply"), "consider": u.get("consider"),
            "pmids": u.get("pmids"),
        })
    scs = []
    for s in data.get("scales", []):
        scs.append({
            "name": s.get("name", ""), "specialty": s.get("specialty", ""),
            "evidence": s.get("evidence", ""), "tool_type": s.get("tool_type", ""),
            "purpose": (s.get("purpose", "") or "")[:160],
        })
    return {
        "specialties": data.get("specialties", []),
        "totals": data.get("totals", {}),
        "updates": ups, "scales": scs,
        "generated_at": data.get("generated_at", ""),
    }


STYLE = """<style>
.af{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#0f172a;font-size:14px;line-height:1.5}
.af-note{background:#fffbeb;border:1px solid #fde68a;color:#92400e;border-radius:8px;padding:8px 11px;font-size:12px;margin:0 0 12px}
.af-title{font-size:16px;font-weight:600;margin:0 0 10px}
.af-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 12px}
.af-stat{background:#eef2ff;border:1px solid #e2e8f0;border-radius:8px;padding:5px 10px;font-size:12.5px;color:#3730a3}
.af-stat b{font-size:15px;margin-right:4px}
.af-search{width:100%;border:1px solid #cbd5e1;border-radius:8px;padding:8px 11px;font-size:14px;margin:0 0 12px;outline:none}
.af-spec{border:1px solid #e2e8f0;border-radius:10px;margin-bottom:10px;overflow:hidden;background:#fff}
.af-spec>summary{cursor:pointer;padding:11px 14px;display:flex;align-items:center;gap:10px;list-style:none;font-weight:600}
.af-spec>summary::-webkit-details-marker{display:none}
.af-pill{font-size:11.5px;color:#64748b;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:999px;padding:2px 8px;margin-left:auto;white-space:nowrap}
.af-body{padding:6px 14px 14px;border-top:1px solid #e2e8f0}
.af-sub{font-size:11.5px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:#64748b;margin:12px 0 6px}
.af-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}
.af-item{border:1px solid #e2e8f0;border-radius:9px;padding:9px 11px;background:#fff}
.af-t{font-weight:600;font-size:13px;margin:0 0 4px}
.af-m{font-size:11.5px;color:#64748b;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.af-b{font-size:10.5px;font-weight:700;border-radius:6px;padding:1px 6px;white-space:nowrap}
.b-ok{background:#dcfce7;color:#166534}.b-warn{background:#fef3c7;color:#92400e}.b-info{background:#e0e7ff;color:#3730a3}.b-gray{background:#f1f5f9;color:#475569}
.af-empty{color:#94a3b8;font-size:12.5px;font-style:italic;padding:4px 0}
.af-chip{display:inline-flex;align-items:center;gap:5px;border:1px solid #e2e8f0;border-radius:7px;padding:4px 8px;font-size:12px;margin:0 6px 6px 0;background:#fff}
</style>"""

CONTENT = """<div class="af">
<div class="af-note">Bản chụp (snapshot) gọn để xem trong app — KHÔNG tự cập nhật và link dashboard không mở từ đây. Bản SỐNG đầy đủ: file Antifacts.html + skill /antifacts. Cần bác sĩ kiểm chứng; nguồn PMID/DOI trong từng dashboard; không PII.</div>
<div class="af-title">Antifacts — Quick View theo chuyên khoa</div>
<div class="af-head" id="af-stats"></div>
<input class="af-search" id="af-q" placeholder="Tìm nhanh: chủ đề, thang điểm, chuyên khoa…" oninput="afSearch(this.value)">
<div id="af-app"></div>
</div>"""

SCRIPT = """<script>
(function(){
var D=DATA;
function esc(s){return (s==null?'':String(s)).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function norm(s){return (s==null?'':String(s)).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/\\u0111/g,'d');}
var q='';
function evB(e){e=(e||'').toLowerCase();var c='b-gray';if(e.indexOf('high')===0)c='b-ok';else if(e.indexOf('mod')===0||e.indexOf('low')===0||e.indexOf('very')===0)c='b-warn';return e?'<span class="af-b '+c+'">'+esc(e)+'</span>':'';}
function updCard(u){var c=[];if(u.apply!=null)c.push('<span class="af-b b-ok">Áp dụng '+u.apply+'</span>');if(u.consider!=null)c.push('<span class="af-b b-warn">Cân nhắc '+u.consider+'</span>');if(u.pmids)c.push('<span class="af-b b-info">'+u.pmids+' PMID</span>');return '<div class="af-item"><p class="af-t">'+esc(u.title)+'</p><div class="af-m">'+(u.date?esc(u.date):'')+'</div>'+(c.length?'<div class="af-m" style="margin-top:5px">'+c.join(' ')+'</div>':'')+'</div>';}
function scaleChip(s){return '<span class="af-chip" title="'+esc(s.purpose||'')+'">'+esc(s.name)+' '+evB(s.evidence)+'</span>';}
function match(t){return !q||norm(t).indexOf(q)>=0;}
function render(){
 document.getElementById('af-stats').innerHTML='<span class="af-stat"><b>'+(D.totals.updates||0)+'</b>cập nhật</span><span class="af-stat"><b>'+(D.totals.scales||0)+'</b>thang điểm</span><span class="af-stat"><b>'+D.specialties.length+'</b>chuyên khoa</span>';
 var html='';
 D.specialties.forEach(function(sp,i){
  var ups=D.updates.filter(function(u){return u.specialty===sp.name&&match(u.title);});
  var scs=D.scales.filter(function(s){return s.specialty===sp.name&&match(s.name+' '+(s.purpose||'')+' '+(s.tool_type||''));});
  if(q&&!ups.length&&!scs.length)return;
  var open=(i===0&&!q)||(q&&(ups.length||scs.length));
  html+='<details class="af-spec"'+(open?' open':'')+'><summary><span>'+(sp.icon||'')+'</span><span>'+esc(sp.name)+'</span><span class="af-pill">'+ups.length+' cập nhật · '+scs.length+' thang</span></summary><div class="af-body">';
  html+='<div class="af-sub">Cập nhật chứng cứ</div>';
  html+=ups.length?('<div class="af-grid">'+ups.map(updCard).join('')+'</div>'):'<div class="af-empty">— chưa có —</div>';
  html+='<div class="af-sub">Thang điểm lâm sàng</div>';
  html+=scs.length?('<div>'+scs.map(scaleChip).join('')+'</div>'):'<div class="af-empty">— chưa có —</div>';
  html+='</div></details>';
 });
 document.getElementById('af-app').innerHTML=html||'<div class="af-empty">Không có kết quả khớp "'+esc(q)+'".</div>';
}
window.afSearch=function(v){q=norm(v).trim();render();};
render();
})();
</script>"""


STANDALONE = ROOT / "Antifacts-QuickView.html"


def main():
    data = lean(load_data())
    frag = STYLE + "\n" + CONTENT + "\n<script>const DATA=" + json.dumps(data, ensure_ascii=False) + ";</script>\n" + SCRIPT
    OUT.write_text(frag, encoding="utf-8")
    # Bản ĐỘC LẬP (mở thẳng trình duyệt / dán vào "New live artifact" của app)
    page = ('<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Antifacts — Quick View theo chuyên khoa</title>'
            '<style>body{margin:0;padding:18px;background:#f5f7fb}</style></head><body>'
            + frag + '</body></html>')
    STANDALONE.write_text(page, encoding="utf-8")
    print("OK -> %s (%d ký tự) + %s (độc lập) | %d cập nhật · %d thang điểm"
          % (OUT.name, len(frag), STANDALONE.name, len(data["updates"]), len(data["scales"])))


if __name__ == "__main__":
    main()
