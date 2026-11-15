# Phase 2 final integration — current decision

READY_FOR_POWER_BI_WITH_LIMITATIONS

This section supersedes prior readiness/integration statuses; historical evidence below is retained. See phase2_final_integration_report.md, phase2_issue_reassessment.md and dashboard_readiness_matrix.md. I01/I03/I04 are not reopened. I02/F11 and F12 remain analytically limited.

| ISSUE | PHASE2_STATUS | EVIDENCE_AND_SCOPE |
| --- | --- | --- |
| I05 | RESOLVED_IN_RELEASE | Per-fact grain/filter contract; only dimension-to-fact joins; invalid filters tested |
| I06 | RESOLVED | Only audited22-column canonical register;14 IDs and six statuses; legacy register deprecated |
| I07 | RESOLVED | Canonical nine-row slow table and paired rate/volume charts retain threshold reversal |
| I08 | RESOLVED_WITH_SCOPE | Primary217 strata +9.93546% has own CI; earlier1777 +12.03143% sensitivity has no CI |
| I09 | RESOLVED | Seven same-split baselines; no tree or incremental R² causal attribution |
| I10 | RESOLVED | Full currency/party mean, median, P75/P90/P95/P99/IQR and both conditional probabilities |
| I14 | RESOLVED_WITH_SCOPE | Legacy03 excludes135 rows; full08 and fixed holdout523941 are separately labelled |
| I15 | RESOLVED_WITH_LIMITATIONS | 66 conditional endpoint groups integrated; approximate consistency not proven independence |
| I18 | RESOLVED_WITH_SCOPE | Full raw, same-support raw and adjusted bridge; selection and reweighting explicitly distinguished |
| I19 | RESOLVED_BY_RESTRICTED_CONTRACT | 4365 rows globally reconciled, never category-allocated; filtered full coverage unknown; quantiles exact grain only |
| I20 | RESOLVED_FOR_FINAL_RELEASE | Dedicated final charts replace legacy presentation; n, units, CIs and sparse caveats; no unequal-bin histogram claim |
| I21 | RESOLVED | 14 complete business evidence cards linked one-to-one to canonical rule IDs |


<!-- PHASE2_CURRENT_END -->

# Phase 1 repair reassessment

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

---

## Pre-Phase 1 audit baseline

# Missing analysis checklist

Overall decision: **NOT_READY**. Existing calculations are distinguished from missing work; audit diagnostics do not silently complete original notebooks.

| ITEM | ANALYSIS | RQ | CLASSIFICATION | CURRENT_STATUS | WHY_IT_MATTERS | EXACT_RECOMMENDED_CALCULATION | ISSUE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Holdout gap validation | RQ3 | RECOMMENDED_ENHANCEMENT | EXISTS; audit adds heldout MAE/RMSE | Model calibration must generalize beyond fitted rows. | Retain development-only predictions; label legacy n<=10 versus full population; integrate audit error summary. | I14 |
| 2 | Conditional endpoint independence | RQ4 | RECOMMENDED_ENHANCEMENT | CALCULATED_IN_THIS_AUDIT | Aggregate independence can conceal dependence. | Integrate all 66 route/gap/participant groups, marginal/product rates, V and BH results, with sparse-cell flags. | I15 |
| 3 | Covered/Indirect duration uncertainty | RQ6 | RECOMMENDED_ENHANCEMENT | STRICTER_ESTIMATE_HAS_CI; original singleton estimator does not | Do not transplant an interval across estimands. | Use min20 effect0.094723257 with its CI and 217 strata, or bootstrap the original 1777-stratum estimand separately. | I08 |
| 4 | BIC confounding of currency-Covered | RQ5/RQ11 | MUST_FIX_BEFORE_POWER_BI | MISSING_JOINT_CONTROL | Bank-network mixture can explain apparent currency branches. | Compare currency+participant+FX+amount+party effects with and without supported pair controls on identical overlap; report per-currency coverage. | I02 |
| 5 | Amount confounding of currency-Covered | RQ5/RQ11 | MUST_FIX_BEFORE_POWER_BI | PARTIAL: four contrasts in 05 include amount bands | Amount cannot be claimed fully controlled for all currencies. | Extend prespecified major-currency comparisons or narrow page4 to four supported contrasts; retain sparse support. | I02/I16 |
| 6 | Direct long-tail explanation | RQ8 | MUST_FIX_BEFORE_POWER_BI | PARTIAL_SCREENING_ONLY | Largest slow-payment volume remains unexplained. | Direct-only threshold profiles and common-support contrasts using currency/amount/party/hour/label and supported BIC; report residual uncertainty. | I03 |
| 7 | Slow threshold sensitivity | RQ15 | MUST_FIX_BEFORE_POWER_BI | TABLES_EXIST; AUDIT_RANK_REVERSAL_SHOWN | Rate ranking is threshold dependent; workload ranking differs. | Use both count/rate at >300/>900/>1800; explain Covered-to-Indirect rate-rank reversal; no official SLA label. | I07 |
| 8 | Nonlinear participant-duration relation | RQ7 | RECOMMENDED_ENHANCEMENT | WITHIN_ROUTE_QUANTILES_EXIST | No constant-seconds-per-bank law is supported. | Add adjacent participant quantile differences and heldout nested baseline comparison without extrapolating sparse tail. | I09 |
| 9 | Currency-duration after adjustment | RQ11 | RECOMMENDED_ENHANCEMENT | USD_EXISTS; OTHERS_MISSING | USD result cannot represent all currencies. | Prespecified currency contrasts on shared route/participant/FX/amount/party support with time sensitivity and BIC caveat. | I16 |
| 10 | Party effect sizes | RQ5/RQ11 | OPTIONAL | EXISTS; route association V0.002488 | Large population can make tiny effects significant. | Keep party as a covariate/segment, not headline rule; retain C_B uncertainty including zero. | I21 |
| 11 | Currency multiple comparisons | RQ5/RQ11 | RECOMMENDED_ENHANCEMENT | ASSOCIATION_TEST_BH_EXISTS; contrast intervals pointwise | Many currency comparisons can exaggerate selected residuals. | Declare test family and show all effect sizes with simultaneous/BH diagnostics or explicit exploratory status. | I16 |
| 12 | Sparse-group thresholds | RQ2/RQ5/RQ6 | RECOMMENDED_ENHANCEMENT | EXISTS_BUT_DIFFERENT_THRESHOLDS | Changing minimum n changes support and estimand. | Document min5/10/20/100/500/1000 roles; compare thresholds on identical/changed support explicitly. | I18/I20 |
| 13 | BIC-pair coverage | RQ5 | MUST_FIX_BEFORE_POWER_BI | AUDIT: >=100 pairs cover8.8614%; singletons21.5422% | A few high-volume pairs cannot represent whole network. | Show pair/transaction coverage and per-currency overlap next to every pair effect. | I02 |
| 14 | Time robustness | RQ3/RQ6/RQ11 | RECOMMENDED_ENHANCEMENT | EXISTS_FOR_GAP,COVERED,USD | Same-data exploration is not external validation. | Extend chronological checks to main adjusted FX/gap/Direct-tail contrasts and label UTC semantics. | I04 |
| 15 | Historical-only anomaly features | RQ12 | RECOMMENDED_ENHANCEMENT | MISSING; recurrence is retrospective | Future matches leak information in real-time interpretations. | Sort within account history and compute strictly prior events; if not implemented, label retrospective QA and downgrade page7. | I11/I12 |
| 16 | Token incremental value | RQ13 | OPTIONAL | MISSING_HELDOUT_INCREMENT | Formatting may simply re-encode existing covariates. | Add tokens to fixed baseline and compare heldout loss only if page7 claims incremental mechanism; otherwise descriptive parser panel only. | I13 |
| 17 | Chart for every final rule | RQ14/RQ15 | MUST_FIX_BEFORE_POWER_BI | PARTIAL | Adjusted rules and rejected hypotheses lack dedicated evidence charts. | Map F01-F12 to appropriate exception/count, calibration or CI plot; explicitly untestedF12 gets no invented mechanism chart. | I20/I21 |
| 18 | Valid metric denominator | RQ15 | MUST_FIX_BEFORE_POWER_BI | STATIC_GRAINS_DOCUMENTED; slicers incomplete | Filtered ratios/percentiles can become invalid. | Build explicit additive numerators/denominators and filter tests; show suppression coverage. | I05/I19 |
| 19 | Dashboard grain and relationships | RQ15 | MUST_FIX_BEFORE_POWER_BI | PARTIAL; data dictionary not a relationship model | Mixing grains can double count rows. | Adopt per-table grain/compatible slicers matrix below; no fact-to-fact or many-to-many summary joins. | I05 |
| 20 | Specific defensible business value | RQ15 | MUST_FIX_BEFORE_POWER_BI | AUDIT_CARDS_ADDED; dashboard not integrated | Unsupported operational recommendations weaken submission. | Use six-question evidence cards; distinguish monitoring/investigation from causal improvements or monetary savings. | I21 |

Additional prerequisite: resolve I01 source authority; integrate the audited rule register (I06). Optional work becomes required only if its page claims the corresponding mechanism.
