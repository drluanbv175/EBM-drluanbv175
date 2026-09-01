"""Quyen so huu nhiem vu giua control plane EBM va cac plugin.

Registry JSON la nguon su that duy nhat. Plugin chi duoc lap ke hoach nhu worker;
owner noi bo chiu trach nhiem hop nhat ket qua, chay guardrail va dung o cong nguoi.
Module nay khong tu goi plugin, vi plugin duoc runtime Claude/Codex cung cap theo phien.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import ROOT

DEFAULT_REGISTRY_PATH = Path(__file__).with_name("plugin_ownership_registry.json")
HIGH_RISK = {"high", "critical"}


@dataclass(frozen=True)
class WorkerSpec:
    provider: str
    unit: str
    mode: str
    allowed_stages: tuple[str, ...] = ()
    match_any: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkerSpec":
        return cls(
            provider=str(data.get("provider", "")),
            unit=str(data.get("unit", "")),
            mode=str(data.get("mode", "worker")),
            allowed_stages=tuple(str(x) for x in data.get("allowed_stages", [])),
            match_any=tuple(str(x).casefold() for x in data.get("match_any", [])),
        )

    @property
    def key(self) -> str:
        return f"{self.provider}:{self.unit}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "unit": self.unit,
            "mode": self.mode,
            "allowed_stages": list(self.allowed_stages),
            "match_any": list(self.match_any),
            "can_release_gate": False,
        }


@dataclass(frozen=True)
class CapabilitySpec:
    capability_id: str
    risk: str
    owner_provider: str
    owner_unit: str
    runtime: str = ""
    intent_kinds: tuple[str, ...] = ()
    entry_agents: tuple[str, ...] = ()
    hard_gates: tuple[str, ...] = ()
    workers: tuple[WorkerSpec, ...] = ()

    @classmethod
    def from_dict(cls, capability_id: str, data: dict[str, Any]) -> "CapabilitySpec":
        owner = data.get("owner") or {}
        return cls(
            capability_id=capability_id,
            risk=str(data.get("risk", "medium")),
            owner_provider=str(owner.get("provider", "")),
            owner_unit=str(owner.get("unit", "")),
            runtime=str(owner.get("runtime", "")),
            intent_kinds=tuple(str(x) for x in data.get("intent_kinds", [])),
            entry_agents=tuple(str(x) for x in data.get("entry_agents", [])),
            hard_gates=tuple(str(x) for x in data.get("hard_gates", [])),
            workers=tuple(WorkerSpec.from_dict(x) for x in data.get("workers", [])),
        )


@dataclass(frozen=True)
class PluginRoutingDecision:
    status: str
    capability_id: str
    risk: str
    owner_provider: str
    owner_unit: str
    runtime: str = ""
    workers: tuple[WorkerSpec, ...] = ()
    blocked_requests: tuple[str, ...] = ()
    hard_gates: tuple[str, ...] = ()
    rules: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "capability": self.capability_id,
            "risk": self.risk,
            "owner": {
                "provider": self.owner_provider,
                "unit": self.owner_unit,
                "runtime": self.runtime,
            },
            "workers": [worker.as_dict() for worker in self.workers],
            "blocked_requests": list(self.blocked_requests),
            "hard_gates": list(self.hard_gates),
            "rules": dict(self.rules),
        }


@dataclass
class PluginOwnershipRegistry:
    providers: dict[str, dict[str, Any]]
    capabilities: dict[str, CapabilitySpec]
    global_rules: dict[str, Any]
    canonical_research_hard_gates: tuple[str, ...]
    policy_id: str
    unbound_providers: frozenset[str] = frozenset()
    path: Path = DEFAULT_REGISTRY_PATH

    @classmethod
    def load(cls, path: Path = DEFAULT_REGISTRY_PATH) -> "PluginOwnershipRegistry":
        data = json.loads(path.read_text(encoding="utf-8"))
        caps = {
            capability_id: CapabilitySpec.from_dict(capability_id, raw)
            for capability_id, raw in (data.get("capabilities") or {}).items()
        }
        unbound = data.get("unbound_providers") or {}
        return cls(
            providers=dict(data.get("providers") or {}),
            capabilities=caps,
            global_rules=dict(data.get("global_rules") or {}),
            canonical_research_hard_gates=tuple(data.get("canonical_research_hard_gates") or ()),
            policy_id=str(data.get("policy_id", "")),
            unbound_providers=frozenset(str(x) for x in unbound.get("providers", [])),
            path=path,
        )

    def capability_for(self, kind: str, entry_agent: str) -> CapabilitySpec | None:
        """Uu tien intent tron ven, sau do moi toi agent chuyen trach."""
        if kind != "single_task":
            by_intent = [cap for cap in self.capabilities.values() if kind in cap.intent_kinds]
            if len(by_intent) == 1:
                return by_intent[0]
        by_agent = [cap for cap in self.capabilities.values() if entry_agent in cap.entry_agents]
        return by_agent[0] if len(by_agent) == 1 else None

    def resolve(
        self,
        capability_id: str,
        requested_workers: tuple[str, ...] | list[str] | None = None,
        *,
        request: str = "",
        stage: str | None = None,
    ) -> PluginRoutingDecision:
        cap = self.capabilities.get(capability_id)
        if cap is None:
            return PluginRoutingDecision(
                status="BLOCKED_UNKNOWN_CAPABILITY",
                capability_id=capability_id,
                risk="unknown",
                owner_provider="",
                owner_unit="",
                blocked_requests=tuple(requested_workers or ()),
                rules=self.global_rules,
            )

        workers = list(cap.workers)
        blocked: list[str] = []
        if requested_workers is not None:
            known = {worker.key: worker for worker in workers}
            known.update({worker.unit: worker for worker in workers})
            selected: list[WorkerSpec] = []
            seen: set[str] = set()
            for request in requested_workers:
                worker = known.get(request)
                if worker is None:
                    blocked.append(request)
                elif worker.key not in seen:
                    selected.append(worker)
                    seen.add(worker.key)
            workers = selected
        else:
            # Worker có `match_any` là chuyên biệt: chỉ bật khi request thật sự mang tín
            # hiệu tương ứng. Worker không có cue là worker nền của capability.
            # Request rỗng (CLI/audit) cố ý trả toàn bộ binding để kiểm kê không bị che.
            text = request.casefold().strip()
            if text:
                workers = [
                    worker
                    for worker in workers
                    if not worker.match_any or any(cue in text for cue in worker.match_any)
                ]

        if stage:
            allowed: list[WorkerSpec] = []
            for worker in workers:
                if not worker.allowed_stages or stage in worker.allowed_stages:
                    allowed.append(worker)
                elif requested_workers is not None:
                    blocked.append(worker.key)
            workers = allowed

        workers.sort(
            key=lambda worker: int(self.providers.get(worker.provider, {}).get("priority", 0)),
            reverse=True,
        )
        status = "READY_WITH_OWNER" if not blocked else "READY_WITH_BLOCKED_WORKERS"
        return PluginRoutingDecision(
            status=status,
            capability_id=cap.capability_id,
            risk=cap.risk,
            owner_provider=cap.owner_provider,
            owner_unit=cap.owner_unit,
            runtime=cap.runtime,
            workers=tuple(workers),
            blocked_requests=tuple(blocked),
            hard_gates=cap.hard_gates,
            rules=self.global_rules,
        )

    def resolve_for_intent(
        self,
        kind: str,
        entry_agent: str,
        *,
        request: str = "",
        stage: str | None = None,
    ) -> PluginRoutingDecision:
        cap = self.capability_for(kind, entry_agent)
        if cap is not None:
            return self.resolve(cap.capability_id, request=request, stage=stage)
        if kind == "single_task" and entry_agent:
            return PluginRoutingDecision(
                status="READY_LOCAL_SPECIALIST_ONLY",
                capability_id="local_specialist_task",
                risk="contextual",
                owner_provider="local-agent",
                owner_unit=entry_agent,
                rules=self.global_rules,
            )
        return PluginRoutingDecision(
            status="BLOCKED_UNKNOWN_CAPABILITY",
            capability_id="unknown",
            risk="unknown",
            owner_provider="",
            owner_unit="",
            rules=self.global_rules,
        )

    def validate(self, local_agents: set[str] | None = None) -> list[str]:
        errors: list[str] = []
        if not self.policy_id:
            errors.append("registry thieu policy_id")
        if not self.global_rules.get("single_owner_per_capability"):
            errors.append("single_owner_per_capability phai bat")
        if not self.global_rules.get("plugins_are_workers_only"):
            errors.append("plugins_are_workers_only phai bat")
        if self.global_rules.get("plugin_may_release_human_gate") is not False:
            errors.append("plugin_may_release_human_gate phai la false")

        unknown_unbound = self.unbound_providers - set(self.providers)
        for provider in sorted(unknown_unbound):
            errors.append(f"unbound provider khong ton tai trong providers: {provider}")

        intent_owners: dict[str, str] = {}
        bound_plugin_providers: set[str] = set()
        for capability_id, cap in self.capabilities.items():
            provider = self.providers.get(cap.owner_provider)
            if provider is None:
                errors.append(f"{capability_id}: owner provider khong ton tai: {cap.owner_provider}")
                continue
            if not provider.get("may_own"):
                errors.append(f"{capability_id}: plugin/worker khong duoc lam owner: {cap.owner_provider}")
            if cap.risk in HIGH_RISK and provider.get("kind") == "plugin":
                errors.append(f"{capability_id}: capability nguy co cao khong duoc co plugin owner")
            if not cap.owner_unit:
                errors.append(f"{capability_id}: owner unit rong")
            if cap.owner_provider == "local-agent" and local_agents is not None:
                if cap.owner_unit not in local_agents:
                    errors.append(f"{capability_id}: owner agent khong ton tai: {cap.owner_unit}")
            if cap.runtime and not (ROOT / cap.runtime).exists():
                errors.append(f"{capability_id}: runtime khong ton tai: {cap.runtime}")

            for kind in cap.intent_kinds:
                if kind in intent_owners:
                    errors.append(
                        f"intent {kind} co nhieu owner: {intent_owners[kind]}, {capability_id}"
                    )
                intent_owners[kind] = capability_id

            seen_workers: set[str] = set()
            for worker in cap.workers:
                worker_provider = self.providers.get(worker.provider)
                if worker_provider is None:
                    errors.append(f"{capability_id}: worker provider khong ton tai: {worker.provider}")
                    continue
                if worker_provider.get("kind") != "plugin" or worker_provider.get("may_own"):
                    errors.append(f"{capability_id}: worker provider phai la plugin khong co quyen owner")
                bound_plugin_providers.add(worker.provider)
                if not worker.unit or not worker.mode:
                    errors.append(f"{capability_id}: worker thieu unit/mode")
                if any(not cue.strip() for cue in worker.match_any):
                    errors.append(f"{capability_id}: worker {worker.key} co match_any rong")
                if worker.key in seen_workers:
                    errors.append(f"{capability_id}: worker trung lap: {worker.key}")
                seen_workers.add(worker.key)

        for provider in sorted(bound_plugin_providers & self.unbound_providers):
            errors.append(
                f"provider vua unbound vua co worker binding: {provider}"
            )

        research = self.capabilities.get("research_lifecycle")
        if research is None:
            errors.append("thieu capability research_lifecycle")
        elif set(research.hard_gates) != set(self.canonical_research_hard_gates):
            errors.append("research_lifecycle hard_gates lech canonical_research_hard_gates")

        for required_kind in ("research_topic", "clinical_case"):
            if required_kind not in intent_owners:
                errors.append(f"intent {required_kind} chua co owner duy nhat")

        return errors

    def summary(self) -> dict[str, Any]:
        workers = sum(len(cap.workers) for cap in self.capabilities.values())
        conditional = sum(
            bool(worker.match_any)
            for cap in self.capabilities.values()
            for worker in cap.workers
        )
        return {
            "policy_id": self.policy_id,
            "providers": len(self.providers),
            "capabilities": len(self.capabilities),
            "worker_bindings": workers,
            "conditional_worker_bindings": conditional,
            "unbound_providers": len(self.unbound_providers),
            "research_hard_gates": list(self.canonical_research_hard_gates),
            "plugins_are_workers_only": self.global_rules.get("plugins_are_workers_only") is True,
        }
