#!/usr/bin/env python3
"""Đồng bộ công cụ dây chuyền dashboard: NGUỒN CHUẨN → mọi bản sao — tự vá bản tụt hậu.

Tên tệp giữ nguyên vì `tu_sua_chua.py`, BH174, CLAUDE.md và agents/A2·A10 gọi đúng tên
này; phạm vi đã mở rộng (xem MỞ RỘNG 17/11 dưới).

Vì sao tồn tại (01/09/2026): chốt ESD02 của
`medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py`
đòi BA bản surveillance_scan.py đồng nhất hash, và hook pre-commit fail-closed toàn cục
sẽ CHẶN MỌI commit khi chúng lệch. Trước công cụ này, bộ ba được giữ khớp BẰNG TAY —
nghĩa là với dây chuyền hằng ngày cơ chế đó không tồn tại (bài học BH41), và ca thật
01/09: bác sĩ bị chặn commit khoá công Ed25519 chỉ vì bản trên OneDrive đã lệch từ một
đợt cập nhật skill trước đó. Chốt PHÁT HIỆN (ESD02) đã có; đây là mảnh TỰ VÁ, nối vào
tu_sua_chua.py để mỗi phiên tự chạy.

MỞ RỘNG 17/11/2026 (BH179) — từ MỘT tệp sang MỌI tool của nguồn chuẩn. Ca thật: PR #402
vá `check_topic_relevance.py` ở nguồn (đọc khoá từ kho bí mật, model mới) và đã gộp,
nhưng dây chuyền trên máy thật nạp bản ở `EBM-Dashboards/tools/`
(`ban_sao_tran.duong_cong_cu_pipeline` ưu tiên bản đó, và `verify_dashboard.py` chèn
thư mục của CHÍNH NÓ vào đầu sys.path trước khi import). Bản đó còn cũ, chỉ đọc khoá từ
môi trường shell ⇒ cổng kiểm lạc chủ đề trả «BỎ QUA — Thiếu ANTHROPIC_API_KEY»: PR đã
gộp mà cổng vẫn trơ. BH11 đã PHÁT HIỆN lệch (đỏ lúc 12:49 cùng ngày) nhưng chỉ
`surveillance_scan.py` có đường tự vá — 7 tool còn lại lệch thì chỉ báo, không ai vá.

Danh sách tool nay TỰ DÒ từ thư mục nguồn (không viết cứng — BH11/BH20: danh sách viết
cứng mục ngay khi có tool mới), và phạm vi đích trùng ĐÚNG phạm vi BH11 canh:

  NGUỒN CHUẨN  sync/skills/cap-nhat-chung-cu-y-khoa/tools/*.py
  BẢN CHẠY     EBM-Dashboards/tools/<tên>     ngoài git — dây chuyền máy thật nạp bản này
               EBM_MASTER/skill_assets/<tên>  ngoài git
  HỢP ĐỒNG     sync/skills/dark-analyst/tools/surveillance_scan.py — RIÊNG tệp này (ESD02).
               dark-analyst là skill KHÁC: tool khác của nó khác là ĐÚNG (BH11); 8 tool
               dùng chung trong git đã có chốt CI test_skill_pipeline_tools_mirror_parity_20260908.py.

Luật chiều đồng bộ — chép NGUYÊN luật nội dung 21/08 (BH71 kề bên), KHÔNG tin mtime:
  (a) bản đích KHÔNG có dòng riêng so với nguồn → nguồn bao trùm → chép đè;
  (b) bản đích CÓ dòng riêng → GIỮ LẠI + in các dòng đó cho bác sĩ quyết —
      chép đè lúc này có thể xoá mất một bản vá mới hơn chưa hồi nguồn
      (BH11: bản vá UTF-8 từng chỉ nằm ở bản chạy, đẩy nguồn mù sẽ xoá nó);
  (c) ngoại lệ của (b), thêm 30/10/2026 (BH174): bản đích TRÙNG KHÍT một phiên
      bản ĐÃ COMMIT của ĐÚNG tệp nguồn tương ứng → nó chỉ tụt hậu, không thể chứa
      bản vá chưa hồi nguồn → chép đè như (a). Thiếu luật này, MỌI bản vá SỬA hoặc
      XOÁ một dòng có sẵn đều làm bản đích «có dòng riêng» — đúng ca #402. Không hỏi
      được git ⇒ về (b).
Bản đích không tồn tại = thiếu nguyên liệu, KHÔNG phải nguy hiểm (BH08) — bỏ qua, không
đỏ (không phải tool nào cũng có bản ở mọi nơi; máy Cloud không có EBM-Dashboards).
Thư mục nguồn vắng hoặc không có tool nào mới là lỗi (mã 2).

Mã thoát: 0 = khớp hết / đã vá xong · 1 = còn lệch (dry-run) hoặc còn bản bị giữ lại chờ
người quyết · 2 = lỗi vận hành. Cần bác sĩ kiểm chứng.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]

THU_MUC_NGUON = Path("sync/skills/cap-nhat-chung-cu-y-khoa/tools")
# Hai nơi BẢN CHẠY ngoài git — đúng hai nơi chốt BH11 canh (`NOI` trong chot_hoi_quy_bai_hoc.py).
THU_MUC_CHAY = (Path("EBM-Dashboards/tools"), Path("EBM_MASTER/skill_assets"))
# Bản sao TRONG git có hợp đồng riêng: chỉ surveillance_scan phải khớp cả bản dark-analyst (ESD02).
DICH_HOP_DONG = {"surveillance_scan.py": (Path("sync/skills/dark-analyst/tools"),)}
TOOL_ESD02 = "surveillance_scan.py"


def cac_cap_dong_bo(goc: Path) -> list[tuple[Path, Path]]:
    """Mọi cặp (nguồn, đích) tương đối với `goc` — TỰ DÒ mọi `*.py` của thư mục nguồn.

    Không lọc theo sự tồn tại của bản đích: đích vắng được xử lý (bỏ qua) ở `main`.
    """
    cap: list[tuple[Path, Path]] = []
    for p in sorted((goc / THU_MUC_NGUON).glob("*.py")):
        for thu_muc in (*DICH_HOP_DONG.get(p.name, ()), *THU_MUC_CHAY):
            cap.append((THU_MUC_NGUON / p.name, thu_muc / p.name))
    return cap


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _dong_thuc(p: Path) -> set:
    """Tập dòng KHÔNG rỗng của file — đơn vị so 'dòng riêng' của luật (a)/(b)."""
    return {d for d in p.read_text(encoding="utf-8").splitlines() if d.strip()}


def _blob_git(p: Path) -> str:
    """Mã blob git của tệp, tính không cần git; lệch dòng kết thúc (CRLF) ⇒ không khớp ⇒ về luật (b) thận trọng."""
    du_lieu = p.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(du_lieu) + du_lieu, usedforsecurity=False).hexdigest()


def _cac_ban_da_commit(goc: Path, nguon_rel: Path) -> set:
    """Mã blob mọi phiên bản của ĐÚNG tệp nguồn này trong lịch sử HEAD — không hỏi được git ⇒ rỗng (về luật (b))."""
    try:
        kq = subprocess.run(["git", "-C", str(goc), "log", "--format=", "--raw", "--no-abbrev", "--", nguon_rel.as_posix()],
                            capture_output=True, text=True, encoding="utf-8", timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return set()
    if kq.returncode != 0:
        return set()
    # Dòng raw: «:100644 100644 <blob cũ> <blob mới> M <đường dẫn>».
    blob = {x for dong in kq.stdout.splitlines() if dong.startswith(":") for x in dong.split()[2:4]}
    return blob - {"0" * 40}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ công cụ dây chuyền: nguồn chuẩn → bản chạy (BH11/BH179) + hợp đồng ESD02")
    ap.add_argument("--ap-dung", action="store_true",
                    help="Chép đè thật các bản đích mà nguồn bao trùm (mặc định: chỉ báo)")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="Im lặng khi mọi bản đã khớp (dùng cho tu_sua_chua/hook)")
    ap.add_argument("--goc", default=None,
                    help="Ghi đè thư mục gốc (chỉ dùng cho kiểm thử)")
    args = ap.parse_args()

    goc = Path(args.goc).resolve() if args.goc else REPO
    thu_muc_nguon = goc / THU_MUC_NGUON
    if not thu_muc_nguon.is_dir():
        print(f"⛔ Không thấy thư mục nguồn chuẩn: {thu_muc_nguon.as_posix()} — không có căn cứ đồng bộ.")
        return 2
    cap = cac_cap_dong_bo(goc)
    if not cap:
        print(f"⛔ Thư mục nguồn chuẩn không có tool nào (*.py): {thu_muc_nguon.as_posix()}")
        return 2

    lech_con_lai = 0
    khop = 0
    vang = 0
    da_va: list[Path] = []
    thong_diep: list[str] = []
    nguon_da_doc: dict[Path, tuple[str, set]] = {}
    da_commit: dict[Path, set] = {}   # hỏi git một lần mỗi tệp nguồn, chỉ khi có bản đích lệch
    for nguon_rel, dich_rel in cap:
        dich = goc / dich_rel
        if not dich.exists():
            # Không phải tool nào cũng có bản ở mọi nơi; máy Cloud không có EBM-Dashboards —
            # thiếu nguyên liệu không phải bằng chứng nguy hiểm (BH08).
            vang += 1
            continue
        nguon = goc / nguon_rel
        try:
            if nguon_rel not in nguon_da_doc:
                nguon_da_doc[nguon_rel] = (_sha(nguon), _dong_thuc(nguon))
        except (OSError, UnicodeDecodeError) as e:
            print(f"⛔ Không đọc được nguồn chuẩn {nguon_rel.as_posix()}: {e}")
            return 2
        hash_nguon, dong_nguon = nguon_da_doc[nguon_rel]
        try:
            if _sha(dich) == hash_nguon:
                khop += 1
                continue
            rieng = sorted(_dong_thuc(dich) - dong_nguon)
            if rieng:
                if nguon_rel not in da_commit:
                    da_commit[nguon_rel] = _cac_ban_da_commit(goc, nguon_rel)
                if _blob_git(dich) in da_commit[nguon_rel]:
                    rieng = []   # luật (c): bản cũ đã commit, không có gì để mất
        except (OSError, UnicodeDecodeError) as e:
            print(f"⛔ Không đọc được {dich_rel.as_posix()}: {e}")
            return 2
        if rieng:
            lech_con_lai += 1
            thong_diep.append(
                f"⛔ {dich_rel.as_posix()}: LỆCH và có {len(rieng)} dòng RIÊNG — giữ lại chờ bác sĩ"
                " (chép đè có thể xoá bản vá chưa hồi nguồn):")
            for d in rieng[:8]:
                thong_diep.append("     RIÊNG: " + d[:100])
        elif args.ap_dung:
            shutil.copyfile(nguon, dich)
            da_va.append(dich_rel)
            thong_diep.append(f"🔧 {dich_rel.as_posix()}: nguồn bao trùm — ĐÃ chép đè khớp nguồn chuẩn.")
        else:
            lech_con_lai += 1
            thong_diep.append(
                f"🟡 {dich_rel.as_posix()}: lệch nhưng nguồn bao trùm — chạy --ap-dung để vá.")

    on_het = lech_con_lai == 0
    if args.im_khi_on and on_het and not da_va:
        return 0
    so_tool = len({n for n, _ in cap})
    print(f"ĐỒNG BỘ CÔNG CỤ DÂY CHUYỀN — nguồn chuẩn: {THU_MUC_NGUON.as_posix()}/ ({so_tool} tool)")
    print(f"  ✅ {khop} bản khớp nguồn chuẩn · ⚪ {vang} chỗ không có bản sao trên máy này (bỏ qua, không phải lỗi)")
    for t in thong_diep:
        print("  " + t)
    if da_va:
        print(f"  Đã vá {len(da_va)} bản. Bản chạy ngoài git có hiệu lực NGAY, không cần commit.")
        if any(p.name == TOOL_ESD02 for p in da_va):
            print("  Kiểm lại ESD02: verify_evidence_surveillance_deployment.py --contract-check")
    print("Cần bác sĩ kiểm chứng.")
    return 0 if on_het else 1


if __name__ == "__main__":
    raise SystemExit(main())
