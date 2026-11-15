# Source authority statement

Phase 1 decision: RAW_CSV_CANONICAL_FOR_COMPUTATION.

The original workbook remains the organizer-delivered source; raw CSV is the preserved computational export, and cleaned CSV preserves its original fields. All 1,048,575 rows and 21 fields were compared; 22 USD_AMOUNT differences and 0 other-field differences were found. Maximum amount difference: USD 0.39; maximum relative amount difference: 4.129222519e-10. No source was changed.

Sensitivity changed 0 fixed amount-band assignments. Maximum relative change across calculated global/currency summaries was 1.08805719598e-10. The declared materiality criterion is no band changes and all summary relative changes below 1e-8; this is an analytical numerical tolerance, not an official accounting threshold. The full sensitivity table is retained. The user explicitly authorized raw CSV computational authority if this impact is immaterial. This decision does not assert workbook/export exact equality or identify the export discrepancy cause.

Mismatch rows contain competition transaction information and remain only in ignored outputs/tables/source_reconciliation; do not commit, publish or upload them. Hashes are retained in the phase completion manifest.
