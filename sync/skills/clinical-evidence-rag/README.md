# Clinical Evidence RAG - Huong dan cai dat & su dung

## 1. Cai dat
Dat ca thu muc clinical-evidence-rag/ vao mot trong cac vi tri:
- Personal (moi project): ~/.claude/skills/clinical-evidence-rag/
- Theo project: <project>/.claude/skills/clinical-evidence-rag/

Kiem tra Claude Code da nhan skill:
    /skills            # liet ke skill kha dung
Skill se tu kich hoat khi cau hoi cua ban lien quan toi mo ta cua no.

## 2. Nap nguon y van
Bo tai lieu vao dung thu muc con trong sources/ (PDF, .md, hoac .txt):
- Phac do vien -> sources/protocols/
- Guideline    -> sources/guidelines/
- Tong quan    -> sources/reviews/
- Bai bao goc  -> sources/papers/
Cap nhat sources/index.md moi khi them/bot tai lieu.

## 3. Cach dung - cau lenh goi y
- "Theo kho nguon cua toi, xu tri X o thai phu Y nhu the nao? Trich dan nguon."
- "Doi chieu phac do vien voi guideline moi nhat ve Z - co khac biet nao khong?"
- "Tom tat bang chung ve A, tach ro phan co nguon va phan suy luan."
- "Cap nhat index.md voi cac bai toi vua them vao sources/papers/."
- "Viet calculator cho B kem bo test cho cac nguong."

## 4. Luong lam viec khuyen nghi
1) Them/cap nhat nguon -> 2) Dat cau hoi lam sang -> 3) Doc cau tra loi co trich
dan -> 4) Mo nguon goc de kiem chung -> 5) Doi chieu boi canh benh nhan -> 6) Quyet dinh.

## 5. Luu y an toan
- Khong luu thong tin dinh danh benh nhan (PHI) trong kho.
- Skill chi ho tro tra cuu; phan doan cuoi cung thuoc ve bac si.
