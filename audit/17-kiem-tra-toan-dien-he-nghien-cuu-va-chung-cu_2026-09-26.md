# 17 · Kiểm tra toàn diện hệ nghiên cứu và cập nhật chứng cứ y khoa (26/09/2026)

> Bác sĩ yêu cầu: «Kiểm tra toàn diện và cho báo cáo chi tiết về hệ thống nghiên cứu và cập nhật chứng cứ y khoa.
> Cho đề xuất để hoàn thiện tốt nhất.»
> Mọi con số dưới đây được **đo sống trong phiên 26/09/2026** bằng chính công cụ kiểm của hệ, không trích từ tài liệu cũ.
> Nơi đo: **phiên Cloud**, hai repo đặt cạnh nhau (`EBM-drluanbv175` ở `012c15f`, `medical-ebm-automation` ở `cd91669`).
> Cần bác sĩ kiểm chứng.

## 0. Phạm vi và giới hạn của lần kiểm này

- Phiên Cloud **không có** các thư mục chỉ nằm trên OneDrive: `EBM-Dashboards/`, `EBM_MASTER/`, `dashboard_mockups/`, `state/`, `queue/`.
  Mọi kiểm cần chúng đều ghi **⚪ không đo được**. ⚪ không có nghĩa là đạt, cũng không có nghĩa là hỏng.
- Cây git là bản **nông** (shallow). Vì vậy báo cáo không rút kết luận kiểu «chưa từng tồn tại trong lịch sử».
- Nguồn thật: `kiem_nguon_that.py` báo 🟢 — cấu hình đúng, **4/4 nguồn phân giải được**. Các phép đo mạng dưới đây đều là dữ liệu thật, không phải dữ liệu giả.

## 1. Tóm tắt điều hành

| Trục | Trạng thái đo được | Nhận định |
|---|---|---|
| Nguồn chứng cứ | 36 nguồn trong sổ: 29 đang chạy · 3 suy giảm · 4 chưa phủ | Lõi miễn phí chạy thật trên cả Cloud lẫn máy thật. Khoảng trống còn lại hầu hết nằm ngoài tầm kỹ thuật (thương mại, cần tổ chức cấp quyền). |
| Cổng liêm chính & rút bài | Pipeline cổng chạy trên fixture: PASS · 0 lỗi cứng | Cổng chạy đúng. Phần hợp đồng template/hub thì ⚪ trên Cloud. |
| Kiểm chéo ngữ nghĩa `apply` (K1–K4) | Đã có mã và đã nối vào `xuat_goi_cap_nhat.py` (chỉ cảnh báo) | Chưa được chặn vì **bộ vàng chưa có nhãn bác sĩ**. |
| Giám sát định kỳ | `BLOCKED_FOR_DEPLOYMENT`: 2 FAIL · 4 cổng người · 2 ⚪ | Chưa có nhật ký chạy tuần/tháng; chưa cấu hình kênh cảnh báo. |
| Điểm khám | Bộ vàng 80/80 câu **bác sĩ đã duyệt** (24/09) | CLAUDE.md từng ghi «chờ duyệt» — đã sửa trong đợt này. |
| Hệ nghiên cứu G0–G10 (máy) | 11/11 script cổng + 11/11 quality gate · canary gài lỗi 9/9 bị bắt · 🔴 0 | Hạ tầng cổng hoàn chỉnh, fail-closed đúng vai. |
| Đề tài thật C1a | 0/4 cổng cứng có chữ ký · 45 việc chưa làm · 3 quyết định treo · 524 chỗ trống | Toàn bộ là **việc của người thật**; máy không có lỗi nào cần sửa (🔴 0). |
| Điều phối & quản trị | 50 agent (21 lâm sàng · 28 nghiên cứu · 1 guardrail) · 0 lỗi quản trị | Cổng cứng khai nhất quán trên 84 tệp agent. Orchestration plugin: PASS. |
| Chốt hồi quy bài học | 88/115 được canh · 0 tái phát · 27 ⚪ | 27 mục cần dữ liệu OneDrive để canh. |
| Kiểm thử | Repo y khoa: **5859 passed · 66 skipped** (CI ngoại tuyến) | CI GitHub: job Linux xanh; job Windows đang chạy lúc viết. |

**Kết luận chung:** phần **máy** của cả hai hệ đã đạt mức hoàn thiện cao. Không có lỗi đỏ nào máy tự sửa được.
Điểm nghẽn chính nằm ở **ba loại việc máy không được làm thay**:
1. chữ ký và quyết định của bác sĩ, Hội đồng Đạo đức, phản biện;
2. dữ liệu và cấu hình chỉ có trên máy thật (nhật ký chạy tuần, kênh cảnh báo, thư mục OneDrive);
3. quyền truy cập nguồn thương mại hoặc nguồn phải xin cấp.

## 2. Hệ cập nhật chứng cứ

### 2.1 Nguồn (`data/sources.json`, 36 mục)

| Trạng thái | Nguồn | Lý do / đường vòng hiện có |
|---|---|---|
| Suy giảm | SRC-015 ACC/AHA (web hội) | Web hội chặn truy cập tự động. Đường vòng: lane Crossref theo tiêu đề (ACC/AHA ×3). |
| Suy giảm | SRC-039 Semantic Scholar | HTTP 429 khi không khoá (nhịp thấp). Không phải proxy chặn. |
| Suy giảm | SRC-042 Wiley TDM | Wiley chỉ cho truy cập theo IP của tổ chức; ngoài dải IP thì chỉ tải được bài Open Access. |
| Chưa phủ | SRC-021 Cục Quản lý Dược VN | `dav.gov.vn` từ chối kết nối TCP từ môi trường phiên. Chưa kiểm được robots.txt nên chưa viết connector. |
| Chưa phủ | SRC-030 UpToDate · DynaMed · Embase | Thương mại, cần hợp đồng tổ chức. |
| Chưa phủ | SRC-036 Epistemonikos | Phải gửi email xin token. SR/MA vẫn được phủ qua PubMed, Europe PMC và Cochrane MCP. |
| Chưa phủ | SRC-045 BTS toàn văn | Connector đã có nhưng chưa kiểm sống. Không có trang mục lục ổn định. |

Đo 25/09 trên Cloud (xem medical `CLAUDE.md`):
- `test-live` chạy thật cho 9 nguồn: pubmed · europepmc · crossref · openalex · clinicaltrials · openfda · core · scopus · consensus.
- 79/80 feed/lane guideline và an toàn thuốc trả bài thật. Mục duy nhất không trả là `fda_medwatch` (www.fda.gov trả HTTP 401 cho truy cập tự động); lỗi này được ghi đúng là `error`, không xanh giả.

### 2.2 Cổng liêm chính, rút bài, kiểm ngữ nghĩa

- `verify_clinical_evidence_update_pipeline.py` — 3 PASS: fixture tổng hợp, cổng liêm chính (0 lỗi cứng) và bộ phái sinh. 3 FAIL, đều vì trên Cloud thiếu `dashboard_mockups/` và `EBM_MASTER/`: hợp đồng template EW, hợp đồng template DA, hợp đồng hub.
- Rút bài trên fixture: 0/2 định danh có dấu vết kiểm còn hạn. Cổng ghi đúng là **«chưa biết», không phải «sạch»** — đúng luật bất đối xứng.
- K1–K4 (`kiem_cheo_ngu_nghia.py` bước ④-bis, `kiem_quan_the_chieu.py` bước ④-ter) chỉ cảnh báo. Chạy thật trên template EW: K1/K4 cho 6 ✓ · 0 🟠 · 2 ⚪; K3 cho 1 báo động giả đã biết (theo `audit/16` §7).

### 2.3 Giám sát định kỳ (`verify_evidence_surveillance_deployment.py`, chạy ngoại tuyến)

| Kiểm | Kết quả | Ghi chú |
|---|---|---|
| ESD01 Hợp đồng triển khai | PASS | chế độ `candidate_only_doctor_review_required` |
| ESD02 Đồng bộ scanner | ⚪ | So được 2/3 bản (hai bản vendor khớp); `EBM-Dashboards/` vắng |
| ESD03 Runtime fail-closed | PASS | |
| ESD04 Pipeline EW offline | ⚪ | thiếu `EBM_MASTER`, `dashboard_mockups` |
| ESD05 Scheduler launchd | Cổng người | Chỉ chạy trên macOS |
| ESD06–08 Canary/Scanner/Dashboard online | Cổng người | Cần `--online`. Đã chạy riêng hôm nay: ESD06 PASS; ESD07 PASS (2 chủ đề, 6 ứng viên thật) |
| **ESD09 Lịch sử runtime tuần/tháng** | **FAIL** | `weekly:missing; monthly:missing` |
| **ESD10 Kênh cảnh báo** | **FAIL** | `email_ready=False; webhook_ready=False` |
| ESD11 UAT và phê duyệt | PASS | 5 mẫu nguồn hợp lệ |

`tu_de_xuat_viec.py` báo cùng khoảng trống: 🔴 «Log giám sát tuần KHÔNG ĐỌC ĐƯỢC — chưa từng chạy trên máy này?».
PR drluanbv175/medical-ebm-automation#16 sửa để canary không ghi cảnh báo giả vào thư mục thật (CI Linux đã xanh).

### 2.4 Tầng cuộc gặp

- Bộ vàng `tra_diem_kham`: 80 câu, `trang_thai = BAC_SI_DA_DUYET` (24/09). Ngoài ra còn 22 câu `da_biet_chua_dat` — đó là khoảng trống độ phủ đang được theo dõi, không phải câu khẳng định.
- `kiem_safety_net.py`: 🟢 8/8 hội chứng có nguồn, 8/8 có lời dặn.

## 3. Hệ nghiên cứu G0–G10

### 3.1 Hạ tầng (`kiem_chi_tiet_he_nghien_cuu.py`)

- 🟢 **37** · 🟡 **36** (việc của người thật) · 🔴 **0** · ⚪ **0**.
- 13/13 tệp biên dịch sạch (11 script cổng, cùng `approve_gate` và `gate_contract`). 11/11 `gN_quality_gate.py` có CLI.
- `approve_gate` gọi quality gate của cả 6 cổng cứng **trước** khi ghi sổ cái.
- G5, G6, G10 tự tra sổ cái của cổng thượng nguồn (fail-closed).
- Canary: gài 9/9 lỗi đều bị bắt; dây nối 3/3.
- `verify_controlled_research_automation.py`: PASS cả 6 nhóm kiểm — cổng thẩm định, bình duyệt, cổng cứng đúng vai, readiness, thống kê, chuẩn hiện hành (WHO TRDS 1.3.1, ICMJE 1/2026, ICH E6(R3) Annex 2).
- `verify_exports_integrity.py`: PASS. `agent_gate_governance.py`: PASS (0 lỗi).

### 3.2 Đề tài thật `hai-long-benh-nhan-C1a-BVQY175` (`study_readiness.py`)

| Cổng | Trạng thái |
|---|---|
| G0 | ✅ PASS_G0_CONFIRMED (bác sĩ đã xác nhận PICO/kết cục chính) |
| G1, G3 | ✅ có checkpoint |
| G2, G4 | 📝 có hồ sơ, **chưa ký** |
| G5–G9 | chưa chạy |
| G10 | có checkpoint nhưng đang BLOCKED đúng (A12 chưa chạy; thượng nguồn G5–G9 còn thiếu) |

- **45 việc chưa làm.** 10 việc đầu gồm: xác nhận effect size (PMID/DOI), tỷ lệ dropout, cập nhật N của G3, codebook 12 biến mới, cognitive interview cùng pilot, thông tin chủ nhiệm.
- **3 quyết định còn treo** có thể làm đổi đề cương. Ví dụ: C6/C9 gộp nhiều vai trò nhân viên trong một câu hỏi (Phụ lục C.2).
- **81 nhãn [CẦN…]** trong 3 tệp đề cương/bài báo giao thức; **524 chỗ trống** trên toàn bộ tài liệu.
- Chưa có `approval_ledger.json` cho đề tài.

## 4. Điều phối và quản trị

- `verify_plugin_orchestration.py`: PASS. 3 worker `bio-research:*` ⚪ vì plugin chưa cài trên phiên này.
- `verify_hard_gate_count_consistency.py`: nguồn sự thật `[G10, G2, G4, G5, G8, G9]`. Quét 84 tệp agent, 0 dòng lệch.
- `verify_claude_code_repo_alignment.py`: PASS, gồm cả ngân sách ký tự CLAUDE.md sau khi sửa 2 câu lỗi thời.
- `kiem_lich_nen.py`: 🟢 nhưng thực chất ⚪ (0 tác vụ có dấu vết trên Cloud; log tuần và `queue/` vắng).
- `audit_ebm_system.py`: FAIL. Nhưng mọi dòng FAIL đều do tệp chỉ có trên OneDrive vắng mặt (template, tệp `.command/.bat`, `CHATGPT_EXPORT/`, `Antifacts.html`, `EBM_MASTER`). Tool sync: SKIP. Clinical runtime/chronic-care: `BLOCKED_FOR_PRODUCTION`, 37 blocker (khoá có chủ ý).

## 5. Tài liệu lệch mã sống (đã sửa trong đợt này)

| Nơi | Ghi cũ | Mã sống |
|---|---|---|
| CLAUDE.md §7 | Bộ vàng điểm khám «CHỜ bác sĩ duyệt» | Đã duyệt 80/80 ngày 24/09 (commit `ae55c10`) |
| CLAUDE.md §6.4 | «CHƯA có kiểm chéo ngữ nghĩa» mục `apply` | K1–K4 đã có và đã nối, chỉ cảnh báo, chưa có bộ vàng |

## 6. Đề xuất hoàn thiện — xếp theo ưu tiên

Ký hiệu: 👤 thẩm quyền bác sĩ · 🖥 cần máy thật (Mac/Windows có OneDrive) · 🤖 máy làm được ngay trong phiên.

### P0 — mở khoá vận hành (tác động lớn nhất, ít công)

1. 🖥👤 **Chạy vòng giám sát tuần lần đầu trên Mac** để đóng ESD09.
   - Lệnh: `bash medical-ebm-automation/scripts/weekly_safety.sh`, sau đó `verify_evidence_surveillance_deployment.py --online`.
   - Đây là việc duy nhất còn 🔴 trong `tu_de_xuat_viec`.
2. 👤🖥 **Cấu hình một kênh cảnh báo** (Gmail App Password qua SMTP, hoặc webhook) trong kho bí mật `~/.ebm-secrets` để đóng ESD10.
   - Bác sĩ tự nhập; không dán khoá vào khung chat.
   - Không có kênh này thì mọi phát hiện an toàn thuốc chỉ nằm trong tệp, không ai được báo.
3. 👤 **Merge drluanbv175/medical-ebm-automation#16** khi job Windows xanh. Như vậy canary chạy trên Mac sẽ không ghi cảnh báo giả vào `alerts/` thật.

### P1 — nâng độ tin cậy nội dung

4. 🖥👤 **Gắn nhãn bộ vàng kiểm chéo ngữ nghĩa (20 mục `apply`).**
   - Lệnh: `python3 tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang` trên Mac, sau đó bác sĩ điền `nhan_bac_si`.
   - Khi đã có số đo báo động giả, mới quyết định có cho K1–K4 **chặn** hay không. Đây là lớp duy nhất kiểm «nội dung đúng», không chỉ «nguồn có thật».
5. 🖥 **Chạy lại trọn bộ chốt trên Mac** (`chot_hoi_quy_bai_hoc.py`, `audit_ebm_system.py`, `kiem_do_tuoi_chung_cu.py`) để canh 27 mục BH đang ⚪ và đo độ tươi thật của các dashboard.
6. 👤 **Khoá Ed25519 cho vai phản biện/IRB** (nút `Phat Khoa Ed25519.command`). HMAC là đối xứng nên không chứng minh được người ký G8 độc lập với chủ nhiệm. Đây là điều kiện để về sau ép chữ ký `ed1`.

### P2 — đề tài C1a đi tiếp

7. 👤 **Giải 3 quyết định treo trước** (C6/C9 gộp vai trò, v.v.), vì chúng có thể đổi đề cương. Sau đó điền effect size có nguồn, dropout và N để khoá G3, rồi mới làm codebook 12 biến và pilot.
8. 👤 **Nộp hồ sơ G2 cho Hội đồng Đạo đức thật.** Đây là cổng cứng đầu tiên; máy đã sẵn quality gate và `approve_gate.py`. Dùng `python3 tools/study_readiness.py --study hai-long-benh-nhan-C1a-BVQY175` để theo dõi số việc còn lại.

### P3 — mở rộng nguồn (phụ thuộc bên ngoài)

9. 👤 Tự mở `dav.gov.vn/canh-bao-va-thu-hoi-cn81.html` và `dav.gov.vn/robots.txt` từ mạng Việt Nam. Tải được thì máy viết connector theo khuôn `kcb_vn_lane()`.
10. 👤 Gửi thư xin token Epistemonikos (thư nháp ở `medical-ebm-automation/docs/xin-cap-quyen-nguon-chung-cu.md`).
11. 🤖 Kiểm sống connector BTS toàn văn với một URL PDF đã biết. Nếu chạy được thì chuyển SRC-045 sang «active».
12. 🤖 Khảo sát robots.txt và điều khoản của ERS/ASCO/ESMO (đang «cần khảo sát thêm»).

### Không khuyến nghị làm

- Không nới cổng để ESD02/04/08 xanh trên Cloud. Đó là ⚪ trung thực vì dữ liệu cố ý nằm ngoài git.
- Không cài máy chủ MCP bên thứ ba cho nguồn đã có (đã đánh giá ở §1ter của `_CONNECTOR-CHUNG-CU.md`).

## 6bis. Trạng thái thi công từng đề xuất (26/09/2026, cùng ngày)

| # | Đề xuất | Trạng thái | Bằng chứng / bước còn lại |
|---|---|---|---|
| 1 | Chạy giám sát tuần lần đầu | 🖥 **Chờ Mac** | Bản đầy đủ ghi sổ cái/hub và có thể gửi email, nên không chạy trên Cloud. Trên Mac: `bash medical-ebm-automation/scripts/weekly_safety.sh`, rồi `python3 medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online`. |
| 2 | Kênh cảnh báo (ESD10) | 🤖 **Đã làm phần máy** · 👤 chờ bác sĩ nhập | Nút mới `Nhap Kenh Canh Bao.command` / `.bat` (`tools/nhap_kenh_canh_bao.py`) cho Gmail (mật khẩu ứng dụng) / SMTP / webhook https. Nhập bằng ô ẩn, ghi nguyên tử vào `~/.ebm-secrets`, không in bí mật. 10 test, 3 đột biến đều đỏ. Khi ESD10 FAIL, thông điệp giờ chỉ thẳng tới nút này (2 test, 2 đột biến đều đỏ). Sau khi nhập: `python run.py notify-test`, và bác sĩ phải thấy thư thử tới nơi (đó là bằng chứng UAT). |
| 3 | Merge PR canary | ✅ **Xong** | drluanbv175/medical-ebm-automation#16 đã merge (`bb88c7e`). |
| 4 | Bộ vàng K1–K4 | 🖥👤 Chờ Mac + nhãn bác sĩ | Cần `EBM-Dashboards/`. Trên Mac: `python3 tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang`, rồi bác sĩ điền `nhan_bac_si` cho 20 mục. |
| 5 | Chạy lại trọn bộ chốt trên Mac | 🖥 Chờ Mac | `python3 tools/chot_hoi_quy_bai_hoc.py` · `python3 tools/audit_ebm_system.py` · `python3 tools/kiem_do_tuoi_chung_cu.py` |
| 6 | Khoá Ed25519 | 👤 Chỉ bác sĩ bấm | Nút `Phat Khoa Ed25519.command` ở gốc repo. Máy không được sinh hay chạm khoá riêng. |
| 7–8 | C1a: 3 quyết định treo → G3 → hồ sơ G2 | 👤 Thẩm quyền chủ nhiệm/IRB | Theo dõi bằng `python3 tools/study_readiness.py --study hai-long-benh-nhan-C1a-BVQY175`. |
| 9 | Cục Quản lý Dược | 👤 Chờ bác sĩ mở từ mạng VN | Hai URL ở §6. Tải được thì báo lại, máy viết connector theo khuôn `kcb_vn_lane()`. |
| 10 | Epistemonikos | 👤 Chờ bác sĩ gửi thư | Thư nháp ở `medical-ebm-automation/docs/xin-cap-quyen-nguon-chung-cu.md`. |
| 11 | BTS toàn văn | ✅ **Xong — kiểm sống** | 2/2 hướng dẫn tải được qua connector thật: nốt phổi (64 trang, 358.145 ký tự) và giãn phế quản người lớn (80 trang, 471.472 ký tự). SRC-045 chuyển sang `active`. |
| 12 | ERS/ASCO/ESMO | ⛔ **Bị chặn bởi cài đặt mạng Cloud** | Proxy và WebFetch đều trả `EGRESS_BLOCKED` cho `www.ersnet.org`, `erj.ersjournals.com`, `www.asco.org`, `ascopubs.org`, `www.esmo.org`, `www.annalsofoncology.org`. Đây là cài đặt mạng của môi trường, không phải trang web từ chối. Muốn làm: bác sĩ thêm 6 host vào Network access của môi trường Cloud (menu môi trường → Edit), hoặc chạy khảo sát trên Mac. |

**Gộp mục 1 + 4 + 5 vào MỘT nút:** `Chay Viec Mac.command` ở gốc thư mục OneDrive «Claude AI».
Nút chạy theo thứ tự: an toàn đồng bộ (🔴 thì dừng) → giám sát tuần → cổng triển khai `--online` → chốt bài học →
kiểm toàn hệ → độ tươi → ứng viên bộ vàng K1–K4 → «hệ còn gì để làm». Nhật ký ghi ở `~/.ebm-logs/viec-mac-*.log`.
Nút không commit, không ký, không chạm khoá. Cần merge PR drluanbv175/EBM-drluanbv175#40 và để OneDrive đồng bộ trước.

## 7. Cách tái lập các số đo

```bash
# repo gốc
python3 tools/tu_de_xuat_viec.py
python3 tools/kiem_nguon_that.py
python3 tools/verify_controlled_research_automation.py
python3 tools/chot_hoi_quy_bai_hoc.py
python3 tools/verify_clinical_evidence_update_pipeline.py
python3 tools/kiem_safety_net.py
# repo y khoa
python3 tools/study_readiness.py --study hai-long-benh-nhan-C1a-BVQY175
python3 tools/kiem_chi_tiet_he_nghien_cuu.py --study hai-long-benh-nhan-C1a-BVQY175   # ghi đè KIEM_CHI_TIET_report.* — git checkout sau khi đo
python3 tools/verify_evidence_surveillance_deployment.py [--online]
bash scripts/run_offline_ci.sh
```

*Báo cáo chỉ ĐO và ĐỀ XUẤT; không ký cổng, không đổi `decision`/`gradeLevel`, không thay IRB/PI/thống kê viên/phản biện. Cần bác sĩ kiểm chứng.*
