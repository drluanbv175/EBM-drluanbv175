# Hợp đồng điều phối rút gọn

Đọc tệp này khi yêu cầu thuộc EBM, có nhiều plugin cùng nhận làm được, hoặc có nguy cơ vượt cổng.

## Một owner, nhiều worker

- `dieu-phoi-lam-sang` sở hữu ca ngoại trú.
- `dieu-phoi-nghien-cuu` sở hữu vòng đời G0–G10.
- Agent chuyên trách sở hữu việc lẻ đúng miền của nó.
- Plugin chỉ là worker theo allowlist và giai đoạn; tên plugin do người dùng gọi không đổi owner.

## Vòng điều phối

`route → owner → worker hẹp nhất → kiểm khả dụng → thực hiện → hợp nhất → guardrail →
retry tối đa 3 → release hoặc dừng cổng`.

## Fail-closed

- Capability lạ hoặc worker ngoài allowlist: `BLOCKED`.
- Worker thiếu trong runtime: `LOCAL_FALLBACK`; không tuyên bố đã dùng plugin.
- Thiếu provenance: kết quả chỉ là nháp và không được mở cổng.
- Mâu thuẫn chưa giải được: giữ `PARTIAL`, nêu các nhánh và chuyển người duyệt.
- PII, nguy cơ an toàn, phê duyệt/cổng người: dừng ngay, không tự sửa bằng vòng lặp.

## Cổng người

- Lâm sàng: A và B.
- Nghiên cứu: G2, G4, G5, G8, G9 và G10.
- Plugin không được ghi approval ledger, seal, `study_meta.json` hoặc nâng thẻ thành `apply`.

Nguồn canonical trong workspace: `.claude/agents/_PLUGIN-ROUTING-CONTRACT.md` và
`tools/orchestrator/plugin_ownership_registry.json`.
