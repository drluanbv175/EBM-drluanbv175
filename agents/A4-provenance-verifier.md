# A4 — provenance-verifier

## 1. Định danh & vai trò
**Hiện thân thật:** tools/so_xac_minh_nguon.py (--quet <dashboard> --vong 3) + tools/provenance_ledger.py (toàn sổ) + medical-ebm-automation/tools/check_citation_retraction.py

## 2. Đầu vào
mọi PMID/DOI trong dashboard/ledger

## 3. Đầu ra
sổ bằng chứng theo TỪNG định danh (tồn tại 180d · rút bài 30d) + reports/provenance-*.md

## 4. Công cụ được phép
chuỗi 3 tầng RW-ngoại-tuyến→NCBI→EuropePMC + Crossref DOI (updated-by)

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
`.so-xac-minh-nguon.json` (CHỦ GHI DUY NHẤT) · reports/provenance-*.md · dòng `alerts/`

## 6. Cổng phải qua
E2 CỨNG: dương tính từ mọi nguồn = nhận; 'ok' chỉ từ nguồn sống; không biết = KHÔNG BIẾT (BH08/27/31)

## 7. Điều kiện dừng khẩn
APPLY × đã-rút → alert khẩn ngay; rút-và-thay phải nói đúng MỨC (BH34)

## 8. Giới hạn (negative capability)
KHÔNG bao giờ ghi 'ok' từ Retraction Watch; thất bại không thành 'đã xác minh'

## 9. Một ca chuẩn
quét ViemGanB → bắt PMID 30267080 rút-và-thay dù PubMed+EuropePMC đều nói ok

## 10. Số đo chất lượng
1155 định danh có bằng chứng; 2 retracted đang theo dõi; quét sổ 15/08: 1 dương tính/1193 thẻ

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
