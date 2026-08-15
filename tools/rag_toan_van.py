#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAG NGỮ NGHĨA cho kho toàn văn OA — hỏi câu tự nhiên, nhận ĐOẠN xếp hạng (Tầng-2, 16/08/2026).

Vì sao: mọi phép tra hiện có (doc_toan_van, «RAG» cũ) là KHỚP CHUỖI CON — hỏi
«chờ lâu có làm bệnh nhân bớt hài lòng không» sẽ trượt bài viết «waiting time was
inversely associated with satisfaction». Lớp này embedding TĨNH đa ngữ
(model2vec · minishlab/potion-multilingual-128M — đo thật 16/08: cùng nghĩa
Việt↔Anh 0.484 vs ngoài chủ đề 0.046, biên 10×; CPU tức thời, KHÔNG cần torch/GPU).

Trung thực phạm vi:
  · Máy chỉ XẾP HẠNG + TRÍCH VỊ TRÍ — không tóm tắt thay, không diễn giải thay.
  · Embedding tĩnh = nghĩa mức TỪ/CỤM gộp — đủ cho «tìm đoạn liên quan», KHÔNG phải
    hiểu suy luận; điểm số chỉ so SÁNH TƯƠNG ĐỐI trong một lượt hỏi.
  · Model tải một lần về ~/.cache/huggingface (ngoài OneDrive); offline chưa có
    cache → nói rõ và CHỈ đường, không lặng lẽ rơi về khớp chuỗi.

Phụ thuộc MỚI (bác sĩ duyệt «Tầng 2» 16/08): `model2vec` trong venv ~/.ebm-venv.
Máy Windows phải cài lại tay:  %USERPROFILE%\\.ebm-venv\\Scripts\\pip install model2vec

Dùng:  python3 tools/rag_toan_van.py --dung-index            # dựng/làm mới chỉ mục
       python3 tools/rag_toan_van.py --tim "chờ lâu có giảm hài lòng?" [--k 5]
       python3 tools/rag_toan_van.py --tim "..." --study <mã>  # kho của MỘT đề tài
Mã thoát: 0 · 1 thiếu kho/chỉ mục · 2 thiếu phụ thuộc/model.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
KHO_CHUNG = REPO / "EBM-Dashboards" / "toan_van_oa"
MODEL_ID = "minishlab/potion-multilingual-128M"
CO_DOAN, CHONG_LAN = 110, 25          # từ mỗi đoạn · từ gối nhau


def _nap_model():
    try:
        from model2vec import StaticModel
    except ImportError:
        print("🔴 Thiếu phụ thuộc `model2vec` — cài: ~/.ebm-venv/bin/pip install model2vec")
        return None
    try:
        return StaticModel.from_pretrained(MODEL_ID)
    except Exception as e:  # noqa: BLE001 — lần đầu cần mạng tải model
        print(f"🔴 Chưa tải được model ({type(e).__name__}) — cần mạng CHO LẦN ĐẦU; "
              "đã có cache thì chạy offline được. KHÔNG rơi về khớp chuỗi im lặng.")
        return None


def _van_ban(p: Path) -> str:
    try:
        return re.sub(r"\s+", " ", " ".join(ET.fromstring(p.read_bytes()).itertext()))
    except ET.ParseError:
        return ""


def _chunks(vb: str) -> list[str]:
    tu = vb.split()
    ra, i = [], 0
    while i < len(tu):
        ra.append(" ".join(tu[i:i + CO_DOAN]))
        i += CO_DOAN - CHONG_LAN
    return ra


def _kho(study: str | None) -> Path:
    if study:
        return REPO / "medical-ebm-automation" / "exports" / study / "toan_van_oa"
    return KHO_CHUNG


def dung_index(kho: Path) -> int:
    import numpy as np
    model = _nap_model()
    if model is None:
        return 2
    files = sorted(kho.glob("PMID-*.xml"))
    if not files:
        print(f"🔴 Kho trống: {kho}")
        return 1
    meta, texts = [], []
    for f in files:
        pm = re.search(r"PMID-(\d+)_PMC(\d+)", f.name)
        for j, ch in enumerate(_chunks(_van_ban(f))):
            meta.append({"pmid": pm.group(1), "pmc": pm.group(2), "doan": j})
            texts.append(ch)
    vec = model.encode(texts)
    vec = vec / (np.linalg.norm(vec, axis=1, keepdims=True) + 1e-9)
    rag = kho / ".rag"
    rag.mkdir(exist_ok=True)
    np.save(rag / "vec.npy", vec.astype("float32"))
    (rag / "chunks.jsonl").write_text(
        "\n".join(json.dumps({**m, "t": t}, ensure_ascii=False)
                  for m, t in zip(meta, texts)) + "\n", encoding="utf-8")
    (rag / "meta.json").write_text(json.dumps(
        {"model": MODEL_ID, "n_file": len(files), "n_doan": len(texts),
         "co_doan": CO_DOAN}, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Chỉ mục ngữ nghĩa: {len(files)} bài → {len(texts)} đoạn "
          f"(~{CO_DOAN} từ/đoạn) → {rag}")
    return 0


def tim(kho: Path, cau_hoi: str, k: int) -> int:
    import numpy as np
    rag = kho / ".rag"
    if not (rag / "vec.npy").exists():
        print(f"🔴 Chưa có chỉ mục cho {kho} — chạy --dung-index trước "
              "(kho đổi sau khi gom thêm bài thì cũng cần dựng lại).")
        return 1
    model = _nap_model()
    if model is None:
        return 2
    vec = np.load(rag / "vec.npy")
    rows = [json.loads(x) for x in
            (rag / "chunks.jsonl").read_text(encoding="utf-8").splitlines() if x]
    q = model.encode([cau_hoi])[0]
    q = q / (np.linalg.norm(q) + 1e-9)
    diem = vec @ q
    thu_tu = np.argsort(-diem)
    print(f"❓ «{cau_hoi}» — top {k} đoạn (xếp hạng ngữ nghĩa, điểm chỉ so tương đối):\n")
    da_in_pmid: set[str] = set()
    in_duoc = 0
    for idx in thu_tu:
        r = rows[int(idx)]
        if r["pmid"] in da_in_pmid:
            continue          # mỗi bài lấy đoạn TỐT NHẤT — tránh một bài chiếm cả bảng
        da_in_pmid.add(r["pmid"])
        print(f"  {diem[int(idx)]:.3f} · PMID {r['pmid']} · "
              f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{r['pmc']}/")
        print(f"        …{r['t'][:230]}…\n")
        in_duoc += 1
        if in_duoc >= k:
            break
    print("Máy chỉ XẾP HẠNG + TRÍCH VỊ TRÍ — diễn giải là của bác sĩ. "
          "Cần bác sĩ kiểm chứng.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="RAG ngữ nghĩa trên kho toàn văn OA")
    ap.add_argument("--tim", help="câu hỏi tự nhiên (Việt/Anh đều được)")
    ap.add_argument("--dung-index", action="store_true")
    ap.add_argument("--study", help="dùng kho của một đề tài thay vì kho chung")
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()
    kho = _kho(a.study)
    if not kho.exists():
        print(f"🔴 Không có kho: {kho}")
        return 1
    if a.dung_index:
        return dung_index(kho)
    if a.tim:
        return tim(kho, a.tim, a.k)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
