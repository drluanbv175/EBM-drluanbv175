# HƯỚNG DẪN PHÁT KHOÁ Ed25519 CHO CỔNG KÝ DUYỆT

> Viết 02/09/2026. Mọi bước dưới đây đã đối chiếu với mã đang chạy
> (`tools/gate_contract.py`, `medical-ebm-automation/tools/setup_gate_approval_key.py`,
> nút `Phat Khoa Ed25519.command`) — không phải mô tả theo trí nhớ.
>
> **★ CHỈ BÁC SĨ TỰ LÀM. KHÔNG nhờ agent (Claude Code/Codex) chạy hộ bất kỳ bước nào có
> chữ «phát khoá».** Đây không phải thủ tục hành chính: khoá RIÊNG mà sinh ra trong tầm với
> của agent thì chữ ký hết là bằng chứng độc lập, và toàn bộ mục đích của Ed25519 mất sạch.

---

## 1. Vì sao cần — vấn đề Ed25519 giải, HMAC không giải

Hệ hiện ký cổng bằng **HMAC — mật mã ĐỐI XỨNG**: máy xác minh buộc phải giữ ĐÚNG khoá đã ký.
Hệ quả thực dụng, đã ghi ở `CLAUDE.md`: **cấu hình duy nhất triển khai được lại chính là cấu
hình một người giữ đủ mọi khoá và ký được mọi vai.** Nên hôm nay:

> Một chữ ký G8 hợp lệ chứng minh **“một người truy cập được khoá đã bấm nút”**.
> Nó **KHÔNG** chứng minh “một người KHÁC chủ nhiệm đã đọc bản thảo”.

**Ed25519 là mật mã BẤT ĐỐI XỨNG** và đảo đúng điều đó:

| | HMAC (`v4:`) | Ed25519 (`ed1:`) |
|---|---|---|
| Máy xác minh cần gì | **khoá bí mật** (chính khoá đã ký) | **chỉ khoá CÔNG** |
| Ai ký được | bất kỳ ai có khoá | **chỉ người giữ khoá riêng** |
| Chứng minh được tính độc lập | ❌ | ✅ |
| Khoá công có commit vào repo được không | — | ✅ an toàn, nên commit |

`sign_approval()` **tự ưu tiên `ed1`** khi thấy khoá riêng của nhóm vai đó trên máy
(`gate_contract.py`, nhánh `if group and ed25519_private_key_available(group)`), và tự lùi về
HMAC khi không có. **Không có bước bật/tắt nào** — phát khoá xong là nó dùng ngay.

---

## 2. Phát khoá cho vai nào — và ai phải giữ

Bảng vai bắt buộc theo cổng (`gate_contract._GATE_REQUIRED_STAKEHOLDERS`, đọc từ mã):

| Cổng | Vai bắt buộc | Ai nên giữ khoá riêng |
|---|---|---|
| **G2** đạo đức | `IRB` | thư ký/đại diện Hội đồng Đạo đức |
| **G4** khoá SAP | `STATISTICIAN` hoặc `PI` | thống kê viên |
| **G5** khoá dữ liệu | `DATA_MANAGER` hoặc `PI` | người quản lý dữ liệu |
| **G8** bình duyệt độc lập | `INDEPENDENT_PEER_REVIEWER` | **người phản biện — KHÔNG phải bác sĩ** |
| **G9** liêm chính tác giả | `PI` | chủ nhiệm đề tài |
| **G10** khoá gói phát hành | `PI` | chủ nhiệm đề tài |

### ✅ Trạng thái THẬT — 4/5 vai ĐÃ CÓ KHOÁ (đo lại 03/09/2026)

| Vai | Khoá công trong repo | Còn phải làm |
|---|---|---|
| `IRB` | ✅ đã phát 01/09 | — |
| `INDEPENDENT_PEER_REVIEWER` | ✅ đã phát 01/09 | — |
| `STATISTICIAN` | ✅ đã phát 01/09 | — |
| `PI` | ✅ đã phát 01/09 | — |
| **`DATA_MANAGER`** | ❌ **chưa có** | **việc duy nhất còn lại** |

Bốn khoá trên nằm ở `config/gate_ed25519_pubkeys/*.pub` trên nhánh `master`, commit `4eeb0c8`
(01/09/2026). **Việc còn lại đúng MỘT vai: `DATA_MANAGER` — cổng G5 khoá dữ liệu thật.**

🔍 **Vì sao đúng vai đó bị bỏ sót — không phải bác sĩ quên.** `setup_gate_approval_key.py` khai
`_ROLE_GROUPS = ("IRB", "STATISTICIAN", "INDEPENDENT_PEER_REVIEWER", "PI")`, và `--role` dùng
`choices=_ROLE_GROUPS`, nên `--role DATA_MANAGER` **bị argparse từ chối thẳng** — trong khi
`_GATE_REQUIRED_STAKEHOLDERS["G5"] = ("DATA_MANAGER", "PI")` vẫn đòi đúng vai đó. Tức bác sĩ đã
phát khoá cho **mọi vai công cụ chịu nhận**, và G5 là cổng cứng duy nhất không thể có khoá
Ed25519 — im lặng. Lỗi đã vá 02/09; nay `--role DATA_MANAGER` chạy được.

> ⚠️ Phát khoá `PI` cho chính bác sĩ **không tăng tính độc lập** — vẫn là một người ký cho
> chính mình, chỉ đổi thuật toán. Nó vẫn đáng làm (chống giả mạo bởi người khác), nhưng đừng
> nhầm nó là “đã có bình duyệt độc lập”.

---

## 3. Cách phát — hai đường, chọn một

### Đường A — bấm nút (khuyên dùng)

Bấm đúp **`Phat Khoa Ed25519.command`** ở thư mục gốc `Claude AI/`, rồi chọn số của vai.
Nút tự chọn `~/.ebm-venv/bin/python` (nơi có sẵn thư viện `cryptography`).

### Đường B — dòng lệnh

```bash
cd ~/OneDrive/…/Claude\ AI/medical-ebm-automation
~/.ebm-venv/bin/python tools/setup_gate_approval_key.py --role INDEPENDENT_PEER_REVIEWER --ed25519
```

Cả hai đường tạo ra **đúng hai file**:

| File | Nội dung | Xử lý |
|---|---|---|
| `~/.ebm-secrets/gate_ed25519_<VAI>.key` | khoá **RIÊNG** (PEM PKCS8) | **BÍ MẬT** — xem §4 |
| `medical-ebm-automation/config/gate_ed25519_pubkeys/<VAI>.pub` | khoá **CÔNG** | **commit vào git** |

Công cụ **từ chối ghi đè** nếu khoá đã tồn tại (in `✋ Đã có khóa…`) — muốn đổi khoá thì phải
tự xoá file cũ trước, có chủ ý.

---

## 4. Bước quan trọng nhất — và là bước duy nhất máy không làm thay được

Sau khi phát khoá cho một vai **KHÔNG phải bác sĩ** (vd `INDEPENDENT_PEER_REVIEWER`):

1. **Chuyển** `~/.ebm-secrets/gate_ed25519_INDEPENDENT_PEER_REVIEWER.key` sang máy (hoặc USB)
   của **chính người phản biện** — qua kênh riêng, không gửi kèm trong email chung.
2. **XOÁ khoá riêng đó khỏi máy bác sĩ.**
3. Từ đó, chỉ người phản biện ký được G8; bác sĩ **không** ký thay được nữa.

> **Nếu bỏ bước 2, toàn bộ việc này vô nghĩa.** Khoá riêng còn nằm trên máy bác sĩ thì bác sĩ
> vẫn ký được vai phản biện — y hệt HMAC, chỉ khác thuật toán. Chính bước xoá này mới biến
> chữ ký thành bằng chứng.

Khoá **CÔNG** thì ngược lại — càng công khai càng tốt: commit nó vào repo để mọi máy xác minh
được mà không cần giữ bí mật nào.

```bash
cd medical-ebm-automation
git add config/gate_ed25519_pubkeys/
git commit -m "chore(gate): phát khoá công Ed25519 cho vai INDEPENDENT_PEER_REVIEWER"
```

🔴 **TUYỆT ĐỐI KHÔNG commit file `.key`.** Nó nằm ở `~/.ebm-secrets/` (ngoài OneDrive, ngoài
repo) nên bình thường không có đường lọt vào git — nhưng nếu bác sĩ chép nó vào repo để “cho
tiện” thì nó sẽ bị commit và **mọi bảo đảm mất ngay lập tức, không khôi phục được bằng cách
xoá commit sau**; lúc đó phải phát khoá MỚI cho vai đó.

---

## 5. Kiểm lại đã ăn chưa

```bash
cd medical-ebm-automation
ls config/gate_ed25519_pubkeys/                 # phải thấy <VAI>.pub
```

> ⛔ **ĐÍNH CHÍNH 03/09/2026 — câu ở đây trong bản đầu là SAI.** Bản viết 02/09 ghi *"chưa có
> khoá công nào được phát"*. Sự thật: **4 khoá đã được phát từ 01/09** (`IRB`,
> `INDEPENDENT_PEER_REVIEWER`, `STATISTICIAN`, `PI`) — xem bảng trạng thái ở mục 2.
>
> **Vì sao tôi viết sai:** cây `medical-ebm-automation` trong phiên cloud hôm đó **lạc hậu 55
> commit** so với `origin/master` và là clone **nông**, nên `ls` trên cây đó thấy thư mục rỗng
> là thật — nhưng *"thư mục rỗng ở đây"* không phải *"chưa phát khoá nào"*. Đây đúng là **BH93**
> (cây lạc hậu ⇒ **âm tính giả**), và chốt `kiem_cay_lam_viec.py` **đã báo 🔴 «LẠC HẬU 55 commit»
> ngay phiên đó** — tôi đọc cảnh báo, báo lại cho bác sĩ, rồi vẫn viết tài liệu dựa trên cây cũ.
> *Bài học: cảnh báo lạc hậu phải chặn việc RÚT KẾT LUẬN, không chỉ để báo cáo.*
> Trước khi khẳng định «chưa có X», chạy `git fetch origin master` rồi
> `git ls-tree -r origin/master --name-only | grep <đường-dẫn>`.

Sau lần ký thật kế tiếp, mở `exports/<mã-đề-tài>/approval_ledger.json` và xem trường chữ ký:

- bắt đầu bằng **`ed1:`** → đã dùng Ed25519 ✅ (luôn kèm phạm vi `role`, không có `shared`)
- vẫn **`v4:`** → còn đi đường HMAC. Đọc tiếp phạm vi ngay sau đó: `v4:role:` là ký bằng khoá
  riêng theo vai, `v4:shared:` là ký bằng khoá CHUNG của máy — mức bảo đảm thấp nhất.
  Thấy `v4:` sau khi đã chuyển khoá riêng đi là ĐÚNG THIẾT KẾ: nó có nghĩa máy này không còn
  ký thay vai đó được nữa, và **người giữ vai phải là người chạy lệnh ký**.

> ⚠️ Chỉ hai tiền tố `v4:` và `ed1:` được `verify_approval_signature()` chấp nhận. Bản ghi
> mang tiền tố khác (`v2:`/`v3:` của các bản cũ) **không xác minh được** — nếu gặp, đừng sửa
> tay, hãy ký lại trên máy hiện tại.

Xác minh không cần bí mật nào:

```bash
~/.ebm-venv/bin/python tools/verify_exports_integrity.py
```

---

## 6. Ba điều Ed25519 **KHÔNG** làm (đừng hiểu quá)

1. **Không chứng minh người đó đã ĐỌC.** Nó chứng minh **ai** ký, không chứng minh **họ có
   thẩm định thật hay không**. Chất lượng bình duyệt vẫn do `g8_quality_gate.py` và bản nhận
   xét `G8_PEER_REVIEW_REPORT_<study>.md` gánh.
2. **Không sửa được chữ ký cũ.** Các bản ghi `v4:` đã có vẫn là HMAC; Ed25519 chỉ áp cho lần
   ký từ nay về sau.
3. **Không chạm tới Cổng A/B lâm sàng.** Hai cổng đó **không có** lớp mật mã tương đương —
   lớp bảo vệ thật vẫn là bác sĩ tự đọc gói quyết định trước khi áp dụng.

---

## 7. Ghi chú vá kèm (02/09/2026)

**(b) Docstring lệch trong `gate_contract.sign_approval()`** ghi chuỗi trả về là `"v2:…"`
trong khi `_SIGNATURE_SCHEME` đã là `"v4"` và bộ xác minh CHỈ nhận `{"v4","ed1"}`. Ai đọc theo
bản cũ sẽ đi tìm nhầm tiền tố khi soi `approval_ledger.json` — đã sửa.

**(a) `DATA_MANAGER` không phát khoá được**

`DATA_MANAGER` là stakeholder bắt buộc của **G5** nhưng **vắng** khỏi danh sách vai phát được
khoá (`_ROLE_GROUPS`) — nên trước hôm nay không đường nào phát khoá Ed25519 cho người quản lý
dữ liệu. Hệ quả không phải là chặn (G5 vẫn ký được bằng `PI`) mà tinh vi hơn: **vai đó vĩnh
viễn chỉ ký được bằng HMAC**, trong khi chính họ mới là người chứng thực dữ liệu đã khoá. Đã
thêm vào cả `_ROLE_GROUPS` lẫn menu của nút.

**Cần bác sĩ kiểm chứng.**
