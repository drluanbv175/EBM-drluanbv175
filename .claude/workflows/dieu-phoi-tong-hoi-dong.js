export const meta = {
  name: 'dieu-phoi-tong-hoi-dong',
  description: 'Điều phối tổng: họp hội đồng LẦN LƯỢT các cổng được chọn của một đề tài (đánh giá chéo + tranh biện), dừng khi cần người có thẩm quyền',
  whenToUse: 'Bác sĩ đồng ý họp hội đồng cho NHIỀU cổng một lượt. args: {study, gates: ["G2","G4",…], max_agent_tong?, max_vong?, chay_thu?}. Chi phí ≈ số cổng × 1–3 triệu token — hỏi trước.',
  phases: [{ title: 'Hội đồng từng cổng', detail: 'gọi workflow hoi-dong-cong cho từng cổng theo thứ tự G0→G10' }],
}

const CONG = ['G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10']
const a = args || {}
if (!a.study) throw new Error('args.study bắt buộc')
const gates = (Array.isArray(a.gates) && a.gates.length ? a.gates : ['G2', 'G4', 'G5', 'G8', 'G9', 'G10'])
  .filter(g => CONG.includes(g)).sort((x, y) => CONG.indexOf(x) - CONG.indexOf(y))
const MAX_TONG = Math.max(Number(a.max_agent_tong || 48), 8)

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
  log(`Họp hội đồng ${g} (còn ${conLai} agent trong trần)`)
  let r = null
  try {
    r = await workflow('hoi-dong-cong', { study: a.study, gate: g, max_vong: a.max_vong || 1, max_agent: Math.min(conLai, 16) })
  } catch (e) {
    ket.push({ gate: g, loi: String(e) })
    break
  }
  daDung += (r && r.so_agent) || 0
  ket.push(r || { gate: g, loi: 'không có kết quả' })
  const canNguoi = r && (r.tranh_bien || []).some(t => t.ket_qua === 'chuyen_bac_si')
  if (!r || r.loi || canNguoi) {
    log(`Dừng sau ${g}: ${canNguoi ? 'có vấn đề CHUYỂN BÁC SĨ — các cổng sau phụ thuộc quyết định này' : 'hội đồng không hoàn tất'}`)
    break
  }
}
return { study: a.study, da_hop: ket, so_agent: daDung,
  luu_y: 'TƯ VẤN — không mở, không chặn cổng. Tóm tắt: python3 tools/hoi_dong_cong.py tom-tat --study ' + a.study +
    ' (trong medical-ebm-automation/). Cần bác sĩ kiểm chứng.' }
