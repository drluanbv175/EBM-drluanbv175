# 10/10/2026 — Họp hội đồng cổng tốn token vì agent làm phần việc máy làm được và chấm lại đầu ra không đổi

Bác sĩ: «Việc họp hãy bàn sau vì rất tốn Token, hãy hoàn thiện theo cách thông minh nhất» (5 lịch họp đêm 10→11/10 đã
tắt, đổi tiêu đề «[TẠM DỪNG — bàn sau]»).

## Đo (10/10, hồ sơ C1a thật, chỉ đọc)

- Số đo gốc: 07/10/2026 họp thí điểm G0 của C1a dùng 16 agent ≈ 6,1 triệu token (~380 nghìn/agent).
- Workflow `hoi-dong-cong.js` cũ tốn ở ba chỗ máy làm thay được:
  - (1) Luôn mở một agent điều phối chỉ để LẬP HỒ SƠ: chấm sống, liệt kê tệp, chọn người chấm.
  - (2) CHẤM LẠI mọi đầu ra, kể cả đầu ra đã có biên bản còn hiệu lực (biên bản gắn SHA-256, tài liệu không đổi thì
    chấm lại cho cùng kết quả) và đầu ra bị trả về sửa mà chưa sửa.
  - (3) Mỗi đầu ra một `giam-khao-cong`, dù doctrine §5 đã nói «gom MỘT giám khảo cho nhiều đầu ra cùng cổng khi
    được».
- Workflow cũ còn tranh biện DP ở cổng chưa có đầu ra (G5–G9 của C1a) và không cảnh báo khi họp một cổng mà cổng tiền
  đề chưa chốt. Khi cổng trước chốt, đầu ra của cổng này sẽ đổi, biên bản thành CŨ và phải họp lại.
- Ước tính theo cách cũ cho cả 11 cổng của C1a: ≈ 86 agent ≈ 32,7 triệu token.

## Vá

- Repo y khoa `tools/hoi_dong_cong.py` có hai lệnh mới, cả hai 0 agent và chỉ đọc:
  - `ho-so --study --gate [--dp …] [--tat-ca] [--json]`: máy lập hồ sơ. Mỗi nhiệm vụ được xếp vào đúng một tình trạng:
    `can_cham` · `khong_ap_dung` · `chua_xac_dinh` · `thieu_dau_ra` · `da_qua` · `cho_sua` · `bat_dong`.
    - Bất đồng chưa tranh biện được đưa vào `bat_dong_treo`, kèm id biên bản thật.
    - DP đã có tranh biện còn hiệu lực thì không tranh biện lại.
    - Cổng còn nhiệm vụ thiếu đầu ra hoặc chưa xác định áp dụng thì CHƯA tranh biện DP.
    - Cổng có tiền đề (ô `^…` của `PHAN_CONG`; `*` = mọi cổng trước) chưa PASS sống thì khuyến nghị
      `nen_cho_cong_truoc`.
  - `uoc-tinh --study --gate GN|ALL [--max-vong] [--gom-giam-khao] [--json]`: tính số agent + token tối thiểu–tối đa
    và so với cách cũ.
- Repo gốc `.claude/workflows/hoi-dong-cong.js`:
  - Nhận `args.ho_so`, kiểm schema, đề tài và cổng. Không còn gì cần họp ⇒ 0 agent.
  - Agent điều phối chỉ soạn luận điểm cho DP cần tranh biện.
  - Chỉ chấm nhiệm vụ `can_cham`. Bất đồng cũ được tranh biện với `nguon_bat_dong` = id thật.
  - Gom giám khảo ≤ 4 đầu ra mỗi lượt (`args.gom_giam_khao`, 1 = như cũ). Đầu ra thiếu bản chấm giám khảo thì không
    ghi biên bản, và việc thiếu được ghi vào kết quả.
  - Không truyền `ho_so` thì chạy như cũ.
- Repo gốc `dieu-phoi-tong-hoi-dong.js` nhận `args.ho_so_theo_cong`:
  - Cổng không cần họp ⇒ 0 agent.
  - Gặp cổng `nen_cho_cong_truoc` thì dừng trước cổng đó, trừ khi bác sĩ truyền `ca_khi_cong_truoc_chua_dat: true`.
  - DP đang chờ bác sĩ thì dừng sau cổng đó.
- Doctrine `_HOI-DONG-CONG.md` §5 (bản cặp y hệt) được sửa và CLAUDE.md thêm một dòng. Không đổi rubric, luật biên bản,
  vai hay mức độc lập.

## Kiểm

- Ước tính mới trên C1a:
  - HỌP ĐƯỢC NGAY: chỉ G0, 10–19 agent ≈ 3,8–7,2 triệu token. Cách cũ cho G0 ≥ 14 agent; G0-T2 bỏ qua vì bất đồng
    đã tranh biện và còn hiệu lực.
  - NÊN CHỜ CỔNG TRƯỚC: G1–G4, G10, tổng 40–70 agent.
  - KHÔNG CẦN HỌP: G5–G9.
- `tests/test_hoi_dong_tiet_kiem_20261010.py` có 23 ca. Đột biến bị bắt 17/17 (có lượt nền xanh), mã nguồn được phục
  hồi y hệt từng byte.
- Workflow được chạy bằng giàn agent GIẢ trên node qua 6 kịch bản:
  - Hồ sơ máy: 11 lời gọi agent. Kịch bản không gom đo được 13. Cách cũ cho cùng hồ sơ là 14 — con số này tính
    theo công thức, không đo.
  - Bất đồng mới.
  - Không cần họp: 0 agent.
  - Không gom giám khảo.
  - Sai cổng: bị chặn.
  - Chế độ cũ.
- Điều phối tổng được chạy qua 3 kịch bản: dừng trước cổng nên chờ · dừng khi chờ bác sĩ · ép họp.
- Chưa làm (đề xuất, chờ bác sĩ quyết): gom phản biện/trọng tài nhiều DP của cùng cổng vào một lượt. Việc này giảm
  thêm agent nhưng đổi mức độc lập giữa các DP.
