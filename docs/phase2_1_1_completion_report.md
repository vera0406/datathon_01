# Phase 2.1.1 completion report

## 1. Executive Summary

Final decision: READY_FOR_POWER_BI_WITH_LIMITATIONS. All eight cleanup gaps are resolved. New approved RUN_ID: 20261115T021543009685Z. No new exploratory hypotheses or statistical strengthening was attempted. Power BI was not constructed.

## 2. Eight Gap-Check Results

| CHECK | OLD_STATUS | NEW_STATUS | EVIDENCE | FILE | LINE_OR_FUNCTION |
| --- | --- | --- | --- | --- | --- |
| 1. Automated semantic visual claims | NOT_FULLY_REMOVED | RESOLVED | PNG-only integrity receipt; semantic status PENDING_MANUAL_OR_AGENT_REVIEW | src/release_verification.py | technical_chart_qa |
| 2. Historical release dependency | NOT_REMOVED | RESOLVED | Candidate supplied explicitly; source AST scan has no literal historical release IDs | src/test_phase2_release_gate.py | test_active_logic_has_no_historical_release_literal |
| 3. Nested comparison semantics | PARTIAL | RESOLVED | M1/M2 reference M0; M3 reference M2; later nested extensions; deltas recomputed only against explicit references | src/phase2_release.py | Integration.nested |
| 4. Cross-phase sample row identity | NOT_HASH_VERIFIED | RESOLVED | Reconstructed Phase1 ordered source identifiers exactly match Phase2 hash | src/release_cleanup.py | reconstruct_phase1_sample / verify_phase2_sample |
| 5. Dynamic rule validation | HARDCODED | RESOLVED | Manifest RULE_COUNT equals actual register; schema, unique/nonblank IDs, vocabulary and card coverage checked | src/release_verification.py | validate_rules |
| 6. Canonical endpoint pointer | HARDCODED | RESOLVED | Source, artifact, authority manifest and original audit source-hash records verified | src/release_cleanup.py | resolve_endpoint |
| 7. Safe report updates | LEGACY_MUTATION_REMAINS | RESOLVED | Legacy free-text replacements removed; marker updater rejects missing, duplicate or reversed markers | src/release_cleanup.py | update_marked_section |
| 8. Legacy verifier deprecation | INACTIVE_NOT_FORMALLY_DEPRECATED | RESOLVED | Execution and import raise explicit deprecation error without writing files | outputs/phase2/verify_release.py | module guard |


## 3. Legacy Verifier Deprecation

The ignored legacy script is now only a module docstring and an unconditional RuntimeError directing users to the independent verifier and promotion gate. The QA suite executes it and verifies failure without approval-pointer mutation. It is not a second implementation.

## 4. Visual QA Separation

Automated checks verify existence, PNG decoding, positive dimensions, content hashes and contact-sheet generation only. All current automated receipts retain VISUAL_REVIEW_STATUS=PENDING_MANUAL_OR_AGENT_REVIEW. No new semantic review was performed or approved by this cleanup. Historical receipts remain archived evidence, not authority for this release.

## 5. Historical Release Dependency Removal

Active verification resolves the supplied candidate and its manifest, never a particular historical run. Old release IDs remain only in historical provenance/receipts. Source-level AST tests reject literal historical run IDs in active release modules.

## 6. Nested Model Semantic Correction

REFERENCE_MODEL and COMPARISON_TYPE are explicit. MODEL_2 uses MODEL_0, not MODEL_1. DELTA_R2=current minus reference; DELTA_MAE=reference minus current, so positive means smaller prediction error. All original fitted R2/MAE/RMSE, train/test N and train/test row hashes were reproduced unchanged within1e-12. The performance chart caption and released nested-model fact use the corrected semantics. No causal variance attribution.

## 7. Cross-Phase Sample Hash Verification
Phase1 SOURCE_ROW_HASH = Phase2 SOURCE_ROW_HASH = `a791199472be184ded4f80dfa97d7369ef2b1abf7117553993f51b0421e749d5`. SAMPLE_N=200000; seed=2026; ordered little-endian int64 source IDs. Canonical artifact: outputs/tables/duration/adjusted/fx_gap_model_sample_design.json.

This is an explicit reconstruction of the deterministic historical sampling design, not a contemporaneously saved original-fit row-hash receipt. Historical source order, source checksum, executed notebook, model sample size and seed were checked. The original module hash `d89ef051837ea2cff9b69ea54548505d2947a7f477df7e9fad9619fe31bb222d` differs from the current module hash `fd241a337d03e131cbbb18f936a5df30677c8ab378efef79626ff3e70d50cc71`; both are recorded without claiming equality. Independent candidate verification reconstructs row identifiers from the cleaned CSV again, and the original Phase2 train/test row hashes and model metrics were reproduced unchanged.
## 8. Dynamic Rule Count Validation

Current RULE_COUNT=14 is measured, not an acceptance constant. Unit tests add a synthetic extra rule/card and accept its new actual count, while rejecting count mismatch, blank/duplicate IDs, invalid status and missing cards. Required schema remains exactly22 columns.

## 9. Canonical Endpoint Audit Pointer

outputs/final_audit/current_audit.json resolves the previously approved diagnostic artifact. Source hash, content hash, authority-manifest hash, and original before/after source-hash records are checked. The historical diagnostic bytes are unchanged; no timestamp literal remains in active code.

## 10. Safe Report Update Mechanism

No legacy report .replace mutation remains. update_marked_section requires exactly one start/end marker in correct order, preserves outside text and atomically replaces the file. Missing, duplicate and reversed markers raise before writing. This report uses an explicit verification-status marker section below.

## 11. Release Gate Tests

<!-- VERIFICATION_STATUS_START -->
Focused QA suite: PASSED.

```text
. ok
test_cross_phase_ordered_sample_hash (__main__.CleanupGateTests.test_cross_phase_ordered_sample_hash) ... ok
test_endpoint_pointer_resolves_and_checks_source_and_hash (__main__.CleanupGateTests.test_endpoint_pointer_resolves_and_checks_source_and_hash) ... ok
test_legacy_execution_is_blocked_without_mutation (__main__.CleanupGateTests.test_legacy_execution_is_blocked_without_mutation) ... ok
test_marked_update_preserves_outside_text (__main__.CleanupGateTests.test_marked_update_preserves_outside_text) ... ok
test_missing_duplicate_or_reversed_markers_fail_without_mutation (__main__.CleanupGateTests.test_missing_duplicate_or_reversed_markers_fail_without_mutation) ... ok
test_nested_reference_metadata_and_arithmetic (__main__.CleanupGateTests.test_nested_reference_metadata_and_arithmetic) ... ok
test_no_active_legacy_calls_or_report_replacement (__main__.CleanupGateTests.test_no_active_legacy_calls_or_report_replacement) ... ok
test_no_literal_rule_count_validation (__main__.CleanupGateTests.test_no_literal_rule_count_validation) ... ok
test_rule_blank_duplicate_status_and_cards_rejected (__main__.CleanupGateTests.test_rule_blank_duplicate_status_and_cards_rejected) ... ok
test_rule_count_accepts_added_rule (__main__.CleanupGateTests.test_rule_count_accepts_added_rule) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.454s

OK

```

All 36 workflow assertions passed. Actual late-build failure and tampering after independent verification were exercised before approval, and neither changed the prior approved pointer.

Files changed: src/phase2_release.py, src/release_verification.py, src/release_cleanup.py, src/test_phase2_release_gate.py, outputs/phase2/verify_release.py, notebook/10_final_analytical_integration.ipynb, notebook/09_dashboard_data_prep.ipynb, canonical metadata/evidence artifacts and this report. Generated local releases/receipts remain ignored.
<!-- VERIFICATION_STATUS_END -->

## 12. New Approved Release

New approved run: 20261115T021543009685Z. Candidate independently verified before promotion and again after promotion. Builder checks=234; independent checks=600; workflow assertions=36. Previous approved pointer was byte-identical through all intentional pre-promotion failures. Pointer approval binds manifest and verification-receipt hashes. See dashboard/data/current_release.json and outputs\phase2_1_1\20261115T021301547191Z\completion.json.

## 13. Source Integrity

All three source hashes match the previous approved release:

- data/raw/swift_payments_raw_export.csv: `ea0eaa18311df2c9332aec336a198307df2996559f7f5abc2840ea0ef2d46d29`
- data/cleaned/swift_payments_cleaned.csv: `f8b2d946f647e02778d3b232be2f10a91f4adbf1b06c72045c075319a3a9d85c`
- data/raw/swift_umdac_datathon_2026_fictitious_payment_data.xlsx: `5787b5f9fee3ebcb8ab35462eab75931e70e77dc601c091f334d72dd9e32ea57`

The previous approved release files, including its manifest and tables, remain byte-identical.

## 14. Statistical Evidence Change Check

No fitted statistical estimates changed. Every prior final statistical table was compared with its preserved baseline; Phase1 duration/BIC/tail CSV checksums remain unchanged. F07/F08 remain REJECTED_HYPOTHESIS; F11/F12 remain INSUFFICIENT_EVIDENCE. Expected changes are nested-model references/deltas/feature labels, sample provenance metadata, audit pointer/provenance, dynamic rule-count metadata, technical chart QA and release validation records. Old evidence versions are preserved under the completion receipt directory. Rule evidence and cards were compared unchanged.

## 15. Remaining Limitations

Currency/BIC common support remains insufficient for a portfolio-wide independent currency effect. Direct long-tail cause remains unexplained; gap association is weak and FX relationships heterogeneous. Automated image checks do not approve semantic chart quality. Power BI must enforce existing filter/aggregation contracts. Local atomic-pointer semantics do not defend against malicious concurrent file mutation or guarantee hardware durability. Failed candidates remain unapproved for forensic inspection.

## 16. Final Decision

READY_FOR_POWER_BI_WITH_LIMITATIONS

Phase2.1.1 cleanup is complete. Stop here; Power BI construction, publication, commits and pushes were not performed.