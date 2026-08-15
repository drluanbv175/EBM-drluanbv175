# -*- coding: utf-8 -*-
"""
human_eval_score.py — TÍNH điểm đánh giá NGƯỜI THẬT cho CAFÉ-S (P3.2 κ + P4.2 Likert).
Chỉ TÍNH từ số do người chấm thật cung cấp; KHÔNG sinh/bịa điểm.
Dùng:
  python3 human_eval_score.py --kappa expert_kappa.csv --likert likert.csv
  python3 human_eval_score.py --selftest        # dữ liệu GIẢ để kiểm công cụ (không phải số thật)
CSV κ: mỗi dòng 1 ca; cột = nhãn của từng chuyên gia, giá trị ∈
  {khop_hoan_toan, khop_phan_lon, khac_biet_nho, khac_biet_lon, ai_nguy_hiem}
CSV Likert: mỗi dòng 1 phiếu; cột c1..c5 (điểm 1–5).
Cần bác sĩ kiểm chứng.
"""
import argparse
import csv
import sys

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
CATS=["khop_hoan_toan","khop_phan_lon","khac_biet_nho","khac_biet_lon","ai_nguy_hiem"]

def fleiss_kappa(rows):
    # rows: list of dict {category: count}; mỗi ca cùng số rater n
    N=len(rows)
    if N==0: return None,0
    n=sum(rows[0].values())
    mat=[[r.get(c,0) for c in CATS] for r in rows]
    if any(sum(r)!=n for r in mat): 
        raise ValueError("Số rater mỗi ca phải bằng nhau")
    Pi=[(sum(x*x for x in r)-n)/(n*(n-1)) for r in mat]
    Pbar=sum(Pi)/N
    pj=[sum(mat[i][j] for i in range(N))/(N*n) for j in range(len(CATS))]
    Pe=sum(p*p for p in pj)
    kappa=(Pbar-Pe)/(1-Pe) if (1-Pe)!=0 else float('nan')
    return kappa,n

def band_p32(k):
    if k is None: return 0,"thiếu dữ liệu"
    if k>=0.80: return 7,"excellent (κ≥0.80)"
    if k>=0.60: return 5,"pass (κ≥0.60)"
    if k>=0.40: return 3,"moderate"
    return 1,"kém (<0.40)"

def band_p42(m):
    if m is None: return 0,"thiếu dữ liệu"
    if m>=4.5: return 5,"excellent (≥4.5)"
    if m>=3.5: return 3.5,"pass (≥3.5)"
    if m>=2.5: return 2,"trung bình"
    return 1,"kém"

def load_kappa(path):
    rows=[]; danger=[]
    with open(path,encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        for i,r in enumerate(rd):
            labels=[v.strip() for k,v in r.items() if k.lower() not in("ca","case","case_id","ma_ca","note","ghi_chu","summary","agent_rec") and v.strip()]
            if not labels: continue
            cnt={c:0 for c in CATS}
            for lb in labels:
                if lb not in CATS: raise ValueError(f"Nhãn lạ '{lb}' (dòng {i+2}) — phải ∈ {CATS}")
                cnt[lb]+=1
            rows.append(cnt)
            if cnt["ai_nguy_hiem"]>0: danger.append(r.get("case_id") or r.get("ca") or f"row{i+2}")
    return rows,danger

def load_likert(path):
    crit=[[],[],[],[],[]]
    with open(path,encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            for j in range(5):
                v=r.get(f"c{j+1}")
                if v and v.strip(): crit[j].append(float(v))
    means=[(sum(c)/len(c) if c else None) for c in crit]
    allv=[x for c in crit for x in c]
    overall=sum(allv)/len(allv) if allv else None
    return means,overall

def report(krows,danger,lmeans,loverall):
    print("="*56)
    if krows is not None:
        k,n=fleiss_kappa(krows)
        pts,lab=band_p32(k)
        print(f"P3.2 ĐỒNG THUẬN CHUYÊN GIA: Fleiss κ = {k:.3f}  ({lab})  → {pts}/7 đ  | {len(krows)} ca × {n} chuyên gia")
        if danger: print(f"  🔴 CỜ ĐỎ — ca bị đánh 'AI nguy hiểm' (rà NGAY, không tính TB che lấp): {danger}")
        else: print("  ✅ Không ca nào bị đánh 'AI nguy hiểm'")
    if lmeans is not None:
        pts2,lab2=band_p42(loverall)
        print(f"\nP4.2 GIẢI THÍCH (Likert): TB tổng = {loverall:.2f}  ({lab2})  → {pts2}/5 đ")
        for j,m in enumerate(lmeans):
            print(f"   c{j+1} = {m:.2f}" if m is not None else f"   c{j+1} = (trống)")
    print("="*56)
    print("→ Cập nhật P3.2 + P4.2 vào _CHUAN-CAFES.md rồi cộng tổng. Cần bác sĩ kiểm chứng.")

def selftest():
    print("⚠️ SELF-TEST — DỮ LIỆU GIẢ, KHÔNG PHẢI SỐ THẬT (chỉ để kiểm công cụ chạy đúng)\n")
    # 4 ca, 3 chuyên gia
    mock=[{"khop_hoan_toan":3},{"khop_hoan_toan":2,"khop_phan_lon":1},
          {"khop_phan_lon":2,"khac_biet_nho":1},{"khop_hoan_toan":3}]
    means=[4.6,4.2,4.4,4.5,4.3]; overall=sum(means)/5
    report(mock,[],means,overall)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--kappa"); ap.add_argument("--likert"); ap.add_argument("--selftest",action="store_true")
    a=ap.parse_args()
    if a.selftest: selftest(); sys.exit(0)
    if not (a.kappa or a.likert): print("Cần --kappa và/hoặc --likert (hoặc --selftest)"); sys.exit(1)
    kr=dn=lm=lo=None
    if a.kappa: kr,dn=load_kappa(a.kappa)
    if a.likert: lm,lo=load_likert(a.likert)
    report(kr,dn,lm,lo)
