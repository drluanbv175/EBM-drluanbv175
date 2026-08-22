#!/usr/bin/env bash
# Nút bấm đúp (macOS) cho sync/nap-ban-nguon.sh — gọi lại đúng script đó,
# không chép nội dung sang đây (hai bản là hai thứ sẽ lệch nhau).
exec bash "$(dirname "${BASH_SOURCE[0]}")/nap-ban-nguon.sh" "$@"
