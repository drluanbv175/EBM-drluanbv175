"""tools_registry.py — Tầng TÍCH HỢP CÔNG CỤ: đăng ký các công cụ Python THẬT của hệ.

Mỗi công cụ có lệnh chạy được + agent dùng nó. `invoke(dry_run=True)` trả về lệnh SẼ chạy
(để plan/kiểm offline); `dry_run=False` gọi thật qua subprocess. Đánh dấu công cụ nào tồn tại
trên đĩa (một số nằm trong `medical-ebm-automation/`).
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from . import ROOT


@dataclass(frozen=True)
class Tool:
    tool_id: str
    rel_path: str          # đường dẫn script tương đối ROOT
    subcommand: str        # subcommand mặc định (vd 'grade', 'icer') hoặc ''
    description: str
    used_by: tuple[str, ...]
    requires_real_data: bool = False  # True = cần dữ liệu thật (không chạy được ở dry-run)

    @property
    def path(self) -> Path:
        return ROOT / self.rel_path

    @property
    def exists(self) -> bool:
        return self.path.exists()


TOOLS: tuple[Tool, ...] = (
    Tool("grade", "medical-ebm-automation/tools/clinical_calc.py", "grade",
         "Tổng hợp GRADE theo thuật toán chính thức (agent chấm domain)",
         ("tham-dinh-grade-nnt",)),
    Tool("nnt", "medical-ebm-automation/tools/clinical_calc.py", "nnt",
         "Tính ARR + NNT/NNH + 95%CI (chuẩn Altman)",
         ("tham-dinh-grade-nnt",)),
    Tool("power", "medical-ebm-automation/tools/run_g3_auto.py", "",
         "Tính cỡ mẫu/power (G3) — fallback mô phỏng qua skill statistical-power",
         ("co-mau-nghien-cuu",)),
    Tool("health-econ", "medical-ebm-automation/tools/health_econ_calc.py", "icer",
         "ICER/Markov/tornado/PSA cho phân tích kinh tế",
         ("kinh-te-y-te",)),
    Tool("clinical-checkpoint", "medical-ebm-automation/tools/clinical_checkpoint.py", "",
         "Kiểm tính hợp lệ checkpoint lâm sàng TRƯỚC khi resume (A2/S2)",
         ("dieu-phoi-lam-sang", "so-cai-ghi-nho")),
    Tool("stats", "medical-ebm-automation/tools/run_stats_analysis.py", "",
         "Chạy script phân tích trên dữ liệu THẬT (G6)",
         ("phan-tich-thong-ke",), requires_real_data=True),
    Tool("verify-dashboard", "EBM-Dashboards/tools/verify_dashboard.py", "",
         "Cổng liêm chính dashboard: PMID/DOI phân giải + disclaimer + không PII",
         ("huong-dan-lam-sang",)),
    Tool("upgrade-verify", "tools/upgrade_verify.py", "",
         "Một lệnh kiểm+đồng bộ toàn hệ (enforce→sync→check→routing→assess→audit)",
         ("(hệ thống)",)),
    Tool("gen-docx", "tools/gen_research_docx.py", "",
         "Xuất Word cho artifact (gói quyết định/GRADE-EtD/…)",
         ("dieu-phoi-lam-sang", "dieu-phoi-nghien-cuu")),
    Tool("research-pipeline", "medical-ebm-automation/tools/run_pipeline.py", "",
         "Orchestrator sản xuất duy nhất cho nghiên cứu G0-G10",
         ("dieu-phoi-nghien-cuu",)),
    Tool("g10-assemble", "medical-ebm-automation/tools/run_g10_assemble.py", "",
         "Lắp ráp, kiểm chất lượng và khóa manifest gói phát hành G10",
         ("dieu-phoi-nghien-cuu",)),
)

# Công cụ chạy-cổng nghiên cứu G0..G8 (medical-ebm-automation)
GATE_RUNNERS: dict[str, str] = {
    **{f"G{n}": f"medical-ebm-automation/tools/run_g{n}_auto.py" for n in range(0, 10)},
    "G10": "medical-ebm-automation/tools/run_g10_assemble.py",
}


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=lambda: {t.tool_id: t for t in TOOLS})

    def get(self, tool_id: str) -> Tool | None:
        return self.tools.get(tool_id)

    def for_agent(self, agent: str) -> list[Tool]:
        return [t for t in self.tools.values() if agent in t.used_by]

    def command(self, tool_id: str, args: list[str] | None = None, python: str | None = None) -> list[str]:
        t = self.tools[tool_id]
        py = python or sys.executable
        cmd = [py, str(t.path)]
        if t.subcommand:
            cmd.append(t.subcommand)
        cmd += (args or [])
        return cmd

    def invoke(self, tool_id: str, args: list[str] | None = None, *, dry_run: bool = True,
               python: str | None = None) -> dict:
        """dry_run=True: chỉ trả lệnh sẽ chạy. False: chạy thật (nếu công cụ tồn tại)."""
        t = self.tools.get(tool_id)
        if t is None:
            return {"ok": False, "error": f"không có công cụ '{tool_id}'"}
        cmd = self.command(tool_id, args, python)
        if not t.exists:
            return {"ok": False, "dry_run": dry_run, "cmd": cmd,
                    "note": f"[CẦN CÔNG CỤ] script chưa có trên đĩa: {t.rel_path}"}
        if dry_run:
            return {"ok": True, "dry_run": True, "cmd": cmd,
                    "note": "dry-run — lệnh sẽ chạy khi có LLM/dữ liệu thật"}
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
        return {"ok": proc.returncode == 0, "dry_run": False, "cmd": cmd,
                "returncode": proc.returncode, "stdout": proc.stdout[-2000:]}

    def inventory(self) -> list[dict]:
        return [{"id": t.tool_id, "exists": t.exists, "path": t.rel_path,
                 "used_by": list(t.used_by)} for t in self.tools.values()]
