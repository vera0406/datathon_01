"""Reproducible, non-destructive evidence reconstruction for notebooks 05--09.

Only aggregate artifacts are exported. Private analytical caches stay in ignored
outputs/. Intervals describe hypothetical independent draws from this generator,
not uncertainty about the observed finite competition population.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize_scalar
from statsmodels.stats.multitest import multipletests

EXPECTED = 1_048_575
SEED = 2026
MAPPING = {
    "SOURCE_ROW_NUMBER": "source_row", "TRANSACTION_TYPE_CODE_STD": "route",
    "CURRENCY_CODE_STD": "currency", "PARTY_PAIR": "party",
    "ORDERING_TYPE_STD": "ordering_type", "BENEFICIARY_TYPE_STD": "beneficiary_type",
    "ANOMALY_TYPE_STD": "anomaly", "USD_AMOUNT_NUM": "amount_usd",
    "TOTAL_DURATION_NUM": "duration_seconds", "PARTICIPANT_COUNT_NUM": "participants",
    "FX_COUNT_NUM": "fx", "EPOCH_SECONDS_NUM": "epoch", "HAS_PATH_GAP": "gap",
    "OBSERVED_BIC_COUNT": "observed_bics", "HAS_ANOMALY_LABEL": "has_label",
    "UNDOCUMENTED_ANOMALY_FLAG": "undocumented_label",
}
NUMERIC = ["source_row", "amount_usd", "duration_seconds", "participants", "fx", "epoch",
           "observed_bics", "has_label", "undocumented_label"]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def wilson(k, n):
    k, n = np.asarray(k, dtype=float), np.asarray(n, dtype=float)
    p = np.divide(k, n, out=np.full_like(k, np.nan), where=n > 0)
    den = 1 + 1.96**2 / n
    center = (p + 1.96**2 / (2*n)) / den
    margin = 1.96 / den * np.sqrt(p*(1-p)/n + 1.96**2/(4*n*n))
    return np.maximum(0, center-margin), np.minimum(1, center+margin)


class Study:
    def __init__(self, root, phase, prerequisites=()):
        self.root = Path(root).resolve()
        self.phase = phase
        self.source = self.root / "data/cleaned/swift_payments_cleaned.csv"
        self.sha = digest(self.source)
        self.run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.tables = self.root / "outputs/tables/remaining" / phase / self.run
        self.charts = self.root / "outputs/charts/remaining" / phase / self.run
        self.rules = self.root / "outputs/rules/remaining" / phase / self.run
        self.cache = self.root / "outputs/cache/remaining"
        for path in (self.tables, self.charts, self.rules, self.cache):
            path.mkdir(parents=True, exist_ok=False if path != self.cache else True)
        self.files, self.checks, self.findings = [], [], []
        self.manifests = {p: self.latest(p) for p in prerequisites}
        assert all(m["source_sha256"] == self.sha for m in self.manifests.values()), "Stale prerequisite"
        self.df = self.load_core()
        self.check("Source population", len(self.df), EXPECTED)
        self.check("Unique source row numbers", self.df.source_row.nunique(), EXPECTED)
        self.check("Sequential Excel row identifiers", bool(np.array_equal(self.df.source_row, np.arange(2, EXPECTED+2))), True)
        self.check("Valid nonnegative numerical fields", bool(np.isfinite(self.df[NUMERIC]).all().all() and (self.df[NUMERIC] >= 0).all().all()), True)
        self.check("Anomaly flag agrees with nonblank label", bool((self.df.has_label == self.df.anomaly.ne("").astype(int)).all()), True)
        self.check("Known route labels", set(self.df.route) == {"DIRECT", "INDIRECT", "COVERED"}, True)
        print(f"{phase}: {len(self.df):,} transactions; source SHA-256 {self.sha}")

    def load_core(self):
        path = self.cache / f"core_{self.sha}.pkl"
        if path.exists():
            return pd.read_pickle(path)
        columns = pd.read_csv(self.source, nrows=0).columns
        missing = set(MAPPING) - set(columns)
        assert not missing, f"Missing required fields: {missing}"
        chunks = []
        for chunk in pd.read_csv(self.source, usecols=list(MAPPING), dtype=str,
                                 keep_default_na=False, chunksize=100_000):
            chunk = chunk.rename(columns=MAPPING)
            for col in NUMERIC:
                chunk[col] = pd.to_numeric(chunk[col], errors="raise")
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
        for col in set(df) - set(NUMERIC):
            if col != "anomaly":
                assert df[col].ne("").all(), f"Blank required category: {col}"
        df["log_duration"] = np.log1p(df.duration_seconds)
        df["log_amount"] = np.log1p(df.amount_usd)
        # Fixed USD bands, not quantile bands selected to maximize effects.
        df["amount_band"] = pd.cut(df.amount_usd, [-np.inf,100,1000,10000,100000,np.inf],
                                   labels=["<=100","100-1000","1000-10000","10000-100000",">100000"])
        df["labeled"] = df.anomaly.where(df.anomaly.ne(""), "UNLABELED")
        for col in set(MAPPING.values()) - set(NUMERIC) | {"labeled"}:
            df[col] = df[col].astype("category")
        df.to_pickle(path)
        return df

    def latest(self, phase):
        paths = sorted((self.root / "outputs/tables/remaining" / phase).glob("*/completion.json"))
        assert paths, f"Execute and validate {phase} first"
        return json.loads(paths[-1].read_text(encoding="utf-8"))

    def prior_table(self, phase, name):
        manifest = self.manifests.get(phase) or self.latest(phase)
        path = self.root / manifest["table_directory"] / name
        return pd.read_csv(path, keep_default_na=False)

    def check(self, name, actual, expected):
        passed = bool(actual == expected)
        self.checks.append({"check": name, "actual": str(actual), "expected": str(expected), "passed": passed})
        assert passed, f"{name}: {actual!r} != {expected!r}"

    def save(self, frame, name, rule=False):
        assert isinstance(frame, pd.DataFrame) and len(frame.columns) > 0
        assert frame.columns.is_unique and all(str(c).strip() for c in frame.columns)
        assert not frame.select_dtypes(include="number").isin([np.inf,-np.inf]).any().any(), name
        path = (self.rules if rule else self.tables) / name
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        self.files.append(str(path.relative_to(self.root)))
        return frame

    def plot(self, frame, x, y, title, ylabel, filename, count="n", top=15):
        view = frame.sort_values(count, ascending=False).head(top)
        fig, ax = plt.subplots(figsize=(11,5))
        ax.bar(np.arange(len(view)), view[y])
        ax.set_xticks(np.arange(len(view)), [f"{a}\n(n={int(n):,})" for a,n in zip(view[x],view[count])], rotation=45, ha="right")
        ax.set(title=title, ylabel=ylabel, xlabel=x.replace("_"," "))
        fig.tight_layout()
        path = self.charts / filename
        fig.savefig(path, dpi=150)
        plt.close(fig)
        self.files.append(str(path.relative_to(self.root)))
        return path

    def finish(self, findings, limitations, next_investigation):
        self.check("Source bytes unchanged during notebook", digest(self.source), self.sha)
        self.save(pd.DataFrame(self.checks), "validation.csv")
        manifest = {"phase": self.phase, "run": self.run, "execution_status": "PASSED",
                    "population": len(self.df), "source_sha256": self.sha,
                    "table_directory": str(self.tables.relative_to(self.root)),
                    "files": self.files, "findings": findings, "limitations": limitations,
                    "next_investigation": next_investigation,
                    "checks_passed": len(self.checks), "unresolved_material_errors": []}
        # Written last: later phases cannot consume an incomplete run.
        (self.tables / "completion.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
        print(json.dumps(manifest, indent=2, default=str))
        return manifest


def profile(df, keys):
    out = df.groupby(keys, observed=True, dropna=False).agg(
        n=("source_row","size"), amount_n=("amount_usd","count"),
        median_amount_usd=("amount_usd","median"), p95_amount_usd=("amount_usd",lambda x:x.quantile(.95)),
        duration_n=("duration_seconds","count"), median_duration_seconds=("duration_seconds","median"),
        p95_duration_seconds=("duration_seconds",lambda x:x.quantile(.95)),
        mean_fx=("fx","mean"), mean_participants=("participants","mean"),
        labeled_n=("has_label","sum")).reset_index()
    out["label_rate"] = out.labeled_n / out.n
    out["label_rate_ci_low"],out["label_rate_ci_high"] = wilson(out.labeled_n,out.n)
    out["small_group"] = out.n < 100
    return out


def association(df, left, right):
    table = pd.crosstab(df[left],df[right],dropna=False)
    table = table.loc[table.sum(axis=1)>0,table.sum(axis=0)>0]
    chi,p,dof,expected = stats.chi2_contingency(table,correction=False)
    return {"left":left,"right":right,"n":int(table.to_numpy().sum()),
            "cramers_v":float(np.sqrt(chi/(table.to_numpy().sum()*(min(table.shape)-1)))),
            "p_value":p,"degrees_of_freedom":dof,"cells_expected_below_5":int((expected<5).sum())}


def matched_effect(df, treatment, strata, outcome="log_duration", min_cell=20):
    """Overlap-weighted difference; no comparison outside shared strata.

    weights=min(n1,n0)/sum(min(n1,n0)); independent-cell variance includes
    both means. Weights are treated as fixed. No causal interpretation.
    """
    work = df[strata+[outcome]].copy()
    work["treated"] = np.asarray(treatment,dtype=int)
    grouped = work.groupby(strata+["treated"],observed=True,dropna=False)[outcome].agg(["size","mean","var"])
    pivot = grouped.unstack("treated")
    for metric in ["size","mean","var"]:
        for arm in (0,1):
            if (metric,arm) not in pivot:
                pivot[(metric,arm)] = np.nan
    eligible = (pivot[("size",0)]>=min_cell)&(pivot[("size",1)]>=min_cell)
    supported = pivot.loc[eligible].copy()
    n1,n0 = int(work.treated.sum()),int((1-work.treated).sum())
    base = {"population_n":len(work),"treated_n":n1,"baseline_n":n0,"outcome":outcome,
            "strata":" + ".join(strata),"min_cell_per_arm":min_cell,"shared_strata":len(supported)}
    if supported.empty:
        return base | {"status":"NO_COMMON_SUPPORT","supported_treated_n":0,"supported_baseline_n":0}, pd.DataFrame()
    weight = np.minimum(supported[("size",0)],supported[("size",1)])
    weight = weight/weight.sum()
    delta = supported[("mean",1)]-supported[("mean",0)]
    variance = supported[("var",1)]/supported[("size",1)]+supported[("var",0)]/supported[("size",0)]
    estimate = float((weight*delta).sum())
    # A singleton has no estimable within-cell variance. Do not silently let
    # pandas skip NaN and return an artificially narrow interval. The earlier
    # min-one reproduction retains its point estimate, with uncertainty unset.
    se = float(np.sqrt((weight**2*variance).sum())) if variance.notna().all() else np.nan
    raw1,raw0 = work.loc[work.treated.eq(1),outcome].mean(),work.loc[work.treated.eq(0),outcome].mean()
    detail = supported.copy()
    detail.columns = [f"{a}_{b}" for a,b in detail.columns]
    detail["difference"] = delta
    detail["weight"] = weight
    result = base | {"status":"ESTIMATED","supported_treated_n":int(supported[("size",1)].sum()),
                     "supported_baseline_n":int(supported[("size",0)].sum()),
                     "treated_support_fraction":float(supported[("size",1)].sum()/n1),
                     "baseline_support_fraction":float(supported[("size",0)].sum()/n0),
                     "raw_difference":float(raw1-raw0),"adjusted_difference":estimate,
                     "ci_low":estimate-1.96*se,"ci_high":estimate+1.96*se,
                     "uncertainty_status":"ESTIMATED" if np.isfinite(se) else "UNAVAILABLE_SINGLETON_CELL",
                     "negative_strata":int((delta<0).sum()),"positive_strata":int((delta>0).sum())}
    if outcome == "log_duration":
        result.update(relative_geometric_duration_plus_one=float(np.expm1(estimate)),
                      relative_ci_low=float(np.expm1(estimate-1.96*se)),
                      relative_ci_high=float(np.expm1(estimate+1.96*se)))
    return result,detail.reset_index()


def currency_party(study):
    df = study.df
    tables = {}
    for name,keys in [("currency_party_profile",["currency","party"]),
                      ("party_profile",["party"]),("currency_profile",["currency"])]:
        tables[name] = study.save(profile(df,keys),name+".csv")
        study.check(name+" population",int(tables[name].n.sum()),EXPECTED)
    counts = df.groupby(["currency","party","route"],observed=True).size().rename("n").reset_index()
    counts["segment_n"] = counts.groupby(["currency","party"],observed=True).n.transform("sum")
    counts["route_rate"] = counts.n/counts.segment_n
    counts["ci_low"],counts["ci_high"] = wilson(counts.n,counts.segment_n)
    study.save(counts,"currency_party_route_rates.csv")
    study.check("Route rate population",int(counts.n.sum()),EXPECTED)
    assoc = pd.DataFrame([association(df,a,b) for a,b in [("currency","party"),("party","route"),("currency","route"),("party","fx")]])
    assoc["p_value_bh"] = multipletests(assoc.p_value,method="fdr_bh")[1]
    study.save(assoc,"association_effects.csv")
    # USD and C_C are predeclared reference contrasts; no choice based on results.
    effects = []
    for kind in ["USD_vs_other","party_vs_C_C"]:
        contrasts = ["USD"] if kind == "USD_vs_other" else sorted(set(df.party)-{"C_C"})
        for level in contrasts:
            sub = df if kind == "USD_vs_other" else df.loc[df.party.isin([level,"C_C"])].copy()
            treatment = sub.currency.eq("USD") if kind == "USD_vs_other" else sub.party.eq(level)
            strata = ["route","participants","fx","amount_band"] + (["party"] if kind=="USD_vs_other" else ["currency"])
            for minimum in [20,100]:
                result,detail = matched_effect(sub,treatment,strata,min_cell=minimum)
                effects.append(result|{"contrast":kind,"level":level})
                if minimum==20 and not detail.empty:
                    study.save(detail,f"duration_strata_{kind}_{level}.csv")
    duration_effects = study.save(pd.DataFrame(effects),"adjusted_duration_contrasts.csv")
    nd = df.loc[df.route.isin(["INDIRECT","COVERED"])].copy()
    nd["covered"] = nd.route.eq("COVERED").astype(float)
    covered = []
    for level in ["USD","EUR","GBP","CHF"]:
        result,_ = matched_effect(nd,nd.currency.eq(level),["participants","fx","party","amount_band"],outcome="covered")
        covered.append(result|{"currency_contrast":level+" vs other currencies"})
    covered = study.save(pd.DataFrame(covered),"adjusted_covered_currency_contrasts.csv")
    study.plot(tables["party_profile"],"party","median_duration_seconds",
               "Duration by party pair: full population; denominator is each party pair",
               "Median duration (seconds)","party_duration.png")
    study.plot(tables["currency_profile"],"currency","median_duration_seconds",
               "Top 15 currencies by count; denominator is each currency",
               "Median duration (seconds)","currency_duration.png")
    return tables,assoc,duration_effects,covered


def duplicate_features(study):
    path = study.cache/f"recurrence_{study.sha}.pkl"
    if path.exists():
        return pd.read_pickle(path)
    cols = ["SOURCE_ROW_NUMBER","ORDERING_ACCOUNT","BENEFICIARY_ACCOUNT","USD_AMOUNT_NUM","CURRENCY_CODE_STD","EPOCH_SECONDS_NUM"]
    frames = []
    for chunk in pd.read_csv(study.source,usecols=cols,dtype=str,keep_default_na=False,chunksize=100_000):
        valid = chunk.ORDERING_ACCOUNT.ne("") & chunk.BENEFICIARY_ACCOUNT.ne("")
        # Hash is an internal grouping aid, never exported. Verify collision-free
        # observed mappings before trusting equality of signatures.
        keycols = ["ORDERING_ACCOUNT","BENEFICIARY_ACCOUNT","USD_AMOUNT_NUM","CURRENCY_CODE_STD"]
        chunk["key"] = pd.util.hash_pandas_object(chunk[keycols],index=False)
        frames.append(chunk[keycols+["key","SOURCE_ROW_NUMBER","EPOCH_SECONDS_NUM"]].assign(valid=valid))
    records = pd.concat(frames,ignore_index=True)
    unique_keys = records.drop_duplicates(["key"])
    unique_values = records.drop_duplicates(["ORDERING_ACCOUNT","BENEFICIARY_ACCOUNT","USD_AMOUNT_NUM","CURRENCY_CODE_STD"])
    assert len(unique_keys)==len(unique_values), "Hash collision: use exact tuple keys"
    valid = records.valid
    repeated = records.duplicated("key",keep=False)&valid
    ordered = records.loc[valid].sort_values(["key","EPOCH_SECONDS_NUM"],key=lambda s:pd.to_numeric(s) if s.name=="EPOCH_SECONDS_NUM" else s)
    ordered["epoch_numeric"] = pd.to_numeric(ordered.EPOCH_SECONDS_NUM)
    previous = ordered.groupby("key").epoch_numeric.diff()
    following = -ordered.groupby("key").epoch_numeric.diff(-1)
    near = (previous.between(0,86400)|following.between(0,86400))
    result = pd.DataFrame({"source_row":pd.to_numeric(records.SOURCE_ROW_NUMBER),"recurrence_evaluable":valid,
                           "repeated_signature":repeated,"repeat_within_86400_seconds":False})
    result.loc[ordered.index,"repeat_within_86400_seconds"] = near.to_numpy()
    result.to_pickle(path)
    return result


def binary_comparison(df, target, feature, label):
    a = df.loc[target,feature].astype(float)
    b = df.loc[~target,feature].astype(float)
    ka,kb = int(a.sum()),int(b.sum())
    pa,pb = a.mean(),b.mean()
    la,ua = wilson(ka,len(a)); lb,ub = wilson(kb,len(b))
    # Newcombe interval for the difference of independent proportions.
    low = pa-pb-np.sqrt((pa-la)**2+(ub-pb)**2)
    high = pa-pb+np.sqrt((ua-pa)**2+(pb-lb)**2)
    return {"contrast":label,"feature":feature,"target_n":len(a),"target_successes":ka,
            "baseline_n":len(b),"baseline_successes":kb,"target_rate":pa,"baseline_rate":pb,
            "risk_difference":pa-pb,"risk_difference_ci_low":float(low),"risk_difference_ci_high":float(high),
            "risk_ratio":pa/pb if pb>0 else np.nan,
            "odds_ratio_haldane":((ka+.5)*(len(b)-kb+.5))/((len(a)-ka+.5)*(kb+.5))}


def anomaly_analysis(study):
    df = study.df
    summaries = study.save(profile(df,["labeled"]),"anomaly_profile.csv")
    study.check("Anomaly categories population",int(summaries.n.sum()),EXPECTED)
    study.check("CUSTOMER_RECALL preserved",bool(df.anomaly.eq("CUSTOMER_RECALL").any()),True)
    composition = df.groupby(["labeled","route","party"],observed=True).size().rename("n").reset_index()
    composition["label_n"] = composition.groupby("labeled",observed=True).n.transform("sum")
    composition["conditional_rate"] = composition.n/composition.label_n
    study.save(composition,"anomaly_route_party_composition.csv")
    study.check("Anomaly composition population",int(composition.n.sum()),EXPECTED)
    effects = []
    for label in sorted(set(df.anomaly)-{""}):
        subset = df.loc[df.anomaly.isin(["",label])].copy()
        for minimum in [5,20]:
            for outcome in ["log_duration","log_amount"]:
                strata = ["route","participants","fx","currency","party"]
                if outcome=="log_duration":
                    strata += ["amount_band"]
                result,_ = matched_effect(subset,subset.anomaly.eq(label),strata,outcome,min_cell=minimum)
                effects.append(result|{"anomaly":label,"baseline":"UNLABELED"})
    effects = study.save(pd.DataFrame(effects),"anomaly_adjusted_contrasts.csv")
    repeats = duplicate_features(study)
    study.check("Recurrence cache source alignment",bool(np.array_equal(repeats.source_row,df.source_row)),True)
    working = df.join(repeats.drop(columns="source_row"))
    repeat_profiles = working.groupby("labeled",observed=True).agg(n=("source_row","size"),
        evaluable_n=("recurrence_evaluable","sum"),repeated_n=("repeated_signature","sum"),
        near_repeat_n=("repeat_within_86400_seconds","sum")).reset_index()
    repeat_profiles["repeated_rate_evaluable"] = repeat_profiles.repeated_n/repeat_profiles.evaluable_n.replace(0,np.nan)
    study.save(repeat_profiles,"anomaly_recurrence_profile.csv")
    eligible = working.loc[working.recurrence_evaluable & working.anomaly.isin(["","DUPLICATE_PAYMENT"])].copy()
    comparisons = [binary_comparison(eligible,eligible.anomaly.eq("DUPLICATE_PAYMENT"),feature,"DUPLICATE_PAYMENT vs UNLABELED")
                   for feature in ["repeated_signature","repeat_within_86400_seconds"]]
    recurrence = study.save(pd.DataFrame(comparisons),"duplicate_label_recurrence_contrasts.csv")
    working["whole_dollar"] = np.isclose(working.amount_usd,np.round(working.amount_usd),rtol=0,atol=1e-8)
    round_profile = working.groupby("labeled",observed=True).agg(n=("source_row","size"),whole_dollar_n=("whole_dollar","sum")).reset_index()
    round_profile["whole_dollar_rate"] = round_profile.whole_dollar_n/round_profile.n
    study.save(round_profile,"anomaly_amount_rounding.csv")
    # All label contrasts are disclosed, not only significant ones.
    associations = pd.DataFrame([association(df,"labeled",col) for col in ["party","route","currency","gap"]])
    associations["p_value_bh"] = multipletests(associations.p_value,method="fdr_bh")[1]
    study.save(associations,"anomaly_associations.csv")
    study.plot(summaries,"labeled","median_amount_usd","Amount by observed label; UNLABELED is not verified normal",
               "Median amount (USD)","anomaly_amount.png")
    study.plot(summaries,"labeled","median_duration_seconds","Duration by observed label; denominator is each label",
               "Median duration (seconds)","anomaly_duration.png")
    return summaries,effects,recurrence,repeat_profiles


TOKEN_RE = re.compile(r"<([^<>:]+):([^<>]*)>")
TOKEN_FIELD_RE = re.compile(r"<([A-Za-z_][A-Za-z_0-9 -]{0,39}):")


def token_features(study):
    path = study.cache/f"tokens_v2_{study.sha}.pkl"
    tagpath = study.cache/f"token_tags_v2_{study.sha}.pkl"
    if path.exists() and tagpath.exists():
        return pd.read_pickle(path),pd.read_pickle(tagpath)
    frames, tag_frames = [], []
    cols = ["SOURCE_ROW_NUMBER","ORDERING_TOKENS","BENEFICIARY_TOKENS","ORDERING_DETAILS","BENEFICIARY_DETAILS"]
    for chunk in pd.read_csv(study.source,usecols=cols,dtype=str,keep_default_na=False,chunksize=50_000):
        features = pd.DataFrame({"source_row":pd.to_numeric(chunk.SOURCE_ROW_NUMBER)})
        for side in ["ORDERING","BENEFICIARY"]:
            prefix = side.lower()
            parsed = chunk[side+"_TOKENS"].map(TOKEN_RE.findall)
            fields = chunk[side+"_TOKENS"].map(TOKEN_FIELD_RE.findall)
            features[prefix+"_blank"] = chunk[side+"_TOKENS"].str.strip().eq("")
            features[prefix+"_characters"] = chunk[side+"_TOKENS"].str.len()
            features[prefix+"_tag_count"] = fields.map(len)
            features[prefix+"_closed_tag_count"] = parsed.map(len)
            features[prefix+"_unrecognized_openings"] = chunk[side+"_TOKENS"].str.count("<")-fields.map(len)
            features[prefix+"_unparsed_brackets"] = chunk[side+"_TOKENS"].str.count("<")-parsed.map(len)
            features[prefix+"_unparsed_closing_brackets"] = chunk[side+"_TOKENS"].str.count(">")-parsed.map(len)
            # Surface occurrence only. Token values may encode shapes rather than
            # literal detail text; absence never proves identity inconsistency.
            features[prefix+"_literal_value_hits"] = [sum(value.casefold() in detail.casefold() for _,value in pairs if value)
                                                       for pairs,detail in zip(parsed,chunk[side+"_DETAILS"])]
            # Compact each chunk immediately instead of retaining millions of
            # Python tuples. Values never leave this loop.
            present = pd.DataFrame({"source_row":features.source_row,
                                    "tag":fields.map(lambda names: sorted(set(names)))})
            present = present.explode("tag").dropna(subset=["tag"])
            present["side"] = prefix
            present["side"] = present.side.astype("category")
            present["tag"] = present.tag.astype("category")
            tag_frames.append(present[["source_row","side","tag"]])
        features["same_token_string"] = chunk.ORDERING_TOKENS.eq(chunk.BENEFICIARY_TOKENS)
        frames.append(features)
    features = pd.concat(frames,ignore_index=True)
    tags = pd.concat(tag_frames,ignore_index=True)
    for col in ["side","tag"]:
        tags[col] = tags[col].astype("category")
    features.to_pickle(path)
    tags.to_pickle(tagpath)
    return features,tags


def tokens_analysis(study):
    df = study.df
    features,tags = token_features(study)
    study.check("Token feature population",len(features),EXPECTED)
    study.check("Token source row alignment",bool(np.array_equal(features.source_row,df.source_row)),True)
    working = df.join(features.drop(columns="source_row"))
    quality = []
    for side in ["ordering","beneficiary"]:
        quality.append({"side":side,"n":len(df),"blank_n":int(working[side+"_blank"].sum()),
                        "zero_parsed_tags_n":int(working[side+"_tag_count"].eq(0).sum()),
                        "unparsed_opening_brackets":int(working[side+"_unparsed_brackets"].sum()),
                        "unparsed_closing_brackets":int(working[side+"_unparsed_closing_brackets"].sum()),
                        "unrecognized_field_openings":int(working[side+"_unrecognized_openings"].sum()),
                        "mean_characters":working[side+"_characters"].mean(),
                        "mean_tags":working[side+"_tag_count"].mean(),
                        "literal_value_hit_n":int(working[side+"_literal_value_hits"].gt(0).sum())})
    quality = study.save(pd.DataFrame(quality),"token_parser_coverage.csv")
    # Strict balanced blocks are a rejected source-format hypothesis. Field
    # openings are counted independently and must account for every '<'.
    study.check("All field openings recognized",int(quality.unrecognized_field_openings.sum()),0)
    tag_counts = tags.groupby(["side","tag"],observed=True).size().rename("transaction_presence_n").reset_index()
    tag_counts["side_population_n"] = len(df)
    tag_counts["presence_rate"] = tag_counts.transaction_presence_n/len(df)
    # Unexpected free-text tag names are not published as categorical tokens.
    allowed = tag_counts.tag.str.fullmatch(r"[A-Za-z_][A-Za-z_0-9 -]{0,39}")
    study.check("Field tags have safe structural names",bool(allowed.all()),True)
    study.save(tag_counts,"token_field_presence.csv")
    profiles = []
    for group in ["party","labeled"]:
        out = working.groupby(group,observed=True).agg(n=("source_row","size"),
            median_ordering_tags=("ordering_tag_count","median"),median_beneficiary_tags=("beneficiary_tag_count","median"),
            mean_ordering_characters=("ordering_characters","mean"),mean_beneficiary_characters=("beneficiary_characters","mean"),
            same_string_n=("same_token_string","sum")).reset_index()
        study.save(out,f"token_profile_by_{group}.csv")
        study.check(f"Token profile by {group} population",int(out.n.sum()),EXPECTED)
        profiles.append(out)
    # Tag presence by party and anomaly: no literal token values exported.
    metadata = df[["source_row","party","labeled"]]
    merged = tags.merge(metadata,on="source_row",validate="many_to_one")
    for group in ["party","labeled"]:
        out = merged.groupby(["side","tag",group],observed=True).size().rename("presence_n").reset_index()
        denom = df.groupby(group,observed=True).size().rename("denominator_n")
        out = out.merge(denom,on=group)
        out["presence_rate"] = out.presence_n/out.denominator_n
        study.save(out,f"token_tag_presence_by_{group}.csv")
    effects = []
    for label in sorted(set(df.anomaly)-{""}):
        sub = working.loc[working.anomaly.isin(["",label])]
        for side in ["ordering","beneficiary"]:
            result,_ = matched_effect(sub,sub.anomaly.eq(label),["party","route","currency","amount_band"],
                                     outcome=side+"_tag_count",min_cell=10)
            effects.append(result|{"anomaly":label,"side":side})
    effects = study.save(pd.DataFrame(effects),"adjusted_token_count_contrasts.csv")
    # Explicit structure hypothesis: both sides' tag counts depend on party type.
    assoc = pd.DataFrame([association(working,"party",side+"_tag_count") for side in ["ordering","beneficiary"]])
    study.save(assoc,"token_party_associations.csv")
    study.plot(profiles[0],"party","median_ordering_tags","Ordering token structure by party pair; full population",
               "Median parsed field count","token_party_structure.png")
    return quality,tag_counts,profiles,effects,assoc


def fit_gap_model(df):
    counts = df.groupby("participants",observed=True).agg(n=("source_row","size"),
                                                          gaps=("gap",lambda s:s.eq("Y").sum())).reset_index()
    links = counts.participants.to_numpy()-1
    n,k = counts.n.to_numpy(),counts.gaps.to_numpy()
    def nll(p):
        q = np.clip(1-(1-p)**links,1e-12,1-1e-12)
        return -np.sum(k*np.log(q)+(n-k)*np.log1p(-q))
    fit = minimize_scalar(nll,bounds=(.00001,.3),method="bounded",options={"xatol":1e-12})
    assert fit.success
    p = float(fit.x)
    q = 1-(1-p)**links
    derivative = links*(1-p)**(links-1)
    se = float(1/np.sqrt(np.sum(n*derivative**2/(q*(1-q)))))
    counts["observed_rate"] = k/n
    counts["model_rate"] = q
    counts["residual_pp"] = (counts.observed_rate-counts.model_rate)*100
    counts["ci_low"],counts["ci_high"] = wilson(k,n)
    counts["small_group"] = counts.n<100
    return {"per_link_probability":p,"ci_low":p-1.96*se,"ci_high":p+1.96*se,"n":len(df),
            "weighted_absolute_error_pp":float(np.average(np.abs(counts.residual_pp),weights=n)),
            "max_absolute_error_pp_n_ge_100":float(counts.loc[counts.n>=100,"residual_pp"].abs().max())},counts


def endpoint_validation(study):
    cols = ["ORDERING_BIC8","BENEFICIARY_BIC8","BIC8_PATH"]
    totals = {"n":0,"ordering_mismatch_n":0,"beneficiary_mismatch_n":0,"both_mismatch_n":0,"no_visible_endpoint_n":0}
    for chunk in pd.read_csv(study.source,usecols=cols,dtype=str,keep_default_na=False,chunksize=100_000):
        nodes = chunk.BIC8_PATH.map(lambda s:[n.strip() for n in s.split(";") if n.strip() not in {"","..."}])
        visible = nodes.map(bool)
        first = nodes.map(lambda x:x[0] if x else "")
        last = nodes.map(lambda x:x[-1] if x else "")
        order = first.ne(chunk.ORDERING_BIC8.str.strip())&visible
        bene = last.ne(chunk.BENEFICIARY_BIC8.str.strip())&visible
        totals["n"] += len(chunk)
        totals["ordering_mismatch_n"] += int(order.sum())
        totals["beneficiary_mismatch_n"] += int(bene.sum())
        totals["both_mismatch_n"] += int((order&bene).sum())
        totals["no_visible_endpoint_n"] += int((~visible).sum())
    n = totals["n"]-totals["no_visible_endpoint_n"]
    a,b,both = totals["ordering_mismatch_n"],totals["beneficiary_mismatch_n"],totals["both_mismatch_n"]
    cells = np.array([[both,a-both],[b-both,n-a-b+both]])
    chi,p,_,_ = stats.chi2_contingency(cells,correction=False)
    totals.update(evaluable_n=n,ordering_rate=a/n,beneficiary_rate=b/n,joint_rate=both/n,
                  independence_expected_joint_rate=a*b/n**2,joint_minus_independence_pp=(both/n-a*b/n**2)*100,
                  independence_cramers_v=float(np.sqrt(chi/n)),independence_p_value=p)
    return pd.DataFrame([totals])


def conditional_counterexamples(df):
    fx = df.groupby(["route","participants","fx"],observed=True).agg(n=("source_row","size"),median_seconds=("duration_seconds","median")).reset_index()
    rows = []
    for (route,participants),sub in fx.groupby(["route","participants"],observed=True):
        lookup = sub.set_index("fx")
        for base in lookup.index:
            if base+1 in lookup.index:
                a,b = lookup.loc[base],lookup.loc[base+1]
                rows.append({"route":route,"participants":participants,"base_fx":base,"next_fx":base+1,
                             "baseline_n":int(a.n),"next_n":int(b.n),"difference_seconds":b.median_seconds-a.median_seconds,
                             "adequate":bool(min(a.n,b.n)>=100)})
    gaps = df.groupby(["route","participants","fx","gap"],observed=True).agg(n=("source_row","size"),median_seconds=("duration_seconds","median")).unstack("gap")
    gaps = gaps.loc[(gaps[("n","N")]>=100)&(gaps[("n","Y")]>=100)].copy()
    gaps["difference_seconds"] = gaps[("median_seconds","Y")]-gaps[("median_seconds","N")]
    gaps.columns = ["_".join(c).rstrip("_") if isinstance(c,tuple) else c for c in gaps.columns]
    return pd.DataFrame(rows),gaps.reset_index()


def validation_analysis(study):
    df = study.df
    structural = []
    definitions = [
        ("S01","DIRECT implies two participants",df.route.eq("DIRECT"),df.participants.eq(2)),
        ("S02","Two participants implies DIRECT",df.participants.eq(2),df.route.eq("DIRECT")),
        ("S03","FX <= participants - 1",pd.Series(True,index=df.index),df.fx.le(df.participants-1)),
        ("S04","FX >= 2 implies non-direct",df.fx.ge(2),df.route.ne("DIRECT")),
        ("S05","Non-direct implies participants >= 3",df.route.ne("DIRECT"),df.participants.ge(3)),
    ]
    rng = np.random.default_rng(SEED)
    random_development = pd.Series(rng.random(len(df))<.5,index=df.index)
    time_cut = float(df.epoch.median())
    masks = {"full":pd.Series(True,index=df.index),"random_development":random_development,
             "random_validation":~random_development,"chronological_early":df.epoch.le(time_cut),
             "chronological_late":df.epoch.gt(time_cut)}
    splits = pd.DataFrame([{"split":k,"n":int(v.sum()),"epoch_min":int(df.loc[v,"epoch"].min()),"epoch_max":int(df.loc[v,"epoch"].max())} for k,v in masks.items()])
    study.save(splits,"split_populations.csv")
    study.check("Disjoint random partitions reconcile",int(random_development.sum()+(~random_development).sum()),EXPECTED)
    study.check("Disjoint chronological partitions reconcile",int(df.epoch.le(time_cut).sum()+df.epoch.gt(time_cut).sum()),EXPECTED)
    for split,mask in masks.items():
        for rule_id,condition,eligible,success in definitions:
            n,k = int((mask&eligible).sum()),int((mask&eligible&success).sum())
            lo,hi = wilson(k,n)
            structural.append({"rule_id":rule_id,"condition":condition,"split":split,"n":n,"successes":k,
                               "exceptions":n-k,"rate":k/n,"ci_low":float(lo),"ci_high":float(hi)})
    structural = study.save(pd.DataFrame(structural),"structural_rule_validation.csv")
    gap_metrics,gap_counts = fit_gap_model(df)
    study.save(gap_counts,"gap_model_calibration.csv")
    mechanisms = []
    split_effects = []
    for split,mask in masks.items():
        sub = df.loc[mask]
        fit,calibration = fit_gap_model(sub)
        mechanisms.append(fit|{"split":split})
        nd = sub.loc[sub.route.isin(["INDIRECT","COVERED"])]
        result,_ = matched_effect(nd,nd.route.eq("COVERED"),["participants","fx","currency","party"],min_cell=20)
        split_effects.append(result|{"split":split,"contrast":"COVERED vs INDIRECT"})
        usd,_ = matched_effect(sub,sub.currency.eq("USD"),["route","participants","fx","party","amount_band"],min_cell=20)
        split_effects.append(usd|{"split":split,"contrast":"USD vs other"})
    mechanisms = study.save(pd.DataFrame(mechanisms),"gap_parameter_stability.csv")
    split_effects = study.save(pd.DataFrame(split_effects),"duration_effect_stability.csv")
    # Fit only development rows, predict validation counts without refitting.
    p_dev = mechanisms.loc[mechanisms.split.eq("random_development"),"per_link_probability"].iloc[0]
    _,held = fit_gap_model(df.loc[masks["random_validation"]])
    held["development_model_rate"] = 1-(1-p_dev)**(held.participants-1)
    held["development_model_error_pp"] = (held.observed_rate-held.development_model_rate)*100
    study.save(held,"gap_heldout_calibration.csv")
    endpoints = study.save(endpoint_validation(study),"endpoint_independence_recomputed.csv")
    study.check("Endpoint scan population",int(endpoints.n.iloc[0]),EXPECTED)
    study.check("All endpoints evaluable",int(endpoints.no_visible_endpoint_n.iloc[0]),0)
    fx,gaps = conditional_counterexamples(df)
    study.save(fx,"fx_direction_counterexamples.csv")
    study.save(gaps,"gap_duration_counterexamples.csv")
    medians = df.groupby("route",observed=True).duration_seconds.agg(["size","median"]).reset_index()
    medians["prior_median_seconds"] = medians.route.map({"DIRECT":39,"INDIRECT":283,"COVERED":378}).astype(float)
    medians["reproduced"] = medians["median"].eq(medians.prior_median_seconds)
    study.save(medians,"prior_route_median_reproduction.csv")
    study.check("Overall prior median reproduced",float(df.duration_seconds.median()),56.)
    study.check("All prior route medians reproduced",bool(medians.reproduced.all()),True)
    # Reproduce earlier estimator exactly before tightening support requirements.
    nd = df.loc[df.route.isin(["INDIRECT","COVERED"])]
    earlier,_ = matched_effect(nd,nd.route.eq("COVERED"),["participants","fx","currency","party"],min_cell=1)
    prior = pd.read_csv(study.root/"outputs/tables/duration/indirect_covered_duration_matched_summary.csv")
    study.check("Earlier Covered estimator reproduced",bool(np.isclose(earlier["adjusted_difference"],prior.WEIGHTED_LOG_DIFFERENCE.iloc[0],atol=1e-10)),True)
    study.save(pd.DataFrame([earlier]),"prior_matched_duration_reproduction.csv")
    metrics = pd.DataFrame([gap_metrics])
    study.save(metrics,"gap_model_summary.csv")
    registry = build_rule_register(study,structural,split_effects,gap_metrics,endpoints,fx,gaps)
    study.save(registry,"validated_rule_register.csv",rule=True)
    # Prior registers remain unchanged, with an explicit disposition for every candidate.
    reconciliation = reconcile_prior_candidates(study,registry)
    study.save(reconciliation,"prior_candidate_reconciliation.csv")
    study.plot(medians.rename(columns={"size":"n","median":"median_duration_seconds"}),"route","median_duration_seconds",
               "Reproduced route duration medians: full population; denominator is each route",
               "Median duration (seconds)","validated_route_medians.png")
    return structural,mechanisms,split_effects,endpoints,fx,gaps,registry,reconciliation


def build_rule_register(study,structural,split_effects,gap_metrics,endpoints,fx,gaps):
    rows = []
    def add(identifier,condition,target,n,baseline,effect,uncertainty,status,confidence,evidence,exceptions,confounders,robustness,business):
        rows.append(dict(rule_id=identifier,condition=condition,target_outcome=target,population_n=int(n),baseline=baseline,
                         effect=effect,uncertainty=uncertainty,status=status,confidence=confidence,evidence=evidence,
                         exceptions=exceptions,confounders=confounders,robustness=robustness,business_implication=business,
                         interpretation_scope="Observed synthetic population; not causal or universal real-world evidence"))
    for row in structural.loc[structural.split.eq("full")].itertuples():
        add(row.rule_id,row.condition,"Structural constraint",row.n,"All eligible rows",
            f"Rate={row.rate:.9f}; exceptions={row.exceptions}",f"Wilson 95% [{row.ci_low:.9f}, {row.ci_high:.9f}]",
            "SUPPORTED_IN_DATA" if row.exceptions==0 else "REJECTED_STRICT_RULE","HIGH_DESCRIPTIVE",
            "structural_rule_validation.csv",str(row.exceptions)+" observed exceptions",
            "May be routing definitions imposed by generator","Disjoint random and chronological partitions",
            "Consistency checks for route metadata")
    add("G01","Participant count >=2","At least one routing gap",EXPECTED,"1-(1-p)^(participants-1)",
        f"p={gap_metrics['per_link_probability']:.9f}; weighted absolute error={gap_metrics['weighted_absolute_error_pp']:.6f} pp",
        f"Model-based p 95% [{gap_metrics['ci_low']:.9f}, {gap_metrics['ci_high']:.9f}]",
        "APPROXIMATE_MECHANISM","MODERATE_MECHANISM","gap_model_summary.csv; gap_heldout_calibration.csv",
        "Nonzero calibration residuals; sparse participant groups are flagged","Link independence not identified by gap indicator",
        "Development-only fit assessed on heldout rows; chronological fits","Set traceability expectations conditional on path complexity")
    ep = endpoints.iloc[0]
    add("E01","Visible path endpoints","Endpoint mismatch and approximate independence",EXPECTED,"Product of marginal mismatch rates",
        f"Ordering={ep.ordering_rate:.9f}; beneficiary={ep.beneficiary_rate:.9f}; joint={ep.joint_rate:.9f}; V={ep.independence_cramers_v:.9f}",
        "Finite population rates; independence is an approximation, not established by nonsignificance",
        "APPROXIMATE_MECHANISM","MODERATE_MECHANISM","endpoint_independence_recomputed.csv",
        f"Joint-minus-product={ep.joint_minus_independence_pp:.6f} pp","Visible endpoint is not a verified real bank identity",
        "Full source path rescan","Distinguish path observability perturbations from operational failures")
    for identifier,contrast in [("D01","COVERED vs INDIRECT"),("C01","USD vs other")]:
        result = split_effects.loc[split_effects.split.eq("full")&split_effects.contrast.eq(contrast)].iloc[0]
        subset = split_effects.loc[split_effects.contrast.eq(contrast)]
        stable = bool((np.sign(subset.adjusted_difference)==np.sign(result.adjusted_difference)).all())
        add(identifier,contrast,"Mean log(1+duration seconds)",result.population_n,"Exact common strata, min 20/arm",
            f"Adjusted={result.adjusted_difference:.9f}; raw={result.raw_difference:.9f}; relative geometric(duration+1)={result.relative_geometric_duration_plus_one:.9f}",
            f"Analytic pointwise 95% [{result.ci_low:.9f}, {result.ci_high:.9f}]",
            "SUPPORTED_ASSOCIATION" if stable else "UNSTABLE_ASSOCIATION","MODERATE_ASSOCIATION",
            "duration_effect_stability.csv",f"{result.negative_strata} negative and {result.positive_strata} positive strata; unsupported strata excluded",
            "Bank/time composition, residual within-band amount effects","Direction checked in random and chronological partitions",
            "Benchmark like-for-like segments; no claimed speed gain")
    adequate = fx.loc[fx.adequate]
    add("D02","Adjacent FX counts within route and participant count","Universal positive median duration increment",EXPECTED,
        "Previous FX count",f"{int((adequate.difference_seconds<0).sum())} negative of {len(adequate)} adequate comparisons",
        "Exact observed medians; no universal-rule uncertainty needed for observed counterexamples",
        "REJECTED_UNIVERSAL_RULE","HIGH_REJECTION","fx_direction_counterexamples.csv",
        "Negative and zero increments contradict strict monotonicity","Currency, party, amount, label mix",
        "Minimum 100 per arm","Do not assume more FX always means slower processing")
    add("D03","Routing gap versus no gap within route/participants/FX","Universal positive duration gap penalty",EXPECTED,
        "No gap",f"{int((gaps.difference_seconds<0).sum())} negative; {int((gaps.difference_seconds>0).sum())} positive of {len(gaps)} comparisons",
        "Exact observed medians; descriptive counterexamples","REJECTED_UNIVERSAL_RULE","HIGH_REJECTION",
        "gap_duration_counterexamples.csv","Both directions observed","Visibility flag may be independent corruption",
        "Minimum 100 per arm","Separate traceability monitoring from latency assumptions")
    recurrence = study.prior_table("06_anomaly_analysis","duplicate_label_recurrence_contrasts.csv")
    r = recurrence.loc[recurrence.feature.eq("repeat_within_86400_seconds")].iloc[0]
    add("A01","DUPLICATE_PAYMENT label with nonblank accounts","Same signature neighbor within 86400 seconds",r.target_n,
        f"UNLABELED n={r.baseline_n}",f"Target rate={r.target_rate:.9f}; baseline={r.baseline_rate:.9f}; RD={r.risk_difference:.9f}; RR={r.risk_ratio}",
        f"Pointwise Newcombe RD 95% [{r.risk_difference_ci_low:.9f}, {r.risk_difference_ci_high:.9f}]; linked rows challenge independence",
        "SUPPORTED_IN_DATA","HIGH_DESCRIPTIVE","06:duplicate_label_recurrence_contrasts.csv",
        "Recurrence also occurs without a label; reverse implication unsupported","Related payments; exact matching definition",
        "Exact tuple hash collision check; full-window and 86400-second comparison","Validate duplicate linkage while preserving repeated rows")
    quality = study.prior_table("07_tokens","token_parser_coverage.csv")
    add("T01","Both token sides","Field-opening markers with imperfect bracket closure",EXPECTED,"All token strings per side",
        f"Unparsed opening={quality.unparsed_opening_brackets.sum()}; closing={quality.unparsed_closing_brackets.sum()}",
        "Field-opening coverage validated; strict balanced-block hypothesis rejected","REVISED_SERIALIZATION","HIGH_DESCRIPTIVE","07:token_parser_coverage.csv",
        "chr fields and extra closing delimiters violate strict block grammar; syntax does not establish semantics","Template-based generator fields","Field-opening counts and strict-block residuals both reported",
        "Reproducible token format QA")
    return pd.DataFrame(rows)


def reconcile_prior_candidates(study,registry):
    routing = {"BR01":"S01","BR02":"S04","BR03":"S02","BR04":"D02","BR05":"D01","BR06":"G01",
               "BR07":"D03","BR08":None,"BR09":"C01"}
    duration = {"DR01":"D01","DR02":None,"DR03":"D02","DR04":"D01","DR05":"D03","DR06":None,
                "DR07":None,"DR08":"C01","DR09":None,"DR10":None}
    hypotheses = {"H01":"S01","H02":"S03","H03":"C01","H04":"G01","H05":None,"H06":"D01",
                  "H07":None,"H08":"D02","H09":"D01","H10":"D03","H11":None,"H12":"C01",
                  "H13":"A01","H14":None,"H15":"T01"}
    rows=[]
    for name,mapping,idcol,hypcol in [
        ("bank_routing_candidate_rules.csv",routing,"RULE_ID","HYPOTHESIS"),
        ("payment_duration_candidate_rules.csv",duration,"RULE_ID","HYPOTHESIS"),
        ("candidate_hypotheses.csv",hypotheses,"ID","HYPOTHESIS")]:
        old = pd.read_csv(study.root/"outputs/rules"/name,keep_default_na=False)
        for _,r in old.iterrows():
            linked = mapping[r[idcol]]
            # A related rule is not a substitute for validating the exact earlier hypothesis.
            # Counterexamples to a universally positive duration penalty do not
            # reject the broader hypothesis of any FX/gap-duration association.
            partial = r[idcol] in {"BR04","BR05","BR07","BR09","DR01","DR03","DR05","DR08","H02","H03","H04","H06","H08","H09","H10","H11","H12","H14","H15"}
            status = "REVIEWED_EXPLORATORY_ONLY" if linked is None else ("RELATED_EVIDENCE_SCOPE_REVISED" if partial else registry.set_index("rule_id").loc[linked,"status"])
            rows.append({"source_register":name,"candidate_id":r[idcol],"original_hypothesis":r[hypcol],
                         "linked_new_rule":linked or "NONE","disposition":status,
                         "limitation":"Earlier hypothesis not fully independently validated; inspect original evidence and new narrower rule" if partial or linked is None else "Scope restricted to observed population",
                         "next_test":"Independent bank/time-stratified replication and explicit common support" if partial or linked is None else "External generator/documentation verification"})
    result=pd.DataFrame(rows)
    study.check("All earlier candidates reconciled",len(result),34)
    return result


def dashboard_prep(study):
    df = study.df
    overview = pd.DataFrame([{"n":len(df),"amount_usd_sum":df.amount_usd.sum(),
        "duration_seconds_sum":df.duration_seconds.sum(),"median_duration_seconds":df.duration_seconds.median(),
        "p95_duration_seconds":df.duration_seconds.quantile(.95),"p99_duration_seconds":df.duration_seconds.quantile(.99),
        "labeled_n":int(df.has_label.sum()),"gap_n":int(df.gap.eq("Y").sum()),
        "unlabeled_n":int(df.has_label.eq(0).sum()),"median_amount_usd":df.amount_usd.median()}])
    study.save(overview,"dashboard_overview.csv")
    for name,keys in [("route",["route"]),("party",["party"]),("currency",["currency"]),("anomaly",["labeled"])]:
        out = profile(df,keys)
        study.save(out,f"dashboard_{name}_profile.csv")
        study.check(f"Dashboard {name} profile population",int(out.n.sum()),EXPECTED)
    cube = df.groupby(["route","currency","party"],observed=True).agg(
        n=("source_row","size"),amount_usd_sum=("amount_usd","sum"),duration_seconds_sum=("duration_seconds","sum"),
        labeled_n=("has_label","sum"),median_duration_seconds=("duration_seconds","median"),
        p95_duration_seconds=("duration_seconds",lambda s:s.quantile(.95))).reset_index()
    # Do not release tiny multifactor cells. Roll their additive totals into one
    # explicit aggregate instead of losing transactions from dashboards.
    tiny = cube.n<20
    suppressed_n = int(cube.loc[tiny,"n"].sum())
    released = cube.loc[~tiny].copy()
    for col in ["route","currency","party"]:
        released[col] = released[col].astype(str)
    if tiny.any():
        rolled = {col:"SUPPRESSED_SMALL_CELLS" for col in ["route","currency","party"]}
        for col in ["n","amount_usd_sum","duration_seconds_sum","labeled_n"]:
            rolled[col] = cube.loc[tiny,col].sum()
        rolled.update(median_duration_seconds=np.nan,p95_duration_seconds=np.nan)
        released = pd.concat([released,pd.DataFrame([rolled])],ignore_index=True)
    released["mean_duration_seconds"] = released.duration_seconds_sum/released.n
    released["label_rate"] = released.labeled_n/released.n
    study.save(released,"dashboard_route_currency_party_cube.csv")
    study.check("Dashboard cube population including suppression",int(released.n.sum()),EXPECTED)
    study.check("Dashboard cube label counts",int(released.labeled_n.sum()),int(df.has_label.sum()))
    study.check("Dashboard cube duration total",bool(np.isclose(released.duration_seconds_sum.sum(),df.duration_seconds.sum(),rtol=1e-12)),True)
    study.check("Dashboard cube amount total",bool(np.isclose(released.amount_usd_sum.sum(),df.amount_usd.sum(),rtol=1e-12)),True)
    durations = df[["route","duration_seconds"]].copy()
    durations["duration_band_seconds"] = pd.cut(durations.duration_seconds,[-np.inf,30,60,300,3600,86400,np.inf],
                  labels=["0-30","(30,60]","(60,300]","(300,3600]","(3600,86400]",">86400"])
    hist = durations.groupby(["route","duration_band_seconds"],observed=True).size().rename("n").reset_index()
    hist["route_denominator_n"] = hist.groupby("route",observed=True).n.transform("sum")
    hist["within_route_rate"] = hist.n/hist.route_denominator_n
    study.save(hist,"dashboard_duration_histogram.csv")
    study.check("Dashboard histogram population",int(hist.n.sum()),EXPECTED)
    # Time is aggregated by UTC date only; no transaction times are released.
    dated = df[["epoch","source_row","duration_seconds","has_label"]].copy()
    dated["date_utc"] = pd.to_datetime(dated.epoch,unit="s",utc=True).dt.strftime("%Y-%m-%d")
    daily = dated.groupby("date_utc").agg(n=("source_row","size"),duration_seconds_sum=("duration_seconds","sum"),labeled_n=("has_label","sum")).reset_index()
    study.save(daily,"dashboard_daily_totals.csv")
    study.check("Dashboard daily population",int(daily.n.sum()),EXPECTED)
    rules_manifest = study.manifests["08_rule_validation"]
    rule_path = next(study.root/p for p in rules_manifest["files"] if p.endswith("validated_rule_register.csv"))
    rule_table = pd.read_csv(rule_path)
    study.save(rule_table,"dashboard_rule_evidence.csv")
    dictionary = [
        {"field":"n","unit":"transactions","aggregation":"sum within one non-overlapping table","denominator":"table grain"},
        {"field":"labeled_n","unit":"observed nonblank anomaly labels","aggregation":"sum","denominator":"n; blank label is not verified normal"},
        {"field":"duration_seconds_sum","unit":"seconds","aggregation":"sum","denominator":"n for mean"},
        {"field":"amount_usd_sum","unit":"USD","aggregation":"sum","denominator":"n for mean"},
        {"field":"median_duration_seconds / p95_duration_seconds / p99_duration_seconds","unit":"seconds","aggregation":"not additive; never average medians or percentiles","denominator":"exact displayed group"},
        {"field":"label_rate / within_route_rate","unit":"fraction 0-1","aggregation":"recompute numerator/denominator after filters","denominator":"n / route_denominator_n respectively"},
        {"field":"SUPPRESSED_SMALL_CELLS","unit":"aggregate of cube cells with n<20","aggregation":"include only in overall totals; cannot allocate to a route/currency/party","denominator":"all suppressed cells"},
        {"field":"currency","unit":"source currency code","aggregation":"categorical; no inferred FX rate","denominator":"observed currency group"},
        {"field":"labeled","unit":"original anomaly label or UNLABELED presentation label","aggregation":"separate categories; CUSTOMER_RECALL retained","denominator":"observed label group"},
    ]
    study.save(pd.DataFrame(dictionary),"dashboard_data_dictionary.csv")
    # Aggregate-column allowlist and input-equivalent row-count guard.
    banned = {"source_row","source_row_number","ordering_account","beneficiary_account","ordering_tokens",
              "beneficiary_tokens","ordering_details","beneficiary_details","ordering_bic8","beneficiary_bic8","bic8_path","epoch"}
    for path in study.tables.glob("dashboard_*.csv"):
        frame = pd.read_csv(path)
        study.check(f"No identifiers or text in {path.name}",not bool({str(c).lower() for c in frame}&banned),True)
        study.check(f"Aggregate row count in {path.name}",bool(len(frame)<EXPECTED),True)
    privacy = pd.DataFrame([{"cube_minimum_cell_n":20,"suppressed_original_cells":int(tiny.sum()),"suppressed_transactions":suppressed_n,
                             "released_rows":len(released),"population_n":len(df),"transaction_level_exports":False}])
    study.save(privacy,"dashboard_release_validation.csv")
    # A local connection manifest points to versioned aggregates; no public publishing.
    connection = {"population":EXPECTED,"source_sha256":study.sha,"table_directory":str(study.tables.relative_to(study.root)),
                  "files":[p for p in study.files if Path(p).name.startswith("dashboard_")],
                  "privacy":"Local aggregate data only. Competition publication still requires organizer authorization.",
                  "filter_caution":"Cube small-cell rollup cannot be attributed after filters; medians and percentiles are not additive."}
    destination = study.root/"dashboard"/f"aggregate_manifest_{study.run}.json"
    destination.write_text(json.dumps(connection,indent=2),encoding="utf-8")
    study.files.append(str(destination.relative_to(study.root)))
    study.plot(profile(df,["route"]),"route","median_duration_seconds","Dashboard QA: route duration medians; full population",
               "Median duration (seconds)","dashboard_route_duration.png")
    return overview,released,hist,daily,privacy,rule_table
