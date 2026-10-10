export const meta = {
  name: 'dieu-phoi-tong-hoi-dong',
  description: 'Điều phối tổng: họp hội đồng LẦN LƯỢT các cổng được chọn của một đề tài (đánh giá chéo + tranh biện), dừng khi cần người có thẩm quyền',
  whenToUse: 'Bác sĩ đồng ý họp hội đồng cho NHIỀU cổng một lượt. args: {study, gates: ["G2","G4",…], ho_so_theo_cong?: {G0: <ho-so --json>, …}, ca_khi_cong_truoc_chua_dat?, max_agent_tong?, max_vong?, chay_thu?}. Chi phí ≈ số cổng × ~6 triệu token (đo 07/10/2026) — hỏi trước.',
  phases: [{ title: 'Hội đồng từng cổng', detail: 'gọi workflow hoi-dong-cong cho từng cổng theo thứ tự G0→G10' }],
}

const CONG = ['G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10']
const a = args || {}
if (!a.study) throw new Error('args.study bắt buộc')
const gates = (Array.isArray(a.gates) && a.gates.length ? a.gates : ['G2', 'G4', 'G5', 'G8', 'G9', 'G10'])
  .filter(g => CONG.includes(g)).sort((x, y) => CONG.indexOf(x) - CONG.indexOf(y))
const MAX_TONG = Math.max(Number(a.max_agent_tong || 48), 8)
// 10/10/2026 — hồ sơ do máy lập theo cổng (`hoi_dong_cong.py ho-so --json`): cổng không cần họp ⇒ 0 agent; cổng mà
// cổng tiền đề chưa đạt (khuyen_nghi nen_cho_cong_truoc) ⇒ DỪNG trước nó (đầu ra còn đổi, biên bản sẽ cũ) trừ khi
// bác sĩ truyền ca_khi_cong_truoc_chua_dat: true.
const HO_SO = a.ho_so_theo_cong || {}

if (a.chay_thu) {
  return { chay_thu: true, study: a.study, gates, max_agent_tong: MAX_TONG,
    ghi_chu: 'Mỗi cổng gọi workflow hoi-dong-cong; dừng ở cổng đầu tiên có CHUYỂN BÁC SĨ hoặc không lập được hồ sơ.' }
}

phase('Hội đồng từng cổng')
const ket = []
let daDung = 0
for (const g of gates) {
  const conLai = MAX_TONG - daDung
  if (conLai < 4) {
    log(`⛔ Hết trần ${MAX_TONG} agent — DỪNG trước ${g} (các cổng còn lại chưa họp: ${gates.slice(gates.indexOf(g)).join(', ')})`)
    ket.push({ gate: g, bo_qua: 'hết trần agent' })
    break
  }
  const hs = HO_SO[g]
  if (hs && hs.can_hop === false) {
    log(`${g}: hồ sơ máy — không cần họp (0 agent)`)
    ket.push({ gate: g, khong_can_hop: true, so_agent: 0 })
    if ((hs.cho_bac_si || []).length) { log(`Dừng sau ${g}: ${hs.cho_bac_si.join(', ')} đang chờ bác sĩ quyết`); break }
    continue
  }
  if (hs && hs.khuyen_nghi === 'nen_cho_cong_truoc' && !a.ca_khi_cong_truoc_chua_dat) {
    log(`⏸ Dừng trước ${g}: cổng tiền đề chưa đạt (${(hs.cong_truoc_chua_dat || []).map(c => c.gate).join(', ')}) — họp lúc này dễ phải họp lại`)
    ket.push({ gate: g, hoan: 'nen_cho_cong_truoc', cong_truoc_chua_dat: hs.cong_truoc_chua_dat || [] })
    break
  }
  log(`Họp hội đồng ${g} (còn ${conLai} agent trong trần)`)
  let r = null
  try {
    r = await workflow('hoi-dong-cong', { study: a.study, gate: g, max_vong: a.max_vong || 1, max_agent: Math.min(conLai, 16),
      ...(hs ? { ho_so: hs } : {}) })
  } catch (e) {
    ket.push({ gate: g, loi: String(e) })
    break
  }
  daDung += (r && r.so_agent) || 0
  ket.push(r || { gate: g, loi: 'không có kết quả' })
  const canNguoi = (r && (r.tranh_bien || []).some(t => t.ket_qua === 'chuyen_bac_si')) || !!(hs && (hs.cho_bac_si || []).length)
  if (!r || r.loi || canNguoi) {
    log(`Dừng sau ${g}: ${canNguoi ? 'có vấn đề CHUYỂN BÁC SĨ — các cổng sau phụ thuộc quyết định này' : 'hội đồng không hoàn tất'}`)
    break
  }
}
return { study: a.study, da_hop: ket, so_agent: daDung,
  luu_y: 'TƯ VẤN — không mở, không chặn cổng. Tóm tắt: python3 tools/hoi_dong_cong.py tom-tat --study ' + a.study +
    ' (trong medical-ebm-automation/). Cần bác sĩ kiểm chứng.' }
