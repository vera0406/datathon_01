# Phase 2 final analytical integration report

## 1. Executive Summary

Decision: **READY_FOR_POWER_BI_WITH_LIMITATIONS**. Immutable local analytical release: `dashboard\data\releases\20261115T014152666003Z`. All 234 release checks passed. No Power BI construction, public release, commit or push was performed. Readiness is conditional on enforcing the supplied contracts in the future report.

## 2. Files Created / Modified

Created src/phase2_release.py, notebook/10_final_analytical_integration.ipynb, final evidence tables/charts, evidence cards, this report, issue reassessment and model contract. Rebuilt notebook/09_dashboard_data_prep.ipynb and updated canonical register plus final audit/readiness/checklists. Prior versions of overwritten outputs/docs are retained under outputs/phase2/. Versioned CSV/PNG inputs, contracts, inventory, dictionary, validations and provenance manifest reside in `dashboard\data\releases\20261115T014152666003Z`. Both notebooks PASSED from separate fresh project-venv kernels. Execution receipts: outputs\phase2\execution\20261115T014114606484Z. Independent on-disk verification: 214 checks PASSED; release log: 234 checks PASSED. All17 final charts were visually reviewed and their exact hashes matched the current release. Receipts and contact sheet: outputs\phase2\verification\20261115T014152666003Z.

## 3. Final Rule Register Status

| STATUS | RULE_COUNT |
| --- | --- |
| EXPLORATORY_ASSOCIATION | 2 |
| INSUFFICIENT_EVIDENCE | 3 |
| PLAUSIBLE_GENERATING_MECHANISM | 2 |
| REJECTED_HYPOTHESIS | 2 |
| STRONG_STATISTICAL_PATTERN | 2 |
| SUPPORTED_STRUCTURAL_RULE | 3 |

22 columns,14 unique rule IDs. F07/F08 remain REJECTED_HYPOTHESIS; F11/F12 remain INSUFFICIENT_EVIDENCE. Architecture equivalences remain F01; FX>=2 non-direct is a consequence of F02, not another independent discovery.

## 4. Covered vs Indirect Final Estimand

| ESTIMAND | MATCH_REQUIREMENT | MATCHED_STRATA | COVERED_N | INDIRECT_N | LOG_DIFFERENCE | GEOMETRIC_RELATIVE_DIFFERENCE | CI_LOW | CI_HIGH | LOG_CI_LOW | LOG_CI_HIGH | CI_UNIT | INTERPRETATION | DASHBOARD_USE | MATCH_VARIABLES | WEIGHTING |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRIMARY_MIN20 | Minimum 20 per route arm | 217 | 38017 | 264393 | 0.09472325684084444 | 0.09935457416632099 | 0.07867227175440016 | 0.12043343598211195 | 0.07573090682588338 | 0.1137156068558055 | relative geometric(duration+1) difference, fraction | Min-arm-weighted conditional geometric mean of duration+1; not median, causal delay or raw-second increase | PRIMARY uncertainty-aware evidence | participants + FX + currency + party | min(nCovered,nIndirect), normalized over eligible strata |
| EARLIER_MIN1_SENSITIVITY | Minimum 1 per route arm | 1777 | 43430 | 326885 | 0.11360927104430983 | 0.12031430011778657 | Not estimable | Not estimable | Not estimable | Not estimable | relative geometric(duration+1) difference, fraction | Min-arm-weighted conditional geometric mean of duration+1; not median, causal delay or raw-second increase | SENSITIVITY ONLY; no valid singleton variance | participants + FX + currency + party | min(nCovered,nIndirect), normalized over eligible strata |

Primary effect is conditional geometric(duration+1), not raw median or causal delay. Original1777-stratum result is sensitivity only; its missing interval is not borrowed.

## 5. Nested Duration Explanatory Results

| MODEL | FEATURE_SET | TRAIN_N | TEST_N | R2_LOG_DURATION | MAE_LOG_DURATION | RMSE_LOG_DURATION | INCREMENTAL_R2_VS_PREVIOUS | INCREMENTAL_MAE_IMPROVEMENT | NOTES | SPLIT_SEED | SAMPLE_N | OUTCOME |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MODEL_0 | Intercept (training mean) | 150000 | 50000 | -3.8994759376853594e-05 | 1.856410925447623 | 2.0126202839382805 | Not estimable | Not estimable | OLS; participant count linear on log scale; M2 is alternative to M1, not nested; increments are predictive, not causal decomposition | 2026 | 200000 | log1p(duration_seconds) |
| MODEL_1 | route | 150000 | 50000 | 0.03436993649367548 | 1.8075258942973433 | 1.9776925025951908 | 0.03440893125305233 | 0.048885031150279756 | OLS; participant count linear on log scale; M2 is alternative to M1, not nested; increments are predictive, not causal decomposition | 2026 | 200000 | log1p(duration_seconds) |
| MODEL_2 | participants | 150000 | 50000 | 0.045234170464536816 | 1.7957644242984685 | 1.9665355948174044 | 0.010864233970861337 | 0.01176146999887484 | OLS; participant count linear on log scale; M2 is alternative to M1, not nested; increments are predictive, not causal decomposition | 2026 | 200000 | log1p(duration_seconds) |
| MODEL_3 | route + participants | 150000 | 50000 | 0.04604696304000899 | 1.7931825550243363 | 1.9656983602815292 | 0.0008127925754721765 | 0.002581869274132176 | OLS; participant count linear on log scale; M2 is alternative to M1, not nested; increments are predictive, not causal decomposition | 2026 | 200000 | log1p(duration_seconds) |
| MODEL_4 | route + participants + fx | 150000 | 50000 | 0.046229041140393945 | 1.7928059933912754 | 1.965510757910417 | 0.00018207810038495253 | 0.000376561633060879 | OLS; participant count linear on log scale; M2 is alternative to M1, not nested; increments are predictive, not causal decomposition | 2026 | 200000 | log1p(duration_seconds) |
| MODEL_5 | route + participants + fx + currency_model | 150000 | 50000 | 0.05284128880948924 | 1.7807826539325546 | 1.9586857191133331 | 0.006612247669095295 | 0.012023339458720805 | OLS; participant count linear on log scale; M2 is alternative to M1, not nested; increments are predictive, not causal decomposition | 2026 | 200000 | log1p(duration_seconds) |
| MODEL_6 | route + participants + fx + currency_model + log_amount + party + gap | 150000 | 50000 | 0.05298006137865685 | 1.7802590132731297 | 1.9585422258407426 | 0.00013877256916761116 | 0.0005236406594248955 | OLS; participant count linear on log scale; M2 is alternative to M1, not nested; increments are predictive, not causal decomposition | 2026 | 200000 | log1p(duration_seconds) |

All models use the same200000 sampled rows,150000 training and50000 heldout. M2 is an alternative to M1; incremental explanatory gains are predictive comparisons, not causal variance decomposition.

## 6. Currency / Party Final Descriptive Evidence

154 currency categories and 4 party pairs each reconcile to1048575. Both conditional-probability directions sum to1 within their explicit conditioning groups. Full amount profiles include mean, median, P75/P90/P95/P99/IQR; duration is in seconds. Currency→Covered evidence remains exploratory with bank confounding; the2030-record BIC frame covers only0.525458% of386330 non-direct transactions. Extreme BIC-frame odds ratios are deliberately excluded from final presentation. See currency_routing_final_diagnostics.csv and raw_vs_adjusted_same_support.csv.

## 7. Gap / Endpoint Diagnostic Integration

| MODEL | FITTED_P | CI_LOW | CI_HIGH | DEVELOPMENT_N | VALIDATION_N | HELDOUT_WEIGHTED_MAE_PP | HELDOUT_WEIGHTED_RMSE_PP | IN_SAMPLE_MAE_PP | IN_SAMPLE_RMSE_PP | POPULATION_SCOPE | CAVEAT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LEGACY03_COMMON_IN_SAMPLE | 0.04989044494255782 | Not estimable | Not estimable | 1048440 | 0 | Not estimable | Not estimable | 0.051495810745790446 | 0.14152456155809212 | Participants2-10; route×participant calibration;135 rows excluded; in-sample only | Consistent with an approximate per-link mechanism; not uniquely identified; model-based pointwise intervals; no external validation |
| FULL08_COMMON_IN_SAMPLE | 0.04988862779638522 | 0.0495525120632303 | 0.050224743529540136 | 1048575 | 0 | Not estimable | Not estimable | 0.022920617695689895 | Not estimable | All participants; pooled participant calibration; different grain from03 | Consistent with an approximate per-link mechanism; not uniquely identified; model-based pointwise intervals; no external validation |
| FIXED_DEVELOPMENT08_HOLDOUT | 0.04975492373982058 | 0.049280502022341445 | 0.050229345457299714 | 524634 | 523941 | 0.061474917688631815 | 0.2007642723807492 | Not estimable | Not estimable | Fixed development predictions on random validation; small upper-participant tail | Consistent with an approximate per-link mechanism; not uniquely identified; model-based pointwise intervals; no external validation |

| CONDITIONAL_GROUPS | ADEQUATELY_SUPPORTED_GROUPS | MAX_CRAMERS_V_SUPPORTED | MAX_ABS_JOINT_MINUS_PRODUCT_PP_SUPPORTED | BH_SIGNIFICANT_SUPPORTED_GROUPS | INTERPRETATION | CAVEAT |
| --- | --- | --- | --- | --- | --- | --- |
| 66 | 26 | 0.0192173579521085 | 0.09346972013623638 | 0 | Observed endpoint mismatches are approximately consistent with independence overall and across adequately supported tested groups. Not proof of independence. | Overlapping diagnostic groups are not additive; sparse expected cells limit tests; pointwise rates and exploratory BH diagnostics |

Heldout calibration uses fixed development predictions. Legacy03 and full08 differ in scope and grouping. Observed endpoint mismatches are approximately consistent with independence overall and across adequately supported tested groups; this is not proof of independence.

## 8. Slow-Payment Final Narrative

| ROUTING_TYPE | TOTAL_N | SLOW_COUNT | THRESHOLD_SECONDS | SLOW_RATE_PERCENT | SLOW_COUNT_RANK | SLOW_RATE_RANK | RATE_LEADER_FLAG | VOLUME_LEADER_FLAG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| COVERED | 43578 | 23399 | 300 | 53.6945247602001 | 3 | 1 | True | False |
| DIRECT | 662245 | 240752 | 300 | 36.35391735686944 | 1 | 3 | False | True |
| INDIRECT | 342752 | 169387 | 300 | 49.41969704042573 | 2 | 2 | False | False |
| COVERED | 43578 | 13117 | 900 | 30.10005048418927 | 3 | 2 | False | False |
| DIRECT | 662245 | 163981 | 900 | 24.76137985186751 | 1 | 3 | False | True |
| INDIRECT | 342752 | 117326 | 900 | 34.23058071141817 | 2 | 1 | True | False |
| COVERED | 43578 | 8091 | 1800 | 18.566707971912432 | 3 | 2 | False | False |
| DIRECT | 662245 | 95678 | 1800 | 14.447523197608136 | 1 | 3 | False | True |
| INDIRECT | 342752 | 73043 | 1800 | 21.310743628045934 | 2 | 1 | True | False |

Direct has the largest slow volume at all cut-offs. Rate leader changes from Covered at300 seconds to Indirect at900/1800. Direct adjusted holdout log-loss / null-loss fraction remains 0.988536701–0.994122051; this is predictive loss, not fraction of unexplained payments. F12 has no established mechanism. Thresholds are analytical, not Swift SLAs.

## 9. Business Evidence Cards

All14 canonical IDs have six-question cards and source/chart mapping in outputs/rules/final_rule_evidence_cards.csv and docs/final_rule_evidence_cards.md. Applications are proposed monitoring/QA uses, with no invented savings or causal operational gains.

## 10. Dashboard Data Model

23 fact tables and 15 dimensions; one-to-many single-direction relationships only; separate fixed evidence, daily aggregates, cube, full profiles and global coverage. See release_table_inventory.csv, dashboard_model_relationships.csv and dashboard_data_model_contract.md.

## 11. Filter Compatibility

Every fact has allowed/disallowed slicers, grain, denominator and source. Currency selects published fixed currency evidence; it never refits models. Date is restricted to daily facts. Rule selectors do not filter transactions. All unsupported interactions must be disabled during Power BI construction.

## 12. Non-Additive Metric Protections

data_dictionary.csv classifies ADDITIVE, WEIGHTED_ADDITIVE, NON_ADDITIVE and FIXED_ESTIMAND fields. Averaged rates/medians, multiple-threshold totals and summed coefficients are rejected by executable release guards. Exact-grain display only for quantiles, model estimates and confidence intervals.

## 13. Suppression Coverage

1044210 visible +4365 globally suppressed =1048575. Suppressed transactions are never allocated to route/currency/party. Filtered cube metrics describe visible cohorts only; full filtered coverage is unknown. Global coverage is a disconnected fact.

## 14. Final Dashboard Page Readiness

| PAGE | TITLE | STATUS | BUSINESS_QUESTION | MAIN_FINDING | EVIDENCE_STATUS | SOURCE_TABLE | SOURCE_CHART | X_DIMENSION | Y_METRIC | DENOMINATOR | UNIT | ALLOWED_SLICERS | DISALLOWED_SLICERS | CAVEAT | BUSINESS_APPLICATION | MISSING_EVIDENCE | REMAINING_ACTION | RELEASE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Payment Characteristics | READY | What payment characteristics shape the population? | Portfolio, currency and party profiles | READY | FactPortfolioOverview; FactCurrencyProfile; FactPartyProfile | Not applicable: exact profile/KPI tables | Currency / Party | N / share / amount and duration quantiles | Full source1048575 | Transactions; USD; seconds; fractions | Global overview has no transaction slicers | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | Use exact-grain quantiles; no synthesized cohort medians | Population monitoring | None for descriptive scope | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |
| 2 | Routing Architecture | READY | Which participant and FX constraints hold? | F01/F02; routing structure fact | READY | FactRoutingStructure | F01_evidence.png; F02_evidence.png | Routing / Participant / FX | N / structural exceptions / FX bound | Full source1048575 | Transactions / participant count / FX count | Routing/Participant/FX only on joint structure fact | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | Equivalent structural statements remain one rule family | Structural QA | None for observed structural scope | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |
| 3 | Path Observability | READY_WITH_LIMITATIONS | How observable are payment paths and endpoints? | F03/F04; heldout gap and66 endpoint diagnostics | READY_WITH_LIMITATIONS | FactGapCalibration; FactEndpointDiagnostics | F03_evidence.png; F04_evidence.png | Participant / conditional diagnostic group | Observed versus predicted gap / joint residual | Gap validation523941; endpoint overlapping groups | Fractions; pp; Cramers V | Participant only for gap; endpoint group only for endpoint evidence | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | Approximate mechanism; not proof of independence; sparse tail flagged | Observability monitoring | Unique generator identification and independence proof unavailable | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |
| 4 | Currency Routing Signals and Network Confounding | READY_WITH_LIMITATIONS | Which currency routing signals remain network-confounded? | F11; all eight prespecified currency diagnostics and coverage | READY_WITH_LIMITATIONS | FactCurrencyRoutingDiagnostics; FactCurrencyBICCoverage | F11_evidence.png | Prespecified currency | Standardized Covered risk difference and BIC coverage | Non-direct386330; selected BIC frame2030/49pairs | Percentage points; coverage percent | Currency selects fixed evidence rows; no model refitting | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | Exploratory signal only; independent global currency effect unresolved | Exploratory routing/network review | Global independent currency effect after BIC control unavailable | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |
| 5 | What Is Associated with Payment Duration? | READY_WITH_LIMITATIONS | Which observables are associated with duration? | F05/F06/F07/F08/F13/F14; quantiles and seven baselines | READY_WITH_LIMITATIONS | FactDurationRouteParticipant; FactDurationNestedBaselines; FactSameSupportEffects; FactAdjustedDurationEffects | duration_nested_model_performance.png; F05_evidence.png; F06_evidence.png; F13_evidence.png; F14_evidence.png | Route / Participant / model / fixed estimand | Duration quantiles / heldout R2 / geometric-duration contrast | Covered primary302410; nested heldout50000; adjusted sample200000 | Seconds; log1p(seconds); relative geometric(duration+1) fraction | Model effects disconnected from transaction filters | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | No causal, raw-median or unique variance attribution | Conditional duration benchmarking | Causal effects and external validation unavailable | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |
| 6 | The Slow-Payment Workload | READY_WITH_LIMITATIONS | Where are slow-payment rates and workloads concentrated? | Nine route/threshold rows; F12 Direct residual diagnostics | READY_WITH_LIMITATIONS | FactSlowPayments; FactDirectTailResidual | slow_payment_rate_by_threshold.png; slow_payment_volume_by_threshold.png; F12_evidence.png | Route / Threshold / Evaluation | Slow count / slow rate / residual log-loss ratio | Source1048575; Direct662245; model sample150000 | Transactions; percent; seconds; loss ratio | Exactly one Threshold; Routing where available; residual fixed evaluation | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | Cut-offs are not SLAs; Direct mechanism remains unexplained | Workload prioritization; no SLA claim | Direct-delay mechanism unresolved | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |
| 7 | Retrospective Anomaly and Token QA | READY_WITH_LIMITATIONS | What retrospective label/token QA is supported? | Path A: F09 duplicate recurrence; F10 token parser quality | READY_WITH_LIMITATIONS | FactDuplicateQA; FactTokenParserQA | F09_evidence.png; F10_evidence.png | QA metric / cohort / token side | Recurrence rate / parser residual count | Duplicate/unlabeled QA1047100; token1048575 strings per side | Retrospective fraction / string marker count | QA metric/cohort and token-side filters only | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | Retrospective supporting QA; no fraud accuracy, token semantics or new scam mechanism | Retrospective supporting QA | Scam mechanisms and incremental token prediction outside Path A | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |
| 8 | Reconstructed Rules and Business Implications | READY_WITH_LIMITATIONS | Which rules are supported, rejected or unresolved? | Audited22-column register;14 six-question evidence cards | READY_WITH_LIMITATIONS | FactRuleEvidence | F01_evidence.png through F14_evidence.png; separate statuses | Rule ID / Status | Effect size / uncertainty / support, each rule separately | Rule-specific mixed and overlapping populations | Rule-specific units; never aggregate unlike effects | Disconnected Rule selector only | Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering | Separate six statuses; rejected/unresolved are not supported discoveries | Evidence-led monitoring proposals | F11/F12 unresolved; rejected hypotheses remain rejected | Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed | dashboard\data\releases\20261115T014152666003Z |


## 15. Remaining Analytical Limitations

F11 independent currency effect and F12 Direct mechanism remain unresolved. FX associations vary across transitions and support; gap association is weak and intervals include zero. No external validation, causal claim, Swift SLA, fraud accuracy or token incremental predictive value. Page7 uses Path A retrospective QA only. Raw CSV is the canonical computational source; organizer workbook is retained as delivery source with22 immaterial amount-precision differences, not exact equality. All three source hashes remain unchanged. Detailed Phase1 evidence is preserved.

## 16. Final Decision

READY_FOR_POWER_BI_WITH_LIMITATIONS

Phase2 analytical integration is complete: both fresh-kernel receipts and independent release hash/contract verification passed. No remaining analytical blocker to constructing the restricted dashboard; enforcing UI measures and slicer compatibility is mandatory. Stop here; Power BI was not constructed.