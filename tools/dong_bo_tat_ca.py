#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỒNG BỘ TẤT CẢ — một lệnh duy nhất cho toàn bộ việc đồng bộ giữa hai máy.

VÌ SAO CÓ (21/08/2026). Hệ có ĐỦ công cụ cho từng làn, nhưng **không có lối vào
duy nhất**: muốn máy này khớp máy kia, bác sĩ phải nhớ và gõ đúng thứ tự chín thứ
rời rạc — `sync_safety_check` · `link-skills` · `dong_bo_skill_claude_codex` ·
`enforce_agent_guardrails` · `sync_agents_to_codex` · `dong_bo_plugin_claude_codex`
· `dong_bo_hook_sessionstart` · `sync_memory` · `kiem_plugin_day_du`. Lệnh gộp duy
nhất đang có là `upgrade_verify.py`, nhưng nó kiểm HỆ AGENT (27 bước) và **không
chạm một làn đồng bộ nào**. Một quy trình phải nhớ chín bước là quy trình sẽ bị bỏ
sót bước — và bỏ sót ở đây không kêu, nó chỉ làm máy kia thiếu lặng lẽ.

THỨ TỰ Ở ĐÂY LÀ THỨ TỰ PHỤ THUỘC, KHÔNG PHẢI DANH SÁCH:
  ① AN TOÀN trước hết — `sync_safety_check` soi conflict-copy OneDrive, git hỏng,
     file lõi chưa tải, dấu hiệu máy khác vừa ghi. **🔴 là DỪNG TẤT CẢ**: đồng bộ
     khi cây thư mục đang hỏng là nhân bản cái hỏng sang máy kia.
  ② GIT — kênh vận chuyển bác sĩ đã chọn (21/08). Việc đã commit mà chưa đẩy thì
     máy kia không thấy; đây là chỗ hở mà không làn nào khác nhìn tới.
  ③–⑧ các làn nội dung: skill · agent · plugin · hook · bộ nhớ · kho công cụ.

BA LUẬT GIỮ CHO BÁO CÁO KHÔNG NÓI QUÁ:
  · **Thiếu NGUYÊN LIỆU ≠ HỎNG.** Làn không có nguyên liệu trên máy này (chưa có
    runtime Cowork, chưa có sổ khai) được ghi «bỏ qua» kèm lý do, không tô đỏ. Tô
    đỏ thứ chưa biết là biến CHƯA BIẾT thành CÓ VẤN ĐỀ (BH08) và bức tường đỏ giả
    sẽ dạy người ta bỏ qua cả cảnh báo thật.
  · **MẠNG là 🟡, CẤU HÌNH mới là 🔴.** Không hỏi được remote chỉ nghĩa là chưa
    biết; mạng bệnh viện chập chờn là chuyện thường (cùng phân tầng với
    `kiem_nguon_that`).
  · **Chỉ kể bước THẬT SỰ chạy.** Không có dòng tổng kết nào khẳng định một làn đã
    kiểm khi làn đó vừa bị bỏ qua.

    python3 tools/dong_bo_tat_ca.py              # KIỂM, không ghi gì (mặc định)
    python3 tools/dong_bo_tat_ca.py --ap-dung    # đồng bộ thật
    python3 tools/dong_bo_tat_ca.py --im-khi-on  # chỉ nói khi có việc (dùng cho hook)

Mã thoát: 0 = mọi làn khớp · 1 = có việc cần làm · 2 = phải DỪNG.
Thuần thư viện chuẩn. Chạy được trên macOS và Windows.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable                     # KHÔNG dùng chuỗi "python3": Windows không có lệnh đó


def ten_may() -> str:
    """Uỷ quyền cho tools/nhan_dien_may.py — MỘT nguồn duy nhất (cloud = «Cloud»).

    SỬA 2026-09-04 (Workflow đối kháng đa-agent vòng 2, MEDIUM) — trước bản vá,
    main() tự tính `may` bằng {"Darwin": "Mac", "Windows": "Windows"}.get(platform.
    system(), platform.system()) — đúng bản chép ten_may() mà nhan_dien_may.py
    (dựng 02/09/2026) sinh ra để THAY THẾ, vì hai bản chép giống hệt nhau ở
    dong_bo_plugin_claude_codex.py/kiem_plugin_day_du.py từng phân kỳ. Bản chép ở
    đây là bản chép THỨ BA chưa ai bắt được: không nhận diện phiên Claude Code
    trên web (biến môi trường CLAUDE_CODE_REMOTE=true) — đo sống trên chính phiên
    cloud đang chạy: bản chép cũ trả 'Linux' trong khi nguồn chuẩn trả 'Cloud'. Một
    máy Linux thật (không phải phiên cloud) vẫn nhận đúng tên hệ điều hành như cũ.
    """
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("nhan_dien_may", Path(__file__).resolve().parent / "nhan_dien_may.py")
    _m = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_m)
    return _m.ten_may()


@dataclass
class KetQua:
    """Kết quả một làn. `bo_qua` tách bạch với `ma` để báo cáo không nói quá."""

    ten: str
    ma: int = 0
    bo_qua: str = ""                    # lý do bỏ qua; rỗng = có chạy
    ghi_chu: list[str] = field(default_factory=list)

    @property
    def bieu_tuong(self) -> str:
        if self.bo_qua:
            return "◌"
        return {0: "🟢", 1: "🟡"}.get(self.ma, "🔴")


def chay(lenh: list[str], im: bool) -> tuple[int, str]:
    """Chạy một công cụ con, trả (mã thoát, đầu ra gộp)."""
    try:
        kq = subprocess.run(lenh, cwd=REPO, check=False, capture_output=True,
                            text=True, timeout=900)
    except (OSError, subprocess.SubprocessError) as exc:
        return 2, f"không chạy được: {exc}"
    ra = ((kq.stdout or "") + (kq.stderr or "")).strip()
    if not im and ra:
        print(ra)
    return kq.returncode, ra


def lan_cong_cu(ten: str, ten_file: str, co: list[str], im: bool) -> KetQua:
    """Làn chạy bằng một công cụ trong tools/. Thiếu file = BỎ QUA, không phải lỗi."""
    f = REPO / "tools" / ten_file
    if not f.is_file():
        return KetQua(ten, bo_qua=f"chưa có tools/{ten_file}")
    if not im:
        print(f"\n── {ten} " + "─" * max(0, 56 - len(ten)))
    ma, _ra = chay([PY, str(f), *co], im)
    return KetQua(ten, ma=ma)


def lan_git(im: bool) -> KetQua:
    """Kênh vận chuyển: việc đã commit mà chưa đẩy thì máy kia không bao giờ thấy.

    Cố ý KHÔNG tự commit và KHÔNG tự push: đẩy hộ là ra quyết định thay bác sĩ về
    thứ được công bố. Làn này chỉ NÓI RA khoảng cách.
    """
    kq = KetQua("Git (kênh giữa 2 máy)")
    git = shutil.which("git")
    if not git:
        kq.bo_qua = "máy không có git"
        return kq

    def g(*a: str) -> tuple[int, str]:
        r = subprocess.run([git, *a], cwd=REPO, check=False,
                           capture_output=True, text=True, timeout=120)
        return r.returncode, (r.stdout or "").strip()

    _, nhanh = g("rev-parse", "--abbrev-ref", "HEAD")
    kq.ghi_chu.append(f"nhánh {nhanh}")

    _, ban = g("status", "--porcelain")
    so_ban = len([d for d in ban.splitlines() if d.strip()])
    if so_ban:
        kq.ma = max(kq.ma, 1)
        kq.ghi_chu.append(f"{so_ban} thay đổi CHƯA commit — máy kia sẽ không thấy")

    ma_up, _ = g("rev-parse", "--abbrev-ref", "@{u}")
    if ma_up != 0:
        kq.ma = max(kq.ma, 1)
        kq.ghi_chu.append("nhánh chưa có upstream — chưa từng đẩy lên máy chủ")
        return kq

    # Hỏi remote. Không hỏi được là chuyện MẠNG ⇒ 🟡, không phải 🔴: dữ liệu không
    # sai đi vì mạng, chỉ là chưa biết. Gộp hai thứ này sẽ khiến bác sĩ quen bỏ qua
    # màu đỏ vì mạng bệnh viện hay chập chờn.
    ma_fetch, _ = g("fetch", "--quiet")
    if ma_fetch != 0:
        kq.ma = max(kq.ma, 1)
        kq.ghi_chu.append("không hỏi được máy chủ (mạng?) — chưa biết có lệch không")
        return kq

    _, dem = g("rev-list", "--left-right", "--count", "@{u}...HEAD")
    sau, truoc = (dem.split() + ["0", "0"])[:2]
    if truoc != "0":
        kq.ma = max(kq.ma, 1)
        kq.ghi_chu.append(f"{truoc} commit chưa ĐẨY — máy kia chưa nhận được")
    if sau != "0":
        kq.ma = max(kq.ma, 1)
        kq.ghi_chu.append(f"{sau} commit chưa KÉO — máy kia đã làm việc mới")
    if truoc == "0" and sau == "0" and not so_ban:
        kq.ghi_chu.append("khớp máy chủ")
    return kq


def lan_agent(ap_dung: bool, im: bool) -> KetQua:
    """Agent .claude/agents/*.md → .Codex/agents/*.toml, đúng thứ tự doctrine ghi:
    enforce → sync → check. Chế độ KIỂM chỉ chạy `--check` (không sinh lại mirror)."""
    kq = KetQua("Agent → Codex")
    if not im:
        print("\n── Agent → Codex " + "─" * 43)
    if ap_dung:
        for f, co in (("enforce_agent_guardrails.py", []), ("sync_agents_to_codex.py", [])):
            duong_dan = REPO / "tools" / f
            if not duong_dan.is_file():
                kq.bo_qua = f"chưa có tools/{f}"
                return kq
            ma, _ = chay([PY, str(duong_dan), *co], im)
            kq.ma = max(kq.ma, ma)
    kiem = REPO / "tools/sync_agents_to_codex.py"
    if not kiem.is_file():
        kq.bo_qua = "chưa có tools/sync_agents_to_codex.py"
        return kq
    ma, _ = chay([PY, str(kiem), "--check"], im)
    kq.ma = max(kq.ma, ma)
    return kq


def phai_dung_som(an_toan: KetQua) -> bool:
    """Chốt an toàn có đủ nặng để DỪNG mọi làn sau không.

    Tách thành hàm thuần để chốt hồi quy kiểm được HÀNH VI mà không phải chạy cả
    lệnh (bộ chốt phải nhanh và ngoại tuyến). Hai vế đều quan trọng:
      · ma >= 2 ⇒ DỪNG — đồng bộ khi cây thư mục hỏng là nhân bản cái hỏng.
      · BỎ QUA (máy chưa có công cụ) ⇒ KHÔNG dừng — thiếu nguyên liệu không phải
        bằng chứng nguy hiểm, và biến nó thành chặn là biến CHƯA BIẾT thành CÓ
        VẤN ĐỀ (BH08).
    """
    return an_toan.ma >= 2 and not an_toan.bo_qua


def cac_lan(ap_dung: bool = False, im: bool = False) -> list[tuple[str, object]]:
    """Bộ làn — NGUỒN DUY NHẤT, trả (tên, hàm chạy) theo đúng thứ tự phụ thuộc.

    `main()` LẶP TRÊN CHÍNH DANH SÁCH NÀY, nên «làn khai ra» và «làn chạy thật»
    không thể lệch nhau về mặt cấu trúc — bản đầu tách hai chỗ và chốt BH68 bắt
    được ngay là chúng đã lệch. Thêm một công cụ đồng bộ mới = thêm một dòng ở đây,
    và nó tự có mặt ở cả `--liet-ke-lan` lẫn lượt chạy.
    """
    def cong_cu(ten: str, ten_file: str, co: list[str]):
        return lambda: lan_cong_cu(ten, ten_file, co, im)

    khi_ap_dung = (["--ap-dung"] if ap_dung else [])
    khi_im = (["--im-khi-on"] if im else [])
    return [
        ("An toàn đồng bộ", cong_cu("An toàn đồng bộ", "sync_safety_check.py", [])),
        ("Git (kênh giữa 2 máy)", lambda: lan_git(im)),
        ("Skill → Claude + Codex", cong_cu("Skill → Claude + Codex",
                                           "dong_bo_skill_claude_codex.py", khi_ap_dung + khi_im)),
        ("Agent → Codex", lambda: lan_agent(ap_dung, im)),
        ("Plugin (2 máy + Codex)", cong_cu("Plugin (2 máy + Codex)",
                                           "dong_bo_plugin_claude_codex.py", khi_ap_dung + khi_im)),
        ("Hook SessionStart", cong_cu("Hook SessionStart", "dong_bo_hook_sessionstart.py",
                                      khi_ap_dung)),
        ("Bộ nhớ Claude", cong_cu("Bộ nhớ Claude", "sync_memory.py",
                                  [] if ap_dung else ["--dry-run"])),
        ("Kho công cụ", cong_cu("Kho công cụ", "kiem_plugin_day_du.py", khi_im)),
    ]


def ten_cac_lan(bo_qua_an_toan: bool = False) -> list[str]:
    """Chỉ tên các làn, suy từ `cac_lan()` — không có bản chép thứ hai."""
    ten = [t for t, _ in cac_lan()]
    return ten[1:] if bo_qua_an_toan else ten


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ toàn bộ giữa hai máy — một lệnh")
    ap.add_argument("--ap-dung", action="store_true", help="đồng bộ thật (mặc định chỉ kiểm)")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có việc (dùng cho hook)")
    ap.add_argument("--bo-qua-an-toan", action="store_true",
                    help="bỏ chốt an toàn ① — CHỈ dùng khi bác sĩ đã tự xử lý mục đỏ")
    ap.add_argument("--liet-ke-lan", action="store_true",
                    help="chỉ in danh sách làn mà lệnh này phủ, không chạy gì")
    ap.add_argument("--json", action="store_true", help="xuất JSON máy đọc")
    a = ap.parse_args()
    if a.liet_ke_lan:
        ten = ten_cac_lan(a.bo_qua_an_toan)
        if a.json:
            print(json.dumps({"lan": ten}, ensure_ascii=False, indent=2))
        else:
            print(f"Lệnh này phủ {len(ten)} làn, theo đúng thứ tự phụ thuộc:")
            for i, t in enumerate(ten, 1):
                print(f"  {i}. {t}")
        return 0
    im = a.im_khi_on or a.json
    may = ten_may()

    if not im:
        print("=" * 64)
        print(f"  ĐỒNG BỘ TẤT CẢ — máy {may} — chế độ "
              f"{'ÁP DỤNG' if a.ap_dung else 'KIỂM (không ghi gì)'}")
        print("=" * 64)

    ket: list[KetQua] = []
    lan = cac_lan(a.ap_dung, im)

    # ① Cổng an toàn. Đây là cổng CHẶN, không phải một mục trong danh sách: đồng bộ
    # khi cây thư mục đang hỏng là nhân bản cái hỏng sang máy kia.
    if a.bo_qua_an_toan:
        lan = lan[1:]
    else:
        an_toan = lan[0][1]()
        lan = lan[1:]
        ket.append(an_toan)
        if phai_dung_som(an_toan):
            an_toan.ghi_chu.append("DỪNG TẤT CẢ — các làn sau không chạy")
            # Đường dừng sớm vẫn phải TRẢ RA JSON. Bản đầu return thẳng nên
            # `--json` không in một ký tự nào: người gọi bằng máy nhận đầu ra rỗng
            # và không phân biệt được «dừng vì nguy hiểm» với «công cụ chết».
            if a.json:
                print(json.dumps({"may": may, "ap_dung": a.ap_dung, "ma": 2,
                                  "dung_som": "chot_an_toan_do",
                                  "lan": [{"ten": an_toan.ten, "ma": an_toan.ma,
                                           "bo_qua": "", "ghi_chu": an_toan.ghi_chu}]},
                                 ensure_ascii=False, indent=2))
                return 2
            print("\n⛔ DỪNG — chốt an toàn báo 🔴. KHÔNG đồng bộ gì khi cây thư mục "
                  "đang hỏng: làm vậy là nhân bản cái hỏng sang máy kia.")
            print("   Xử lý mục đỏ ở trên rồi chạy lại. Đã tự xử lý thì thêm "
                  "--bo-qua-an-toan.")
            return 2

    for _ten, chay_lan in lan:
        ket.append(chay_lan())

    da_chay = [k for k in ket if not k.bo_qua]
    tong = max([k.ma for k in da_chay], default=0)

    if a.json:
        print(json.dumps({"may": may, "ap_dung": a.ap_dung, "ma": tong,
                          "lan": [{"ten": k.ten, "ma": k.ma, "bo_qua": k.bo_qua,
                                   "ghi_chu": k.ghi_chu} for k in ket]},
                         ensure_ascii=False, indent=2))
        return tong
    if a.im_khi_on and tong == 0:
        return 0

    print("\n" + "=" * 64)
    print("  TỔNG KẾT")
    print("=" * 64)
    for k in ket:
        duoi = f"  ({k.bo_qua})" if k.bo_qua else (f"  {' · '.join(k.ghi_chu)}" if k.ghi_chu else "")
        print(f"  {k.bieu_tuong} {k.ten}{duoi}")
    bo = [k for k in ket if k.bo_qua]
    print("-" * 64)
    print(f"  {len(da_chay)} làn đã chạy" + (f" · {len(bo)} bỏ qua vì thiếu nguyên liệu" if bo else ""))
    if tong == 0:
        print("  🟢 Mọi làn đã chạy đều khớp."
              + (" (Chế độ KIỂM — chưa ghi gì.)" if not a.ap_dung else ""))
    elif tong == 1:
        print("  🟡 Có việc cần làm — xem các làn 🟡 ở trên."
              + ("  Chạy lại với --ap-dung để đồng bộ." if not a.ap_dung else ""))
    else:
        print("  🔴 Có làn hỏng — đọc phần tương ứng ở trên trước khi làm tiếp.")
    print("  Cần bác sĩ kiểm chứng — công cụ chỉ đồng bộ MÁY MÓC, không đụng nội dung y khoa.")
    return tong


if __name__ == "__main__":
    raise SystemExit(main())
