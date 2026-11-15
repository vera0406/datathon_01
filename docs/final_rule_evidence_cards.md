# Final business evidence cards

All applications are proposed monitoring/QA/benchmarking uses, not demonstrated savings, speedups, fraud prevention or SLA improvements. Rejected and unresolved rows are not supported discoveries.

## F01: Direct iff two participants

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F01 |
| RULE_NAME | Direct iff two participants |
| WHAT_HAPPENED | DIRECT iff participants=2; non-direct participants>=3 |
| UNDER_WHAT_CONDITIONS | All observed transactions |
| EFFECT_SIZE | 100 |
| RELIABILITY | Wilson intervals by directional scope in source table; Random and chronological splits |
| ALTERNATIVE_EXPLANATIONS | Definition-compatible synthetic constraint; inverse and non-direct consequence merged; not 3 discoveries |
| WHY_IT_MATTERS | Route metadata consistency; proposed Validate route-participant metadata |
| SUPPORT_N | 1048575.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | percent satisfying constraint |
| STATUS | SUPPORTED_STRUCTURAL_RULE |
| CONFIDENCE | HIGH_DESCRIPTIVE |
| SOURCE_TABLE | outputs/tables/remaining/08_rule_validation/20261114T145941443291Z/structural_rule_validation.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F01_evidence.png |
| DASHBOARD_PAGE | 2 |
| CAVEAT | Definition-compatible synthetic constraint; inverse and non-direct consequence merged; not 3 discoveries |

## F02: FX link-count upper bound

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F02 |
| RULE_NAME | FX link-count upper bound |
| WHAT_HAPPENED | FX<=participants-1 |
| UNDER_WHAT_CONDITIONS | All observed transactions |
| EFFECT_SIZE | 100 |
| RELIABILITY | Wilson lower bound 0.999996336; Random/time splits |
| ALTERNATIVE_EXPLANATIONS | FX>=2 implies non-direct is a consequence of F01+F02, omitted as independent discovery |
| WHY_IT_MATTERS | FX metadata constraints; proposed Validate synthetic FX feasibility |
| SUPPORT_N | 1048575.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | percent satisfying constraint |
| STATUS | SUPPORTED_STRUCTURAL_RULE |
| CONFIDENCE | HIGH_DESCRIPTIVE |
| SOURCE_TABLE | outputs/tables/routing/advanced/fx_observed_upper_bounds.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F02_evidence.png |
| DASHBOARD_PAGE | 2 |
| CAVEAT | FX>=2 implies non-direct is a consequence of F01+F02, omitted as independent discovery |

## F03: Approximate per-link gap probability

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F03 |
| RULE_NAME | Approximate per-link gap probability |
| WHAT_HAPPENED | Gap probability approximates 1-(1-p)^(n-1) |
| UNDER_WHAT_CONDITIONS | Participants>=2 |
| EFFECT_SIZE | 0.04988862779638522 |
| RELIABILITY | Model-based 95% [0.049552512,0.050224744]; Fixed-development heldout n=523941; WMAE=0.061475 pp; WRMSE=0.200764 pp |
| ALTERNATIVE_EXPLANATIONS | Counts are calibration coverage, not binary rule confidence; links not observed; unique mechanism not identified; tail sparse |
| WHY_IT_MATTERS | Traceability expectations; proposed Monitor gap rates conditional on route complexity |
| SUPPORT_N | 1048575.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | probability per hypothetical link |
| STATUS | PLAUSIBLE_GENERATING_MECHANISM |
| CONFIDENCE | MODERATE_MECHANISM |
| SOURCE_TABLE | outputs/tables/final_evidence/gap_final_calibration.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F03_evidence.png |
| DASHBOARD_PAGE | 3 |
| CAVEAT | Counts are calibration coverage, not binary rule confidence; links not observed; unique mechanism not identified; tail sparse |

## F04: Approximately independent endpoint mismatch

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F04 |
| RULE_NAME | Approximately independent endpoint mismatch |
| WHAT_HAPPENED | Joint mismatch near product of marginals |
| UNDER_WHAT_CONDITIONS | Visible endpoints |
| EFFECT_SIZE | -0.002963653255599972 |
| RELIABILITY | Finite-population rates; no proof of independence; 66 conditional audit groups; multiplicity and sparse-cell flags |
| ALTERNATIVE_EXPLANATIONS | No nonsignificance-as-proof; shared endpoint patterns remain possible |
| WHY_IT_MATTERS | Path QA; proposed Separate endpoint perturbation from latency assumptions |
| SUPPORT_N | 1048575.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | percentage points joint minus product |
| STATUS | PLAUSIBLE_GENERATING_MECHANISM |
| CONFIDENCE | MODERATE_MECHANISM |
| SOURCE_TABLE | outputs/tables/final_evidence/endpoint_final_diagnostics.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F04_evidence.png |
| DASHBOARD_PAGE | 3 |
| CAVEAT | No nonsignificance-as-proof; shared endpoint patterns remain possible |

## F05: Covered versus Indirect adjusted duration

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F05 |
| RULE_NAME | Covered versus Indirect adjusted duration |
| WHAT_HAPPENED | Within217 sufficiently supported matched strata, Covered showed 9.94% higher conditional geometric mean of duration+1 than Indirect under the specified matching framework. |
| UNDER_WHAT_CONDITIONS | Within217 matched participant/FX/currency/party strata; >=20 per arm |
| EFFECT_SIZE | 0.09935457416632099 |
| RELIABILITY | Pointwise95% relative interval [0.078672272,0.120433436]; log interval [0.075730907,0.113715607]; Direction stable in random/time partitions |
| ALTERNATIVE_EXPLANATIONS | Primary min20 estimand only; earlier min1 point is sensitivity without valid singleton variance; no median/raw-second/causal claim; amount/BIC residual confounding remains. |
| WHY_IT_MATTERS | Like-for-like latency benchmarking; proposed Monitor supported payment segments |
| SUPPORT_N | 302410.0 |
| SCOPE_N | 386330 |
| EFFECT_UNIT | Relative conditional geometric(duration+1) difference (fraction) |
| STATUS | EXPLORATORY_ASSOCIATION |
| CONFIDENCE | MODERATE_ASSOCIATION |
| SOURCE_TABLE | outputs/tables/final_evidence/covered_indirect_duration_estimands.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F05_evidence.png |
| DASHBOARD_PAGE | 5 |
| CAVEAT | Primary min20 estimand only; earlier min1 point is sensitivity without valid singleton variance; no median/raw-second/causal claim; amount/BIC residual confounding remains. |

## F06: USD versus other adjusted duration

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F06 |
| RULE_NAME | USD versus other adjusted duration |
| WHAT_HAPPENED | Mean log(1+duration) difference |
| UNDER_WHAT_CONDITIONS | USD vs other |
| EFFECT_SIZE | -0.1392869449772893 |
| RELIABILITY | 95% [-0.149472003,-0.129101886]; expm1=-0.130021643; Direction stable in random/time partitions |
| ALTERNATIVE_EXPLANATIONS | Not median effect; support differs from earlier +12.03143%; no causal interpretation; Covered contrast lacks amount/BIC control |
| WHY_IT_MATTERS | Like-for-like latency benchmarking; proposed Monitor supported payment segments |
| SUPPORT_N | 1032510.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | log(1+duration seconds) |
| STATUS | STRONG_STATISTICAL_PATTERN |
| CONFIDENCE | MODERATE_ASSOCIATION |
| SOURCE_TABLE | outputs\tables\remaining\05_currency_party\20261114T141027551754Z\adjusted_duration_contrasts.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F06_evidence.png |
| DASHBOARD_PAGE | 5 |
| CAVEAT | Not median effect; support differs from earlier +12.03143%; no causal interpretation; Covered contrast lacks amount/BIC control |

## F07: Universal positive adjacent-FX median increment

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F07 |
| RULE_NAME | Universal positive adjacent-FX median increment |
| WHAT_HAPPENED | Rejected a universal positive observed median penalty. Did NOT reject every association, heterogeneous transition, or causal mechanism hypothesis. |
| UNDER_WHAT_CONDITIONS | Comparable cells with >=100/arm |
| EFFECT_SIZE | negative=18; zero=0 |
| RELIABILITY | Finite observed medians; not population stochastic proof; All qualifying groups retained |
| ALTERNATIVE_EXPLANATIONS | Rejects universality only; does not reject any association; currency/amount/party residual confounding |
| WHY_IT_MATTERS | Avoid unsupported latency penalties; proposed Use conditional evidence instead of a universal surcharge |
| SUPPORT_N | 11.0 |
| SCOPE_N | 29 |
| EFFECT_UNIT | comparison groups, not transactions |
| STATUS | REJECTED_HYPOTHESIS |
| CONFIDENCE | HIGH_FINITE_POPULATION_REJECTION |
| SOURCE_TABLE | outputs/tables/duration/adjusted/fx_median_counterexamples_rechecked.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F07_evidence.png |
| DASHBOARD_PAGE | 5 |
| CAVEAT | Rejects universality only; does not reject any association; currency/amount/party residual confounding |

## F08: Universal positive gap median penalty

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F08 |
| RULE_NAME | Universal positive gap median penalty |
| WHAT_HAPPENED | Rejected a universal positive observed median penalty. Did NOT reject every association, heterogeneous transition, or causal mechanism hypothesis. |
| UNDER_WHAT_CONDITIONS | Comparable cells with >=100/arm |
| EFFECT_SIZE | negative=19; zero=1 |
| RELIABILITY | Finite observed medians; not population stochastic proof; All qualifying groups retained |
| ALTERNATIVE_EXPLANATIONS | Rejects universality only; does not reject any association; currency/amount/party residual confounding |
| WHY_IT_MATTERS | Avoid unsupported latency penalties; proposed Use conditional evidence instead of a universal surcharge |
| SUPPORT_N | 9.0 |
| SCOPE_N | 29 |
| EFFECT_UNIT | comparison groups, not transactions |
| STATUS | REJECTED_HYPOTHESIS |
| CONFIDENCE | HIGH_FINITE_POPULATION_REJECTION |
| SOURCE_TABLE | outputs/tables/duration/adjusted/gap_median_counterexamples_rechecked.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F08_evidence.png |
| DASHBOARD_PAGE | 5 |
| CAVEAT | Rejects universality only; does not reject any association; currency/amount/party residual confounding |

## F09: Duplicate-label exact recurrence

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F09 |
| RULE_NAME | Duplicate-label exact recurrence |
| WHAT_HAPPENED | Exact account-pair/amount/currency neighbor within 86400 seconds |
| UNDER_WHAT_CONDITIONS | DUPLICATE_PAYMENT with evaluable accounts |
| EFFECT_SIZE | 0.9999828084826767 |
| RELIABILITY | Pointwise Newcombe 95% [0.949329868,0.999989125]; Full-window and 86400-second comparison |
| ALTERNATIVE_EXPLANATIONS | Related-row dependence; repeat is not fraud; future-neighbor linkage is descriptive, not deployable historical prediction |
| WHY_IT_MATTERS | Duplicate QA; proposed Check label-linkage consistency while preserving repeated rows |
| SUPPORT_N | 72.0 |
| SCOPE_N | 72 |
| EFFECT_UNIT | risk difference |
| STATUS | STRONG_STATISTICAL_PATTERN |
| CONFIDENCE | HIGH_DESCRIPTIVE |
| SOURCE_TABLE | outputs\tables\remaining\06_anomaly_analysis\20261114T141310667842Z\duplicate_label_recurrence_contrasts.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F09_evidence.png |
| DASHBOARD_PAGE | 7 |
| CAVEAT | Related-row dependence; repeat is not fraud; future-neighbor linkage is descriptive, not deployable historical prediction |

## F10: Recognizable field openings

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F10 |
| RULE_NAME | Recognizable field openings |
| WHAT_HAPPENED | All opening markers recognized |
| UNDER_WHAT_CONDITIONS | Both token sides; same transaction population |
| EFFECT_SIZE | 0 unrecognized openings; 1650 strict-block opening residuals; 7661 closing residuals |
| RELIABILITY | Full observed strings; Independent source/cache checks |
| ALTERNATIVE_EXPLANATIONS | Marker syntax is not semantic validity; balanced-block hypothesis revised; no novel entity/fraud rule |
| WHY_IT_MATTERS | Token formatting QA; proposed Use field-opening parser and retain residual diagnostics |
| SUPPORT_N | 1048575.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | marker/bracket counts |
| STATUS | SUPPORTED_STRUCTURAL_RULE |
| CONFIDENCE | HIGH_DESCRIPTIVE |
| SOURCE_TABLE | outputs\tables\remaining\07_tokens\20261114T142113971612Z\token_parser_coverage.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F10_evidence.png |
| DASHBOARD_PAGE | 7 |
| CAVEAT | Marker syntax is not semantic validity; balanced-block hypothesis revised; no novel entity/fraud rule |

## F11: Currency-associated routing signals remain network-confounded

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F11 |
| RULE_NAME | Currency-associated routing signals remain network-confounded |
| WHAT_HAPPENED | Exploratory participant/FX-standardized routing differences exist; broad independent currency effects after BIC control remain unestablished. Extreme selected-frame odds ratios are not shown. |
| UNDER_WHAT_CONDITIONS | Non-direct transactions; CHF example |
| EFFECT_SIZE | CHF: INSUFFICIENT_COMMON_SUPPORT; GBP: INSUFFICIENT_COMMON_SUPPORT; CNY: INSUFFICIENT_COMMON_SUPPORT; EUR: INSUFFICIENT_COMMON_SUPPORT; USD: INSUFFICIENT_COMMON_SUPPORT; SGD: INSUFFICIENT_COMMON_SUPPORT; HKD: INSUFFICIENT_COMMON_SUPPORT; CAD: INSUFFICIENT_COMMON_SUPPORT |
| RELIABILITY | Fixed-baseline diagnostic variance only; not external validation; CHF/GBP/EUR/USD contrasts retain direction with amount/party |
| ALTERNATIVE_EXPLANATIONS | Exploratory participant/FX-standardized currency-versus-rest diagnostics only; BIC frame2030/386330 (49pairs) is nonrepresentative; no broad independent currency effect. Phase1 extreme odds ratios are not portfolio rules. |
| WHY_IT_MATTERS | Currency-aware route baselines; proposed Use as an investigation lead until BIC sensitivity is checked |
| SUPPORT_N | 2030.0 |
| SCOPE_N | 386330 |
| EFFECT_UNIT | percentage points observed minus expected |
| STATUS | INSUFFICIENT_EVIDENCE |
| CONFIDENCE | MODERATE_DESCRIPTIVE |
| SOURCE_TABLE | outputs/tables/final_evidence/currency_routing_final_diagnostics.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F11_evidence.png |
| DASHBOARD_PAGE | 4 |
| CAVEAT | Exploratory participant/FX-standardized currency-versus-rest diagnostics only; BIC frame2030/386330 (49pairs) is nonrepresentative; no broad independent currency effect. Phase1 extreme odds ratios are not portfolio rules. |

## F12: Direct residual long tail remains largely unexplained

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F12 |
| RULE_NAME | Direct residual long tail remains largely unexplained |
| WHAT_HAPPENED | Unresolved: Direct residual long tail remains largely unexplained. No positive mechanism or exact-zero effect is established. |
| UNDER_WHAT_CONDITIONS | DIRECT with two participants |
| EFFECT_SIZE | Internal holdout residual log-loss fraction range=0.988537 to 0.994122 across 300/900/1800-second thresholds |
| RELIABILITY | No validated mechanism interval; All three thresholds and random/chronological partitions; heldout log loss and Brier versus training prevalence |
| ALTERNATIVE_EXPLANATIONS | Residual log loss is not a fraction of payments with an identified cause. No causal generating mechanism established; BIC support is audited but sparse BIC dummies excluded. |
| WHY_IT_MATTERS | Direct-payment slow volume; proposed Investigate supported Direct segments; no causal SLA claim |
| SUPPORT_N | Not estimable |
| SCOPE_N | 662245 |
| EFFECT_UNIT | transactions; mechanism untested |
| STATUS | INSUFFICIENT_EVIDENCE |
| CONFIDENCE | LOW_MECHANISTIC |
| SOURCE_TABLE | outputs/tables/duration/direct_tail/direct_adjustment_residual_metrics.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F12_evidence.png |
| DASHBOARD_PAGE | 6 |
| CAVEAT | Residual log loss is not a fraction of payments with an identified cause. No causal generating mechanism established; BIC support is audited but sparse BIC dummies excluded. |

## F13: Adjusted fx duration association

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F13 |
| RULE_NAME | Adjusted fx duration association |
| WHAT_HAPPENED | Mean log1p(duration seconds); slow900 odds sensitivity |
| UNDER_WHAT_CONDITIONS | Fixed seed probability sample with observed covariates |
| EFFECT_SIZE | -0.057189241368764424 |
| RELIABILITY | HC1 pointwise95%[-0.075504005,-0.038874477]; Random/time direction stable=True; all minimum20 matching comparisons retained |
| ALTERNATIVE_EXPLANATIONS | The single linear FX coefficient averages heterogeneous transitions: minimum20-arm matching shows negative FX1-vs0 and positive FX2-vs1 effects. No universal speedup, causal effect or external validation; other observable and bank confounding remains. |
| WHY_IT_MATTERS | Avoid equating non-universality with no association; proposed Conditional latency investigation |
| SUPPORT_N | 200000.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | log(1+duration seconds) per FX or gap unit |
| STATUS | EXPLORATORY_ASSOCIATION |
| CONFIDENCE | MODERATE_CONDITIONAL |
| SOURCE_TABLE | outputs/tables/duration/adjusted/common_support_fx_gap_comparisons.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F13_evidence.png |
| DASHBOARD_PAGE | 5 |
| CAVEAT | The single linear FX coefficient averages heterogeneous transitions: minimum20-arm matching shows negative FX1-vs0 and positive FX2-vs1 effects. No universal speedup, causal effect or external validation; other observable and bank confounding remains. |

## F14: Adjusted gap duration association

| FIELD | VALUE |
| --- | --- |
| RULE_ID | F14 |
| RULE_NAME | Adjusted gap duration association |
| WHAT_HAPPENED | Unresolved: Adjusted gap duration association. No positive mechanism or exact-zero effect is established. |
| UNDER_WHAT_CONDITIONS | Fixed seed probability sample with observed covariates |
| EFFECT_SIZE | 0.003266042783015035 |
| RELIABILITY | HC1 pointwise95%[-0.028730216,0.035262302]; Random/time direction stable=False; all minimum20 matching comparisons retained |
| ALTERNATIVE_EXPLANATIONS | Associational; linear/additive conditional model; pooled rare currency group; matched support differs; no external validation. CI crossing zero is insufficient evidence, not proof of zero effect. |
| WHY_IT_MATTERS | Avoid equating non-universality with no association; proposed Conditional latency investigation |
| SUPPORT_N | 200000.0 |
| SCOPE_N | 1048575 |
| EFFECT_UNIT | log(1+duration seconds) per FX or gap unit |
| STATUS | INSUFFICIENT_EVIDENCE |
| CONFIDENCE | LOW_ASSOCIATION_EVIDENCE |
| SOURCE_TABLE | outputs/tables/duration/adjusted/adjusted_fx_gap_effects.csv; outputs/tables/duration/adjusted/common_support_fx_gap_comparisons.csv |
| SOURCE_CHART | outputs\charts\final_evidence\F14_evidence.png |
| DASHBOARD_PAGE | 5 |
| CAVEAT | Associational; linear/additive conditional model; pooled rare currency group; matched support differs; no external validation. CI crossing zero is insufficient evidence, not proof of zero effect. |
