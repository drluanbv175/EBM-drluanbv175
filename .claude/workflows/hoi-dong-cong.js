export const meta = {
  name: 'hoi-dong-cong',
  description: 'Hội đồng MỘT cổng G0–G10: đánh giá chéo đầu ra các agent + tranh biện điểm quyết định trước kết luận (tư vấn, không mở cổng)',
  whenToUse: 'Bác sĩ đồng ý triệu tập hội đồng cho MỘT cổng của một đề tài sau khi các nhiệm vụ của cổng đã có đầu ra. args: {study, gate, ho_so?, gom_giam_khao?, dp?, max_vong?, max_agent?, chay_thu?, trong_tai?: "subagent"|"codex"}. Tốn ≈6 triệu token cho một cổng 4 nhiệm vụ (đo 07/10/2026) — hỏi trước; ước tính trước bằng `hoi_dong_cong.py uoc-tinh`, họp với ho_so = `hoi_dong_cong.py ho-so --json` (máy lập hồ sơ, chỉ họp phần chưa có biên bản còn hiệu lực).',
  phases: [
    { title: 'Hồ sơ cổng', detail: 'điều phối cổng chấm sống (chỉ đọc), liệt kê đầu ra có thật + kết luận dự kiến cho từng điểm quyết định' },
    { title: 'Đánh giá chéo', detail: 'người chấm chuyên môn theo ma trận + giám khảo độc lập, rubric RQ1–RQ8' },
    { title: 'Tranh biện', detail: 'phản biện ↔ đề xuất (trần vòng), trọng tài phán từng phản đối' },
    { title: 'Biên bản', detail: 'điều phối cổng ghi biên bản qua tools/hoi_dong_cong.py (công cụ kiểm luật, vi phạm thì không ghi)' },
  ],
}

// ── Tham số + trần chi phí (CLAUDE.md §0.6: không mở agent khi chưa hỏi; không cắt im lặng) ─────────────────────────
const CONG = ['G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10']
const a = args || {}
if (!a.study || typeof a.study !== 'string' || !/^[A-Za-z0-9._-]+$/.test(a.study)) {
  throw new Error('args.study bắt buộc (mã đề tài, chỉ chữ/số/._-)')
}
if (!CONG.includes(a.gate)) throw new Error('args.gate phải thuộc G0…G10')
const STUDY = a.study
const GATE = a.gate
const DIEU_PHOI = `dieu-phoi-${GATE.toLowerCase()}`
const MAX_VONG = Math.min(Math.max(Number(a.max_vong || 1), 1), 2)
const MAX_AGENT = Math.max(Number(a.max_agent || 16), 4)
// 07/10/2026 — trọng tài Codex (bác sĩ giao): mô hình KHÁC phán qua tools/trong_tai_codex.py (sandbox chỉ-đọc, schema
// chặt, kiểm bằng chính luật biên bản). Chế độ này GỬI trích đoạn hồ sơ cấp đầu của đề tài tới dịch vụ Codex.
if (a.trong_tai !== undefined && !['subagent', 'codex'].includes(a.trong_tai)) {
  throw new Error('args.trong_tai phải là "subagent" hoặc "codex"')
}
const CHE_DO = a.trong_tai === 'codex' ? 'codex' : 'subagent'
const TEN_TRONG_TAI = CHE_DO === 'codex' ? 'codex:trong-tai-tranh-bien' : 'trong-tai-tranh-bien'
const Y = 'medical-ebm-automation'
// 10/10/2026 — HỌP TIẾT KIỆM (bác sĩ: «việc họp rất tốn token, hãy hoàn thiện theo cách thông minh nhất»). Hồ sơ do
// MÁY lập: `python3 tools/hoi_dong_cong.py ho-so --study … --gate … --json` (0 agent) truyền qua args.ho_so ⇒ bỏ agent
// lập hồ sơ (chỉ còn agent soạn luận điểm khi có DP cần tranh biện), chỉ chấm đầu ra CHƯA có biên bản còn hiệu lực,
// chỉ tranh biện DP chưa có biên bản còn hiệu lực + bất đồng còn treo. Không truyền ho_so ⇒ lập hồ sơ bằng agent như cũ.
const HS = a.ho_so
if (HS !== undefined && !(HS && HS.schema === 'hoi_dong_cong/ho_so/v1' && HS.study === STUDY && HS.gate === GATE &&
    Array.isArray(HS.nhiem_vu) && Array.isArray(HS.dp) && Array.isArray(HS.bat_dong_treo))) {
  throw new Error('args.ho_so phải là đầu ra `hoi_dong_cong.py ho-so --json` của ĐÚNG đề tài + cổng')
}
// §5 «gom MỘT giám khảo cho nhiều đầu ra cùng cổng khi được»: một giam-khao-cong chấm ≤ GOM đầu ra (mỗi đầu ra một bản
// chấm riêng). 1 = mỗi đầu ra một giám khảo như trước. Cùng mặc định với hoi_dong_cong.GOM_GIAM_KHAO.
const GOM = Math.min(Math.max(Number(a.gom_giam_khao === undefined ? 4 : a.gom_giam_khao) || 1, 1), 8)
let soAgent = 0
const boQua = []

async function goi(prompt, opts) {
  // 07/10/2026 (lộ ở lượt họp thí điểm G0): bước GHI BIÊN BẢN cũng tính vào trần — hết suất thì kết quả cả hội đồng
  // không vào sổ. Nay GIỮ CHỖ một suất cho bước ghi: các vai khác dùng tối đa MAX_AGENT − 1.
  const tran = opts.phase === 'Biên bản' ? MAX_AGENT : MAX_AGENT - 1
  if (soAgent >= tran) {
    boQua.push(opts.label)
    log(`⛔ Chạm trần ${MAX_AGENT} agent — BỎ «${opts.label}» (ghi vào kết quả, không cắt im lặng)`)
    return null
  }
  soAgent += 1
  return agent(prompt, opts)
}

const CAN_CU = {
  type: 'array', minItems: 1,
  items: { type: 'object', required: ['loai', 'gia_tri'], properties: {
    loai: { enum: ['tep', 'tieu_chi', 'pmid', 'doi', 'lenh'] }, gia_tri: { type: 'string' }, ket_qua: { type: 'string' } } },
}
const LUAN_DIEM = { type: 'object', required: ['ma', 'noi_dung'], properties: {
  ma: { type: 'string' }, phan_doi: { type: 'string' }, noi_dung: { type: 'string' }, can_cu: CAN_CU,
  nhuong: { type: 'boolean' } } }
// 10/10/2026 — bài học HỆ THỐNG (không bắt buộc): lỗi của công cụ/agent/điều phối/doctrine/quy trình, tách khỏi lỗi
// của đầu ra đề tài, để vòng hoàn thiện sau họp sửa đúng chỗ (_HOI-DONG-CONG §3, `hoi_dong_cong.py bai-hoc`).
const BAI_HOC = { type: 'array', items: { type: 'object', required: ['pham_vi', 'doi_tuong', 'van_de', 'can_cu'], properties: {
  pham_vi: { enum: ['cong_cu', 'agent', 'dieu_phoi', 'doctrine', 'quy_trinh_hoi_dong'] }, doi_tuong: { type: 'string' },
  van_de: { type: 'string' }, de_xuat: { type: 'string' }, can_cu: CAN_CU } } }
const BAI_HOC_LOI = 'Lỗi của HỆ (công cụ/bộ chấm, tài liệu agent, điều phối, doctrine, quy trình hội đồng) — KHÔNG phải lỗi ' +
  'của đầu ra — ghi riêng ở bai_hoc_he_thong (pham_vi, doi_tuong cụ thể, van_de, de_xuat, can_cu kiểm được); không thấy ' +
  'lỗi hệ thì bỏ trống, KHÔNG bịa cho có.'
const HO_SO = { type: 'object', required: ['trang_thai_song', 'nhiem_vu', 'dp'], properties: {
  trang_thai_song: { type: 'string' },
  nhiem_vu: { type: 'array', items: { type: 'object', required: ['ma', 'tac_gia', 'tai_lieu', 'cham_chuyen_mon'],
    properties: { ma: { type: 'string' }, tac_gia: { type: 'string' }, tai_lieu: { type: 'array', items: { type: 'string' } },
      cham_chuyen_mon: { type: 'string' }, ap_dung: { type: 'boolean' }, ly_do_khong_ap_dung: { type: 'string' } } } },
  dp: { type: 'array', items: { type: 'object', required: ['ma', 'tai_lieu_xet', 'ket_luan_de_xuat', 'luan_diem'],
    properties: { ma: { type: 'string' }, tai_lieu_xet: { type: 'array', items: { type: 'string' } },
      ket_luan_de_xuat: { type: 'string' }, luan_diem: { type: 'array', minItems: 1, items: LUAN_DIEM } } } },
  ghi_chu: { type: 'string' } } }
const MUC_CHAM = { type: 'object', required: ['nguoi_cham', 'vai', 'tieu_chi', 'ket_luan'], properties: {
  nguoi_cham: { type: 'string' }, vai: { enum: ['chuyen_mon', 'giam_khao'] },
  tieu_chi: { type: 'array', minItems: 8, maxItems: 8, items: { type: 'object', required: ['ma', 'muc'], properties: {
    ma: { enum: ['RQ1', 'RQ2', 'RQ3', 'RQ4', 'RQ5', 'RQ6', 'RQ7', 'RQ8'] },
    muc: { enum: ['dat', 'can_sua', 'loi_do', 'khong_ap_dung'] }, nhan_xet: { type: 'string' },
    can_cu: { type: 'array', items: CAN_CU.items } } } },
  ket_luan: { enum: ['dat', 'dat_co_luu_y', 'tra_ve_sua'] }, bai_hoc_he_thong: BAI_HOC } }
const VONG = { type: 'object', required: ['luan_diem'], properties: { luan_diem: { type: 'array', minItems: 1, items: LUAN_DIEM } } }
const DE_XUAT = { type: 'object', required: ['ket_luan_de_xuat', 'luan_diem'], properties: {
  ket_luan_de_xuat: { type: 'string' }, luan_diem: { type: 'array', minItems: 1, items: LUAN_DIEM } } }
// 06/10/2026 — bác sĩ quyết: hội đồng TƯ VẤN, ĐƯA RA GIẢI PHÁP TỐT NHẤT ⇒ phán quyết bắt buộc giai_phap_tot_nhat
// (hoi_dong_cong.py biên bản v2 từ chối ghi khi thiếu/thiếu căn cứ/viết như trạng thái cổng).
const GIAI_PHAP = { type: 'object', required: ['phuong_an', 'can_cu'], properties: {
  phuong_an: { type: 'string' }, can_cu: { type: 'array', minItems: 1, items: CAN_CU.items },
  phuong_an_khac: { type: 'array', items: { type: 'object', required: ['phuong_an', 'vi_sao_khong_chon'], properties: {
    phuong_an: { type: 'string' }, vi_sao_khong_chon: { type: 'string' } } } } } }
const PHAN_QUYET = { type: 'object', required: ['tung_luan_diem', 'ket_qua', 'ket_luan_cuoi', 'giai_phap_tot_nhat'], properties: {
  tung_luan_diem: { type: 'array', items: { type: 'object', required: ['ma', 'ket', 'ly_do'], properties: {
    ma: { type: 'string' }, ket: { enum: ['chap_nhan', 'bac', 'chua_du_can_cu'] }, ly_do: { type: 'string' } } } },
  ket_qua: { enum: ['giu_ket_luan', 'sua_ket_luan', 'chuyen_bac_si'] }, ket_luan_cuoi: { type: 'string' },
  viec_sua: { type: 'array', items: { type: 'string' } },
  chuyen_bac_si: { type: 'array', items: { type: 'object', required: ['van_de', 'vi_sao'], properties: {
    van_de: { type: 'string' }, vi_sao: { type: 'string' } } } },
  giai_phap_tot_nhat: GIAI_PHAP, bai_hoc_he_thong: BAI_HOC } }
const KQ_CODEX = { type: 'object', required: ['ok'], properties: {
  ok: { type: 'boolean' }, phan_quyet: PHAN_QUYET, loi: { type: 'string' },
  nguon_trong_tai: { type: 'object', properties: { cong_cu: { type: 'string' }, codex: { type: 'string' },
    model: { type: 'string' }, luc: { type: 'string' } } } } }
const KQ_GHI = { type: 'object', required: ['ket_qua'], properties: {
  ket_qua: { type: 'array', items: { type: 'object', properties: { loai: { type: 'string' }, ma: { type: 'string' },
    ma_thoat: { type: 'number' }, dau_ra: { type: 'string' } } } }, tom_tat: { type: 'string' },
  // 09/10/2026: bảng trách nhiệm của điều phối cổng lúc bàn giao (`hoi_dong_cong.py trach-nhiem --ghi`, _HOI-DONG-CONG §1b).
  trach_nhiem: { type: 'object', properties: { ket_luan: { type: 'string' }, ma_thoat: { type: 'number' },
    tep_luu: { type: 'string' }, agent_con_viec: { type: 'array', items: { type: 'string' } } } } } }

const CHUNG = `Đề tài «${STUDY}», cổng ${GATE}. Mọi lệnh chạy trong thư mục ${Y}/. Đường dẫn tệp là tương đối exports/${STUDY}/. ` +
  'KHÔNG sửa tệp đề tài, KHÔNG ghi gate_params/approval_ledger, KHÔNG chạy approve_gate.py, KHÔNG PII. ' +
  'Căn cứ phải kiểm được: tep (<tệp>:<dòng>), tieu_chi (G4-AUTO-09…), pmid, doi, lenh (kèm ket_qua). Trả lời đúng schema.'

// ── Chạy thử: in kế hoạch, KHÔNG mở agent ─────────────────────────────────────────────────────────────────────────────
if (a.chay_thu && HS) {
  return { chay_thu: true, ho_so_may: true, study: STUDY, gate: GATE, khuyen_nghi: HS.khuyen_nghi, gom_giam_khao: GOM,
    cham: HS.nhiem_vu.filter(n => n.can_cham).map(n => n.ma),
    tranh_bien_dp: HS.dp.filter(d => d.can_tranh_bien).map(d => d.ma),
    bat_dong_treo: HS.bat_dong_treo.map(b => b.ma),
    bo_qua: [...HS.nhiem_vu.filter(n => !n.can_cham).map(n => `${n.ma}: ${n.ly_do}`),
      ...HS.dp.filter(d => !d.can_tranh_bien).map(d => `${d.ma}: ${d.ly_do}`)],
    ghi_chu: `Số agent + token: python3 tools/hoi_dong_cong.py uoc-tinh --study ${STUDY} --gate ${GATE}` }
}
if (a.chay_thu) {
  const vaiTrongTai = CHE_DO === 'codex' ? 'trọng tài Codex (tools/trong_tai_codex.py)' : 'trọng tài'
  return { chay_thu: true, study: STUDY, gate: GATE, dieu_phoi: DIEU_PHOI, max_vong: MAX_VONG, max_agent: MAX_AGENT,
    trong_tai: CHE_DO,
    ke_hoach: ['1 hồ sơ cổng', '2 người chấm × mỗi nhiệm vụ áp dụng', MAX_VONG >= 2 ? `mỗi DP: phản biện + đề xuất đáp + phản biện vòng 2 + ${vaiTrongTai}` : `mỗi DP: phản biện + ${vaiTrongTai}`,
      '1 ghi biên bản'], ghi_chu: 'Danh mục: python3 tools/hoi_dong_cong.py danh-muc --gate ' + GATE }
}

// ── Pha 1: hồ sơ cổng ─────────────────────────────────────────────────────────────────────────────────────────────────
phase('Hồ sơ cổng')
const dpYeuCau = Array.isArray(a.dp) && a.dp.length ? `chỉ các DP: ${a.dp.join(', ')}` :
  'các DP BẮT BUỘC của cổng (cổng cứng) hoặc mọi DP (cổng mềm)'
if (HS && !HS.can_hop) {  // máy đã lập hồ sơ: không còn gì cần họp ⇒ 0 agent
  return { study: STUDY, gate: GATE, khong_can_hop: true, so_agent: 0, khuyen_nghi: HS.khuyen_nghi,
    cho_bac_si: HS.cho_bac_si || [], bo_qua: HS.nhiem_vu.map(n => `${n.ma}: ${n.ly_do}`)
      .concat(HS.dp.map(d => `${d.ma}: ${d.ly_do}`)),
    luu_y: 'TƯ VẤN — không mở, không chặn cổng. Cần bác sĩ kiểm chứng.' }
}
const DP_HO_SO = { type: 'object', required: ['dp'], properties: { dp: HO_SO.properties.dp } }
async function lapHoSo() {
  if (!HS) return null
  const dpCan = HS.dp.filter(d => d.can_tranh_bien)
  let dp = []
  if (dpCan.length) {
    const r = await goi(
      `${CHUNG}\nBạn là ${DIEU_PHOI} ở BƯỚC 1–2 của hội đồng. MÁY đã lập hồ sơ tất định (trạng thái sống ${HS.trang_thai_song}; ` +
      'đầu ra đem chấm, người chấm, phần đã có biên bản còn hiệu lực) — bạn CHỈ soạn điểm quyết định, không giao việc mới, ' +
      `không sửa gì. Với MỖI DP: ${JSON.stringify(dpCan.map(d => ({ ma: d.ma, cau_hoi: d.cau_hoi, tham_quyen: d.tham_quyen })))} ` +
      'nêu kết luận dự kiến (đề xuất cho người có thẩm quyền — KHÔNG viết «đã ký/đã duyệt/PASS_…»), tai_lieu_xet (tệp có ' +
      `thật; hồ sơ cổng: ${HS.tai_lieu_cong.join(', ')}), và 1–4 luận điểm mã L1… mỗi luận điểm ≥1 căn cứ đã tự kiểm.`,
      { label: `luận điểm DP ${GATE}`, phase: 'Hồ sơ cổng', agentType: DIEU_PHOI, schema: DP_HO_SO })
    if (!r) return { loi: true }
    dp = (r.dp || []).filter(d => dpCan.some(x => x.ma === d.ma))
  }
  return { trang_thai_song: HS.trang_thai_song, dp,
    nhiem_vu: HS.nhiem_vu.filter(n => n.can_cham && n.cham_chuyen_mon)
      .map(n => ({ ma: n.ma, tac_gia: n.agent, tai_lieu: n.tai_lieu, cham_chuyen_mon: n.cham_chuyen_mon })) }
}
const hoSo = HS ? await lapHoSo() : await goi(
  `${CHUNG}\nBạn là ${DIEU_PHOI} ở BƯỚC 1–2 của hội đồng (chuẩn bị hồ sơ — không giao việc mới, không sửa gì).\n` +
  `1) Chạy \`python3 tools/hoi_dong_cong.py cham-song --study ${STUDY} --gate ${GATE}\` và \`python3 tools/hoi_dong_cong.py danh-muc --gate ${GATE} --json\`.\n` +
  `2) Với MỖI nhiệm vụ của danh mục: tác giả đúng danh mục; tai_lieu = các tệp đầu ra CÓ THẬT trong exports/${STUDY}/ (ls để kiểm); ` +
  'cham_chuyen_mon = MỘT người chấm trong ma trận của nhiệm vụ đó (không phải tác giả); nhiệm vụ có điều kiện không áp dụng ⇒ ap_dung=false + lý do; ' +
  'nhiệm vụ chưa có đầu ra ⇒ ap_dung=false + «chưa có đầu ra».\n' +
  `3) Với ${dpYeuCau}: kết luận dự kiến (đề xuất cho người có thẩm quyền — KHÔNG viết «đã ký/đã duyệt/PASS_…»), ` +
  'tai_lieu_xet (tệp có thật), và 1–4 luận điểm mã L1… mỗi luận điểm ≥1 căn cứ đã tự kiểm.',
  { label: `hồ sơ ${GATE}`, phase: 'Hồ sơ cổng', agentType: DIEU_PHOI, schema: HO_SO })
if (!hoSo || hoSo.loi) return { loi: 'không lập được hồ sơ cổng', bo_qua: boQua }
const nhiemVu = (hoSo.nhiem_vu || []).filter(n => n.ap_dung !== false && (n.tai_lieu || []).length)
log(`${GATE}: ${nhiemVu.length} đầu ra đem chấm · ${(hoSo.dp || []).length} DP đem tranh biện · trạng thái sống ${hoSo.trang_thai_song}`)

// ── Pha 2: đánh giá chéo (song song theo nhiệm vụ, hai người chấm mỗi đầu ra) ─────────────────────────────────────────
const chamMot = (n, nguoi, vai) => goi(
  `${CHUNG}\nBạn là người chấm «${nguoi}» (vai ${vai}) cho ĐẦU RA nhiệm vụ ${n.ma} của tác giả «${n.tac_gia}». ` +
  `Tệp: ${n.tai_lieu.join(', ')}. Chấm ĐỦ RQ1–RQ8 theo rubric của .claude/agents/_HOI-DONG-CONG.md §3 ` +
  `(trạng thái sống chỉ đọc: \`python3 tools/hoi_dong_cong.py cham-song --study ${STUDY} --gate ${GATE}\`). ` +
  'can_sua/loi_do bắt buộc có nhận xét + căn cứ; lỗi đỏ RQ3/RQ6/RQ7 ⇒ tra_ve_sua; khong_ap_dung phải nêu lý do. ' +
  `${BAI_HOC_LOI} Trả nguoi_cham="${nguoi}", vai="${vai}".`,
  { label: `chấm ${n.ma} · ${nguoi}`, phase: 'Đánh giá chéo', agentType: nguoi, schema: MUC_CHAM })
const chamXong = (cham, n) => {
  const hopLe = (cham || []).filter(Boolean)
  const phia = new Set(hopLe.map(c => c.ket_luan !== 'tra_ve_sua'))
  return { nhiem_vu: n, cham: hopLe, dong_thuan: hopLe.length === 2 && phia.size === 1 }
}
const vongPB = (d, so, truoc) => goi(
  `${CHUNG}\nBạn là phan-bien-tranh-bien, vòng ${so}. Điểm quyết định ${d.ma}. Kết luận dự kiến: «${d.ket_luan_de_xuat}». ` +
  `Tài liệu: ${d.tai_lieu_xet.join(', ')}. Các bên đã nói: ${JSON.stringify(truoc)}. ` +
  'Nêu phản đối MẠNH NHẤT có căn cứ (mã P…, phan_doi trỏ L…); không có thì MỘT luận điểm nhuong=true. Không bịa.',
  { label: `phản biện ${d.ma} v${so}`, phase: 'Tranh biện', agentType: 'phan-bien-tranh-bien', schema: VONG })
const vongDX = (d, so, truoc) => goi(
  `${CHUNG}\nBạn là ${DIEU_PHOI} (bên đề xuất), vòng ${so}. Điểm quyết định ${d.ma}. Đáp các phản đối bằng căn cứ ` +
  `(mã L${so}…), hoặc nhượng bằng cách nêu sẽ sửa gì. Các bên đã nói: ${JSON.stringify(truoc)}.`,
  { label: `đề xuất ${d.ma} v${so}`, phase: 'Tranh biện', agentType: DIEU_PHOI, schema: VONG })
async function tranh(d) {
  if (!d.luan_diem) {  // bất đồng: điều phối cổng tự lập kết luận dự kiến + luận điểm từ hai bản chấm
    const dx = await goi(
      `${CHUNG}\nBạn là ${DIEU_PHOI} (bên đề xuất). Hai người chấm BẤT ĐỒNG về đầu ra ${d.nguon}: ${JSON.stringify(d.cham)}. ` +
      `Tài liệu: ${d.tai_lieu_xet.join(', ')}. Nêu kết luận dự kiến (đề xuất — không viết «đã ký/đã duyệt/PASS_…») và 1–4 luận ` +
      'điểm mã L1… có căn cứ đã tự kiểm.',
      { label: `đề xuất ${d.ma}`, phase: 'Tranh biện', agentType: DIEU_PHOI, schema: DE_XUAT })
    if (!dx) return null
    d = { ...d, ket_luan_de_xuat: dx.ket_luan_de_xuat, luan_diem: dx.luan_diem }
  }
  const vong = [{ so: 1, ben: 'de_xuat', luan_diem: d.luan_diem }]
  const pb1 = await vongPB(d, 1, vong)
  if (!pb1) return null
  vong.push({ so: 1, ben: 'phan_bien', luan_diem: pb1.luan_diem })
  if (MAX_VONG >= 2 && pb1.luan_diem.some(l => !l.nhuong)) {
    const dx2 = await vongDX(d, 2, vong)
    if (dx2) {
      const pb2 = await vongPB(d, 2, [...vong, { so: 2, ben: 'de_xuat', luan_diem: dx2.luan_diem }])
      if (pb2) vong.push({ so: 2, ben: 'de_xuat', luan_diem: dx2.luan_diem }, { so: 2, ben: 'phan_bien', luan_diem: pb2.luan_diem })
    }
  }
  if (CHE_DO === 'codex') {
    // Vai trọng tài KHÔNG tự phán: chạy trình Codex (mô hình khác) và trả NGUYÊN VĂN phán quyết đã qua luật biên bản.
    const nhap = { loai: 'tranh_bien', diem_quyet_dinh: { ma: d.ma }, tai_lieu_xet: d.tai_lieu_xet,
      ket_luan_de_xuat: d.ket_luan_de_xuat, vai: { de_xuat: DIEU_PHOI, phan_bien: 'phan-bien-tranh-bien' }, vong,
      ...(d.nguon ? { nguon_bat_dong: d.nguon_id || `(id biên bản đánh giá ${d.nguon} — điều phối cổng điền khi ghi)` } : {}) }
    const kq = await goi(
      `${CHUNG}\nBạn là trong-tai-tranh-bien ở CHẾ ĐỘ CODEX — KHÔNG tự phán, KHÔNG sửa phán quyết. ` +
      '1) Ghi BẢN NHÁP dưới đây NGUYÊN VĂN ra một tệp trong thư mục tạm của hệ điều hành (KHÔNG ghi vào exports/). ' +
      `2) Chạy \`python3 tools/trong_tai_codex.py --study ${STUDY} --gate ${GATE} --tep <tệp đó> --json\` (KHÔNG --ghi — ` +
      'điều phối cổng ghi ở bước biên bản). 3) Mã thoát 0 và hop_le=true ⇒ ok=true, phan_quyet = bien_ban.phan_quyet ' +
      'NGUYÊN VĂN (bỏ trường trong_tai), nguon_trong_tai = bien_ban.nguon_trong_tai. Mã 2 (không chạy được) hoặc 3 (vi ' +
      'phạm luật) ⇒ ok=false, loi = mã thoát + thông điệp — KHÔNG tự phán thay, KHÔNG chạy lại với Claude.\n' +
      `BẢN NHÁP: ${JSON.stringify(nhap)}`,
      { label: `trọng tài Codex ${d.ma}`, phase: 'Tranh biện', agentType: 'trong-tai-tranh-bien', schema: KQ_CODEX })
    if (!kq || !kq.ok || !kq.phan_quyet) {
      boQua.push(`trọng tài Codex ${d.ma}`)
      log(`⛔ Trọng tài Codex ${d.ma}: ${(kq && kq.loi) || 'không chạy được'} — không ghi biên bản tranh biện này`)
      return null
    }
    return { d, vong, pq: kq.phan_quyet, nguon: kq.nguon_trong_tai || null }
  }
  const pq = await goi(
    `${CHUNG}\nBạn là trong-tai-tranh-bien (ngữ cảnh mới). Điểm quyết định ${d.ma}; kết luận dự kiến «${d.ket_luan_de_xuat}»; ` +
    `tài liệu ${d.tai_lieu_xet.join(', ')}. Hồ sơ các vòng: ${JSON.stringify(vong)}. Kiểm căn cứ của từng bên rồi phán MỌI ` +
    'phản đối P… (chap_nhan/bac/chua_du_can_cu + lý do). Đã chấp nhận phản đối thì KHÔNG giữ nguyên kết luận; tranh chấp thuộc ' +
    'thẩm quyền người ⇒ chuyen_bac_si (van_de + vi_sao). ket_luan_cuoi là ĐỀ XUẤT — không viết «đã ký/đã duyệt/PASS_…/…_LOCKED». ' +
    'BẮT BUỘC giai_phap_tot_nhat: phuong_an = khuyến nghị CỤ THỂ làm được + can_cu kiểm được; sua_ket_luan/chuyen_bac_si thì ' +
    'thêm ≥1 phuong_an_khac đã cân nhắc + vi_sao_khong_chon (bác sĩ quyết 06/10/2026: hội đồng ĐƯA RA GIẢI PHÁP TỐT NHẤT). ' +
    BAI_HOC_LOI,
    { label: `trọng tài ${d.ma}`, phase: 'Tranh biện', agentType: 'trong-tai-tranh-bien', schema: PHAN_QUYET })
  return pq ? { d, vong, pq } : null
}
const MUC_CHAM_NV = { ...MUC_CHAM, required: [...MUC_CHAM.required, 'ma_nhiem_vu'],
  properties: { ...MUC_CHAM.properties, ma_nhiem_vu: { type: 'string' } } }
const GOM_CHAM = { type: 'object', required: ['danh_gia'], properties: { danh_gia: { type: 'array', items: MUC_CHAM_NV } } }
const chamGom = nhom => goi(
  `${CHUNG}\nBạn là giam-khao-cong (vai giam_khao), chấm ĐỘC LẬP ${nhom.length} đầu ra của cổng — MỖI đầu ra một bản chấm ` +
  'riêng đủ RQ1–RQ8, xét từng đầu ra trên tệp của chính nó, không để nhận xét đầu ra này lan sang đầu ra khác: ' +
  nhom.map(n => `${n.ma} (tác giả «${n.tac_gia}»; tệp: ${n.tai_lieu.join(', ')})`).join(' · ') +
  `. Rubric .claude/agents/_HOI-DONG-CONG.md §3 (trạng thái sống chỉ đọc: \`python3 tools/hoi_dong_cong.py cham-song --study ${STUDY} --gate ${GATE}\`). ` +
  'can_sua/loi_do bắt buộc có nhận xét + căn cứ; lỗi đỏ RQ3/RQ6/RQ7 ⇒ tra_ve_sua; khong_ap_dung phải nêu lý do. ' +
  `${BAI_HOC_LOI} Trả danh_gia = đúng một mục cho MỖI mã nhiệm vụ (ma_nhiem_vu), nguoi_cham="giam-khao-cong", vai="giam_khao".`,
  { label: `giám khảo ${nhom.map(n => n.ma).join('+')}`, phase: 'Đánh giá chéo', agentType: 'giam-khao-cong', schema: GOM_CHAM })
const nhomGK = []
for (let i = 0; i < nhiemVu.length; i += GOM) nhomGK.push(nhiemVu.slice(i, i + GOM))
if (GOM > 1 && nhiemVu.length > 1) log(`Gom giám khảo: ${nhiemVu.length} đầu ra → ${nhomGK.length} lượt giam-khao-cong`)
phase('Đánh giá chéo')
const [chuyenMon, giamKhao, tranhDP] = await parallel([
  () => parallel(nhiemVu.map(n => () => chamMot(n, n.cham_chuyen_mon, 'chuyen_mon'))),
  () => GOM > 1 ? parallel(nhomGK.map(nh => () => chamGom(nh)))
    : parallel(nhiemVu.map(n => () => chamMot(n, 'giam-khao-cong', 'giam_khao'))),
  () => pipeline((hoSo.dp || []).map(d => ({ ...d, nguon: null })), tranh),
])
const gkTheoMa = {}
if (GOM > 1) {
  for (const r of (giamKhao || []).filter(Boolean)) {
    for (const c of r.danh_gia || []) {
      if (!nhiemVu.some(n => n.ma === c.ma_nhiem_vu) || gkTheoMa[c.ma_nhiem_vu]) continue
      const { ma_nhiem_vu, ...cham } = c
      gkTheoMa[ma_nhiem_vu] = { ...cham, nguoi_cham: 'giam-khao-cong', vai: 'giam_khao' }
    }
  }
} else nhiemVu.forEach((n, i) => { if (giamKhao && giamKhao[i]) gkTheoMa[n.ma] = giamKhao[i] })
const thieuGK = nhiemVu.filter(n => !gkTheoMa[n.ma]).map(n => n.ma)
if (thieuGK.length) log(`⛔ Thiếu bản chấm giám khảo cho ${thieuGK.join(', ')} — đầu ra đó KHÔNG ghi biên bản (ghi vào kết quả)`)
boQua.push(...thieuGK.map(m => `giám khảo ${m}`))
const danhGia = nhiemVu.map((n, i) => chamXong([chuyenMon && chuyenMon[i], gkTheoMa[n.ma]], n))
phase('Tranh biện')
const batDong = [
  ...(HS ? HS.bat_dong_treo.map(b => ({ ma: b.ma, nguon: b.nguon, nguon_id: b.nguon_id, tai_lieu_xet: b.tai_lieu_xet,
    cham: b.cham })) : []),
  ...danhGia.filter(dg => !dg.dong_thuan && dg.cham.length === 2).map(dg => ({
    ma: `BD-${dg.nhiem_vu.ma}`, nguon: dg.nhiem_vu.ma, tai_lieu_xet: dg.nhiem_vu.tai_lieu, cham: dg.cham })),
]
if (batDong.length) log(`${batDong.length} đầu ra bất đồng ⇒ tranh biện BD-…`)
const tranhBien = [...(tranhDP || []), ...(await pipeline(batDong, tranh))]

// ── Pha 4: dựng biên bản TỪ đầu ra có cấu trúc (không diễn giải lại) → điều phối cổng ghi qua công cụ ──────────────────
phase('Biên bản')
const bienBan = []
for (const dg of danhGia.filter(Boolean)) {
  if (dg.cham.length < 2) continue
  bienBan.push({ loai: 'danh_gia_cheo', ma: dg.nhiem_vu.ma, json: { loai: 'danh_gia_cheo',
    dau_ra: { ma_nhiem_vu: dg.nhiem_vu.ma, tac_gia: dg.nhiem_vu.tac_gia, tai_lieu: dg.nhiem_vu.tai_lieu },
    danh_gia: dg.cham } })
}
for (const tb of tranhBien.filter(Boolean)) {
  bienBan.push({ loai: 'tranh_bien', ma: tb.d.ma, json: { loai: 'tranh_bien', che_do: CHE_DO,
    diem_quyet_dinh: { ma: tb.d.ma }, nguon_bat_dong: tb.d.nguon_id || (tb.d.nguon ? `(id biên bản đánh giá ${tb.d.nguon} — điều phối cổng điền sau khi ghi)` : undefined),
    tai_lieu_xet: tb.d.tai_lieu_xet, ket_luan_de_xuat: tb.d.ket_luan_de_xuat,
    vai: { de_xuat: DIEU_PHOI, phan_bien: 'phan-bien-tranh-bien', trong_tai: TEN_TRONG_TAI },
    vong: tb.vong, phan_quyet: { viec_sua: [], chuyen_bac_si: [], ...tb.pq, trong_tai: TEN_TRONG_TAI },
    ...(tb.nguon ? { nguon_trong_tai: tb.nguon } : {}) } })
}
const ghi = await goi(
  `${CHUNG}\nBạn là ${DIEU_PHOI} ở BƯỚC 7 (ghi biên bản). Ghi LẦN LƯỢT từng biên bản dưới đây, NGUYÊN VĂN (không sửa nội dung), ` +
  `bằng \`python3 tools/hoi_dong_cong.py ghi --study ${STUDY} --gate ${GATE} --tep -\` với JSON qua stdin. Ghi biên bản danh_gia_cheo ` +
  'TRƯỚC; với tranh biện BD-…, thay nguon_bat_dong bằng id biên bản đánh giá vừa ghi của đúng nhiệm vụ (đã là id thật dạng ' +
  `«${GATE}-DG-…» thì GIỮ NGUYÊN — bất đồng từ lần họp trước). Công cụ trả mã 3 = vi phạm ` +
  'luật ⇒ KHÔNG lách, ghi lại mã thoát + thông điệp. Cuối cùng chạy `python3 tools/hoi_dong_cong.py tom-tat --study ' + STUDY + '`, rồi ' +
  `\`python3 tools/hoi_dong_cong.py trach-nhiem --study ${STUDY} --gate ${GATE} --ghi\` (bạn CHỊU TRÁCH NHIỆM kết quả cổng — trả ` +
  'trach_nhiem: kết luận, mã thoát, tệp lưu, mã các tiêu chí «agent còn việc»; KHÔNG tự khai hoàn chỉnh khi mã ≠ 0).\n' +
  `BIÊN BẢN: ${JSON.stringify(bienBan)}`,
  { label: `ghi biên bản ${GATE}`, phase: 'Biên bản', agentType: DIEU_PHOI, schema: KQ_GHI })

return {
  study: STUDY, gate: GATE, trong_tai: CHE_DO, trang_thai_song: hoSo.trang_thai_song, so_agent: soAgent, bo_qua: boQua,
  ho_so_may: !!HS, gom_giam_khao: GOM,
  so_bai_hoc_he_thong: danhGia.reduce((s, d) => s + d.cham.reduce((x, c) => x + ((c.bai_hoc_he_thong || []).length), 0), 0)
    + tranhBien.filter(Boolean).reduce((s, tb) => s + ((tb.pq.bai_hoc_he_thong || []).length), 0),
  khong_hop_lai: HS ? HS.nhiem_vu.filter(n => !n.can_cham).map(n => `${n.ma}: ${n.ly_do}`)
    .concat(HS.dp.filter(d => !d.can_tranh_bien).map(d => `${d.ma}: ${d.ly_do}`)) : [],
  danh_gia: danhGia.filter(Boolean).map(d => ({ ma: d.nhiem_vu.ma, dong_thuan: d.dong_thuan, ket_luan: d.cham.map(c => `${c.nguoi_cham}:${c.ket_luan}`) })),
  tranh_bien: tranhBien.filter(Boolean).map(t => ({ dp: t.d.ma, ket_qua: t.pq.ket_qua, ket_luan_cuoi: t.pq.ket_luan_cuoi,
    chuyen_bac_si: t.pq.chuyen_bac_si || [], giai_phap_tot_nhat: t.pq.giai_phap_tot_nhat || null })),
  ghi_bien_ban: ghi,
  trach_nhiem: ghi && ghi.trach_nhiem ? ghi.trach_nhiem : null,
  luu_y: 'TƯ VẤN — không mở, không chặn cổng; cổng do bộ chấm + chữ ký người có thẩm quyền. Cần bác sĩ kiểm chứng.',
}
