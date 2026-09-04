#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_vi.py — Việt hoá dòng MÔ TẢ hiện ra khi bác sĩ gõ `/` để gọi skill/lệnh/agent.

Dòng đó chính là trường `description:` trong YAML frontmatter của SKILL.md /
commands/*.md / agents/*.md. Script thay nó bằng bản tiếng Việt trong
`vi_descriptions.json`, và LƯU bản gốc vào `description-en:` ngay trong frontmatter.

Ba tính chất bắt buộc (vì file plugin bị ghi đè mỗi lần cập nhật):
  1. IDEMPOTENT — chạy lại bao nhiêu lần cũng ra cùng kết quả.
  2. KHÔI PHỤC ĐƯỢC — `--restore` trả mọi mô tả về nguyên bản tiếng Anh.
  3. KHÔNG IM LẶNG BỎ SÓT — khi plugin cập nhật làm đổi mô tả gốc, script
     BÁO ĐỘNG (mô tả tiếng Việt có thể đã lỗi thời) thay vì âm thầm giữ bản cũ;
     mục mới chưa có bản dịch cũng được liệt kê ra.

Cách dùng:
    python3 tools/vietnamize/apply_vi.py --dry-run    # xem trước, không ghi
    python3 tools/vietnamize/apply_vi.py              # áp bản dịch
    python3 tools/vietnamize/apply_vi.py --restore    # trả về tiếng Anh gốc
    python3 tools/vietnamize/apply_vi.py --report     # chỉ báo cáo độ phủ

CHẠY LẠI SAU MỖI LẦN CẬP NHẬT/CÀI THÊM PLUGIN — bản dịch nằm trong thư mục
cài đặt có số phiên bản nên sẽ mất khi plugin lên bản mới.
"""
from __future__ import annotations

# --- Ép stdout sang UTF-8 (vá 05/08/2026) ---------------------------------
# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt làm script chết giữa
# chừng bằng UnicodeEncodeError, trong khi phần việc chính đã chạy xong. Ép ở
# đây thay vì bắt người dùng nhớ đặt PYTHONIOENCODING trước mỗi lệnh.
import sys as _sys

for _luong in (_sys.stdout, _sys.stderr):
    if _luong is not None and (getattr(_luong, "encoding", "") or "").lower().replace("-", "") != "utf8":
        try:
            _luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass          # luồng bị chuyển hướng kiểu không reconfigure được — bỏ qua
# --------------------------------------------------------------------------

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "catalog_raw.json"
DICT = HERE / "vi_descriptions.json"

FM_KEY = re.compile(r"^([a-zA-Z_][\w-]*):", re.MULTILINE)
# Dấu tiếng Việt — dùng chung định nghĩa với extract_catalog.py (cùng thư mục)
from extract_catalog import VN_CHARS  # noqa: E402

# SỬA 2026-09-04 (Workflow đối kháng đa-agent vòng 2, MEDIUM) — VN_CHARS chỉ bắt
# ký tự CÓ DẤU, nên một mô tả tiếng Việt KHÔNG DẤU do bác sĩ tự gõ tay (cách gõ
# nhanh phổ biến, và CHÍNH `bo_dau.py` trong thư mục này sinh ra unaccented
# Vietnamese có chủ đích khi font không vẽ được dấu) bị đọc nhầm thành "chưa dịch"
# ở luật giữ-bản-tự-viết bên dưới — apply_vi.py sẽ ĐÈ bản không dấu tự viết bằng
# bản dịch từ điển (có dấu), mất nội dung gốc mà không một cảnh báo nào. Danh sách
# đủ ĐẶC HIỆU (không lẫn từ tiếng Anh thông thường) + đòi ≥3 khớp để không báo
# nhầm một câu tiếng Anh chỉ tình cờ chứa MỘT từ trùng ngẫu nhiên. Cố ý LOẠI các
# từ ngắn trùng từ/tên tiếng Anh thật (theo→"Theo", dan→"Dan", thong/tin→từ tiếng
# Anh thật, si→mượn tiếng Tây Ban Nha, bac→viết tắt "BAC", chan→từ hiếm nhưng có
# thật, moi/gia→dễ trùng tên riêng) để giảm rủi ro dương tính giả.
_TU_TIENG_VIET_KHONG_DAU = frozenset({
    "khong", "duoc", "cua", "nhung", "benh", "nhan", "kham", "thuoc",
    "dieu", "doan", "nghien", "cuu", "chung", "truoc", "hoac", "trong",
    "ngoai", "danh", "quyet", "dinh", "huong", "phuong", "phap", "nguoi",
})


def _co_dau_hieu_tieng_viet_khong_dau(text: str) -> bool:
    """True nếu văn bản có ≥3 từ trong danh sách đặc trưng tiếng Việt không dấu."""
    tu = re.findall(r"[a-z]+", text.lower())
    return sum(1 for t in tu if t in _TU_TIENG_VIET_KHONG_DAU) >= 3


def digest(text: str) -> str:
    """Vân tay của mô tả gốc — để phát hiện plugin đã đổi mô tả sau khi ta dịch."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """Tách (khối frontmatter, phần thân). Trả None nếu file không có frontmatter."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end], text[end:]


try:                                    # PyYAML là TÙY CHỌN: công cụ phải chạy được
    import yaml                         # cả trên máy chưa dựng venv.
except ImportError:                     # pragma: no cover
    yaml = None                         # type: ignore[assignment]


def read_field(block: str, key: str) -> str | None:
    """Đọc một trường trong frontmatter.

    Ưu tiên PyYAML vì đó là parser mà hệ thống thật dùng: mô tả dạng block scalar
    (`description: >` hoặc `|`) trải nhiều dòng, nếu tự gộp bằng khoảng trắng sẽ
    ra giá trị KHÁC bản gốc — lỗi này từng làm 17 mục lưu sai `description-en`
    (2026-08-01), chỉ lộ ra khi kiểm bằng verify_vi.py.
    """
    if yaml is not None:
        try:
            data = yaml.safe_load(block)
            if isinstance(data, dict):
                val = data.get(key)
                if val is None:
                    return None
                return val if isinstance(val, str) else str(val)
        except Exception:               # noqa: BLE001 — frontmatter lạ thì dùng cách thủ công
            pass
    return _read_field_thu_cong(block, key)


def _read_field_thu_cong(block: str, key: str) -> str | None:
    """Đọc thủ công — chỉ dùng khi máy chưa có PyYAML."""
    lines = block.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if not m:
            continue
        buf = [m.group(1)]
        for nxt in lines[i + 1:]:
            if re.match(r"^[a-zA-Z_][\w-]*:", nxt) or nxt.startswith("---"):
                break
            if nxt.strip():
                buf.append(nxt.strip())
        val = " ".join(buf).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            # Chuỗi nháy kép có thể chứa escape (\" bên trong mô tả). Phải GIẢI MÃ,
            # không được bóc nháy thô: bóc thô làm dấu escape nhân đôi sau mỗi lần
            # ghi lại, hỏng dần bản mô tả gốc tiếng Anh.
            if val[0] == '"':
                try:
                    return json.loads(val)
                except json.JSONDecodeError:
                    pass
            val = val[1:-1]
        return val
    return None


def replace_field(block: str, key: str, value: str) -> str:
    """Thay (hoặc thêm) một trường, ghi ở dạng chuỗi nháy kép hợp lệ YAML.

    Dùng json.dumps vì JSON là tập con của YAML → an toàn với dấu tiếng Việt,
    dấu hai chấm, dấu ngoặc trong mô tả.
    """
    encoded = json.dumps(value, ensure_ascii=False)
    lines = block.splitlines()
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        if re.match(rf"^{re.escape(key)}:\s*", line):
            out.append(f"{key}: {encoded}")
            i += 1
            # Nuốt TRỌN phần tiếp nối của trường cũ, tới tận khoá kế tiếp ở cột 0.
            # Không được dừng ở dòng trống: mô tả dạng block scalar nhiều dòng
            # (`description: |`) có dòng trống ở giữa, dừng sớm sẽ để lại phần đuôi
            # thành rác phá vỡ frontmatter (đã xảy ra với skill learn và scgpt).
            while i < len(lines) and not re.match(r"^[a-zA-Z_][\w-]*:", lines[i]):
                i += 1
            replaced = True
            continue
        out.append(line)
        i += 1
    if not replaced:
        # chèn ngay sau `name:` nếu có, để frontmatter dễ đọc
        for idx, line in enumerate(out):
            if line.startswith("name:"):
                out.insert(idx + 1, f"{key}: {encoded}")
                break
        else:
            out.append(f"{key}: {encoded}")
    return "\n".join(out)


def trong_repo_git(path: Path) -> Path | None:
    """Trả thư mục gốc repo git chứa `path`, hoặc None nếu không nằm trong repo nào.

    Đi ngược lên tìm `.git`. Cố ý KHÔNG gọi lệnh `git` — repo nguồn của aipoch nặng
    778 MB, `git status` ở đó mất hơn 2 phút; kiểm sự tồn tại thư mục thì tức thì.

    SỬA 2026-09-04 (Workflow đối kháng đa-agent vòng 2, MEDIUM→cao hơn dự kiến) —
    PHẢI đi ngược từ đường dẫn ĐÃ RESOLVE SYMLINK, không phải đường dẫn cho trước.
    `~/.claude/skills/<skill>/SKILL.md` (43 skill của bác sĩ, đo thật 2026-09-04)
    là SYMLINK trỏ thẳng vào `sync/skills/<skill>/SKILL.md` — một file NẰM TRONG
    repo git đã track. Đi ngược từ đường dẫn SYMLINK thì tổ tiên của nó
    (`~/.claude/skills`, `~/.claude`, `~`) không hề chứa `.git`, nên hàng rào
    "skip-git-repo" (dựng 10/08/2026 để chặn CHÍNH kịch bản ghi tiếng Việt vào
    nguồn git-tracked) bị SYMLINK VÔ HIỆU HOÁ HOÀN TOÀN cho toàn bộ 43 skill này
    — đúng lớp nguy hiểm mà hàng rào đó sinh ra để chặn, chỉ khác cơ chế bỏ qua.
    `Path.resolve()` chỉ là syscall đọc symlink/stat, không phải lệnh git, nên
    không tái phạm vấn đề hiệu năng đã ghi ở trên.
    """
    that = path.resolve()
    for cha in [that, *that.parents]:
        if (cha / ".git").exists():
            return cha
    return None


def process(item: dict, vi_entry: dict, *, restore: bool, dry: bool,
            qua_ten: bool = False) -> str:
    """Trả về mã kết quả: applied | already | restored | nothing | skip-* | STALE."""
    path = Path(item["path"])
    if not path.exists():
        return "skip-missing"

    # RÀO AN TOÀN (2026-08-10): TUYỆT ĐỐI không ghi tiếng Việt vào file nằm trong một
    # repo git. Bình thường công cụ này chỉ chạm CACHE plugin (~/.claude/plugins/cache)
    # — cache là sản phẩm phái sinh, sửa vào đó không ảnh hưởng gì tới việc cập nhật.
    # NHƯNG với plugin cài kiểu "directory" (aipoch trỏ vào ~/Documents/GitHub/
    # medical-research-skills), `extract_catalog.py` sẽ trỏ thẳng vào NGUỒN mỗi khi
    # cache chưa dựng — máy mới, vừa gỡ-cài lại, hoặc vừa dọn cache. Ghi vào đó là
    # làm bẩn 605 file của một repo git ⇒ `git pull` lần sau XUNG ĐỘT và bác sĩ không
    # cập nhật được plugin nữa. Bỏ qua ở đây KHÔNG mất tiếng Việt: bản dịch sống
    # trong `vi_descriptions.json`, và cả `build_danh_muc.py` lẫn
    # `build_trang_tra_cuu.py` đều áp nó như LỚP PHỦ lúc dựng.
    if not restore:
        repo = trong_repo_git(path)
        if repo is not None:
            return "skip-git-repo"

    text = path.read_text(encoding="utf-8", errors="replace")
    parts = split_frontmatter(text)
    if parts is None:
        return "skip-nofrontmatter"
    block, body = parts

    cur_desc = read_field(block, "description") or ""
    saved_en = read_field(block, "description-en")

    if restore:
        # CHỈ khôi phục file do CHÍNH công cụ này sửa — nhận biết bằng vân tay
        # `description-src`. Không được dựa vào sự có mặt của `description-en`:
        # một số plugin (claude-code-harness) dùng chính tên trường đó cho cơ chế
        # đa ngữ riêng của họ, và bản vá này ra đời sau khi `--restore` lỡ xoá
        # trường ấy ở 39 skill của harness (2026-08-01).
        if saved_en is None or read_field(block, "description-src") is None:
            return "nothing"
        nb = replace_field(block, "description", saved_en)
        nb = "\n".join(l for l in nb.splitlines()
                       if not l.startswith("description-en:")
                       and not l.startswith("description-src:"))
        if not dry:
            path.write_text("---" + nb + body, encoding="utf-8")
        return "restored"

    vi = vi_entry.get("vi", "").strip()
    if not vi:
        return "no-translation"

    # Bản dịch khớp qua fallback THEO TÊN (không phải id riêng) mà mô tả đang có đã là
    # tiếng Việt do người viết tay (không mang dấu `description-src` của công cụ này)
    # → GIỮ NGUYÊN. Cùng một skill có thể vừa nằm trong kho plugin (mô tả tiếng Anh,
    # được dịch gọn) vừa nằm trong hub sync/skills của bác sĩ (mô tả tiếng Việt tự
    # viết, dài và kỹ hơn); khớp theo tên sẽ lấy bản gọn đè lên bản kỹ. Đã xảy ra
    # 03/08/2026 với hypothesis-generation, phát hiện khi soi diff Git.
    # GIỮ mô tả tiếng Việt DO NGƯỜI VIẾT — không đè bằng bản dịch trong từ điển.
    # `description-src` là dấu vết của CHÍNH apply_vi; vắng nó mà nội dung đã là
    # tiếng Việt nghĩa là file vốn được viết bằng tiếng Việt, không phải do đây dịch.
    # 24/08/2026 — TRƯỚC ĐÂY luật này chỉ chạy khi bản dịch khớp qua khoá `name:`,
    # nên đường khoá `id` vẫn đè được. Vô hại chừng nào catalog chỉ quét file plugin
    # (vốn tiếng Anh), nhưng ngay khi thêm Cowork — nơi chứa CHÍNH skill của bác sĩ —
    # nó đã đè mất mô tả tự viết của 3 skill (clinical-evidence-rag, ebm-master,
    # literature-review). Bỏ điều kiện `qua_ten`: nguồn gốc của khoá không đổi được
    # sự thật rằng mô tả đang có là do người viết.
    if ((VN_CHARS.search(cur_desc) or _co_dau_hieu_tieng_viet_khong_dau(cur_desc))
            and read_field(block, "description-src") is None):
        return "giữ-bản-việt-tự-viết"

    original_en = saved_en if saved_en is not None else cur_desc
    src_hash = read_field(block, "description-src")

    # Plugin đã cập nhật và đổi mô tả gốc → bản dịch có thể lỗi thời.
    stale = bool(src_hash) and src_hash != digest(original_en)

    if cur_desc == vi and saved_en is not None and not stale:
        return "already"

    nb = replace_field(block, "description", vi)
    nb = replace_field(nb, "description-en", original_en)
    nb = replace_field(nb, "description-src", digest(original_en))

    if not dry:
        bak = path.with_suffix(path.suffix + ".vi-bak")
        if not bak.exists():
            shutil.copy2(path, bak)
        path.write_text("---" + nb + body, encoding="utf-8")
    return "STALE" if stale else "applied"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="xem trước, không ghi")
    ap.add_argument("--restore", action="store_true", help="trả mô tả về tiếng Anh gốc")
    ap.add_argument("--report", action="store_true", help="chỉ báo cáo độ phủ")
    ap.add_argument("--tier", type=int, default=0, help="chỉ xử lý một tầng (1/2/3)")
    ap.add_argument("--tu-quet", action="store_true",
                    help="quét lại catalog TRƯỚC khi làm việc — bắt buộc sau khi plugin "
                         "cập nhật, vì catalog cũ còn trỏ vào thư mục phiên bản CŨ")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="chỉ KIỂM (ngầm --dry-run): im lặng khi mọi mô tả đã tiếng Việt, "
                         "mã thoát 1 khi có mục bị bản cập nhật plugin trả về tiếng Anh")
    args = ap.parse_args()
    if args.im_khi_on:
        args.dry_run = True

    if args.tu_quet:
        # 24/08/2026 — VÌ SAO BẮT BUỘC. `catalog_raw.json` ghi ĐƯỜNG DẪN TUYỆT ĐỐI có
        # kèm số phiên bản (…/claude-code-harness/5.11.0/…). Plugin cập nhật xong thì
        # thư mục ĐANG DÙNG đổi sang 5.12.0, còn catalog vẫn trỏ 5.11.0 — nơi tiếng
        # Việt vẫn còn nguyên. Chốt --im-khi-on đọc catalog cũ nên báo "sạch", trong
        # khi thư mục thật đang 100% tiếng Anh. Đo ngày 24/08: chốt báo sạch trong lúc
        # 147 mô tả (harness 85 + academic-research-skills 62) đã về tiếng Anh.
        # Cùng họ lỗi với `return` sớm 12/08: luật có chạy, chỉ là chạy trên dữ liệu
        # không còn đúng. Quét lại tốn ~1,3 giây — rẻ hơn nhiều so với hỏng im lặng.
        import subprocess
        r = subprocess.run([_sys.executable, str(HERE / "extract_catalog.py")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("✗ Quét lại catalog thất bại:", (r.stderr or r.stdout)[-400:])
            return 2
    if not CATALOG.exists():
        print("✗ Chưa có catalog_raw.json — chạy extract_catalog.py trước.")
        return 1
    if yaml is None and args.im_khi_on:
        # BH08: thiếu NGUYÊN LIỆU không phải bằng chứng có vấn đề. Parser thủ công
        # đọc sai mô tả nhiều dòng ⇒ sẽ báo "lệch" giả. Im lặng, đừng kêu oan.
        return 0
    if yaml is None and not (args.report or args.dry_run):
        # TỪ CHỐI GHI, không chỉ cảnh báo. Parser thủ công lưu SAI bản gốc với mô tả
        # nhiều dòng, và bản gốc sai thì --restore không trả lại được nữa — đúng kiểu
        # hỏng IM LẶNG đã xảy ra ngày 10/08/2026 với 6 file agent. Xem trước thì cho,
        # ghi đè thì không.
        print("✗ Máy chưa có PyYAML → TỪ CHỐI ghi (parser thủ công có thể lưu SAI bản\n"
              "  gốc với mô tả nhiều dòng, và bản gốc sai thì --restore vô dụng).\n"
              "  Chạy lại bằng venv đã có PyYAML:\n"
              "     ~/.ebm-venv/bin/python tools/vietnamize/apply_vi.py\n"
              "  Chỉ muốn xem trước thì thêm --dry-run (không cần PyYAML).")
        return 2
    items = json.loads(CATALOG.read_text(encoding="utf-8"))
    vi_map = json.loads(DICT.read_text(encoding="utf-8")) if DICT.exists() else {}

    if args.report:
        # Phải tính CẢ khoá `name:` — bỏ qua nó sẽ báo thiếu oan những mục đã dịch
        # qua fallback theo tên (toàn bộ bmad và nhóm claude.ai dùng kiểu khoá này).
        def da_dich(i: dict) -> bool:
            return (i["id"] in vi_map or f"name:{i['name']}" in vi_map
                    or i["already_vi"])

        for tier in (1, 2, 3):
            sub = [i for i in items if i["tier_guess"] == tier]
            have = sum(1 for i in sub if da_dich(i))
            print(f"  Tầng {tier}: {have}/{len(sub)} mục đã có mô tả tiếng Việt")
        missing = [i for i in items if i["tier_guess"] <= 2 and not da_dich(i)]
        print(f"\nTầng 1-2 CÒN THIẾU bản dịch: {len(missing)}")
        for i in missing[:15]:
            print(f"   - {i['id']}")
        if len(missing) > 15:
            print(f"   … và {len(missing)-15} mục nữa")
        return 0

    counts: dict[str, int] = {}
    stale_ids: list[str] = []
    for item in items:
        if args.tier and item["tier_guess"] != args.tier:
            continue
        # Khoá chính là id đầy đủ. Fallback `name:<tên>` để MỘT bản dịch áp cho mọi
        # bản sao cùng tên — bmad-method lặp nguyên bộ 50 skill ở cả 6 plugin con,
        # viết 300 dòng id cho cùng một nội dung là vô ích. id luôn thắng fallback.
        entry = vi_map.get(item["id"])
        qua_ten = entry is None
        entry = entry or vi_map.get(f"name:{item['name']}") or {}
        if not entry and not args.restore:
            continue
        res = process(item, entry, restore=args.restore, dry=args.dry_run,
                      qua_ten=qua_ten)
        counts[res] = counts.get(res, 0) + 1
        if res == "STALE":
            stale_ids.append(item["id"])

    if args.im_khi_on:
        n = counts.get("applied", 0)
        if not n:
            return 0
        print(f"⚠ VIỆT HOÁ BỊ TRẢ VỀ TIẾNG ANH: {n} mô tả — dấu hiệu plugin vừa cập nhật\n"
              "  (bản cập nhật tạo thư mục phiên bản MỚI với file gốc tiếng Anh; bản đã\n"
              "   Việt hoá nằm lại thư mục cũ). Sửa:\n"
              "     ~/.ebm-venv/bin/python tools/vietnamize/apply_vi.py --tu-quet")
        return 1

    mode = "XEM TRƯỚC (chưa ghi gì)" if args.dry_run else "ĐÃ GHI"
    print(f"=== {mode} ===")
    for k, v in sorted(counts.items()):
        print(f"  {k:20s}: {v}")
    if stale_ids:
        print("\n⚠ Mô tả GỐC đã đổi sau lần dịch trước (plugin cập nhật) —"
              " cần xem lại bản tiếng Việt:")
        for i in stale_ids:
            print(f"   - {i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
