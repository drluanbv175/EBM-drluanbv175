# 12/11/2026 — Khoá «Access this article» của Springer khớp nhầm câu giấy phép Open Access

**Hiện tượng.** Lượt 20, lô 3 làn Chrome: bài OA PMID 40838698 (J Clin Sleep Med, DOI 10.5664/jcsm.11864, nay đăng trên
link.springer.com, thân bài 68.629 ký tự, có meta PDF) bị bộ lưu báo `ok:false` — «khoá trên trang: Access This article».

**Gốc.** Mẫu `khoaTrang` của `springer_link` trong `tools/lan_chrome/cau_hinh.json` là `Access this article|Buy article PDF|Buy Now`
(cờ i, không ranh giới) ⇒ khớp «Access This article» nằm TRONG câu giấy phép «Open Access This article is licensed under a
Creative Commons…» mà mọi bài OA của Springer đều in. Cùng họ lỗi với «Purchase» trần của Cochrane (PR #320) và «sign out»
trong «sign outside» (10/11).

**Hậu quả nếu không bắt.** Agent ghi `--khong-truy-cap` ⇒ bài OA bị đánh dấu «không quyền» 90 ngày, rời hàng chờ toàn văn.
Agent lô 3 đã soi ngữ cảnh trước khi ghi nên KHÔNG ghi; bài 32222797 (Eur Radiol 2020) ghi `k` cùng lúc đã đối chiếu Unpaywall:
`oa_status: closed` — ghi đúng.

**Sửa.** Mẫu thành `(?<!Open )\bAccess this article\b|\bBuy article PDF\b|\bBuy Now\b`; tường phí thật («Access this article
· Log in via an institution · Subscribe and save», PMID 42289039) vẫn khoá. Test
`tools/test_lan_chrome_springer_khoa_oa_20261112.py` chạy chính `danhGia` của bo_luu.js qua node; đột biến (trả mẫu cũ, bỏ
lookbehind) đều đỏ đúng chỗ.

**Bài học.** Mọi chuỗi khoá trang của NXB phải thử trên câu giấy phép OA của chính NXB đó (Springer, Wiley, Elsevier đều in câu
«Open Access … licensed under…») trước khi vào cấu hình.
