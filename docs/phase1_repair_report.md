# Phase 1 repair report

**Final decision: PHASE_1_STILL_BLOCKED**. All four authorized analyses were implemented and executed. Analytical completion is distinct from passing the readiness gate: insufficient common support must remain a limitation, not be manufactured away.

## 1. Files created or modified

- `src/phase1_analysis.py`
- `notebook/00B_source_amount_reconciliation.ipynb`
- `notebook/04B_direct_long_tail.ipynb`
- `notebook/04C_duration_adjusted_robustness.ipynb`
- `notebook/05B_currency_bic_robustness.ipynb`
- `docs/source_authority_statement.md`
- `outputs/rules/final_rule_register.csv`
- `docs/final_analytical_output_audit.md`
- `docs/missing_analysis_checklist.md`
- `docs/pre_powerbi_fix_list.md`
- `docs/dashboard_readiness_matrix.md`
- `docs/phase1_repair_report.md`

Prior audit/rule versions are retained in `outputs\phase1\integration\20261115T005419890530Z`. Existing notebooks00–09 and their current kernel-crash records were not edited. Current new notebook execution does not prove those old user sessions recovered.

## 2. Fresh-kernel execution

| notebook | fresh_kernel | code_cells | unhandled_errors | source_population |
| --- | --- | --- | --- | --- |
| 00B_source_amount_reconciliation | PASS | 3 | 0 | 1048575 |
| 04B_direct_long_tail | PASS | 3 | 0 | 1048575 |
| 04C_duration_adjusted_robustness | PASS | 3 | 0 | 1048575 |
| 05B_currency_bic_robustness | PASS | 3 | 0 | 1048575 |

## Phase 1 evidence update

Decision: **PHASE_1_STILL_BLOCKED**. This section supersedes the earlier audit where statuses differ; the baseline is retained for provenance. No Power BI construction was performed.

| issue | status | evidence |
| --- | --- | --- |
| I01 | RESOLVED_COMPUTATIONAL_AUTHORITY | 00B full comparison and sensitivity; authorized immutable raw computational source if declared tolerance met |
| I02 | PARTIAL_GLOBAL_COMMON_SUPPORT_BLOCKED | Same-row models executed on 2030 rows / 49 pairs; coverage 0.525458%; all prespecified currencies reported |
| I03 | RESOLVED_INVESTIGATION_WITH_UNEXPLAINED_RESIDUAL | All Direct segment rates; random/time models; residual loss fraction 0.988537-0.994122. Mechanism remains insufficient; F12 not promoted. |
| I04 | RESOLVED_SCOPED_ADJUSTED_ASSOCIATION | FX/gap GLM and OLS; thresholds; exact minimum20 overlap; heterogeneity and five partitions. F07/F08 remain separate universal-hypothesis tests. |

### Dashboard reassessment

| page | status | reason |
| --- | --- | --- |
| 4 | NOT_READY | Insufficient BIC/currency common support for global routing claim; report fixed-frame results only. |
| 5 | READY_WITH_LIMITATIONS | Adjusted FX/gap evidence now available, with fixed model sample and supported matching; no causal effect or median interpretation. |
| 6 | READY_WITH_LIMITATIONS | Threshold-sensitive workload and Direct residual uncertainty quantified; do not claim a reconstructed cause. |
| 8 | READY_WITH_LIMITATIONS | Canonical audited22-column register updated with associations, rejected universality and insufficient mechanisms. Import this file directly; legacy09 rule table remains deprecated. |

### Calculated source reconciliation

| n | original_fields | mismatched_amounts | other_original_field_differences | max_absolute_difference_usd | max_relative_difference | amount_band_changes | max_summary_relative_change | immaterial_under_declared_1e_8_summary_tolerance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1048575 | 21 | 22 | 0 | 0.39 | 4.129222518998437e-10 | 0 | 1.0880571959777519e-10 | True |

### Currency effects on identical supported rows

| currency | support_n | covered_n | reference_other_n | source_currency_n | bic_coverage_percent | common_population_n | bic_pairs | effect_unit | interval_type | baseline_log_odds | baseline_odds_ratio | baseline_ci_low | baseline_ci_high | baseline_p_value | baseline_pair_cluster_ci_low | baseline_pair_cluster_ci_high | bic_adjusted_log_odds | bic_adjusted_odds_ratio | bic_adjusted_ci_low | bic_adjusted_ci_high | bic_adjusted_p_value | bic_adjusted_pair_cluster_ci_low | bic_adjusted_pair_cluster_ci_high | effect_change_log_odds | direction_stable | status | baseline_p_value_bh | bic_adjusted_p_value_bh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHF | 529 | 480 | 55 | 30870 | 1.7136378360868156 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | 3.353350940914022 | 28.59840482481034 | 14.395129859271103 | 56.81565685890576 | 1.0245777529204899e-21 | 6.139455810961841 | 133.2151877473329 | 5.13391608572657 | 169.6803012620413 | 53.208478874661886 | 541.1055765040427 | 4.076150856029031e-18 | 49.44941614774501 | 582.2395263546509 | 1.780565144812548 | True | INSUFFICIENT_COMMON_SUPPORT | 2.5614443823012245e-21 | 1.0190377140072578e-17 |
| GBP | 481 | 454 | 55 | 33614 | 1.4309513893020764 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | 3.928670361596286 | 50.83933477693481 | 24.400408734518873 | 105.92601085836752 | 9.650987155475663e-26 | 24.630768917947776 | 104.93533389767204 | 4.733773919463999 | 113.72393849670605 | 42.17857668317609 | 306.6280373647901 | 8.42703748021812e-21 | 38.70698083533627 | 334.1292425317685 | 0.8051035578677133 | True | INSUFFICIENT_COMMON_SUPPORT | 4.825493577737831e-25 | 4.21351874010906e-20 |
| CNY | 162 | 150 | 55 | 12610 | 1.2846946867565425 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | 3.662671608128135 | 38.96530396062825 | 16.528747171668844 | 91.8578339286713 | 5.714156499067185e-17 | 17.28192051955311 | 87.85452467660194 | 5.015566210449691 | 150.74146399916972 | 38.91494334887202 | 583.9142245409854 | 3.893684500828979e-13 | 28.081607832840564 | 809.1769212031784 | 1.3528946023215562 | True | INSUFFICIENT_COMMON_SUPPORT | 9.523594165111975e-17 | 6.489474168048299e-13 |
| EUR | 666 | 521 | 55 | 126591 | 0.526103751451525 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | 2.348959634186774 | 10.474666569072399 | 5.479406799369024 | 20.02381713032832 | 1.2018724595119266e-12 | 3.8120299608645696 | 28.782208130483514 | 2.9942624637060473 | 19.970625395870606 | 8.766458615856516 | 45.494525917319365 | 1.0187948102697293e-12 | 7.664044409641753 | 52.03856572131144 | 0.6453028295192733 | True | INSUFFICIENT_COMMON_SUPPORT | 1.5023405743899082e-12 | 1.2734935128371616e-12 |
| USD | 137 | 102 | 55 | 66284 | 0.20668637982016777 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | 2.1525142264977823 | 8.606469832276753 | 4.151961228097925 | 17.84008060398556 | 7.135529805964092e-09 | 2.6773411049253797 | 27.666001480955966 | 2.762649862056831 | 15.841765873045642 | 5.284685023006727 | 47.48845860895013 | 8.133008670003017e-07 | 3.824353009975489 | 65.62196149826715 | 0.6101356355590486 | True | INSUFFICIENT_COMMON_SUPPORT | 7.135529805964092e-09 | 8.133008670003017e-07 |
| SGD | 7 | 2 | 55 | 14070 | 0.04975124378109453 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | INSUFFICIENT_COMMON_SUPPORT | Not estimable | Not estimable |
| HKD | 8 | 3 | 55 | 7538 | 0.1061289466702043 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | INSUFFICIENT_COMMON_SUPPORT | Not estimable | Not estimable |
| CAD | 2 | 0 | 55 | 4139 | 0.048320850446967864 | 2030 | 49 | odds ratio vs OTHER_OR_SPARSE pool; not probability ratio | Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable | INSUFFICIENT_COMMON_SUPPORT | Not estimable | Not estimable |

### Direct internal holdout residuals

| threshold_seconds | evaluation | fit_n | evaluation_n | events | observed_rate | log_loss | null_log_loss | remaining_log_loss_fraction | brier | null_brier | auc_descriptive | model_columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300 | random_development_to_random_validation | 75375 | 74625 | 27323 | 0.36613735343383585 | 0.6526940864121252 | 0.6568813803159225 | 0.9936254946033279 | 0.23014109488465734 | 0.2320870528385653 | 0.5531134605147896 | 56 |
| 300 | chronological_early_to_chronological_late | 75000 | 75000 | 27370 | 0.36493333333333333 | 0.6510951464632799 | 0.6562039704120429 | 0.9922145793394772 | 0.22939723568164758 | 0.23175700693333331 | 0.5585043932222955 | 56 |
| 900 | random_development_to_random_validation | 75375 | 74625 | 18606 | 0.24932663316582915 | 0.5561278167348455 | 0.5616018925706604 | 0.9902527468154388 | 0.18507243217315167 | 0.18716574673460257 | 0.5663993329784185 | 56 |
| 900 | chronological_early_to_chronological_late | 75000 | 75000 | 18572 | 0.24762666666666666 | 0.5533041486499121 | 0.5597203909051924 | 0.9885367008964889 | 0.18390133686794405 | 0.186310568 | 0.5695786553405764 | 56 |
| 1800 | random_development_to_random_validation | 75375 | 74625 | 10849 | 0.14538023450586265 | 0.4121750758231631 | 0.41461214502537425 | 0.9941220506165781 | 0.12361977568412053 | 0.12424505048004864 | 0.556011831604412 | 56 |
| 1800 | chronological_early_to_chronological_late | 75000 | 75000 | 10790 | 0.14386666666666667 | 0.4089294763276781 | 0.4119470614876458 | 0.9926748229515938 | 0.12243636499816275 | 0.12317553440000004 | 0.5603381116381474 | 56 |

### Adjusted FX and gap main estimates

| feature | coefficient | ci_low | ci_high | p_value | split | outcome | model_n | effect_unit | exp_coefficient | exp_ci_low | exp_ci_high | exp_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fx | -0.057189241368764424 | -0.07550400541773494 | -0.03887447731979391 | 9.349531379347144e-10 | full | log_duration | 200000 | log(1+duration seconds) per unit | 0.9444153300048839 | 0.9272760163987592 | 0.9618714382500307 | Ratio of conditional geometric(duration+1); not median |
| gap | 0.003266042783015035 | -0.028730216157055625 | 0.0352623017230857 | 0.8414298758924926 | full | log_duration | 200000 | log(1+duration seconds) per unit | 1.0032713821119885 | 0.971678572288126 | 1.0358913892632722 | Ratio of conditional geometric(duration+1); not median |
| fx | 0.010617112460444413 | -0.01077349091520374 | 0.03200771583609256 | 0.33064390328524285 | full | IS_SLOW_900 | 200000 | log odds per unit | 1.0106736739951043 | 0.9892843352883823 | 1.0325254720716872 | Odds ratio; not risk ratio |
| gap | -0.01613381126392645 | -0.053127652656402596 | 0.02086003012854969 | 0.392671556347291 | full | IS_SLOW_900 | 200000 | log odds per unit | 0.9839956415449544 | 0.9482589569811182 | 1.021079121321441 | Odds ratio; not risk ratio |

### Common-support heterogeneity: log1p(seconds)

| contrast | population_n | shared_strata | supported_treated_n | supported_baseline_n | adjusted_difference | ci_low | ci_high | negative_strata | positive_strata |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gap 1 vs 0 | 1048575 | 687 | 63700 | 840184 | -0.01015177934320655 | -0.02593311479226585 | 0.005629556105852751 | 343.0 | 344.0 |
| FX 1 vs 0 | 731454 | 195 | 517400 | 112024 | -0.14699845549981008 | -0.16052635938989326 | -0.1334705516097269 | 139.0 | 56.0 |
| FX 2 vs 1 | 829292 | 308 | 188381 | 55332 | 0.019275893663811775 | 0.001138397723973221 | 0.03741338960365033 | 141.0 | 167.0 |
| FX 3 vs 2 | 281780 | 216 | 57474 | 26046 | 0.005775339100450905 | -0.020855549818539543 | 0.032406228019441354 | 110.0 | 106.0 |
| FX 4 vs 3 | 93649 | 118 | 16085 | 9628 | 0.0022791202797193453 | -0.04084323660877542 | 0.04540147716821411 | 57.0 | 61.0 |
| FX 5 vs 4 | 31386 | 57 | 4086 | 3124 | -0.01222022348920561 | -0.08657202867067729 | 0.06213158169226607 | 27.0 | 30.0 |
| FX 6 vs 5 | 10432 | 17 | 739 | 727 | 0.027959096406970283 | -0.12816472634779122 | 0.18408291916173178 | 6.0 | 11.0 |
| FX 7 vs 6 | 3503 | 3 | 96 | 92 | -0.06725841180512801 | -0.47684762339913367 | 0.3423307997888776 | 2.0 | 1.0 |
| FX 8 vs 7 | 1170 | 0 | 0 | 0 | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable |
| FX 9 vs 8 | 402 | 0 | 0 | 0 | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable |
| FX 10 vs 9 | 134 | 0 | 0 | 0 | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable |
| FX 11 vs 10 | 44 | 0 | 0 | 0 | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable |
| FX 12 vs 11 | 17 | 0 | 0 | 0 | Not estimable | Not estimable | Not estimable | Not estimable | Not estimable |

The negative single FX regression coefficient is an additive trend, not a uniform effect of every extra conversion. Matched FX1-vs0 is negative while FX2-vs1 is positive with a pointwise interval above zero; later transitions are uncertain and upper FX groups lack support. The full matched gap interval includes zero, with nearly balanced stratum directions. Do not sum populations across overlapping FX comparisons or interpret these as causal speedups.

## 3. Rules and issue resolution

| RULE_ID | STATUS | EFFECT_SIZE | UNCERTAINTY | LIMITATIONS |
| --- | --- | --- | --- | --- |
| F07 | REJECTED_HYPOTHESIS | negative=18; zero=0 | Finite observed medians; not population stochastic proof | Rejects universality only; does not reject any association; currency/amount/party residual confounding |
| F08 | REJECTED_HYPOTHESIS | negative=19; zero=1 | Finite observed medians; not population stochastic proof | Rejects universality only; does not reject any association; currency/amount/party residual confounding |
| F11 | INSUFFICIENT_EVIDENCE | CHF: INSUFFICIENT_COMMON_SUPPORT; GBP: INSUFFICIENT_COMMON_SUPPORT; CNY: INSUFFICIENT_COMMON_SUPPORT; EUR: INSUFFICIENT_COMMON_SUPPORT; USD: INSUFFICIENT_COMMON_SUPPORT; SGD: INSUFFICIENT_COMMON_SUPPORT; HKD: INSUFFICIENT_COMMON_SUPPORT; CAD: INSUFFICIENT_COMMON_SUPPORT | Fixed-baseline diagnostic variance only; not external validation | Selected outcome-overlap BIC pairs cover a small, nonrepresentative frame; thresholds and per-currency coverage disclosed; odds ratios are not risk ratios; no global currency claim. |
| F12 | INSUFFICIENT_EVIDENCE | Internal holdout residual log-loss fraction range=0.988537 to 0.994122 across 300/900/1800-second thresholds | No validated mechanism interval | Residual log loss is not a fraction of payments with an identified cause. No causal generating mechanism established; BIC support is audited but sparse BIC dummies excluded. |
| F13 | EXPLORATORY_ASSOCIATION | -0.057189241368764424 | HC1 pointwise95%[-0.075504005,-0.038874477] | The single linear FX coefficient averages heterogeneous transitions: minimum20-arm matching shows negative FX1-vs0 and positive FX2-vs1 effects. No universal speedup, causal effect or external validation; other observable and bank confounding remains. |
| F14 | INSUFFICIENT_EVIDENCE | 0.003266042783015035 | HC1 pointwise95%[-0.028730216,0.035262302] | Associational; linear/additive conditional model; pooled rare currency group; matched support differs; no external validation. CI crossing zero is insufficient evidence, not proof of zero effect. |

## 4. Remaining blockers

- I02: the data cannot support a broad independent currency effect at adequate bank-pair overlap. Additional overlapping observations, a separately justified partially pooled model with sensitivity, or removal of the global currency mechanism claim is needed. Do not generalize the selected frame.
- I05 and UI-specific I07/I19 remain Phase2 data-model/presentation work; no false cross-grain slicers or median-of-medians.
- Legacy09 still points to its original13-row evidence snapshot. This Phase1 release uses only `outputs/rules/final_rule_register.csv` (22columns). Do not import the legacy snapshot into the final dashboard.
- Anomaly-history and token-incremental claims remain unsupported outside retrospective QA scope.
- Pointwise HC1 and pair-cluster intervals are conditional diagnostics, not causal or external validation.

## 5. Source integrity and privacy

All three source hashes agree before/after each new notebook. No source amount, account, token, BIC placeholder, anomaly or outlier was changed or removed. The explicitly requested22-row mismatch file and BIC segment tables contain competition transaction information and remain under ignored outputs; do not commit or publish them. Raw CSV authority is a documented authorized computational policy, not a claim of workbook equality.

## 6. Phase 1 completion

Implementation and execution scope: COMPLETE. Readiness goal: NOT COMPLETE: global currency/BIC common-support blocker remains; final decision PHASE_1_STILL_BLOCKED. No dashboard was built.

## 7. Final acceptance and artifact inventory

All 47 cross-notebook acceptance checks passed. The Wilson endpoint audit used a1e-12 arithmetic tolerance after diagnosing at most2.22e-16 floating-point roundoff; no statistical results were edited to pass. All five chart artifacts were visually inspected. The Direct coefficient chart displays a fixed prefix of30 non-intercept terms; the complete56-column model is in the coefficient table.

Verification: outputs/phase1/verification/20261115T005246408900Z/acceptance_checks.csv. Full generated table/chart file list with hashes: outputs/phase1/verification/20261115T005246408900Z/artifact_inventory.json. Generated table/chart artifacts: 47.
