"""orchestrator.py — ĐIỀU PHỐI AGENT/PLUGIN: ghép 8 năng lực thành control plane chạy được.

Orchestrator.handle(request):
  route intent → dựng plan theo flow → chạy từng bước qua executor (dry-run mặc định) →
  dừng ở cổng (Cổng A/B/G) → chốt guardrail 2 lớp → released / gate_pending / returned.
Grounded vào registry 50 agent thật + registry quyền sở hữu plugin; không để plugin tự tranh owner.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .agent_adapter import AgentExecutor, DryRunExecutor
from .context import ContextStore, Session
from .flows import CLINICAL_FLOW, FlowStep, GUARDRAIL_STEP, all_agents_in_flows, flow_for, sa
from .intent import SINGLE_TASK_RULES, route
from .knowledge import KnowledgeLayer
from .lifecycle import GATES, MAX_RETRIES, Lifecycle
from .plugin_ownership import PluginOwnershipRegistry
from .registry import Registry
from .signals import SIGNAL_CUES, Signals, detect as detect_signals
from .tools_registry import ToolRegistry
from .worker_inventory import LY_DO_CHUA_CAI, WorkerInventory

# Cổng cho VIỆC LẺ (agent đơn phát ra khuyến cáo / vượt cổng cứng)
GATE_HINTS: dict[str, str] = {
    "ke-don-an-toan": "A", "quan-ly-khang-dong": "A", "quyet-dinh-chung": "A",
    "dau-man-tinh": "A", "cham-soc-giam-nhe": "A", "tram-cam-lo-au": "A",
    "tham-dinh-grade-nnt": "A", "theo-doi-benh-man": "A", "du-phong-tam-soat": "A",
    "tham-dinh-do-chinh-xac-chan-doan": "A",
    "dao-duc-dang-ky": "G2", "thiet-ke-nghien-cuu": "G4", "nop-bai-phan-hoi": "G9",
}

# Đích RE-ROUTE mặc định theo mã lỗi guardrail SỬA ĐƯỢC (khi verdict không chỉ định
# `reroute_to`). R1/CIT-GHOST = trích dẫn ma/không phân giải → kiểm chứng trích dẫn;
# thiếu nguồn/PARTIAL/nghi bịa → truy xuất lại nguồn thật. Mọi đích là agent THẬT trong registry.
REROUTE_DEFAULT: dict[str, str] = {
    "R1": "kiem-chung-trich-dan", "R1b": "kiem-chung-trich-dan", "CIT-GHOST": "kiem-chung-trich-dan",
    "R4": "tra-cuu-chung-cu", "R9": "tra-cuu-chung-cu", "PARTIAL": "tra-cuu-chung-cu",
    "R8": "phan-tich-thong-ke", "STAT-MISMATCH": "phan-tich-thong-ke",
    "STD-REPORT": "viet-ban-thao", "AI-DISCLOSE": "nop-bai-phan-hoi",
}

# Mã verdict KHÔNG chẩn đoán được (verdict_fn ném lỗi / trả dị dạng) → FAIL-CLOSED: block +
# leo thang NGAY, KHÔNG re-route mù, KHÔNG tự release. Cổng an toàn phải đóng khi bất định.
_FAIL_CLOSED_CODES = {"GUARDRAIL_ERROR", "GUARDRAIL_INDETERMINATE"}


@dataclass
class Orchestrator:
    registry: Registry = field(default_factory=Registry.load)
    tools: ToolRegistry = field(default_factory=ToolRegistry)
    knowledge: KnowledgeLayer = field(default_factory=KnowledgeLayer)
    plugin_ownership: PluginOwnershipRegistry = field(default_factory=PluginOwnershipRegistry.load)
    worker_inventory: WorkerInventory = field(default_factory=WorkerInventory)

    # ── Năng lực 1: điều phối ────────────────────────────────────────
    def handle(self, request: str, executor: AgentExecutor | None = None,
               store: ContextStore | None = None, persist: bool = True,
               guardrail_verdict: Callable[[Session], dict] | None = None) -> Session:
        ex = executor or DryRunExecutor()
        session = Session(request=request)
        lc = Lifecycle()

        # Năng lực 3: định tuyến intent
        intent = route(request)
        session.intent = intent.as_dict()
        session.kind = intent.kind
        session.entry_agent = intent.target
        lc.to("routed", intent.reason)

        # Tín hiệu ngữ cảnh cần có TRƯỚC nhánh 'unknown' bên dưới (BƯỚC 0 cờ đỏ dùng nó
        # qua _run_step) — tách khỏi vị trí gốc (Năng lực 4, ngay sau nhánh unknown cũ).
        signals = detect_signals(request)

        if intent.kind == "unknown" or not intent.target:
            # SỬA 2026-09-03 (Workflow đối kháng đa-agent vòng 2, phát hiện CRITICAL):
            # trước đây nhánh này trả needs_clarification NGAY LẬP TỨC — 0 bước, 0 bản ghi
            # trace — nghĩa là BƯỚC 0 cờ đỏ (sang-loc-co-do) KHÔNG BAO GIỜ chạy khi router
            # không nhận diện được câu, kể cả khi câu mô tả một ca có dấu hiệu nguy hiểm
            # thật (đo được bằng chạy sống: "Phụ nữ mang thai 32 tuần bị đau đầu dữ dội
            # kèm phù chân, huyết áp 160/100" — gợi ý tiền sản giật — và "Bé trai 8 tuổi
            # khó thở về đêm, nghi hen" đều rơi 'unknown' và bỏ qua sàng lọc hoàn toàn).
            # Đúng tinh thần bất biến BH88 đã tuyên bố ("over-route sang nơi CÓ sàng lọc
            # cờ đỏ là chiều an toàn, under-route bỏ qua cờ đỏ thì không") — 'unknown' còn
            # tệ hơn under-route vì nó là KHÔNG định tuyến gì cả. Nay LUÔN chạy BƯỚC 0 cờ
            # đỏ (agent tự quyết định có gì đáng ngại hay không) TRƯỚC KHI trả lời "cần
            # làm rõ" cho bác sĩ — không đổi kết cục needs_clarification, chỉ đảm bảo an
            # toàn không bị bỏ qua trong lúc chờ làm rõ.
            self._run_step(session, CLINICAL_FLOW[0], ex, signals)
            session.status = "needs_clarification"
            lc.to("blocked", intent.reason)
            session.checkpoint(
                "routed", None,
                "cần làm rõ intent — đã chạy sàng lọc cờ đỏ (BƯỚC 0) trước khi hỏi lại",
            )
            return self._finish(session, lc, store, persist)

        # Plugin khong tu tranh quyen voi nhac truong. Moi request duoc gan mot owner
        # duy nhat; plugin chi xuat hien trong danh sach worker duoc phep cua capability.
        plugin_decision = self.plugin_ownership.resolve_for_intent(
            intent.kind,
            intent.target,
            request=request,
        )
        session.plugin_routing = self._routing_with_availability(plugin_decision)
        session.checkpoint(
            "plugin_routing",
            None,
            f"owner `{plugin_decision.owner_unit}`; plugin chi la worker",
            session.plugin_routing,
        )
        if plugin_decision.status.startswith("BLOCKED"):
            session.status = "blocked · chưa xác định quyền sở hữu plugin"
            lc.to("blocked", plugin_decision.status)
            return self._finish(session, lc, store, persist)

        # Năng lực 4 (một phần): tín hiệu ngữ cảnh — quyết định nhánh nào THỰC SỰ áp dụng
        # (vá lỗ hổng cũ: trước đây plan chạy mù mọi nhánh dù request không đúng bối cảnh).
        # `signals` đã tính ở trên (trước nhánh 'unknown') — không tính lại.
        session.checkpoint("signals", None, "tín hiệu ngữ cảnh đã khớp", signals.as_dict())

        # SỬA 2026-09-04 (Workflow đối kháng đa-agent, phát hiện HIGH — cùng họ với vá
        # BH88/vòng 2 cho nhánh 'unknown'): RESEARCH_FLOW (G0→G10) KHÔNG có bước nào
        # tương đương BƯỚC 0 cờ đỏ của CLINICAL_FLOW. intent.py's luật "sang-loc-co-do"
        # (vòng 3) chỉ cứu được khi câu khớp ĐÚNG cụm hẹp ("cấp cứu"/"chuyển viện"/
        # "cờ đỏ"/"có nguy hiểm"/"đừng bỏ sót") — một đề tài mô tả quần thể vẫn có thể
        # lồng mô tả lâm sàng nguy hiểm mà không dùng đúng cụm đó. Đo sống: "Nghiên cứu
        # cắt ngang tỷ lệ đau đầu dữ dội kèm sốt cao ở phụ nữ mang thai..." chạy trọn
        # G0→G10 (25 bước) mà KHÔNG MỘT LẦN nào sang-loc-co-do được gọi. Cùng nguyên tắc
        # bất biến BH88: over-route sang nơi CÓ sàng lọc cờ đỏ là chiều an toàn. Chạy
        # BƯỚC 0 như một LỚP PHÒNG THỦ BỔ SUNG cho research_topic — KHÔNG đổi kind/
        # routing/cổng, chỉ thêm một bước sàng lọc trước khi vào G0 (agent tự quyết định
        # có gì đáng ngại hay không, giống hệt cách 'unknown' đã dùng).
        if intent.kind == "research_topic":
            self._run_step(session, CLINICAL_FLOW[0], ex, signals)

        # Năng lực 1: dựng plan (flow) theo loại intent
        steps = self._plan(intent.kind, intent.target)
        lc.to("planned", f"{len(steps)} bước · điểm vào `{intent.target}`")

        # Năng lực 1+6: chạy từng bước, dừng ở cổng
        lc.to("running")
        for step in steps:
            self._run_step(session, step, ex, signals)
            if step.gate and step is not GUARDRAIL_STEP:
                session.gates_pending.append(step.gate)
                session.checkpoint(step.step_id, step.gate, GATES.get(step.gate, step.gate))

        # Năng lực 6: chốt guardrail 2 lớp (đã là bước cuối trong flow)
        lc.to("guardrail", "chốt kiểm 2 lớp qua `tham-dinh-dau-ra` (R1–R14 + Q1–Q7)")

        # Năng lực 6+2: VÒNG RE-ROUTE khi guardrail TRẢ-VỀ-SỬA lỗi sửa được (vd trích dẫn
        # không phân giải → quay lại truy xuất/kiểm chứng). `guardrail_verdict` là SEAM:
        # production cắm `run_eval.py`/`tham-dinh-dau-ra`; None = giữ nguyên hành vi cũ
        # (tương thích ngược). Đây là nơi `lifecycle.guardrail_fail()` (retry ≤3) TRỞ THÀNH
        # MÃ SỐNG — trước đây là dead-code không ai gọi.
        if guardrail_verdict is not None and not self._guardrail_reroute_loop(
                session, lc, ex, guardrail_verdict):
            return self._finish(session, lc, store, persist)  # đã BLOCK/leo thang → dừng

        # Kết cục control-plane (dry-run): dừng ở cổng nếu có, ngược lại released
        if session.gates_pending:
            g = session.gates_pending[0]
            lc.hit_gate(g)
            session.status = "plan_ready · dừng cổng " + g
        else:
            lc.guardrail_pass()
            session.status = "plan_ready · released (không cổng)"

        return self._finish(session, lc, store, persist)

    # ── dựng plan ────────────────────────────────────────────────────
    def _plan(self, kind: str, entry_agent: str) -> list[FlowStep]:
        flow = flow_for(kind)
        if flow:
            return list(flow)
        # `cong_cu`: chủ là LỆNH/SKILL/công cụ, không phải agent — không dựng bước agent
        # (ex.execute tra registry AGENT, tên lệnh sẽ thành tham chiếu treo). Vẫn giữ
        # guardrail: đầu ra công cụ có yếu tố y khoa vẫn phải qua `tham-dinh-dau-ra`.
        if kind == "cong_cu":
            return [GUARDRAIL_STEP]
        # single_task: một agent + guardrail; suy cổng từ GATE_HINTS
        gate = GATE_HINTS.get(entry_agent)
        step = FlowStep("task", "Việc lẻ", (sa(entry_agent),), gate=gate,
                        note="định tuyến thẳng agent chuyên trách")
        return [step, GUARDRAIL_STEP]

    def _run_step(self, session: Session, step: FlowStep, ex: AgentExecutor, signals: Signals) -> None:
        for agent in step.agents:
            if agent.condition and not signals.is_set(agent.condition):
                session.record({
                    "step": step.step_id, "title": step.title, "gate": step.gate,
                    "agent": agent.name, "status": "skipped",
                    "summary": f"nhánh không áp dụng — chưa phát hiện tín hiệu '{agent.condition}' trong request",
                    "tool_calls": [], "needs_input": "",
                    "condition": agent.condition, "signal_matched": False,
                })
                continue
            # Định tuyến PHÂN CẤP: nhạc trưởng tổng chọn owner của request; tại từng bước,
            # agent chuyên trách lại chọn đúng worker của capability hẹp hơn. Nhờ vậy G1
            # có thể dùng đúng 1 planner AIPOCH theo chủ đề thay vì nạp cả kho.
            stage = step.step_id if step.step_id.startswith("G") else None
            scoped = self.plugin_ownership.resolve_for_intent(
                "single_task",
                agent.name,
                request=session.request,
                stage=stage,
            )
            scoped_data = self._routing_with_availability(scoped)
            res = ex.execute(agent.name, self.registry, self.tools)
            session.record({
                "step": step.step_id, "title": step.title, "gate": step.gate,
                "condition": agent.condition, "signal_matched": bool(agent.condition),
                "worker_routing": scoped_data,
                **res.as_dict(),
            })

    def _routing_with_availability(self, decision) -> dict:
        """Gắn trạng thái runtime vào quyết định mà không thay owner canonical."""

        data = decision.as_dict()
        unavailable: list[dict] = []
        for worker_data, worker in zip(data["workers"], decision.workers):
            availability = self.worker_inventory.locate(worker)
            worker_data["available"] = availability.available
            worker_data["source"] = availability.source
            if not availability.available:
                unavailable.append(availability.as_dict())
        data["unavailable_workers"] = unavailable
        if unavailable and not data["status"].startswith("BLOCKED"):
            data["status"] = "READY_WITH_LOCAL_FALLBACK"
        return data

    # ── Năng lực 6+2: vòng re-route khi guardrail trả-về-sửa ─────────
    def _guardrail_reroute_loop(self, session: Session, lc: Lifecycle,
                                ex: AgentExecutor, verdict_fn: Callable[[Session], dict]) -> bool:
        """Chạy verdict guardrail; nếu TRẢ-VỀ-SỬA lỗi SỬA ĐƯỢC → re-route tới agent truy
        xuất/kiểm chứng rồi thử lại (≤ MAX_RETRIES qua `lifecycle.guardrail_fail`).

        Mỗi lần re-route ghi 1 mục trace + 1 checkpoint (artifact "log re-route" cho D3).
        Trả True nếu ĐẠT (đi tiếp sang cổng/release); False nếu BỊ BLOCK/leo thang (dừng ngay).
        `verdict_fn(session)` trả dict: {'status':'pass'} hoặc
        {'status':'returned_for_fix','code':<mã>,'reroute_to':<agent?>}.
        """
        while True:
            # FAIL-CLOSED: verdict_fn ném lỗi hoặc trả dị dạng → KHÔNG coi là pass (M3).
            try:
                verdict = verdict_fn(session)
            except Exception as e:  # noqa: BLE001 — seam sản xuất có thể ném bất kỳ; đóng cổng, không release
                verdict = {"status": "returned_for_fix", "code": "GUARDRAIL_ERROR", "reason": str(e)[:200]}
            if not isinstance(verdict, dict) or "status" not in verdict:
                verdict = {"status": "returned_for_fix", "code": "GUARDRAIL_INDETERMINATE"}
            if verdict["status"] == "pass":
                return True
            code = verdict.get("code", "?")
            # Lỗi verdict KHÔNG chẩn đoán được, HOẶC lỗi cổng-cứng (verdict.escalate=True: PII/
            # nhân quả/thiếu câu hỏi an toàn) → KHÔNG re-route auto-fix; block + leo thang NGAY.
            if code in _FAIL_CLOSED_CODES or verdict.get("escalate"):
                why = "cổng cứng (PII/nhân quả/an toàn)" if verdict.get("escalate") else "bất định/lỗi verdict"
                lc.to("blocked", f"guardrail {code} — LEO THANG NGAY ({why})")
                session.retries = lc.retries
                session.status = f"blocked · guardrail [{code}] {why} — leo thang bác sĩ NGAY"
                session.record({
                    "step": "guardrail", "title": "Chốt kiểm đầu ra 2 lớp", "gate": None,
                    "agent": "tham-dinh-dau-ra", "status": "blocked", "condition": None,
                    "signal_matched": False, "reroute_for": code,
                    "summary": f"guardrail [{code}] {why} — KHÔNG re-route auto-fix, LEO THANG bác sĩ NGAY",
                    "tool_calls": [], "needs_input": "bác sĩ xử lý thủ công",
                })
                return False
            can_retry = lc.guardrail_fail()          # ← MÃ SỐNG: tăng retries; False khi hết lượt
            session.retries = lc.retries
            if not can_retry:
                session.status = f"blocked · guardrail [{code}] quá {MAX_RETRIES} vòng — leo thang bác sĩ"
                session.record({
                    "step": "guardrail", "title": "Chốt kiểm đầu ra 2 lớp", "gate": None,
                    "agent": "tham-dinh-dau-ra", "status": "blocked", "condition": None,
                    "signal_matched": False, "reroute_for": code, "retry": lc.retries,
                    "summary": f"guardrail TRẢ-VỀ-SỬA [{code}] quá {MAX_RETRIES} vòng — LEO THANG bác sĩ",
                    "tool_calls": [], "needs_input": "bác sĩ xử lý thủ công",
                })
                return False
            reroute = verdict.get("reroute_to") or REROUTE_DEFAULT.get(code, "tra-cuu-chung-cu")
            res = ex.execute(reroute, self.registry, self.tools)
            # L1: KHÔNG che `status:'error'` của agent treo bằng 'reroute' — giữ để guard bắt được.
            rr_status = "error" if res.status == "error" else "reroute"
            session.record({
                "step": "reroute", "title": f"Re-route sửa lỗi guardrail [{code}]", "gate": None,
                "condition": None, "signal_matched": False, "reroute_for": code, "retry": lc.retries,
                **res.as_dict(),
                "summary": f"guardrail TRẢ-VỀ-SỬA [{code}] → re-route `{reroute}` "
                           f"(vòng {lc.retries}/{MAX_RETRIES}): {res.summary}",
                "status": rr_status,
            })
            session.checkpoint("reroute", None,
                               f"re-route [{code}] → {reroute} (vòng {lc.retries}/{MAX_RETRIES})",
                               {"code": code, "reroute_to": reroute, "retry": lc.retries})
            # lặp: verdict_fn gọi lại (production: sau khi agent sửa; test: lượt sau trả pass)

    def _finish(self, session: Session, lc: Lifecycle, store: ContextStore | None, persist: bool) -> Session:
        session.checkpoints.append({"lifecycle": lc.summary()})
        session.exit_code = lc.exit_code()  # type: ignore[attr-defined]
        if persist:
            (store or ContextStore()).save(session)
        return session

    # ── Năng lực 2: resume ───────────────────────────────────────────
    def resume(self, session_id: str, store: ContextStore | None = None) -> Session | None:
        return (store or ContextStore()).load(session_id)

    # ── Tự kiểm tích hợp (điều phối ⇄ registry) ──────────────────────
    def validate(self, *, check_runtime: bool = False) -> list[str]:
        """Cảnh báo nếu flow/việc lẻ/gate-hint/reroute tham chiếu agent không có trong
        registry (tham chiếu treo). Quét CẢ 4 nguồn: flows.py (all_agents_in_flows),
        intent.SINGLE_TASK_RULES, GATE_HINTS.keys(), REROUTE_DEFAULT.values() — trước đây
        chỉ quét flows.py nên agent treo trong 3 nguồn còn lại lọt lưới (vá 2026-07-11)."""
        warns: list[str] = []
        referenced: set[str] = set(all_agents_in_flows())
        referenced.update(agent for _kws, agent, _note in SINGLE_TASK_RULES)
        referenced.update(GATE_HINTS.keys())
        referenced.update(REROUTE_DEFAULT.values())
        for name in sorted(referenced):
            if not self.registry.has(name):
                warns.append(f"Flow/việc lẻ/gate-hint/reroute tham chiếu agent KHÔNG có trong registry: `{name}`")
        warns += self.registry.validate()
        warns += self.plugin_ownership.validate(set(self.registry.agents))
        if check_runtime:
            for availability in self.worker_inventory.audit(self.plugin_ownership):
                if not availability.available:
                    if availability.reason == LY_DO_CHUA_CAI:
                        # ⚪ KHÔNG phải lỗi thật — plugin third-party chưa cài trên MÁY
                        # ĐANG CHẠY, khác binding treo/cấu hình sai. Cùng phân loại đã
                        # dùng ở verify_plugin_orchestration.py (BH08/BH85): gộp chung
                        # vào `warns` không tiền tố sẽ biến "chưa biết/chưa cài" thành
                        # "có vấn đề" — đúng anti-pattern BH08 đã vá nhiều lần trong repo
                        # này. Tiền tố ⚪ để caller (run_orchestrator.py --validate) tách
                        # khỏi quyết định exit-code mà KHÔNG mất khả năng hiển thị.
                        warns.append(
                            f"⚪ worker binding chưa kiểm được: {availability.worker} — {availability.reason}")
                    else:
                        warns.append(f"worker binding không khả dụng: {availability.worker} — {availability.reason}")
        warns += self.knowledge.verify_against_ssot()
        return warns

    # ── báo cáo năng lực (cho CLI/self-doc) ──────────────────────────
    def capabilities(self) -> dict:
        c = self.registry.counts()
        return {
            "1_dieu_phoi_agent": (f"{c['total']} agent · 2 nhạc trưởng + guardrail; flow lâm sàng 8 bước "
                                  f"(nhánh chuyên biệt/chẩn đoán/CLS có điều kiện) / nghiên cứu G0–G10 "
                                  f"(agent PROM/mô hình/kinh tế/định tính có điều kiện qua {len(SIGNAL_CUES)} tín hiệu)"),
            "2_quan_ly_ngu_canh": "Session + checkpoint + resume (~/.ebm-orchestrator)",
            "3_dinh_tuyen_intent": "IntentRouter: clinical_case / research_topic / single_task",
            "4_tich_hop_tri_thuc": f"{len(self.knowledge.tiers)} tầng nguồn (Cấp 0/0.5/1 + thuốc); thứ tự §2bis",
            "5_tich_hop_cong_cu": f"{len(self.tools.tools)} công cụ đăng ký ({sum(t.exists for t in self.tools.tools.values())} có trên đĩa)",
            "6_vong_doi_request": "Lifecycle: routed→planned→running→gate→guardrail→released/returned (retry ≤3, 4 mã thoát)",
            "7_dieu_phoi_plugin": (
                f"{len(self.plugin_ownership.capabilities)} capability · "
                f"{len(self.plugin_ownership.providers)} provider; một owner nội bộ/capability, "
                "plugin chỉ là worker và không được mở cổng người"
            ),
            "8_vong_khep_kin": (
                "định tuyến phân cấp theo từng bước + kiểm worker thật trên runtime + "
                f"guardrail re-route tối đa {MAX_RETRIES} vòng + LOCAL_FALLBACK khi thiếu plugin"
            ),
        }
