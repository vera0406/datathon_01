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

# Final analytical output audit

## A. Executive Summary

**Decision: NOT_READY.** All 11 notebooks pass fresh-kernel execution in an isolated project copy, but execution success is not analytical readiness. Essential gaps affect currency-versus-bank confounding, Direct long-tail explanation, adjusted FX/gap duration interpretation and dashboard filter validity. A source-authority gate also remains:22 original workbook amounts differ from raw CSV by USD0.01-0.39. No source values were edited to make checks pass.

This audit follows the supplied UMDAC final audit standard. It is a review plus explicitly labeled diagnostic calculations, not implementation of every proposed fix. No Power BI dashboard was built. All generated project prose and code are English.

Primary story: payment characteristics → routing architecture → participants/FX → path observability → duration → slow-payment workload. Currency, party, anomaly and token evidence is promoted only within its supported scope.

Audit workspace: `outputs\final_audit\20261114T154100298050Z`. Fresh-kernel results, source hashes, artifact inventory, output comparisons, conditional endpoints, pair coverage and threshold sensitivity are retained there. Existing notebooks and outputs were not overwritten. Source datasets were real isolated copies; no source-data hardlinks were used. The virtual environment junction resolved to the existing project `.venv`; no packages were installed.

## B. Research Question Coverage Matrix

| RQ | STATUS | EVIDENCE | MISSING_WORK_OR_SCOPE |
| --- | --- | --- | --- |
| RQ1 | PARTIALLY_ANSWERED | 03 structural tables; 08 full/split constraints | Direct iff two participants is strong; complete Covered versus Indirect assignment is not reconstructed. Joint currency/BIC/amount/party support-adjusted selection analysis is missing. |
| RQ2 | ANSWERED_WITH_STRONG_EVIDENCE | 03 participant-FX-path tables; 08 structural validation | No missing basic constraints; distinguish derived implications and scope of visible paths. |
| RQ3 | ANSWERED_WITH_STRONG_EVIDENCE | 03 gap model comparison; 08 heldout calibration; audit heldout metrics | Approximate mechanism only; unique per-link independence not identifiable from any-gap flag. |
| RQ4 | ANSWERED_WITH_STRONG_EVIDENCE | 03 overall rates; audit conditional_endpoint_diagnostics.csv | 66 conditional groups checked; no adequately supported BH-significant group; this does not prove independence. |
| RQ5 | PARTIALLY_ANSWERED | 03 adjusted currency/BIC-pair effects; 05 amount/party-adjusted currency contrasts | Joint currency plus BIC-pair common-support control is missing; standalone party/amount Covered contrasts also missing. |
| RQ6 | PARTIALLY_ANSWERED | 04 distribution, segment quantiles, tree; 05 adjusted contrasts | No complete duration mechanism; jointly controlled FX/gap effects and Direct-tail residual explanation needed. |
| RQ7 | PARTIALLY_ANSWERED | 04 route-participant quantiles and shallow tree | Nested heldout explanatory baselines: route, participants, route+participants, then other features; report change in log and raw-scale error, not causal partition. |
| RQ8 | PARTIALLY_ANSWERED | 04 Direct FX ECDF, bands, currency profiles, route-hour screening | Direct-only slow outcome at each threshold versus currency, amount band, party, hour, label and sufficiently supported BIC; investigate residual tail, not just display it. |
| RQ9 | PARTIALLY_ANSWERED | 04 adjacent FX medians; 08 counterexamples | No uniform positive direction established. Currency/amount/party-adjusted FX comparison with uncertainty and overlap is missing. |
| RQ10 | PARTIALLY_ANSWERED | 04 matched route/participants/FX medians; 08 counterexamples | Add currency/amount/party/time-adjusted gap contrast with uncertainty; absence of universal penalty is not absence of any association. |
| RQ11 | PARTIALLY_ANSWERED | 05 USD duration and four Covered contrasts; 03 all-currency residuals | Extend adjusted duration beyond USD; BIC control, joint support and declared multiplicity for major currency contrasts. |
| RQ12 | PARTIALLY_ANSWERED | 06 exact recurrence and label profiles | Duplicate linkage supported; Romance/CEO/account-replacement history and fat-finger peer multipliers not reconstructed. Intended amount and external events remain unobserved. |
| RQ13 | EXPLORATORY_ONLY | 07 parser, party associations and adjusted anomaly field-count differences | No heldout incremental duration/routing information test beyond baseline covariates, nor semantic redundancy/label-leakage assessment. |
| RQ14 | PARTIALLY_ANSWERED | 08 original register plus audited final_rule_register.csv | Audited register deduplicates architecture/FX consequences and supplies required schema; 09 still points to legacy 13-row register and needs integration. |
| RQ15 | PARTIALLY_ANSWERED | Routing QA, traceability baselines, slow volume/rate evidence | Specify operational metric/threshold/owner as proposed applications; no evidence for savings or causal intervention benefit. |

## C. Notebook Quality Review

All tests started new kernels with outputs cleared in memory and were saved only in the isolated copy. Project notebook outputs05-09 remain intentionally cleared following the user’s earlier privacy request; this is not treated as execution failure. No variables pass between notebook kernels.

| NOTEBOOK | FRESH_KERNEL_RUN | ALL_CELLS_EXECUTED | OUTPUTS_REPRODUCIBLE | UNRESOLVED_ERRORS | POPULATION | MAIN_QUESTION | MAIN_OUTPUTS_AND_CHARTS | MAIN_FINDINGS | MISSING_OR_WEAK | FINAL_USE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00_environment_check.ipynb | PASS | YES | YES: environment/path checks only | 0 | Not applicable: environment only | Does the project environment import required packages and locate the workbook? | No analytical tables/charts | Imports pass; workbook exists | No full package-version/export provenance in original notebook | READY_FOR_ENVIRONMENT_CHECK_ONLY |
| 00_data_audit.ipynb | PASS | YES | YES | 0 | 1048575 CSV rows; original Excel check100 sampled rows | Are original data structurally valid? | audit_* tables; no charts | Population1048575; gaps80504; no continuity disagreement | Original workbook validation was a100-row sample, superseded by separate full reconciliation finding22 amount differences | NOT_FINAL_SOURCE_RECONCILIATION |
| 01_data_cleaning.ipynb | PASS | YES | YES | 0 | 1048575 | Are original fields preserved while features are added? | cleaning_actions_log; cleaning_validation_report; audit_cleaning_comparison | 21 original columns preserved;25 derived fields; all rows retained | Original validation correctly says Excel equality PARTIAL; canonical source decision pending | READY_WITH_SOURCE_LIMITATION |
| 02_eda.ipynb | PASS | YES | YES | 0 | 1048575 | What is portfolio composition and where are candidate patterns? | eda_* frequency/quantile/token overview;8 EDA PNGs | Global median56 seconds; category/route baseline and candidate hypotheses | Exploratory only; raw FX/participant medians confounded; hypotheses are not final rules | READY_AS_EXPLORATORY_CONTEXT |
| 03_bank_routing.ipynb | PASS | YES | YES | 0 | 1048575; gap-model legacy<=10 participant population1048440 | Which architecture and observability mechanisms are plausible? | routing_*; participant_fx; structural_rule_evidence; advanced/*;4 routing/gap PNGs | Direct iff2; FX<=n-1; approximate5% link gaps; endpoint marginals near5% | Joint currency/BIC confounding unresolved; pair coverage8.86%; dependent rules duplicated; sparse calibration chart tail lacks n/CI | READY_WITH_LIMITATIONS_FOR_STRUCTURE; NOT_FINAL_FOR_CURRENCY |
| 04_payment_duration.ipynb | PASS | YES | YES | 0 | 1048575; tree sample200000/train150000/test50000 | What explains duration and slow-payment workload? | duration_global_statistics; route/participant/FX/gap profiles; matched strata; threshold tables; tree metrics;5 duration PNGs | Median56; route39/283/378; original matched geometric(duration+1)+12.03143%; logR2 .046579 | Direct-tail explanation incomplete; adjusted FX/gap robustness missing; nested explanatory baselines missing; singleton estimator uncertainty unavailable | NOT_FINAL_FOR_PRIMARY_MECHANISTIC_STORY |
| 05_currency_party.ipynb | PASS | YES | YES | 0 | 1048575; contrast support separately reported | Do currency and party differences persist after basic adjustment? | currency/party profiles; associations; adjusted contrasts;2PNG | Currency-party V.071511; USD adjusted logdifference-.139286945; party-route V.002488 | OnlyUSD adjusted duration; only 4adjustedCovered currency contrasts; amount mean/P90/P99/IQR absent; BIC jointly uncontrolled; generic interpretations | PARTIAL |
| 06_anomaly_analysis.ipynb | PASS | YES | YES | 0 | 1048575;1547 labeled;1047028 unlabeled | Do labels reveal observable mechanisms? | anomaly_profile; adjusted_contrasts; recurrence profiles/contrasts; rounding;2PNG | 72/72 duplicate labels exact match within86400 sec vs18/1047028 unlabeled; CUSTOMER_RECALL32 | Other scam histories/multipliers not reconstructed; retrospective neighboring uses future rows; rare labels no min20support except Romance | READY_ONLY_AS_RETROSPECTIVE_SUPPORTING_QA |
| 07_tokens.ipynb | PASS | YES | YES | 0 | 1048575 per side | Are token structures parseable and informative beyond composition? | parser_coverage; tag_presence; profiles; adjusted_token_count;1PNG | Zero unrecognized openings; opening residual710/940; closing2842/4819; partyV.108285/.101377 | No incremental duration/routing value or semantics/redundancy validation; parser coverage is syntax only | READY_ONLY_FOR_PARSER_QA |
| 08_rule_validation.ipynb | PASS | YES | YES | 0 | 1048575; shared contrast populations in tables | Which rules withstand exception and internal stability checks? | structural_validation; gapcalibration/stability; endpoint; counterexamples; legacy13 rules;1PNG | 25rule×split checks zeroexceptions; p.049888628; stricterCovered+9.93546%;18/29negativeFX;19/29negativegap | Legacy rule dependencies/schema/statuses not compliant; corrected4hypothesis statuses preserved; audited final register must be integrated | PARTIAL; AUDIT_REGISTER_SUPPLIED |
| 09_dashboard_data_prep.ipynb | PASS | YES | YES | 0 | 1048575; cube948 rows including4365suppressed transactions | Can aggregates support a defensible Power BI model? | 12 CSVs including dictionary/validation; connectionmanifest;1PNG | Counts/sums reconcile; no direct account/BIC/token columns; medians explicitly nonadditive | No complete relationship/slicer model; missing calibrated/slow/adjusted facts for plannedpages; legacyrules stillreferenced | NOT_READY_FOR_FULL_EIGHT_PAGE_MODEL |

### Execution and output comparison evidence

| notebook | fresh_kernel_run | all_cells_executed | executed_code_cells | unresolved_errors | seconds |
| --- | --- | --- | --- | --- | --- |
| 00_environment_check | PASS | YES | 2 | 0 | 8.922303915023804 |
| 00_data_audit | PASS | YES | 11 | 0 | 70.75160503387451 |
| 01_data_cleaning | PASS | YES | 9 | 0 | 35.71855545043945 |
| 02_eda | PASS | YES | 20 | 0 | 16.350170373916626 |
| 03_bank_routing | PASS | YES | 24 | 0 | 35.58853626251221 |
| 04_payment_duration | PASS | YES | 16 | 0 | 13.529657363891602 |
| 05_currency_party | PASS | YES | 4 | 0 | 12.41402292251587 |
| 06_anomaly_analysis | PASS | YES | 4 | 0 | 15.681643724441528 |
| 07_tokens | PASS | YES | 4 | 0 | 46.653698444366455 |
| 08_rule_validation | PASS | YES | 5 | 0 | 9.003829002380371 |
| 09_dashboard_data_prep | PASS | YES | 4 | 0 | 6.326356887817383 |

All regenerated analytical CSVs with matching original filenames were compared (142 tables). Common numeric columns use rtol1e-9/atol1e-8; strings compare in row order. Detailed ledger: `outputs\final_audit\20261114T154100298050Z\fresh_output_comparison.csv`. Empty or changed columns are not silently accepted. This comparison does not assert semantic equality for row-order differences; exceptions appear below.

| source_table | fresh_table | rows | differing_common_columns | new_columns | removed_columns |
| --- | --- | --- | --- | --- | --- |
| outputs\tables\remaining\05_currency_party\20261114T141027551754Z\adjusted_covered_currency_contrasts.csv | outputs\final_audit\20261114T154100298050Z\isolated_project\outputs\tables\remaining\05_currency_party\20261114T154413926971Z\adjusted_covered_currency_contrasts.csv | 4 |  | uncertainty_status |  |
| outputs\tables\remaining\05_currency_party\20261114T141027551754Z\adjusted_duration_contrasts.csv | outputs\final_audit\20261114T154100298050Z\isolated_project\outputs\tables\remaining\05_currency_party\20261114T154413926971Z\adjusted_duration_contrasts.csv | 8 |  | uncertainty_status |  |
| outputs\tables\remaining\06_anomaly_analysis\20261114T141310667842Z\anomaly_adjusted_contrasts.csv | outputs\final_audit\20261114T154100298050Z\isolated_project\outputs\tables\remaining\06_anomaly_analysis\20261114T154426684588Z\anomaly_adjusted_contrasts.csv | 24 |  | uncertainty_status |  |
| outputs\tables\remaining\07_tokens\20261114T142113971612Z\adjusted_token_count_contrasts.csv | outputs\final_audit\20261114T154100298050Z\isolated_project\outputs\tables\remaining\07_tokens\20261114T154442077354Z\adjusted_token_count_contrasts.csv | 12 |  | uncertainty_status |  |

The four schema-only differences are the added `uncertainty_status` metadata column in older05/06/07 tables. All 142 compared tables reproduce their common-column values; no numerical/common-column discrepancy was found. Thus OUTPUTS_REPRODUCIBLE is YES for the tested calculations, with schema evolution disclosed separately. Refresh or pin the four older artifacts before release. The isolated regenerated cleaned CSV is byte-identical to the current project cleaned CSV.

### Known04 reproducibility risk

`global_stats` is explicitly calculated in zero-based cell3 (global distribution), before cells4 and15 reference it. All 16 code cells passed fresh execution. The previously suspected undefined-variable issue does not exist in the current file. Original notebooks use notebook-directory working-directory conventions; this test used that documented context. The new notebooks additionally check the exact project virtual-environment executable.

## D. Data Integrity Review

The prior independent source audit compared **22,020,075 original cells** (1048575 rows×21 columns), in order, with zero raw-to-cleaned differences. All 25 derived fields and current compact/token caches independently matched source. Exact tuple recurrence matched the hash-based cache. That report passed 70 independent checks after matching the documented z=1.96 convention and an appropriate floating optimizer tolerance.

Accounts and BICs are read as strings in source/linkage scans. Currency categories remain source codes; B/C meanings are not invented. Amount uses USD_AMOUNT_NUM for cross-currency value comparisons, not unobserved FX prices. Durations remain numeric seconds; log1p is a reversible analytical transformation, not replacement of original values. All anomalies and extreme/long-tail rows remain in source; blank labels are UNLABELED, never confirmed legitimate. CUSTOMER_RECALL remains separate (32 rows). No duplicate-looking transaction was deleted. `drop_duplicates` in the helper is limited to validating observed key/hash mappings and does not modify the primary population.

Path gaps (80504) and placeholders remain intact. The full audit scan found zero disagreements between HAS_PATH_GAP=Y and CONTINUITY_QFLAG_STD=N. Observable-node counting excludes placeholders only in a derived feature. Endpoint definitions must remain explicit: visible endpoints versus literal outer path tokens are different conventions if placeholders occur at boundaries.

**Workbook/export reconciliation:** full 21-field/1048575-row comparison found22 USD_AMOUNT mismatches, no extra rows, and no differences in the other original fields. They range USD0.01–0.39, maximum relative difference4.129222518998437191681277563E-10. None disappear when rounded to cents. Their cause is not established; small relative size does not establish strict equality. This pre-existing source-chain discrepancy is retained as I01/P0 for exact-amount authority until documented resolution, not a claim of new-notebook corruption. Do not silently repair the workbook or CSV.

All original source files remained byte-identical during the current isolated execution:

| SOURCE | SHA256_BEFORE | UNCHANGED_AFTER |
| --- | --- | --- |
| data\raw\swift_payments_raw_export.csv | ea0eaa18311df2c9332aec336a198307df2996559f7f5abc2840ea0ef2d46d29 | True |
| data\raw\swift_umdac_datathon_2026_fictitious_payment_data.xlsx | 5787b5f9fee3ebcb8ab35462eab75931e70e77dc601c091f334d72dd9e32ea57 | True |
| data\cleaned\swift_payments_cleaned.csv | f8b2d946f647e02778d3b232be2f10a91f4adbf1b06c72045c075319a3a9d85c | True |

No organizer-signed baseline or independent original copy was available. Current hashes, full comparisons and historical recorded cleaned hashes cannot establish all modifications or intent before the first recorded baseline. New code was not committed, pushed, or published by this audit. Existing raw/cleaned data and outputs remain ignored by Git.

## E. Statistical Methodology Review

- Exact enumeration is appropriate for observed structural constraints. Wilson bounds describe hypothetical independent generator draws, not uncertainty about observed finite counts. F01 merges Direct→2,2→Direct and non-direct→>=3; FX>=2→non-direct follows F01+F02. There are two independent architecture constraints here, not five discoveries.
- The03 common gap fit uses participants2–10, n1048440, excluding135 rows. Its in-sample common-model weighted MAE0.051496 pp and RMSE0.141525 pp are calculated over route×participant cells. Its routing-specific p values are diagnostic, not independent causal effects. The08 full fit pools participant counts and has different population/grain; its errors are not interchangeable with 03 errors.
- The08 full p=0.049888628, model-based95%CI[0.049552512,0.050224744]. Fixed-development random validation covers 523,941 rows: weighted MAE0.061475 pp, RMSE0.200764 pp. Sparse upper participant counts are retained and flagged. Random/chronological partitions are internal stability checks after exploration, not independent external validation.
- Conditional endpoint diagnostic:66 groups; maximum V among adequately supported/non-sparse groups0.019217, maximum absolute joint-minus-product residual0.093470 pp. No adequately supported BH-significant group was found. Sparse expected cells limit chi-square interpretation. Groups overlap; BH is exploratory, not a proof of conditional independence.
- Matching uses exact common strata and weights proportional to min(n1,n0), with coverage reported. Independent-cell analytic intervals treat weights as fixed and can understate uncertainty under account-family dependence. No extrapolation to unsupported strata is justified. Original 1777-stratum minimum-one estimator includes singleton cells and cannot estimate their variance; its CI remains unavailable. The217-stratum minimum20 estimator is a different estimand with a valid conditional analytic interval.
- expm1 of a mean log1p-duration contrast compares weighted geometric means of duration+1. It is not a median difference, raw-second percentage change, or causal route effect. Covered matching does not control amount/BIC; USD duration uses amount bands/party but residual BIC and within-band composition remain.
- A weighted standardized log contrast is expm1 of the weighted stratum log differences. It is not an arithmetic weighted average of individual percentage changes. Raw full-population and adjusted restricted-support estimates must not be attributed solely to confounding; selection and weighting change too.
- Mixed conditional median directions refute a uniform positive pattern in the observed grouping; they do not prove zero independent association or a negative causal FX effect. Currency/amount/party-adjusted FX/gap robustness remains missing.
- Cramér V and rate differences are preferable to p-only selection at this n. Sparse categorical tests flag expected cells; BH correction exists for selected overall association tests, not all currency subgroup contrasts. Pointwise intervals must remain labeled as such.
- Tree R2(log-duration)=0.0465793484 and MAE(log-duration)=1.79133253 on50000 test rows are weak explanatory performance, not causal feature attribution or evidence that route/participants uniquely explain4.66% of raw duration. Preselecting top10 currencies on the entire exploratory sample is mild test-set feature-definition leakage; if reporting predictive validation, learn grouping on training data only.
- Duplicate matching uses exact cleaned-numeric amount serialization, account pair/currency and time proximity; this narrow definition can miss near duplicates. Full-window/future neighbors are acceptable retrospective diagnostics, not historical-only deployment features. Related rows challenge independent-binomial intervals.
- No mixture model or formal regime identification was found. Log-spaced count histograms suggest hypotheses, but uneven bin width and composition can create apparent modes; visual appearance cannot establish multiple generating regimes.
- Token field-opening coverage does not validate literal values or semantics. Token/anomaly count comparisons do not establish incremental duration/routing explanation; template redundancy and label leakage remain alternatives. No association-rule miner was used, so support/confidence/lift requirements for such mining are not applicable.

## F. Major Supported Findings

| METRIC | VALUE | UNIT |
| --- | --- | --- |
| TRANSACTIONS | 1048575.0 | Transactions |
| MEAN_DURATION | 772.4185938058794 | Seconds |
| MEDIAN_DURATION | 56.0 | Seconds |
| STD_DURATION | 1227.873621008158 | Seconds |
| MIN_DURATION | 2.0 | Seconds |
| P25_DURATION | 26.0 | Seconds |
| P75_DURATION | 1108.0 | Seconds |
| P90_DURATION | 2548.0 | Seconds |
| P95_DURATION | 3404.0 | Seconds |
| P99_DURATION | 5288.0 | Seconds |
| MAX_DURATION | 13831.0 | Seconds |

Route distributions (all durations in seconds):

| ROUTING_TYPE | TRANSACTION_COUNT | MEAN_DURATION | MEDIAN_DURATION | P90_DURATION | P95_DURATION | P99_DURATION | MEDIAN_VS_DIRECT_RATIO | MEDIAN_VS_DIRECT_DIFFERENCE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DIRECT | 662245 | 663.3842928221428 | 39.0 | 2344.0 | 3146.0 | 4833.0 | 1.0 | 0.0 |
| INDIRECT | 342752 | 964.7069747222481 | 283.0 | 2927.0 | 3815.0 | 5789.0 | 7.256410256410256 | 244.0 |
| COVERED | 43578 | 916.9913947404654 | 378.0 | 2801.0 | 3774.0 | 5851.0 | 9.692307692307692 | 339.0 |

Covered versus Indirect on stricter matching: n=386,330, retained38,017 Covered and264,393 Indirect in 217 strata; adjusted logdifference0.094723257,95%CI[0.075730907,0.113715607], geometric(duration+1) relative difference9.935457% (CI7.867227%–12.043344%). The earlier +12.031430% point estimate is reproduced separately with 1777 strata and no singleton variance interval.

USD versus others: adjusted logdifference-0.139286945,95%CI[-0.149472003,-0.129101886], geometric(duration+1)-13.002164%;283 shared strata. This is a narrow robust association under tested controls, not a global currency mechanism.

Currency-Covered observed/expected diagnostic examples (participant+FX standardized, non-direct denominators):

| CURRENCY | TOTAL | OBSERVED_RATE_PERCENT | EXPECTED_RATE_PERCENT | DIFFERENCE_PP | OBSERVED_EXPECTED_RATIO |
| --- | --- | --- | --- | --- | --- |
| EUR | 126591 | 12.477980267159593 | 11.408324656525668 | 1.0696556106339248 | 1.0937609721706218 |
| USD | 66284 | 9.96620602256955 | 11.297871472177402 | -1.3316654496078524 | 0.8821312976619299 |
| GBP | 33614 | 16.945320402213362 | 11.186422495361388 | 5.758897906851974 | 1.5148114072430205 |
| CHF | 30870 | 18.649173955296405 | 11.191679085533712 | 7.457494869762693 | 1.6663428081495117 |
| SGD | 14070 | 6.162046908315565 | 11.183922920095801 | -5.021876011780236 | 0.5509736567696929 |
| CNY | 12610 | 17.11340206185567 | 11.179742336229543 | 5.933659725626127 | 1.5307510269174327 |
| HKD | 7538 | 5.120721676837357 | 11.18305160060198 | -6.062329923764622 | 0.4579002100430003 |
| CAD | 4139 | 3.165015704276395 | 11.18656625409995 | -8.021550549823555 | 0.2829300459483174 |

05 additional amount/party adjustment covers CHF/GBP/EUR/USD only; it is currency-versus-other risk difference and not the same observed-versus-expected estimand above. Do not join these estimates as identical measures.

Label profiles (UNLABELED is unverified; medians in USD and seconds):

| labeled | n | median_amount_usd | median_duration_seconds |
| --- | --- | --- | --- |
| ACCOUNT_REPLACEMENT_SCAM | 82 | 3457.225 | 532.0 |
| CEO_SCAM | 97 | 24647.11 | 836.0 |
| CUSTOMER_RECALL | 32 | 3070.605 | 45.0 |
| DUPLICATE_PAYMENT | 72 | 1891.935 | 463.0 |
| FAT_FINGER_MISTAKE | 199 | 241433.93 | 48.0 |
| ROMANCE_SCAM | 1065 | 140.03 | 1228.0 |
| UNLABELED | 1047028 | 3656.785 | 56.0 |

## G. Rejected / Revised Hypotheses

- Uniformly positive adjacent FX increments: 18/29 adequately supported comparisons are negative.
- Uniformly positive gap penalties: 19 negative,9 positive,1 zero among 29 adequate comparisons.
- Broad FX-duration and gap-duration association questions are **not rejected** merely by those counterexamples. The four previously erroneous dispositions were corrected before this audit.
- A definitive independent-link generator is not identified; an approximate model is supported. Endpoint approximate independence is compatible with perturbation, not evidence of operational failure.
- Universal balanced token blocks are rejected/revised; field openings remain recognized. Literal token/detail mismatch is not evidence of identity fraud.
- Party type is not a major route determinant in this population (V≈0.002488), despite any large-n p-value. Currency-party V≈0.071511 is modest; C_B versus C_C adjusted duration interval contains zero.
- Source equality is restricted to raw→cleaned; full workbook→raw equality is rejected at22 amount cells. Original 100-row sample validation was never full equivalence.
- Scam labels, extreme amounts and parser fields do not substantiate email compromise, account replacement, intended multipliers, or a strong fraud classifier. Such mechanisms remain insufficient/exploratory.

## H. Missing Analyses

All 20 mandatory gap checks and exact proposed calculations are in [missing_analysis_checklist.md](missing_analysis_checklist.md). Full prioritized issue contracts are in [pre_powerbi_fix_list.md](pre_powerbi_fix_list.md).

| ISSUE_ID | PRIORITY | NOTEBOOK | PROBLEM | STATUS |
| --- | --- | --- | --- | --- |
| I01 | P0 | 00/01 | 22 USD_AMOUNT cells differ from the original workbook by USD 0.01-0.39. Raw-to-cleaned equality is exact, but workbook equivalence is false. | OPEN_SOURCE_AUTHORITY_REQUIRED |
| I02 | P1 | 03/05 | BIC pair not jointly controlled with currency; high-volume pair sample covers only 92918/1048575 rows. | OPEN |
| I03 | P1 | 04 | FX and currency profiles display the tail but do not sufficiently explain it. | OPEN |
| I04 | P1 | 04/08 | Conditional median direction tests do not establish independent effects or independence after all relevant controls. | OPEN |
| I05 | P1 | 09 | Aggregate profiles have incompatible grains; no explicit star-model/filter contract for all eight pages. | OPEN |
| I06 | P1 | 08/09 | Legacy 13-row register counts equivalent architecture statements and dependent FX consequences separately; schema/status vocabulary differs from standard. | AUDIT_REGISTER_CREATED; DOWNSTREAM_INTEGRATION_OPEN |
| I07 | P1 | 04/09 | Highest-rate route reverses between 300 and 900/1800 seconds; Direct has highest volume at all thresholds. | DIAGNOSTIC_COMPLETE; PRESENTATION_OPEN |
| I08 | P2 | 04/08 | Original 1777-stratum +12.03143% estimator lacks estimable singleton-cell variance; stricter estimate changes support. | PARTLY_RESOLVED_BY_STRICTER_ESTIMATOR |
| I09 | P2 | 04 | Tree R2=0.046579 is not the fraction uniquely explained by route or participant count. | OPEN |
| I10 | P2 | 05 | Mean/P90/P99/IQR and explicit P(currency / party) shares are missing from 05 profiles. | OPEN |
| I11 | P2 | 06 | No sender-recipient concentration, historical beneficiary changes or contextual 10x/100x/0.1x/0.01x tests. | OPEN; DOWNGRADE_PAGE_IF_NOT_IMPLEMENTED |
| I12 | P2 | 06 | Only full-window versus 86400-second recurrence; route similarity, broader windows and false-match context missing. | OPEN |
| I13 | P2 | 07 | Adjusted token-count/label differences do not establish incremental duration/routing explanation. | OPEN; OPTIONAL_IF_PAGE_DOWNGRADED |
| I14 | P2 | 03/08 | 03 comparison excludes participants >10 (135 records); 08 fits all participants. | AUDIT_SCOPE_AND_HELDOUT_METRICS_CREATED |
| I15 | P2 | 03/08 | Original register has overall approximation, not a complete conditional independence check. | AUDIT_DIAGNOSTIC_COMPLETE; INTEGRATION_OPEN |
| I16 | P2 | 05/08 | Pointwise adjusted currency contrasts are exploratory; large-N significance cannot substitute for practical magnitude. | PARTIAL |
| I17 | P2 | 05-09 | Caches lack content checks; latest manifests select by timestamp; helper report has hardcoded narratives. | OPEN; CURRENT_CONTENT_INDEPENDENTLY_VERIFIED |
| I18 | P2 | 05-09 | Raw difference uses all rows; adjusted difference restricts and reweights. | OPEN |
| I19 | P2 | 09 | 4365 rows are pooled into unassignable small-cell rollup; cube medians cannot be recombined. | LIMITATION_DOCUMENTED; UI_CONTRACT_OPEN |
| I20 | P3 | 02-09 | Legacy gap plot connects small Covered groups without pointwise n/CI; many charts omit population context. Log-spaced histograms use counts per unequal-width bin. | OPEN |
| I21 | P2 | 03-09 | Several implications are generic; no complete six-question evidence card per final finding. | AUDIT_CARDS_CREATED; DASHBOARD_INTEGRATION_OPEN |
| I22 | P3 | 08 | Four association hypotheses formerly inherited a universal-positive rejection. | RESOLVED_BEFORE_THIS_AUDIT |

## I. Business Value Review

Each evidence card below answers what, conditions, effect size, reliability, alternatives and operational application. Monitoring applications are proposals, not demonstrated improvements or monetary savings.

### F01: Direct iff two participants

**What / conditions:** All observed transactions → DIRECT iff participants=2; non-direct participants>=3.

**Size:** 100 (percent satisfying constraint); baseline: All transactions.

**Reliability:** support1048575; scope1048575; Wilson intervals by directional scope in source table. Random and chronological splits.

**Alternatives / limitations:** Definition-compatible synthetic constraint; inverse and non-direct consequence merged; not 3 discoveries.

**Business use:** Route metadata consistency; proposed application: Validate route-participant metadata. Evidence status: SUPPORTED_STRUCTURAL_RULE.

### F02: FX link-count upper bound

**What / conditions:** All observed transactions → FX<=participants-1.

**Size:** 100 (percent satisfying constraint); baseline: Participants minus one.

**Reliability:** support1048575; scope1048575; Wilson lower bound 0.999996336. Random/time splits.

**Alternatives / limitations:** FX>=2 implies non-direct is a consequence of F01+F02, omitted as independent discovery.

**Business use:** FX metadata constraints; proposed application: Validate synthetic FX feasibility. Evidence status: SUPPORTED_STRUCTURAL_RULE.

### F03: Approximate per-link gap probability

**What / conditions:** Participants>=2 → Gap probability approximates 1-(1-p)^(n-1).

**Size:** 0.04988862779638522 (probability per hypothetical link); baseline: Common per-link model.

**Reliability:** support1048575; scope1048575; Model-based 95% [0.049552512,0.050224744]. Fixed-development heldout n=523941; WMAE=0.061475 pp; WRMSE=0.200764 pp.

**Alternatives / limitations:** Counts are calibration coverage, not binary rule confidence; links not observed; unique mechanism not identified; tail sparse.

**Business use:** Traceability expectations; proposed application: Monitor gap rates conditional on route complexity. Evidence status: PLAUSIBLE_GENERATING_MECHANISM.

### F04: Approximately independent endpoint mismatch

**What / conditions:** Visible endpoints → Joint mismatch near product of marginals.

**Size:** -0.002963653255599972 (percentage points joint minus product); baseline: Product of marginal rates.

**Reliability:** support1048575; scope1048575; Finite-population rates; no proof of independence. 66 conditional audit groups; multiplicity and sparse-cell flags.

**Alternatives / limitations:** No nonsignificance-as-proof; shared endpoint patterns remain possible.

**Business use:** Path QA; proposed application: Separate endpoint perturbation from latency assumptions. Evidence status: PLAUSIBLE_GENERATING_MECHANISM.

### F05: Covered versus Indirect adjusted duration

**What / conditions:** COVERED vs INDIRECT → Mean log(1+duration) difference.

**Size:** 0.09472325684084444 (log(1+duration seconds)); baseline: COVERED vs INDIRECT.

**Reliability:** support302410; scope386330; 95% [0.075730907,0.113715607]; expm1=0.099354574. Direction stable in random/time partitions.

**Alternatives / limitations:** Not median effect; support differs from earlier +12.03143%; no causal interpretation; Covered contrast lacks amount/BIC control.

**Business use:** Like-for-like latency benchmarking; proposed application: Monitor supported payment segments. Evidence status: EXPLORATORY_ASSOCIATION.

### F06: USD versus other adjusted duration

**What / conditions:** USD vs other → Mean log(1+duration) difference.

**Size:** -0.1392869449772893 (log(1+duration seconds)); baseline: USD vs other.

**Reliability:** support1032510; scope1048575; 95% [-0.149472003,-0.129101886]; expm1=-0.130021643. Direction stable in random/time partitions.

**Alternatives / limitations:** Not median effect; support differs from earlier +12.03143%; no causal interpretation; Covered contrast lacks amount/BIC control.

**Business use:** Like-for-like latency benchmarking; proposed application: Monitor supported payment segments. Evidence status: STRONG_STATISTICAL_PATTERN.

### F07: Universal positive adjacent-FX median increment

**What / conditions:** Comparable cells with >=100/arm → All conditional observed median differences positive.

**Size:** negative=18; zero=0 (comparison groups, not transactions); baseline: Adjacent FX / no-gap median.

**Reliability:** support11; scope29; Finite observed medians; not population stochastic proof. All qualifying groups retained.

**Alternatives / limitations:** Rejects universality only; does not reject any association; currency/amount/party residual confounding.

**Business use:** Avoid unsupported latency penalties; proposed application: Use conditional evidence instead of a universal surcharge. Evidence status: REJECTED_HYPOTHESIS.

### F08: Universal positive gap median penalty

**What / conditions:** Comparable cells with >=100/arm → All conditional observed median differences positive.

**Size:** negative=19; zero=1 (comparison groups, not transactions); baseline: Adjacent FX / no-gap median.

**Reliability:** support9; scope29; Finite observed medians; not population stochastic proof. All qualifying groups retained.

**Alternatives / limitations:** Rejects universality only; does not reject any association; currency/amount/party residual confounding.

**Business use:** Avoid unsupported latency penalties; proposed application: Use conditional evidence instead of a universal surcharge. Evidence status: REJECTED_HYPOTHESIS.

### F09: Duplicate-label exact recurrence

**What / conditions:** DUPLICATE_PAYMENT with evaluable accounts → Exact account-pair/amount/currency neighbor within 86400 seconds.

**Size:** 0.9999828084826767 (risk difference); baseline: UNLABELED: 18/1047028.

**Reliability:** support72; scope72; Pointwise Newcombe 95% [0.949329868,0.999989125]. Full-window and 86400-second comparison.

**Alternatives / limitations:** Related-row dependence; repeat is not fraud; future-neighbor linkage is descriptive, not deployable historical prediction.

**Business use:** Duplicate QA; proposed application: Check label-linkage consistency while preserving repeated rows. Evidence status: STRONG_STATISTICAL_PATTERN.

### F10: Recognizable field openings

**What / conditions:** Both token sides; same transaction population → All opening markers recognized.

**Size:** 0 unrecognized openings; 1650 strict-block opening residuals; 7661 closing residuals (marker/bracket counts); baseline: Strict balanced-block grammar.

**Reliability:** support1048575; scope1048575; Full observed strings. Independent source/cache checks.

**Alternatives / limitations:** Marker syntax is not semantic validity; balanced-block hypothesis revised; no novel entity/fraud rule.

**Business use:** Token formatting QA; proposed application: Use field-opening parser and retain residual diagnostics. Evidence status: SUPPORTED_STRUCTURAL_RULE.

### F11: Currency residual in Covered selection

**What / conditions:** Non-direct transactions; CHF example → Observed Covered exceeds participant/FX-expected rate.

**Size:** 7.457494869762693 (percentage points observed minus expected); baseline: CHF observed18.649174% vs expected11.191679%.

**Reliability:** support30870; scope386330; Fixed-baseline diagnostic variance only; not external validation. CHF/GBP/EUR/USD contrasts retain direction with amount/party.

**Alternatives / limitations:** BIC confounding untested jointly; other currencies and tests exploratory; 18.649% is within-CHF, not a global rate.

**Business use:** Currency-aware route baselines; proposed application: Use as an investigation lead until BIC sensitivity is checked. Evidence status: EXPLORATORY_ASSOCIATION.

### F12: Direct long-tail generating mechanism

**What / conditions:** DIRECT with two participants → A specific mechanism explains residual slow Direct payments.

**Size:** 240752 Direct rows >300 seconds (transactions; mechanism untested); baseline: Direct FX/currency/amount/time strata.

**Reliability:** supportnot tested; scope662245; No validated mechanism interval. Threshold distributions available.

**Alternatives / limitations:** Displayed long tail is not a reconstructed cause; no formal regime identification; label/history/BIC controls incomplete.

**Business use:** Direct-payment slow volume; proposed application: Investigate supported Direct segments; no causal SLA claim. Evidence status: INSUFFICIENT_EVIDENCE.


## J. Dashboard Readiness

See [dashboard_readiness_matrix.md](dashboard_readiness_matrix.md) for all 8 page contracts and every09 export table. Pages1–3 can be limited-scope descriptive/structural panels; page7 is downgraded to supporting retrospective QA. Currency decisions(page4), duration drivers(page5), full slow-payment mechanism(page6) and final integrated rules(page8) are not ready as planned. A workload-only page6 could be limited-scope ready if it does not claim to explain the Direct tail.

No fact-to-fact joins or arbitrary cross-grain slicers are defensible. Per-rule statistical estimates are disconnected fixed estimands. Suppression preserves total counts, not filter attribution. Percentiles are exact-grain only. Metadata and validation files are not transaction facts.

## K. Final Recommendation

**Do not begin the full Power BI submission yet.** Resolve source authority I01/P0 and essential P1 gaps for the primary story, or explicitly narrow/remove unsupported claims and pages. Retain negative findings; do not fill the story with weak anomaly/token discoveries. An honest residual “Direct long tail remains unexplained under tested variables” can be presented only after adequate investigation, not as an invented mechanism.

The audited final register uses the 22 required columns and six permitted statuses. F01 merges logically equivalent architecture statements; F02 absorbs the FX>=2 consequence. Support percentages are transaction-coverage percentages for descriptive/calibration associations, not predictive confidence; F07/F08 use comparison-group units. F12 is explicitly untested/insufficient, with blank support rather than zero. Register entries include rejected and insufficient hypotheses and must not all be counted as supported discoveries. The09 pipeline still references the legacy register: integration remains open.


### Final quality gate

| GATE | RESULT |
| --- | --- |
| Population/original columns/derived preservation | PASS raw→cleaned; workbook source authority BLOCKED |
| Fresh-kernel execution | 11/11 PASS; zero original files overwritten |
| Structural and FX constraints | PASS; dependencies merged in audit register |
| Gap and endpoint mechanisms | PASS_WITH_LIMITATIONS; audit diagnostics require integration |
| Currency-Covered major confounders | BLOCKED: joint BIC support/control missing |
| Duration statistics and transformed effect interpretation | PASS; original-vs-stricter interval/support separated |
| Independent FX/gap duration and Direct tail | BLOCKED: insufficient adjusted explanatory work |
| Slow thresholds and negative evidence | CALCULATED; threshold rank reversal must be integrated |
| Anomaly/token methodology | LIMITED_TO_RETROSPECTIVE_QA; expanded mechanisms unsupported |
| Final rules and evidence | AUDIT_REGISTER_CREATED; downstream integration/chart gaps open |
| Page source tables/grain/slicers/business use | CONTRACTS_CREATED; primary pages NOT_READY |
| Overall approval | NOT_READY |
