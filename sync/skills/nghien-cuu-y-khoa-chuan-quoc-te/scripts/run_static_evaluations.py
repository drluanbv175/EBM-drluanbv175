from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in root.rglob("*.md"))
checks = {
    "Cổng G0-G9": ["G0", "G9", "Sẵn sàng triển khai", "Sẵn sàng phân tích"],
    "Chống bịa đặt": ["Không tạo số liệu", "Không bịa"],
    "Dữ liệu và bảo mật Việt Nam": ["91/2025/QH15", "dữ liệu sức khỏe", "khử định danh"],
    "Đạo đức Việt Nam": ["43/2024/TT-BYT", "Hội đồng đạo đức"],
    "Khám chữa bệnh Việt Nam": ["15/2023/QH15"],
    "Đạo đức quốc tế": ["Declaration of Helsinki", "ICH E6(R3)"],
    "Chuẩn quan sát/dữ liệu thường quy": ["STROBE", "RECORD"],
    "Thử nghiệm lâm sàng": ["SPIRIT", "CONSORT"],
    "Tổng quan hệ thống": ["PRISMA"],
    "Chẩn đoán/dự báo/AI": ["STARD", "TRIPOD+AI"],
    "Khảo sát/PROM": ["COSMIN"],
    "Liêm chính công bố/AI": ["ICMJE", "AI không là tác giả"],
    "Kiểm thử sau upload": ["Ca 1.", "Ca 8.", "Model/phiên bản Claude"],
}
failed = []
for group, terms in checks.items():
    missing = [t for t in terms if t not in all_text]
    if missing:
        failed.append((group, missing))

if failed:
    print("KHÔNG ĐẠT: thiếu độ bao phủ chỉ dẫn")
    for group, missing in failed:
        print(f"- {group}: thiếu {', '.join(missing)}")
    sys.exit(1)

print("ĐẠT: gói skill bao phủ các neo nội dung an toàn, phương pháp và kiểm thử bắt buộc.")
print("Lưu ý: đây là đánh giá tĩnh; phải chạy ca kiểm thử trong Claude sau khi upload.")
