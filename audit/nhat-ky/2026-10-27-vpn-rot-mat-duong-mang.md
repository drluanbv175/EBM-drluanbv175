# 27/10/2026 — Kaspersky VPN rớt ⇒ Mac mini mất đường ra Internet 1 giờ 50 phút tới khi khởi động lại (BH171)

**Bối cảnh.** Bác sĩ hỏi «sao mạng hay bị gián đoạn». Đo 27/10/2026 ~18:50 trên Mac mini M4 (Mac16,10), ở nhà, Wi-Fi 2,4 GHz,
Kaspersky VPN bật (mặc định của hệ vì NCBI gắn cờ IP đi thẳng).

**Số đo (ảnh chụp 27/10, không trích lại làm hiện trạng):**
- 15:28 VPN `reasserting` → `connected` → `disconnected, last stop reason Plugin initiated`. Từ đó log `com.apple.network` ghi
  `unsatisfied (No network route)` ~930–1.000 dòng/phút (15:00–15:10: 0 dòng; 16:30–16:40: 2.221 dòng; sau khởi động lại: 0)
  ⇒ mất mạng ≈ 1 giờ 50 phút, hết khi bác sĩ khởi động lại 17:18. 18:37–18:39 VPN chập chờn 3 vòng (reasserting 19 giây mỗi vòng)
  ⇒ khởi động lại 18:46. Hôm đó khởi động lại 3 lần (17:18 · 18:20 · 18:46).
- Wi-Fi KHÔNG rớt giữa các lần khởi động (chỉ có join lúc bật máy); ping router 60 giây 0% mất, ~5 ms.
- Máy chủ VPN lúc đầu xa: chặng đầu trong đường hầm ~256 ms, DNS qua VPN 242–380 ms. Sau khi ngắt/nối lại 19:10 Kaspersky đổi máy
  chủ: chặng đầu 80–160 ms, DNS ~96 ms; `do_mang_nguon.py` 27/28 nguồn tới được (chỉ BJGP RSS `cloudflare-chan`).
- `scutil --nc stop` ngắt được; `scutil --nc start` lần 1 (19:08) bị app Kaspersky dừng lại («Signature check failed» → «Plugin
  failed»), lần 2 (19:10) nối được ⇒ bật VPN bằng dòng lệnh LÚC ĐƯỢC LÚC KHÔNG.

**Nguyên nhân.** Không có gì canh đường ra Internet; khi VPN rớt, máy ở trạng thái không có tuyến cho tới khi đường hầm được dựng
lại, và cách chữa duy nhất bác sĩ biết được là khởi động lại máy.

**Cách vá.** `tools/canh_mang_vpn.py`: agent launchd mỗi phút (`--chay-nen`) phân loại ON / VPN_TAT / VPN_DANG_NOI / MAT_MANG /
KHONG_DO; sự cố tính khi ≥ 2 mẫu xấu liên tiếp; MẤT MẠNG ⇒ thông báo macOS ngay (nhắc lại mỗi 15 phút) + tự nối lại VPN ≤ 2 lần
cách ≥ 10 phút (VPN tắt ⇒ bật; VPN «đang nối» mà mất mạng ≥ 3 mẫu ⇒ ngắt rồi bật); VPN tắt mà vẫn có mạng CHỈ nhắc (sau 5 phút,
lặp mỗi giờ); `--tam-dung` khi cố ý tắt VPN. Hook SessionStart `--doc --im-khi-on --do-nguon-nen`: báo mất mạng 24 giờ qua, nhắc
cài agent, máy chủ VPN đổi ⇒ chạy lại `do_mang_nguon.py` ở nền và báo nguồn bị chặn ở phiên sau. State + bản chạy nền ở
`~/.ebm-canh-mang/` (NGOÀI OneDrive: agent ghi mỗi phút). Cài agent là việc bác sĩ: `--cai-launchd --ap-dung`.

**Kiểm hồi quy.** `tools/test_canh_mang_vpn.py` (47 test, có test phát lại đúng ca 27/10); 9/9 đột biến bắt được (chớp tắt thành
sự cố · mất mạng mà «Connected» thành xanh · bỏ trần nối lại · tự bật khi VPN tắt có mạng · bỏ tạm dừng · state về trong repo ·
không đo được im như xanh · bỏ nhắc lặp · báo kết quả đo nguồn mỗi phiên); chốt BH171 trong `tools/chot_hoi_quy_bai_hoc.py`.

**Còn lại cho bác sĩ.** Cắm dây LAN cho Mac mini (cổng Ethernet bỏ trống) hoặc chuyển Wi-Fi 5 GHz; router WPA2-AES, kênh 1/6/11;
cố định vị trí máy chủ VPN gần trong app Kaspersky.
