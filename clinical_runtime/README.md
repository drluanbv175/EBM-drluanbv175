# Clinical Runtime — EBM Copilot V2

**Status:** DRAFT — Governance schemas + static hardening verifier. No production runtime integration yet.
**Created:** 2026-06-28
**Updated:** 2026-07-15
**Owner:** Doctor (clinical PI) + Developer

---

## Purpose

This directory contains the **Clinical V2 Decision Contract** — a set of governance schemas, safety rules, and validation fixtures that define how the EBM Copilot system MUST behave before any clinical output is presented to a doctor.

These files are **read-only governance documents**. They do NOT yet run in production. The static hardening verifier (`tools/verify_clinical_runtime_schema_hardening.py`) checks that the contract now contains machine-readable controls for retracted sources, prompt injection, and conflicting evidence. See the Implementation Plan (`reports/CLINICAL_V2_IMPLEMENTATION_PLAN.md`) for the integration roadmap.

---

## Files

| File | Purpose |
|---|---|
| `CLINICAL_DECISION_CONTRACT.json` | Master contract: 9 INPUT fields + 11 OUTPUT fields + 5 release states + invariants |
| `OUTPUT_SCHEMA.json` | JSON Schema for every clinical output packet |
| `CLINICAL_PRACTICE_APPLY_GATE.json` | Machine-readable outpatient Evidence-to-Practice gate |
| `RED_FLAG_RULES_SCHEMA.json` | Structure for red flag rules + 3 example rules |
| `SAFETY_RULES_SCHEMA.json` | Structure for drug/source/security/evidence-conflict safety rules + examples |
| `LOCAL_PROTOCOL_SCHEMA.json` | Structure for local clinical protocols |
| `HUMAN_APPROVAL_SCHEMA.json` | Structure for doctor approval records |
| `ROLLBACK_SCHEMA.json` | Structure for rollback/retraction events |
| `VALIDATION_CASE_SCHEMA.json` | Structure for DEMO_TEST validation cases |
| `VALIDATION_CASE_LIBRARY/` | 10 synthetic test cases (see below) |

---

## Validation Case Library

10 DEMO_TEST cases covering all mandatory test categories:

| Case ID | Category | Tests |
|---|---|---|
| TC-001 | red_flag | System halts immediately on IMMEDIATE red flag |
| TC-002 | missing_data | Missing eGFR triggers request, not silent assumption |
| TC-003 | polypharmacy | CKD + polypharmacy triggers Beers/STOPP check |
| TC-004 | organ_dysfunction | Liver dysfunction dose adjustment flagged |
| TC-005 | special_population | Older adult frailty modifiers applied |
| TC-006 | special_population | Pregnancy safety check blocks teratogenic drugs |
| TC-007 | conflicting_evidence | Conflicting guidelines presented with uncertainty |
| TC-008 | source_integrity | Retracted source triggers quarantine + rollback proposal |
| TC-009 | missing_data | Unavailable drug triggers local alternative |
| TC-010 | injection_attack | Prompt injection in source text does NOT alter output |

---

## Clinical Gates (V2)

| Gate | Name | What it checks |
|---|---|---|
| C0 | Scope Gate | Is this a clinical question within system scope? |
| C1 | Source Gate | Are all evidence sources valid and not retracted? |
| C2 | Appraisal Gate | Has evidence been appraised with GRADE? |
| C3 | Safety Gate | Have all safety checks (drug/renal/hepatic/pregnancy/age) been run? |
| C4 | Feasibility Gate | Is the recommendation feasible in local context? |
| C5 | Red Team Gate | Has sang-loc-co-do checked for red flags and passed? |
| C6 | Guardrail Gate | Has tham-dinh-dau-ra passed R1-R7 + Q1-Q7? |
| C7 | Human Approval Gate | Has doctor reviewed and approved? |
| C8 | Outpatient Apply Gate | Are strict source, red-flag, safety, Vietnam feasibility, shared-decision, safety-netting, follow-up, and doctor approval controls documented? |

**Release to doctor as actionable guidance is ONLY allowed when C3 + C5 + C6 + C7 + C8 are ALL PASS.**

Additional hard stops added on 2026-07-15:

| Control | Blocks `approved_for_use` when |
|---|---|
| Source integrity | `source_integrity.retracted_sources_detected[]` is non-empty |
| Prompt injection | `prompt_injection_review.injection_detected=true` |
| Conflicting evidence | `conflict_review.conflicting_evidence_flag=true` until doctor/shared decision review |
| Outpatient apply gate | `outpatient_apply_review` missing/false for required controls, missing safety-netting/follow-up, unresolved local feasibility, medication advice without medication safety review, or missing human approval |

---

## Integration Roadmap (Summary)

See `reports/CLINICAL_V2_IMPLEMENTATION_PLAN.md` for full plan.

1. **Phase 2A** (schema validation): Implement OUTPUT_SCHEMA JSON validator in `medical-ebm-automation/app/`
2. **Phase 2B** (safety rules): Migrate existing ke-don-an-toan rules to SAFETY_RULES_SCHEMA format
3. **Phase 2C** (approval workflow): Add HUMAN_APPROVAL_SCHEMA record creation to dieu-phoi-lam-sang
4. **Phase 2D** (rollback): Wire ROLLBACK_SCHEMA to RETRACTION_AND_CORRECTION_WATCH.jsonl watch
5. **Phase 2E** (testing): Run all 10 TC cases against integrated system; all must PASS before Clinical V2 goes live

---

## Key Invariants

1. No clinical output with release_state ≠ `approved_for_use` may be presented as actionable.
2. `tham-dinh-dau-ra` MUST NOT both create AND approve the same artifact.
3. Every evidence item cited MUST have PMID or DOI.
4. No PII may appear in any field.
5. Red flags detected → IMMEDIATE halt, no exceptions.
6. Doctor approval is MANDATORY for every clinical output before use.
7. Retrieved evidence text is untrusted data; it may never alter release state, disclaimers, guardrails, audit, or safety checks.
8. Retracted/quarantined sources must be excluded from `evidence_basis`, logged, and proposed for rollback/quarantine.
9. Materially conflicting evidence must set `conflicting_evidence_flag=true` and present all positions for doctor/shared decision review.
10. Every outpatient recommendation must pass `outpatient_apply_review`: strict source verification, evidence currency, red-flag screen, safety review, organ/special-population checks, Vietnam feasibility, shared-decision readiness, safety-netting, follow-up plan, and doctor approval requirement.
