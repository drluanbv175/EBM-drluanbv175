/* BỘ LƯU TOÀN VĂN — LÀN CHROME (17/10/2026). Dán vào javascript_tool trên tab bài báo ĐANG MỞ trong Chrome thật của bác sĩ.
 * Không tự chạy: `tools/lan_chrome.py toan-van` in tệp này kèm MỘT lời gọi `__ebmTai(...)` đã điền cấu hình của miền.
 * Trước đây hàm này chỉ sống trong localStorage của từng miền và script tạm của một phiên ⇒ phiên/máy khác phải dò lại.
 *
 * Luật (khớp tools/phien_uy_quyen_chrome.py — công cụ đó KIỂM LẠI mọi thứ ở bước --nhan, đây chỉ là bước dựng tệp):
 *  • CHỈ thân bài (vùng `chon`), bỏ script/nav/header/footer/form và mọi khối tài khoản; dòng đầu tệp là dấu phiên
 *    `<!-- ebm-phien:<mã> pmid:<n> url:<URL> -->`.
 *  • PDF của NXB nhúng vào chính tệp HTML (MỘT lần tải mỗi bài — Chrome chặn lặng lẽ lần tải thứ hai trên cùng trang).
 *  • Không quyền ⇒ KHÔNG tạo nút tải: URL mang dấu chuyển hướng (`dau_khong_quyen_url`), đề mục tường phí (`khoaDeMuc`, vd
 *    Nature «Access options»), chuỗi khoá trong thân bài (`khoa`) hoặc trên trang (`khoaTrang`), thân bài ngắn hơn `min`.
 *  • KHÔNG bấm xác minh chống bot, KHÔNG gõ mật khẩu — nút tải do Claude bấm sau khi bác sĩ đã vượt chặn.
 */
(function (g) {
  'use strict';

  /** Phán quyết THUẦN (không đụng DOM — test bằng node): {ok, ly}. */
  function danhGia(t) {
    t = t || {};
    var o = t.o || {};
    var urlKhoa = (t.khongQuyenUrl || []).concat(o.khongQuyenUrl || []);
    for (var i = 0; i < urlKhoa.length; i++) {
      if (new RegExp(urlKhoa[i], 'i').test(t.href || '')) return {ok: false, ly: 'không quyền — URL chuyển hướng: ' + urlKhoa[i]};
    }
    if (!t.soVung) return {ok: false, ly: 'không thấy vùng thân bài «' + (o.chon || 'article') + '»'};
    var toiThieu = o.min || 12000;
    if ((t.doDai || 0) < toiThieu) return {ok: false, ly: 'thân bài ngắn ' + (t.doDai || 0) + ' < ' + toiThieu};
    var deMuc = (t.deMuc || []).map(function (x) { return String(x).trim(); });
    var khoaDeMuc = o.khoaDeMuc || [];
    for (var j = 0; j < khoaDeMuc.length; j++) {
      if (deMuc.indexOf(khoaDeMuc[j]) >= 0) return {ok: false, ly: 'đề mục tường phí «' + khoaDeMuc[j] + '»'};
    }
    if (o.khoa) {
      var m = String(t.vung || '').match(new RegExp(o.khoa, 'i'));
      if (m) return {ok: false, ly: 'khoá trong thân bài: ' + m[0]};
    }
    if (o.khoaTrang) {
      // Cờ 'i' (KHÔNG 'm'): giữ đúng hành vi đã kiểm 14/10 — «Get Access$» của T&F so với CUỐI văn bản trang.
      var m2 = String(t.trang || '').match(new RegExp(o.khoaTrang, 'i'));
      if (m2) return {ok: false, ly: 'khoá trên trang: ' + m2[0]};
    }
    return {ok: true, ly: ''};
  }

  function dauPdf(buf) {
    return String.fromCharCode.apply(null, Array.prototype.slice.call(new Uint8Array(buf)));
  }

  async function taiPdf(u) {
    var r = await fetch(u, {credentials: 'include'});
    var b = await r.blob();
    var dau = dauPdf(await b.slice(0, 5).arrayBuffer());
    return {b: b, ok: dau === '%PDF-', ly: dau === '%PDF-' ? '' : 'không phải PDF (HTTP ' + r.status + ', ' + b.size + ' byte)'};
  }

  function nut(ok, nhan) {
    var cu = document.getElementById('__ebm_nut');
    if (cu) cu.remove();
    var a = document.createElement(ok ? 'a' : 'div');
    a.id = '__ebm_nut';
    a.style.cssText = 'position:fixed;left:0;top:0;width:320px;height:110px;z-index:2147483647;background:' +
      (ok ? '#c00' : '#888') + ';color:#fff;font:bold 20px sans-serif;display:flex;align-items:center;justify-content:center';
    a.textContent = nhan;
    document.body.appendChild(a);
    return a;
  }

  /** Bước 1: dựng tệp HTML thân bài (+ PDF nhúng nếu lấy được) và đặt nút tải đỏ ở góc trái trên. */
  async function tai(ma, pmid, url, o) {
    o = o || {};
    var ds = (o.chon || 'article').split(',').map(function (s) { return document.querySelector(s.trim()); }).filter(Boolean);
    var vung = ds.map(function (e) { return e.innerText; }).join('\n');
    var deMuc = Array.prototype.slice.call(document.querySelectorAll('h1,h2,h3')).map(function (h) { return h.innerText; });
    var kq = danhGia({o: o, href: location.href, khongQuyenUrl: o.dauKhongQuyenUrl || [], soVung: ds.length,
      doDai: vung.length, vung: vung, trang: document.body.innerText, deMuc: deMuc});
    var pdfB64 = '', pdfLy = '', pdf2 = '';
    if (kq.ok) {
      var pdfU = o.pdf === 'meta' ? ((document.querySelector('meta[name="citation_pdf_url"]') || {}).content || '') : (o.pdf || '');
      if (!pdfU && o.pdfXem) {
        // Trang XEM PDF (Cochrane): meta trỏ tới trang HTML nhỏ chứa liên kết tệp PDF thật.
        try {
          var xem = (document.querySelector('meta[name="citation_pdf_url"]') || {}).content || '';
          var t = xem ? await (await fetch(xem, {credentials: 'include'})).text() : '';
          var lk = t.match(new RegExp(o.pdfXem));
          pdfU = lk ? new URL(lk[0], location.origin).href : '';
          if (!pdfU) pdfLy = 'trang xem PDF không có liên kết khớp mẫu';
        } catch (e) { pdfLy = String(e); }
      }
      if (pdfU) {
        try {
          var p = await taiPdf(pdfU);
          if (p.ok) {
            pdfB64 = await new Promise(function (res) { var fr = new FileReader(); fr.onload = function () { res(fr.result.split(',')[1]); }; fr.readAsDataURL(p.b); });
          } else pdfLy = p.ly;
        } catch (e2) { pdfLy = String(e2); }
      }
      if (o.pdf2) {
        pdf2 = o.pdf2 === 'meta' ? ((document.querySelector('meta[name="citation_pdf_url"]') || {}).content || '') : new URL(o.pdf2, location.origin).href;
      }
    }
    if (!kq.ok) { nut(false, 'EBM bỏ ' + pmid); g.__ebmOk = false; g.__pdf2 = ''; return {ok: false, ly: kq.ly, len: vung.length}; }
    var c = document.createElement('div');
    ds.forEach(function (e) { c.appendChild(e.cloneNode(true)); });
    c.querySelectorAll('script,style,noscript,iframe,nav,header,footer,aside,form,button,svg,[class*="account"],[class*="login"],[class*="signin"]')
      .forEach(function (e) { e.remove(); });
    var taiKhoan = /sign out|log ?out|my account/i.test(c.innerText);
    var html = '<!-- ebm-phien:' + ma + ' pmid:' + pmid + ' url:' + url + ' -->\n<!doctype html><html><head><meta charset="utf-8"><title>PMID ' +
      pmid + '</title></head><body>\n' + c.innerHTML + '\n' +
      (pdfB64 ? '<script type="application/pdf;base64" id="ebm-pdf">' + pdfB64 + '</scr' + 'ipt>\n' : '') + '</body></html>';
    var a = nut(true, 'EBM tải PMID ' + pmid);
    a.href = URL.createObjectURL(new Blob([html], {type: 'text/html'}));
    a.download = 'PMID-' + pmid + '_phien.html';
    g.__ebmOk = true;
    g.__pdf2 = pdf2;
    return {ok: true, ly: taiKhoan ? 'CÓ DẤU TÀI KHOẢN — đừng bấm, báo bác sĩ' : '', len: vung.length, coPdf: !!pdfB64, pdfLy: pdfLy, pdf2: pdf2};
  }

  /** Bước 2 (NXB tách PDF sang trang riêng — ScienceDirect /pdfft, OUP silverchair): đang đứng trên trang PDF ⇒ tải lại đúng
   *  URL hiện tại (url rỗng) hoặc `url`, kiểm `%PDF-` và URL chứa `kiem` (PII/hậu tố DOI — chống PDF nhầm bài, đo 14/10). */
  async function pdfNut(pmid, url, kiem) {
    var u = url || location.href;
    if (kiem && u.toLowerCase().indexOf(String(kiem).toLowerCase()) < 0) {
      nut(false, 'EBM bỏ PDF ' + pmid);
      return {ok: false, ly: 'URL PDF không chứa «' + kiem + '» — nghi PDF NHẦM BÀI'};
    }
    var p = await taiPdf(u);
    if (!p.ok) { nut(false, 'EBM bỏ PDF ' + pmid); return {ok: false, ly: p.ly}; }
    var a = nut(true, 'EBM tải PDF ' + pmid);
    a.href = URL.createObjectURL(p.b);
    a.download = 'PMID-' + pmid + '_phien.pdf';
    return {ok: true, ly: '', byte: p.b.size};
  }

  g.__ebmDanhGia = danhGia;
  g.__ebmTai = tai;
  g.__ebmPdfNut = pdfNut;
  if (typeof module !== 'undefined' && module.exports) module.exports = {danhGia: danhGia};
})(typeof window !== 'undefined' ? window : globalThis);
