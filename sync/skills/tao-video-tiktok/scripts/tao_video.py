#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tao_video.py — Dựng video TikTok dọc 1080x1920 từ KỊCH BẢN văn bản.

Tính năng:
- Giọng đọc tiếng Việt MỀM MẠI, ngắt nghỉ tự nhiên (edge-tts: HoaiMy nữ / NamMinh nam),
  tự lùi về giọng macOS "Linh" khi mất mạng.
- Phụ đề ĐỘNG (karaoke) đồng bộ từng chữ với giọng (libass).
- 3 chế độ hình ảnh: kinetic (chữ trên nền), slide (trình chiếu ảnh), whiteboard (bảng trắng).
- Tuỳ chọn nhạc nền lồng dưới giọng (tự nhỏ tiếng + fade).

KHÔNG cần cài thêm gì khi chạy bằng python của venv ~/.ebm-venv
(đã có edge-tts + imageio-ffmpeg + Pillow). Xem README và SKILL.md.

Cách dùng:
    python tao_video.py KICH_BAN.md --out THU_MUC
Xem `python tao_video.py --help` và file references/cu-phap-kich-ban.md.
"""

import argparse
import asyncio
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import wave
from pathlib import Path

# ====================== HẰNG SỐ CHUNG ======================
W, H = 1080, 1920            # khung dọc TikTok
SR = 24000                   # tần số lấy mẫu (mono, 16-bit)
FPS = 30

# Bản đồ giọng đọc edge-tts (cần mạng); fallback offline = macOS "say -v Linh"
GIONG = {
    "nu": "vi-VN-HoaiMyNeural",     # nữ, dịu, mềm mại (mặc định)
    "nam": "vi-VN-NamMinhNeural",   # nam, trầm ấm
}

# Thời lượng nghỉ mặc định (giây) — tạo nhịp đọc "ngắt nghỉ, mềm mại"
NGHI = {
    "cau": 0.22,      # sau dấu . ! ?
    "ba_cham": 0.40,  # dấu … hoặc ...
    "doan": 0.55,     # hết một đoạn (dòng trống) — lấy hơi
    "dai": 0.80,      # dấu || do người soạn đặt
}


# ====================== TIỆN ÍCH ======================
def tim_ffmpeg() -> str:
    """Tìm ffmpeg: ưu tiên bản đi kèm imageio-ffmpeg, sau đó ffmpeg hệ thống."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        exe = shutil.which("ffmpeg")
        if exe:
            return exe
    sys.exit("❌ Không tìm thấy ffmpeg. Cài: pip install imageio-ffmpeg")


def slugify(text: str, max_len: int = 50) -> str:
    """Chuẩn hoá tiêu đề thành tên thư mục an toàn (bỏ dấu tiếng Việt)."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (text[:max_len] or "video").strip("-")


def hex_to_ass(hex_color: str) -> str:
    """#RRGGBB -> &H00BBGGRR (định dạng màu ASS, alpha 00 = đục)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"&H00{b:02X}{g:02X}{r:02X}"


def ass_time(t: float) -> str:
    """Giây -> H:MM:SS.cc (centisecond) cho file ASS."""
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    cs = int(round((t - int(t)) * 100))
    if cs == 100:
        cs = 0
        s += 1
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def chay(cmd, **kw):
    """Chạy lệnh con; báo lỗi rõ ràng nếu thất bại."""
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)
    if p.returncode != 0:
        err = p.stderr.decode("utf-8", "ignore")[-1500:]
        raise RuntimeError("Lệnh lỗi:\n  " + " ".join(map(str, cmd[:3])) + " ...\n" + err)
    return p


# ====================== ĐỌC & PHÂN TÍCH KỊCH BẢN ======================
def doc_kich_ban(path: Path):
    """
    Đọc file kịch bản (.md/.txt). Trả về (meta, blocks).

    Dòng directive bắt đầu bằng "::"  -> cấu hình (xem references/cu-phap-kich-ban.md).
    Dòng trống -> ngắt đoạn (lấy hơi). "::slide ẢNH" -> mở đoạn mới gắn ảnh.
    Các dòng còn lại = LỜI ĐỌC.
    """
    meta = {
        "tieu_de": "",          # tiêu đề ghim trên đầu video (tuỳ chọn)
        "voice": None,          # nu | nam | <id edge-tts>
        "rate": "-10%",         # tốc độ (âm = chậm hơn = mềm hơn)
        "pitch": "+0Hz",
        "che_do": "kinetic",    # kinetic | slide | whiteboard
        "nen": "gradient",      # gradient | toi | sang | #hex | đường-dẫn-ảnh
        "nhac": None,           # đường dẫn nhạc nền
        "hashtag": "",
        "nguon": [],            # PMID/DOI cho nội dung y khoa
        "disclaimer": None,     # None = tự suy đoán theo nội dung
        "zoom": None,           # None = tự quyết theo nền
    }
    blocks = []  # mỗi block: {"text": str, "image": str|None}
    cur_lines, cur_image = [], None

    def flush():
        nonlocal cur_lines, cur_image
        txt = " ".join(cur_lines).strip()
        if txt:
            blocks.append({"text": txt, "image": cur_image})
        cur_lines = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        s = line.strip()
        if s.startswith("::"):
            parts = s[2:].split(None, 1)
            key = parts[0].lower()
            val = parts[1].strip() if len(parts) > 1 else ""
            if key in ("slide", "anh", "image"):
                flush()
                cur_image = val or None
            elif key in ("tieu-de", "title"):
                meta["tieu_de"] = val
            elif key in ("voice", "giong"):
                meta["voice"] = val
            elif key in ("rate", "toc-do"):
                meta["rate"] = val
            elif key == "pitch":
                meta["pitch"] = val
            elif key in ("che-do", "mode"):
                meta["che_do"] = val
            elif key in ("nen", "background", "bg"):
                meta["nen"] = val
            elif key in ("nhac", "music"):
                meta["nhac"] = val or None
            elif key == "hashtag":
                meta["hashtag"] = val
            elif key in ("nguon", "source"):
                meta["nguon"].append(val)
            elif key == "disclaimer":
                meta["disclaimer"] = val
            elif key == "zoom":
                meta["zoom"] = val.lower() not in ("0", "off", "khong", "không", "no")
            # directive lạ -> bỏ qua
        elif s == "":
            flush()  # dòng trống = ngắt đoạn
        elif s.startswith("#") and not cur_lines and not blocks and not meta["tieu_de"]:
            meta["tieu_de"] = s.lstrip("# ").strip()  # tiêu đề Markdown đầu file
        else:
            cur_lines.append(line.strip())
    flush()

    if not blocks:
        sys.exit("❌ Kịch bản trống — không có lời đọc nào.")

    # Nếu chế độ slide nhưng có block thiếu ảnh -> dùng lại ảnh trước đó
    if meta["che_do"] == "slide":
        last = None
        for b in blocks:
            if b["image"]:
                last = b["image"]
            else:
                b["image"] = last
    return meta, blocks


def tach_cum(text: str):
    """
    Tách một đoạn lời thành danh sách (cụm_đọc, nghỉ_sau_giây).
    CHỈ tách ở dấu nghỉ do người soạn đặt: ||  …  ...  [Ns].
    Các câu trong cùng một cụm để edge-tts tự ngắt nghỉ tự nhiên -> ÍT request
    hơn nhiều, tránh bị dịch vụ chặn tần suất, mà nhịp đọc vẫn mềm mại.
    """
    text = re.sub(r"\.\.\.", "…", text)
    tokens = re.split(r"(\[\d+(?:\.\d+)?s\]|\|\||…)", text)
    phrases = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i].strip()
        pause = NGHI["cau"]  # nghỉ nhẹ mặc định cuối mỗi cụm
        if i + 1 < len(tokens):
            m = tokens[i + 1]
            if m == "||":
                pause = NGHI["dai"]
            elif m == "…":
                pause = NGHI["ba_cham"]
            elif m.startswith("["):
                nums = re.findall(r"[\d.]+", m)
                pause = float(nums[0]) if nums else pause
        if chunk:
            phrases.append((chunk, pause))
        i += 2
    return phrases


def xay_phrases(blocks):
    """Gộp toàn bộ block thành danh sách cụm đọc, gắn ảnh + chỉ số block."""
    phrases = []
    for bi, b in enumerate(blocks):
        ph = tach_cum(b["text"])
        if not ph:
            continue
        for k, (t, p) in enumerate(ph):
            if k == len(ph) - 1:
                p = max(p, NGHI["doan"])  # hết block -> nghỉ lấy hơi
            phrases.append({"text": t, "pause": p, "image": b.get("image"), "block": bi})
    return phrases


# ====================== TỔNG HỢP GIỌNG (TTS) ======================
async def _synth_edge(text, voice, rate, pitch, volume="+0%"):
    """
    edge-tts: trả (mp3_bytes, [(chữ, offset_giây, dur_giây), ...]).
    LƯU Ý: luôn truyền cả rate+volume+pitch — edge-tts 7.x báo "No audio"
    nếu đặt rate khác mặc định mà thiếu volume.
    """
    import edge_tts
    # boundary="WordBoundary" BẮT BUỘC để lấy mốc thời gian TỪNG CHỮ (làm phụ đề
    # karaoke). Mặc định của edge-tts là "SentenceBoundary" -> KHÔNG có mốc chữ.
    com = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch,
                               boundary="WordBoundary")
    audio = bytearray()
    words = []
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            words.append((ch["text"], ch["offset"] / 1e7, ch["duration"] / 1e7))
    return bytes(audio), words


def co_mang() -> bool:
    """Kiểm tra nhanh có kết nối tới dịch vụ edge-tts không."""
    import socket
    try:
        socket.create_connection(("speech.platform.bing.com", 443), timeout=4).close()
        return True
    except Exception:
        return False


async def _edge_retry(text, voice, rate, pitch, ff, attempts=8):
    """
    Gọi edge-tts có RETRY + BACKOFF. Dịch vụ Microsoft hay chặn tần suất khi
    gọi dồn (trả 'No audio'), nhưng thử lại với khoảng chờ tăng dần là được.
    Trả (pcm, words) khi thành công; None nếu hết lượt vẫn lỗi.
    """
    for i in range(attempts):
        try:
            mp3, words = await _synth_edge(text, voice, rate, pitch)
            if not mp3:
                raise RuntimeError("edge-tts trả audio rỗng")
            pcm = _to_pcm(mp3, ff)
            if pcm:
                return pcm, words
            raise RuntimeError("giải mã mp3 rỗng")
        except Exception:
            if i < attempts - 1:
                await asyncio.sleep(min(1.0 * (i + 1), 6.0))  # backoff tăng dần, tối đa 6s
    return None


def _to_pcm(data: bytes, ff: str, fmt_in=None) -> bytes:
    """Giải mã audio (mp3/aiff) -> PCM s16le mono 24k."""
    cmd = [ff, "-hide_banner", "-loglevel", "error"]
    if fmt_in:
        cmd += ["-f", fmt_in]
    cmd += ["-i", "pipe:0", "-ar", str(SR), "-ac", "1", "-f", "s16le", "pipe:1"]
    p = subprocess.run(cmd, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout


def _synth_say(text, ff):
    """Fallback offline: macOS `say -v Linh`. Không có mốc từng chữ -> chia đều."""
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
        aiff = f.name
    try:
        subprocess.run(["say", "-v", "Linh", "-o", aiff, text],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raw = Path(aiff).read_bytes()
    finally:
        try:
            os.unlink(aiff)
        except OSError:
            pass
    pcm = _to_pcm(raw, ff)
    dur = len(pcm) / 2 / SR
    toks = text.split()
    words = []
    if toks and dur > 0:
        step = dur / len(toks)
        for k, w in enumerate(toks):
            words.append((w, k * step, step * 0.92))
    return pcm, words


def co_chu(text: str) -> bool:
    """Có ký tự đọc được không (tránh tổng hợp cụm chỉ toàn dấu câu)."""
    return any(c.isalnum() for c in text)


async def _build_audio_async(phrases, voice, rate, pitch, ff):
    pcm_all = bytearray()
    timeline = []
    block_times = {}
    t = 0.0
    so_say = 0
    online = co_mang()
    if not online:
        print("   ⚠️  Không có mạng → dùng giọng offline 'Linh' cho toàn bộ.", file=sys.stderr)

    for ph in phrases:
        text = ph["text"]
        if not co_chu(text):
            # chỉ là dấu câu -> coi như một khoảng nghỉ
            t += ph["pause"]
            pcm_all += b"\x00\x00" * int(ph["pause"] * SR)
            continue

        pcm, words = None, None
        if online:
            res = await _edge_retry(text, voice, rate, pitch, ff)
            if res is not None:
                pcm, words = res
                await asyncio.sleep(0.2)  # nhẹ tay với dịch vụ giữa các cụm
        if pcm is None:
            if online:
                print(f"   ⚠️  Cụm bị chặn tần suất sau nhiều lần thử, dùng giọng 'Linh' cho cụm này.",
                      file=sys.stderr)
            pcm, words = _synth_say(text, ff)
            so_say += 1

        seg_start = t
        pcm_all += pcm
        seg_dur = len(pcm) / 2 / SR
        for (w, off, dur) in (words or []):
            gs = seg_start + off
            ge = min(seg_start + off + max(dur, 0.12), seg_start + seg_dur)
            if w.strip():
                timeline.append([w, gs, ge])
        t = seg_start + seg_dur

        # chèn khoảng lặng = nghỉ sau cụm (tạo nhịp ngắt nghỉ mềm mại)
        sil = int(ph["pause"] * SR)
        pcm_all += b"\x00\x00" * sil
        t += ph["pause"]

        bt = block_times.setdefault(ph["block"], [seg_start, t])
        bt[1] = t

    return bytes(pcm_all), timeline, block_times, t, so_say > 0


def build_audio(phrases, voice, rate, pitch, ff):
    """
    Tổng hợp toàn bộ giọng -> (pcm, timeline_chữ, block_times, tong_giay, dung_say).
    timeline_chữ: list [chữ, bắt_đầu, kết_thúc] trên trục thời gian toàn video.
    Chạy một vòng lặp asyncio duy nhất; retry/backoff vượt qua giới hạn tần suất edge-tts.
    """
    return asyncio.run(_build_audio_async(phrases, voice, rate, pitch, ff))


def write_wav(path: Path, pcm: bytes):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)


# ====================== PHỤ ĐỀ ĐỘNG (ASS) ======================
def nhom_dong(timeline, max_words=4, gap=0.55):
    """Gom các chữ thành dòng phụ đề ngắn (ngắt theo số chữ, dấu câu, khoảng nghỉ)."""
    lines, cur = [], []
    for i, (w, s, e) in enumerate(timeline):
        cur.append((w, s, e))
        het_cau = bool(re.search(r"[.!?…:;]$", w))
        gap_sau = (timeline[i + 1][1] - e) if i + 1 < len(timeline) else 99
        if len(cur) >= max_words or het_cau or gap_sau > gap:
            lines.append(cur)
            cur = []
    if cur:
        lines.append(cur)
    return lines


def _esc(w: str) -> str:
    return w.replace("{", "(").replace("}", ")").replace("\\", "/")


def kara_text(line):
    """Sinh chuỗi karaoke {\\kf..} để chữ sáng dần đúng lúc đọc."""
    start = line[0][1]
    cursor = start
    parts = []
    for (w, ws, we) in line:
        k = max(1, int(round((we - cursor) * 100)))  # centisecond tô đến hết chữ này
        parts.append(r"{\kf%d}%s " % (k, _esc(w)))
        cursor = we
    return "".join(parts).strip()


STYLE = {
    # nền tối -> chữ sáng
    "toi": dict(font="Arial Black", size=92, base="#F2F4F8", hi="#FFD24A",
                outline="#0A0F1A", border=6, shadow=2, back="#000000", marginv=760),
    # nền sáng -> chữ mực
    "sang": dict(font="Arial Black", size=92, base="#1F2937", hi="#2563EB",
                 outline="#FFFFFF", border=5, shadow=0, back="#FFFFFF", marginv=760),
    # bảng trắng -> mực + chữ tay
    "giay": dict(font="Bradley Hand", size=96, base="#2A2A28", hi="#C2410C",
                 outline="#FFFFFF", border=4, shadow=0, back="#FFFFFF", marginv=720),
}


def viet_ass(path: Path, timeline, tong_giay, st, tieu_de="", chan_text=""):
    """Tạo file .ass: phụ đề karaoke + (tuỳ chọn) tiêu đề ghim + dòng chân."""
    base = hex_to_ass(st["base"])
    hi = hex_to_ass(st["hi"])
    out = hex_to_ass(st["outline"])
    back = hex_to_ass(st["back"])

    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{st['font']},{st['size']},{hi},{base},{out},{back},1,0,0,0,100,100,0,0,1,{st['border']},{st['shadow']},2,80,80,{st['marginv']},1
Style: Title,{st['font']},56,{base},{base},{out},{back},1,0,0,0,100,100,0,0,1,5,1,8,90,90,140,1
Style: Foot,Arial,40,{base},{base},{out},{back},0,0,0,0,100,100,0,0,1,3,0,2,70,70,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if tieu_de:
        ev.append(f"Dialogue: 0,{ass_time(0)},{ass_time(tong_giay)},Title,,0,0,0,,"
                  f"{{\\fad(250,250)}}{_esc(tieu_de)}")
    if chan_text:
        ev.append(f"Dialogue: 0,{ass_time(0)},{ass_time(tong_giay)},Foot,,0,0,0,,"
                  f"{{\\fad(250,250)}}{_esc(chan_text)}")

    lines = nhom_dong(timeline)
    for i, line in enumerate(lines):
        start = line[0][1]
        nxt = lines[i + 1][0][1] if i + 1 < len(lines) else tong_giay
        end = min(line[-1][2] + 0.30, nxt)
        if end <= start:
            end = start + 0.4
        ev.append(f"Dialogue: 1,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,"
                  f"{{\\fad(120,90)}}{kara_text(line)}")

    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ====================== NỀN (Pillow) ======================
def nen_gradient(path: Path, top, bot):
    from PIL import Image
    base = Image.new("RGB", (1, H))
    for y in range(H):
        f = y / (H - 1)
        base.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3)))
    base.resize((W, H)).save(path)


def nen_solid(path: Path, rgb):
    from PIL import Image
    Image.new("RGB", (W, H), tuple(rgb)).save(path)


def nen_giay(path: Path):
    """Nền giấy trắng ngà có dòng kẻ mờ cho chế độ bảng trắng."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), (251, 250, 245))
    d = ImageDraw.Draw(img)
    for y in range(140, H, 96):
        d.line([(70, y), (W - 70, y)], fill=(228, 226, 214), width=2)
    img.save(path)


def hex_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def chuan_bi_nen(meta, st_key, tmp: Path):
    """Trả (đường_dẫn_nền_png_hoặc_ảnh, là_ảnh_người_dùng, nên_zoom)."""
    nen = meta["nen"]
    is_image = False
    bg = tmp / "bg.png"

    if meta["che_do"] == "whiteboard":
        nen_giay(bg)
        zoom = meta["zoom"] if meta["zoom"] is not None else True
        return bg, False, zoom

    if nen == "gradient":
        nen_gradient(bg, (22, 42, 68), (8, 14, 26))
    elif nen == "toi":
        nen_solid(bg, (12, 17, 28))
    elif nen == "sang":
        nen_gradient(bg, (244, 247, 251), (212, 222, 234))
    elif nen.startswith("#"):
        nen_solid(bg, hex_rgb(nen))
    else:
        p = Path(nen).expanduser()
        if not p.exists():
            print(f"   ⚠️  Không thấy ảnh nền '{nen}', dùng gradient mặc định.", file=sys.stderr)
            nen_gradient(bg, (22, 42, 68), (8, 14, 26))
        else:
            is_image = True
            bg = p
    zoom = meta["zoom"] if meta["zoom"] is not None else is_image
    return bg, is_image, zoom


# ====================== GHÉP VIDEO (ffmpeg) ======================
def _zoom_filter(dur):
    """Zoom rất chậm (Ken Burns) cho cảm giác mềm, sống động."""
    frames = max(1, int(dur * FPS))
    inc = 0.10 / frames  # tổng phóng to ~10%
    return (f"zoompan=z='min(zoom+{inc:.6f},1.10)':d=1:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")


def _scale_crop():
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}")


def ghep_kinetic(bg, is_image, zoom, voice_wav, ass, out_mp4, dur, music, darken, ff):
    """Một nền tĩnh/ảnh + phụ đề + giọng (+nhạc). Dùng cho kinetic & whiteboard."""
    vf = [_scale_crop(), "setsar=1"]
    if darken and is_image:
        vf.append(f"drawbox=0:0:{W}:{H}:black@0.38:t=fill")
    if zoom:
        vf.append(_zoom_filter(dur))
    else:
        vf.append(f"fps={FPS}")
    vf.append(f"ass={_ass_arg(ass)}")
    vchain = "[0:v]" + ",".join(vf) + "[v]"

    cmd = [ff, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1"]
    if zoom:
        cmd += ["-framerate", str(FPS)]
    cmd += ["-t", f"{dur:.3f}", "-i", str(bg), "-i", str(voice_wav)]

    filt = [vchain]
    amap = "1:a"
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        filt.append(_music_mix(dur))
        amap = "[aout]"
    cmd += ["-filter_complex", ";".join(filt), "-map", "[v]", "-map", amap,
            "-t", f"{dur:.3f}", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_mp4)]
    chay(cmd)


def ghep_slide(blocks, block_times, voice_wav, ass, out_mp4, dur, music, ff, tmp):
    """Trình chiếu ảnh: mỗi block hiện ảnh của nó đúng khoảng thời gian đang đọc."""
    # Thu thập (ảnh, thời lượng) theo thứ tự block
    fallback = tmp / "bg_fallback.png"
    nen_gradient(fallback, (22, 42, 68), (8, 14, 26))
    segs = []
    idxs = sorted(block_times.keys())
    for n, bi in enumerate(idxs):
        st, en = block_times[bi]
        if n == len(idxs) - 1:
            en = max(en, dur)  # block cuối kéo đến hết
        img = blocks[bi].get("image")
        p = Path(img).expanduser() if img else None
        if not p or not p.exists():
            if img:
                print(f"   ⚠️  Không thấy ảnh '{img}', dùng nền gradient.", file=sys.stderr)
            p = fallback
        segs.append((p, max(0.2, en - st)))

    cmd = [ff, "-hide_banner", "-loglevel", "error", "-y"]
    for (p, d) in segs:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", str(p)]
    cmd += ["-i", str(voice_wav)]
    audio_idx = len(segs)

    parts = []
    for i, (p, d) in enumerate(segs):
        parts.append(f"[{i}:v]{_scale_crop()},setsar=1,{_zoom_filter(d)}[v{i}]")
    concat_in = "".join(f"[v{i}]" for i in range(len(segs)))
    parts.append(f"{concat_in}concat=n={len(segs)}:v=1:a=0[vc]")
    parts.append(f"[vc]ass={_ass_arg(ass)}[v]")

    amap = f"{audio_idx}:a"
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        parts.append(_music_mix(dur, voice_label=f"{audio_idx}:a", music_label=f"{audio_idx+1}:a"))
        amap = "[aout]"

    cmd += ["-filter_complex", ";".join(parts), "-map", "[v]", "-map", amap,
            "-t", f"{dur:.3f}", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_mp4)]
    chay(cmd)


def _music_mix(dur, voice_label="1:a", music_label="2:a"):
    fade_st = max(0.0, dur - 1.4)
    return (f"[{music_label}]volume=0.12,afade=t=out:st={fade_st:.2f}:d=1.4[m];"
            f"[{voice_label}][m]amix=inputs=2:duration=first:dropout_transition=0[aout]")


def _ass_arg(ass: Path) -> str:
    """Tham số cho filter ass: escape dấu cho ffmpeg + chỉ thư mục font hệ thống."""
    p = str(ass).replace("\\", "/").replace(":", r"\:")
    fontsdir = "/System/Library/Fonts/Supplemental"
    if Path(fontsdir).exists():
        return f"{p}:fontsdir={fontsdir}"
    return p


# ====================== MÔ TẢ ĐĂNG BÀI ======================
def la_y_khoa(text: str) -> bool:
    tu = ["bệnh", "thuốc", "điều trị", "chẩn đoán", "lâm sàng", "huyết áp", "đái tháo",
          "ung thư", "kháng sinh", "triệu chứng", "guideline", "khuyến cáo", "pmid", "doi",
          "tăng huyết", "tim mạch", "đột quỵ", "bác sĩ", "liều", "tác dụng phụ"]
    low = text.lower()
    return sum(t in low for t in tu) >= 2


def viet_mo_ta(path: Path, meta, full_text, dung_say):
    """Sinh file mô tả/caption để dán khi đăng TikTok."""
    lines = []
    if meta["tieu_de"]:
        lines.append(meta["tieu_de"])
        lines.append("")
    is_med = meta["disclaimer"] if isinstance(meta["disclaimer"], str) else None
    auto_med = la_y_khoa(full_text) if meta["disclaimer"] is None else False
    if meta["disclaimer"] and meta["disclaimer"] not in ("0", "off", "khong"):
        lines.append("⚠️ " + (is_med or "Nội dung tham khảo — Cần bác sĩ kiểm chứng."))
    elif auto_med:
        lines.append("⚠️ Nội dung tham khảo, không thay thế tư vấn y tế. Cần bác sĩ kiểm chứng.")
    if meta["nguon"]:
        lines.append("Nguồn: " + " · ".join(meta["nguon"]))
    if meta["hashtag"]:
        lines.append("")
        lines.append(meta["hashtag"])
    if dung_say:
        lines.append("")
        lines.append("(Ghi chú: dựng bằng giọng offline 'Linh' do không có mạng lúc tạo.)")
    noi_dung = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).strip())
    path.write_text(noi_dung + "\n", encoding="utf-8")


# ====================== MAIN ======================
def main():
    ap = argparse.ArgumentParser(description="Dựng video TikTok có giọng đọc mềm + phụ đề động.")
    ap.add_argument("kich_ban", help="File kịch bản .md/.txt")
    ap.add_argument("--out", help="Thư mục xuất (mặc định: video_out/<slug>)")
    ap.add_argument("--voice", help="nu | nam | <id edge-tts> (ghi đè directive)")
    ap.add_argument("--rate", help="Tốc độ đọc, vd -10% (âm = chậm/mềm hơn)")
    ap.add_argument("--pitch", help="Cao độ, vd -2Hz")
    ap.add_argument("--che-do", dest="che_do", choices=["kinetic", "slide", "whiteboard"])
    ap.add_argument("--nen", help="gradient | toi | sang | #hex | đường-dẫn-ảnh")
    ap.add_argument("--nhac", help="Đường dẫn nhạc nền")
    ap.add_argument("--tieu-de", dest="tieu_de", help="Tiêu đề ghim trên đầu video")
    ap.add_argument("--khong-zoom", action="store_true", help="Tắt hiệu ứng zoom")
    ap.add_argument("--giu-tmp", action="store_true", help="Giữ file tạm để soi lỗi")
    args = ap.parse_args()

    kb = Path(args.kich_ban).expanduser()
    if not kb.exists():
        sys.exit(f"❌ Không thấy kịch bản: {kb}")

    ff = tim_ffmpeg()
    meta, blocks = doc_kich_ban(kb)

    # CLI ghi đè directive
    if args.voice:
        meta["voice"] = args.voice
    if args.rate:
        meta["rate"] = args.rate
    if args.pitch:
        meta["pitch"] = args.pitch
    if args.che_do:
        meta["che_do"] = args.che_do
    if args.nen:
        meta["nen"] = args.nen
    if args.nhac:
        meta["nhac"] = args.nhac
    if args.tieu_de:
        meta["tieu_de"] = args.tieu_de
    if args.khong_zoom:
        meta["zoom"] = False

    voice_id = GIONG.get((meta["voice"] or "nu").lower(), meta["voice"] or GIONG["nu"])
    full_text = " ".join(b["text"] for b in blocks)

    out_dir = Path(args.out).expanduser() if args.out else \
        kb.parent / "video_out" / slugify(meta["tieu_de"] or kb.stem)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="tiktok_"))

    print(f"🎬 Kịch bản: {kb.name}  |  chế độ: {meta['che_do']}  |  giọng: {voice_id}")
    try:
        # 1) Giọng đọc + mốc thời gian từng chữ
        print("🎙️  Đang tổng hợp giọng đọc (ngắt nghỉ mềm mại)...")
        phrases = xay_phrases(blocks)
        pcm, timeline, block_times, tong, dung_say = build_audio(
            phrases, voice_id, meta["rate"], meta["pitch"], ff)
        dur = tong + 0.4  # đuôi nhỏ
        voice_wav = out_dir / "voice.wav"
        write_wav(voice_wav, pcm)
        print(f"   ✔ {len(phrases)} cụm đọc, {len(timeline)} chữ, dài {dur:.1f}s"
              + ("  (giọng offline Linh)" if dung_say else ""))

        # 2) Phụ đề động
        print("📝 Đang tạo phụ đề động (karaoke)...")
        st_key = "giay" if meta["che_do"] == "whiteboard" else \
                 ("sang" if meta["nen"] == "sang" else "toi")
        st = STYLE[st_key]
        chan = ""
        if meta["nguon"]:
            chan = ("Nguồn: " + " · ".join(meta["nguon"]))[:80]
        # Ghi ASS vào thư mục TẠM (đường dẫn không dấu cách/ngoặc) để filter 'ass'
        # của ffmpeg không bị lỗi phân tích khi out_dir nằm trong path có dấu cách/(2).
        ass = tmp / "captions.ass"
        viet_ass(ass, timeline, dur, st, tieu_de=meta["tieu_de"], chan_text=chan)

        # 3) Ghép hình
        print("🖼️  Đang ghép hình + lồng tiếng...")
        out_mp4 = out_dir / "video.mp4"
        if meta["che_do"] == "slide":
            ghep_slide(blocks, block_times, voice_wav, ass, out_mp4, dur,
                       meta["nhac"], ff, tmp)
        else:
            bg, is_image, zoom = chuan_bi_nen(meta, st_key, tmp)
            if meta["zoom"] is False:
                zoom = False
            ghep_kinetic(bg, is_image, zoom, voice_wav, ass, out_mp4, dur,
                         meta["nhac"], darken=True, ff=ff)

        # 4) Mô tả đăng bài + lưu kịch bản đã đọc + bản phụ đề
        shutil.copy(str(ass), str(out_dir / "captions.ass"))
        viet_mo_ta(out_dir / "mo-ta.txt", meta, full_text, dung_say)
        (out_dir / "loi-doc.txt").write_text(full_text + "\n", encoding="utf-8")

        size_mb = out_mp4.stat().st_size / 1e6
        print(f"\n✅ XONG. Video dọc {W}x{H}, {dur:.1f}s, {size_mb:.1f} MB")
        print(f"   📹 {out_mp4}")
        print(f"   📄 {out_dir/'mo-ta.txt'} (caption + hashtag để dán khi đăng)")
    finally:
        if not args.giu_tmp:
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"   (file tạm giữ tại {tmp})")


if __name__ == "__main__":
    main()
