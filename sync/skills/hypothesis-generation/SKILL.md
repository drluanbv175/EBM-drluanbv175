---
name: hypothesis-generation
description: 'Hình thức hóa GIẢ THUYẾT khoa học từ quan sát/dữ liệu — sinh 3-5 giả thuyết CẠNH TRANH kèm CƠ CHẾ, chấm chất lượng theo 7 tiêu chí (khả kiểm định, khả bác bỏ theo Popper, tính đơn giản, sức giải thích, phạm vi, nhất quán, tính mới), rồi gợi ý pattern thiết kế thí nghiệm phân biệt giữa các giả thuyết. Dùng SAU khi đã có câu hỏi PICO/H0-H1 thô (cau-hoi-nghien-cuu, G0) và TRƯỚC khi chọn thiết kế (thiet-ke-nghien-cuu, G1) — lấp khoảng trống hình thức hóa giả thuyết mà 2 agent đó chưa có. Thuần tài liệu tham khảo + template LaTeX, chạy offline không cần API.'
allowed-tools: Read Write Edit Bash
license: MIT license
metadata: {"version": "1.1", "skill-author": "K-Dense Inc."}
---

<!-- EBM-VN-GUARD -->
> **⚕️ Bản điều chỉnh cho bác sĩ EBM ngoại trú (Việt Nam).** Skill gốc của K-Dense Inc. đã được chỉnh để phù hợp quy ước trong `CLAUDE.md` của người dùng.
>
> **QUY TẮC BẮT BUỘC — đọc trước, GHI ĐÈ mọi hướng dẫn tiếng Anh bên dưới:**
> 1. **Ngôn ngữ:** Mọi trao đổi và đầu ra cho người dùng viết bằng **tiếng Việt** (giữ thuật ngữ y khoa tiếng Anh khi cần; tên thuốc theo INN).
> 2. **Disclaimer:** Mọi đầu ra y khoa kết thúc bằng câu **"⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."**
> 3. **Nguồn:** Mọi nhận định/khuyến cáo phải **ghi nguồn (PMID/DOI)**; không có nguồn thì không khẳng định. **Tuyệt đối không bịa dữ liệu hay nguồn.**
> 4. **Không PII:** **KHÔNG** lưu hay tạo thông tin định danh bệnh nhân (tên, ngày sinh, số hồ sơ, địa chỉ...). Dùng mã ẩn danh.
> 5. **Chỉ nguồn miễn phí:** Khi tra cứu y văn dùng **PubMed E-utilities** (miễn phí, không cần API key) và các CSDL mở. **KHÔNG** dùng dịch vụ trả phí (parallel.ai, Perplexity, OpenRouter...). Nếu một lệnh gốc gọi `parallel-cli`/Perplexity, thay bằng `python scripts/pubmed_lookup.py "..."` hoặc REST miễn phí.
> 6. **Bối cảnh:** Bỏ qua phần chỉ phục vụ ngữ cảnh dược phẩm/pháp lý Mỹ (HIPAA/FDA/ICH-CSR) khi không liên quan ngoại trú VN; ưu tiên guideline quốc tế mới nhất rồi hiệu chỉnh theo Bộ Y tế VN.
>
> Phần kỹ thuật chi tiết (template, script, references) giữ nguyên tiếng Anh nhưng phải tạo ra **đầu ra tiếng Việt** theo các quy tắc trên.


# Scientific Hypothesis Generation

## Overview

Hypothesis generation is a systematic process for developing testable explanations. Formulate evidence-based hypotheses from observations, design experiments, explore competing explanations, and develop predictions. Apply this skill for scientific inquiry across domains.

## When to Use This Skill

This skill should be used when:
- Developing hypotheses from observations or preliminary data
- Designing experiments to test scientific questions
- Exploring competing explanations for phenomena
- Formulating testable predictions for research
- Conducting literature-based hypothesis generation
- Planning mechanistic studies across scientific domains

## Visual Enhancement

This skill does not include AI-based figure generation (no paid API calls). If a diagram would help — hypothesis framework, mechanistic pathway, experimental design flowchart, prediction decision tree — use the markdown-mermaid-writing skill instead.

---

## Workflow

Follow this systematic process to generate robust scientific hypotheses:

### 1. Understand the Phenomenon

Start by clarifying the observation, question, or phenomenon that requires explanation:

- Identify the core observation or pattern that needs explanation
- Define the scope and boundaries of the phenomenon
- Note any constraints or specific contexts
- Clarify what is already known vs. what is uncertain
- Identify the relevant scientific domain(s)

### 2. Conduct Comprehensive Literature Search

Search existing scientific literature to ground hypotheses in current evidence. Use both PubMed (for biomedical topics) and general web search (for broader scientific domains):

**For biomedical topics:**
- Use WebFetch with PubMed URLs to access relevant literature
- Search for recent reviews, meta-analyses, and primary research
- Look for similar phenomena, related mechanisms, or analogous systems

**For all scientific domains:**
- Use WebSearch to find recent papers, preprints, and reviews
- Search for established theories, mechanisms, or frameworks
- Identify gaps in current understanding

**Search strategy:**
- Begin with broad searches to understand the landscape
- Narrow to specific mechanisms, pathways, or theories
- Look for contradictory findings or unresolved debates
- Consult `references/literature_search_strategies.md` for detailed search techniques

### 3. Synthesize Existing Evidence

Analyze and integrate findings from literature search:

- Summarize current understanding of the phenomenon
- Identify established mechanisms or theories that may apply
- Note conflicting evidence or alternative viewpoints
- Recognize gaps, limitations, or unanswered questions
- Identify analogies from related systems or domains

### 4. Generate Competing Hypotheses

Develop 3-5 distinct hypotheses that could explain the phenomenon. Each hypothesis should:

- Provide a mechanistic explanation (not just description)
- Be distinguishable from other hypotheses
- Draw on evidence from the literature synthesis
- Consider different levels of explanation (molecular, cellular, systemic, population, etc.)

**Strategies for generating hypotheses:**
- Apply known mechanisms from analogous systems
- Consider multiple causative pathways
- Explore different scales of explanation
- Question assumptions in existing explanations
- Combine mechanisms in novel ways

### 5. Evaluate Hypothesis Quality

Assess each hypothesis against established quality criteria from `references/hypothesis_quality_criteria.md`:

**Testability:** Can the hypothesis be empirically tested?
**Falsifiability:** What observations would disprove it?
**Parsimony:** Is it the simplest explanation that fits the evidence?
**Explanatory Power:** How much of the phenomenon does it explain?
**Scope:** What range of observations does it cover?
**Consistency:** Does it align with established principles?
**Novelty:** Does it offer new insights beyond existing explanations?

Explicitly note the strengths and weaknesses of each hypothesis.

### 6. Design Experimental Tests

For each viable hypothesis, propose specific experiments or studies to test it. Consult `references/experimental_design_patterns.md` for common approaches:

**Experimental design elements:**
- What would be measured or observed?
- What comparisons or controls are needed?
- What methods or techniques would be used?
- What sample sizes or statistical approaches are appropriate?
- What are potential confounds and how to address them?

**Consider multiple approaches:**
- Laboratory experiments (in vitro, in vivo, computational)
- Observational studies (cross-sectional, longitudinal, case-control)
- Clinical trials (if applicable)
- Natural experiments or quasi-experimental designs

### 7. Formulate Testable Predictions

For each hypothesis, generate specific, quantitative predictions:

- State what should be observed if the hypothesis is correct
- Specify expected direction and magnitude of effects when possible
- Identify conditions under which predictions should hold
- Distinguish predictions between competing hypotheses
- Note predictions that would falsify the hypothesis

### 8. Present Structured Output

Generate a professional LaTeX document using the template in `assets/hypothesis_report_template.tex`. The report should be well-formatted with colored boxes for visual organization and divided into a concise main text with comprehensive appendices.

**Document Structure:**

**Main Text (Maximum 4 pages):**
1. **Executive Summary** - Brief overview in summary box (0.5-1 page)
2. **Competing Hypotheses** - Each hypothesis in its own colored box with brief mechanistic explanation and key evidence (2-2.5 pages for 3-5 hypotheses)
   - **IMPORTANT:** Use `\newpage` before each hypothesis box to prevent content overflow
   - Each box should be ≤0.6 pages maximum
3. **Testable Predictions** - Key predictions in amber boxes (0.5-1 page)
4. **Critical Comparisons** - Priority comparison boxes (0.5-1 page)

Keep main text highly concise - only the most essential information. All details go to appendices.

**Page Break Strategy:**
- Always use `\newpage` before hypothesis boxes to ensure they start on fresh pages
- This prevents content from overflowing off page boundaries
- LaTeX boxes (tcolorbox) do not automatically break across pages

**Appendices (Comprehensive, Detailed):**
- **Appendix A:** Comprehensive literature review with extensive citations
- **Appendix B:** Detailed experimental designs with full protocols
- **Appendix C:** Quality assessment tables and detailed evaluations
- **Appendix D:** Supplementary evidence and analogous systems

**Colored Box Usage:**

Use the custom box environments from `hypothesis_generation.sty`:

- `hypothesisbox1` through `hypothesisbox5` - For each competing hypothesis (blue, green, purple, teal, orange)
- `predictionbox` - For testable predictions (amber)
- `comparisonbox` - For critical comparisons (steel gray)
- `evidencebox` - For supporting evidence highlights (light blue)
- `summarybox` - For executive summary (blue)

**Each hypothesis box should contain (keep concise for 4-page limit):**
- **Mechanistic Explanation:** 1-2 brief paragraphs (6-10 sentences max) explaining HOW and WHY
- **Key Supporting Evidence:** 2-3 bullet points with citations (most important evidence only)
- **Core Assumptions:** 1-2 critical assumptions

All detailed explanations, additional evidence, and comprehensive discussions belong in the appendices.

**Critical Overflow Prevention:**
- Insert `\newpage` before each hypothesis box to start it on a fresh page
- Keep each complete hypothesis box to ≤0.6 pages (approximately 15-20 lines of content)
- If content exceeds this, move additional details to Appendix A
- Never let boxes overflow off page boundaries - this creates unreadable PDFs

**Citation Requirements:**

Aim for extensive citation to support all claims:
- **Main text:** 10-15 key citations for most important evidence only (keep concise for 4-page limit)
- **Appendix A:** 40-70+ comprehensive citations covering all relevant literature
- **Total target:** 50+ references in bibliography

Main text citations should be selective - cite only the most critical papers. All comprehensive citation and detailed literature discussion belongs in the appendices. Use `\citep{author2023}` for parenthetical citations.

**LaTeX Compilation:**

The template requires XeLaTeX or LuaLaTeX for proper rendering:

```bash
xelatex hypothesis_report.tex
bibtex hypothesis_report
xelatex hypothesis_report.tex
xelatex hypothesis_report.tex
```

**Required packages:** The `hypothesis_generation.sty` style package must be in the same directory or LaTeX path. It requires: tcolorbox, xcolor, fontspec, fancyhdr, titlesec, enumitem, booktabs, natbib.

**Page Overflow Prevention:**

To prevent content from overflowing on pages, follow these critical guidelines:

1. **Monitor Box Content Length:** Each hypothesis box should fit comfortably on a single page. If content exceeds ~0.7 pages, it will likely overflow.

2. **Use Strategic Page Breaks:** Insert `\newpage` before boxes that contain substantial content:
   ```latex
   \newpage
   \begin{hypothesisbox1}[Hypothesis 1: Title]
   % Long content here
   \end{hypothesisbox1}
   ```

3. **Keep Main Text Boxes Concise:** For the 4-page main text limit:
   - Each hypothesis box: Maximum 0.5-0.6 pages
   - Mechanistic explanation: 1-2 brief paragraphs only (6-10 sentences max)
   - Key evidence: 2-3 bullet points only
   - Core assumptions: 1-2 items only
   - If content is longer, move details to appendices

4. **Break Long Content:** If a hypothesis requires extensive explanation, split across main text and appendix:
   - Main text box: Brief mechanistic overview + 2-3 key evidence points
   - Appendix A: Detailed mechanism explanation, comprehensive evidence, extended discussion

5. **Test Page Boundaries:** Before each new box, consider if remaining page space is sufficient. If less than 0.6 pages remain, use `\newpage` to start the box on a fresh page.

6. **Appendix Page Management:** In appendices, use `\newpage` between major sections to avoid overflow in detailed content areas.

**Quick Reference:** See `assets/FORMATTING_GUIDE.md` for detailed examples of all box types, color schemes, and common formatting patterns.

## Quality Standards

Ensure all generated hypotheses meet these standards:

- **Evidence-based:** Grounded in existing literature with citations
- **Testable:** Include specific, measurable predictions
- **Mechanistic:** Explain how/why, not just what
- **Comprehensive:** Consider alternative explanations
- **Rigorous:** Include experimental designs to test predictions

## Resources

### references/

- `hypothesis_quality_criteria.md` - Framework for evaluating hypothesis quality (testability, falsifiability, parsimony, explanatory power, scope, consistency)
- `experimental_design_patterns.md` - Common experimental approaches across domains (RCTs, observational studies, lab experiments, computational models)
- `literature_search_strategies.md` - Effective search techniques for PubMed and general scientific sources

### assets/

- `hypothesis_generation.sty` - LaTeX style package providing colored boxes, professional formatting, and custom environments for hypothesis reports
- `hypothesis_report_template.tex` - Complete LaTeX template with main text structure and comprehensive appendix sections
- `FORMATTING_GUIDE.md` - Quick reference guide with examples of all box types, color schemes, citation practices, and troubleshooting tips

### Related Skills

When preparing hypothesis-driven research for publication, consult the **venue-templates** skill for writing style guidance:
- `venue_writing_styles.md` - Master guide comparing styles across venues
- Venue-specific guides for Nature/Science, Cell Press, medical journals, and ML/CS conferences
- `reviewer_expectations.md` - What reviewers look for when evaluating research hypotheses

