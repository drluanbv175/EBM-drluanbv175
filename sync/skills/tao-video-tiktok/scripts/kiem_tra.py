#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kiem_tra.py — Kiểm tra môi trường cho skill tạo video TikTok.
Chạy: python kiem_tra.py
In trạng thái edge-tts / ffmpeg / Pillow / giọng macOS và mạng.
"""
import shutil
import subprocess
import sys


def ok(b):
    return "✅" if b else "❌"


def main():
    print("== Kiểm tra môi trường tao-video-tiktok ==\n")
    print(f"Python: {sys.version.split()[0]}")

    # edge-tts
    try:
        import edge_tts
        print(f"{ok(True)} edge-tts {getattr(edge_tts, '__version__', '?')}  (giọng HoaiMy/NamMinh)")
        has_edge = True
    except Exception as e:
        print(f"{ok(False)} edge-tts CHƯA có — cài: pip install edge-tts   ({e})")
        has_edge = False

    # ffmpeg + libass
    ff = None
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"{ok(True)} ffmpeg (imageio): {ff}")
    except Exception:
        ff = shutil.which("ffmpeg")
        print(f"{ok(bool(ff))} ffmpeg hệ thống: {ff}")
    if ff:
        try:
            v = subprocess.run([ff, "-hide_banner", "-version"],
                               capture_output=True, text=True).stdout
            for cap in ("libass", "fontconfig", "libfreetype"):
                print(f"   {ok(cap in v)} {cap}")
        except Exception as e:
            print(f"   ⚠️ không đọc được cấu hình ffmpeg: {e}")

    # Pillow
    try:
        import PIL
        print(f"{ok(True)} Pillow {PIL.__version__}")
    except Exception:
        print(f"{ok(False)} Pillow CHƯA có — cài: pip install pillow")

    # macOS say (fallback offline)
    say = shutil.which("say")
    if say:
        out = subprocess.run([say, "-v", "?"], capture_output=True, text=True).stdout
        has_linh = "Linh" in out
        print(f"{ok(has_linh)} macOS 'say' giọng Linh (vi_VN) — fallback offline")
    else:
        print("⚠️  Không có lệnh 'say' (không phải macOS) — không có fallback offline.")

    # mạng cho edge-tts
    if has_edge:
        import socket
        try:
            socket.create_connection(("speech.platform.bing.com", 443), timeout=4).close()
            print("✅ Có mạng → dùng được giọng mềm HoaiMy/NamMinh.")
        except Exception:
            print("⚠️  Không kết nối được dịch vụ edge-tts → sẽ tự dùng giọng Linh.")

    print("\nXong. Nếu mọi mục ✅ là sẵn sàng dựng video.")


if __name__ == "__main__":
    main()
