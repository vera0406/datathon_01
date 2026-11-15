"""Focused Phase 1 repairs. Originals are read-only; private outputs stay local."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from itertools import zip_longest
from decimal import Decimal
import csv
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import patsy
from scipy import stats
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score
from statsmodels.stats.multitest import multipletests
from threadpoolctl import threadpool_limits
from remaining_analysis import digest, wilson, matched_effect

N=1_048_575
SEED=2026
MAJOR=['CHF','GBP','CNY','EUR','USD','SGD','HKD','CAD']


class Phase:
    def __init__(self, root, name, directory):
        self.root=Path(root).resolve();self.name=name
        self.source=self.root/'data/cleaned/swift_payments_cleaned.csv'
        self.run=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        self.out=self.root/'outputs/tables'/directory
        self.charts=self.root/'outputs/charts'/directory
        self.private=self.root/'outputs/phase1'/name/self.run
        for d in [self.out,self.charts,self.private]:d.mkdir(parents=True,exist_ok=True)
        self.files=[];self.checks=[]
        self.hashes={str(p.relative_to(self.root)):digest(p) for p in [self.source,*sorted((self.root/'data/raw').glob('*'))] if p.is_file()}
        self.df=self.load()
        self.check('Full source population',len(self.df)==N)
        self.check('Unique sequential source rows',np.array_equal(self.df.source_row,np.arange(2,N+2)))

    def check(self,name,passed):
        self.checks.append({'check':name,'passed':bool(passed)})
        assert passed,name

    def load(self):
        mapping={'SOURCE_ROW_NUMBER':'source_row','TRANSACTION_TYPE_CODE_STD':'route','CURRENCY_CODE_STD':'currency','PARTY_PAIR':'party','ANOMALY_TYPE_STD':'anomaly','USD_AMOUNT_NUM':'amount','TOTAL_DURATION_NUM':'duration','PARTICIPANT_COUNT_NUM':'participants','FX_COUNT_NUM':'fx','EPOCH_SECONDS_NUM':'epoch','HAS_PATH_GAP':'path_gap','ORDERING_BIC8':'ordering_bic','BENEFICIARY_BIC8':'beneficiary_bic'}
        cache=self.root/'outputs/cache/phase1';cache.mkdir(parents=True,exist_ok=True)
        key=digest(self.source);path=cache/f'compact_v1_{key}.pkl';meta=path.with_suffix('.json')
        if path.exists() and meta.exists() and json.loads(meta.read_text())['cache_sha256']==digest(path):
            return pd.read_pickle(path)
        parts=[]
        for ch in pd.read_csv(self.source,usecols=list(mapping),dtype=str,keep_default_na=False,chunksize=100_000):
            ch=ch.rename(columns=mapping)
            for c in ['source_row','amount','duration','participants','fx','epoch']:ch[c]=pd.to_numeric(ch[c],errors='raise')
            parts.append(ch)
        d=pd.concat(parts,ignore_index=True)
        assert np.isfinite(d[['amount','duration','participants','fx','epoch']]).all().all()
        assert (d[['amount','duration','participants','fx']]>=0).all().all()
        d['gap']=d.path_gap.eq('Y').astype(int);d['label']=d.anomaly.ne('').astype(int)
        d['labeled']=d.anomaly.where(d.anomaly.ne(''),'UNLABELED')
        d['log_amount']=np.log1p(d.amount);d['log_duration']=np.log1p(d.duration)
        d['amount_band']=pd.cut(d.amount,[-np.inf,100,1000,10000,100000,np.inf],labels=['<=100','100-1000','1000-10000','10000-100000','>100000']).astype(str)
        d['currency_group']=d.currency.where(d.currency.isin(MAJOR),'OTHER')
        dt=pd.to_datetime(d.epoch,unit='s',utc=True);d['hour']=dt.dt.hour;d['day']=dt.dt.dayofweek
        d['pair']=d.ordering_bic+'|'+d.beneficiary_bic
        for c in ['route','currency','party','labeled','currency_group','amount_band','ordering_bic','beneficiary_bic','pair']:d[c]=d[c].astype('category')
        d.to_pickle(path);meta.write_text(json.dumps({'source_sha256':key,'cache_sha256':digest(path),'schema':list(d)}))
        return d

    def save(self,d,name):
        path=self.out/name
        if path.exists():
            import shutil
            shutil.copy2(path,self.private/(name+'.before'))
        d.to_csv(path,index=False,encoding='utf-8-sig');self.files.append(str(path.relative_to(self.root)))
        return d

    def finish(self,findings,limits):
        self.check('Original source hashes unchanged',all(digest(self.root/p)==h for p,h in self.hashes.items()))
        self.save(pd.DataFrame(self.checks),'validation.csv')
        result={'name':self.name,'run':self.run,'source_population':N,'source_hashes':self.hashes,'files':self.files,'findings':findings,'limitations':limits,'checks':self.checks,'analysis_code_sha256':digest(Path(__file__))}
        (self.private/'completion.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
        print(json.dumps(result,indent=2,default=str));return result


def intervals_plot(p,d,label,effect,low,high,title,file,unit):
    d=d.dropna(subset=[effect,low,high]).head(30)
    fig,ax=plt.subplots(figsize=(10,max(4,len(d)*.28)))
    y=np.arange(len(d));ax.errorbar(d[effect],y,xerr=[d[effect]-d[low],d[high]-d[effect]],fmt='o')
    ax.set_yticks(y,d[label].astype(str));ax.axvline(0,color='grey',ls='--');ax.set(title=title,xlabel=unit)
    fig.tight_layout();path=p.charts/file;fig.savefig(path,dpi=150);plt.close(fig);p.files.append(str(path.relative_to(p.root)))


def design(d,formula):
    x=patsy.dmatrix(formula,d,return_type='dataframe')
    # A route/participant support constraint may cause exact dependencies.
    # QR drops only redundant columns, retaining named FX/gap coefficients.
    from scipy.linalg import qr
    _,r,pivot=qr(x.to_numpy(),mode='economic',pivoting=True)
    rank=int((abs(np.diag(r))>1e-9).sum())
    keep=sorted(pivot[:rank]);return x.iloc[:,keep]


def fit(d,x,outcome,binary):
    with threadpool_limits(limits=1):
        if binary:
            model=sm.GLM(d[outcome].to_numpy(),x,family=sm.families.Binomial()).fit(maxiter=80,cov_type='HC1')
            assert model.converged,'GLM did not converge'
        else:model=sm.OLS(d[outcome].to_numpy(),x).fit(cov_type='HC1')
    assert np.isfinite(model.params).all() and np.isfinite(model.bse).all(),'Invalid model coefficients'
    return model


def coefficients(model,split,outcome,n):
    ci=model.conf_int();return pd.DataFrame({'feature':model.params.index,'coefficient':model.params.values,'ci_low':ci.iloc[:,0].values,'ci_high':ci.iloc[:,1].values,'p_value':model.pvalues.values,'split':split,'outcome':outcome,'model_n':n})


def split_masks(d):
    rng=np.random.default_rng(SEED);a=rng.random(len(d))<.5
    cut=d.epoch.median()
    return {'full':np.ones(len(d),dtype=bool),'random_development':a,'random_validation':~a,'chronological_early':d.epoch.le(cut).to_numpy(),'chronological_late':d.epoch.gt(cut).to_numpy()}


def supported_match(d,treatment,strata,outcome,min_cell):
    result,detail=matched_effect(d,treatment,strata,outcome,min_cell)
    result['effect_unit']='log(1+duration seconds)' if outcome=='log_duration' else 'rate fraction; use difference_pp for percentage points'
    if not detail.empty:
        result['raw_difference_common_support']=float((detail.mean_1*detail.size_1).sum()/detail.size_1.sum()-(detail.mean_0*detail.size_0).sum()/detail.size_0.sum())
        result['minimum_stratum_difference']=float(detail.difference.min());result['maximum_stratum_difference']=float(detail.difference.max())
    if outcome!='log_duration' and result['status']=='ESTIMATED':
        for key in ['adjusted_difference','ci_low','ci_high']:
            result[{'adjusted_difference':'difference_pp','ci_low':'ci_low_pp','ci_high':'ci_high_pp'}[key]]=100*result[key]
    return result,detail


def source_reconciliation(p):
    from openpyxl import load_workbook
    raw=p.root/'data/raw/swift_payments_raw_export.csv';excel=p.root/'data/raw/swift_umdac_datathon_2026_fictitious_payment_data.xlsx'
    wb=load_workbook(excel,read_only=True,data_only=True);rows=wb.worksheets[0].iter_rows(values_only=True);header=list(next(rows))
    mismatch=[];other=Counter();count=0
    with raw.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.reader(stream);p.check('Excel/raw headers agree',next(reader)==header)
        numeric={'EPOCH_SECONDS','USD_AMOUNT','TOTAL_DURATION','CURRENCY_CONVERSION_COUNT','PARTICIPANT_COUNT'}
        for er,cr in zip_longest(rows,reader):
            assert er is not None and cr is not None
            count+=1
            for col,e,c in zip(header,er,cr):
                es='' if e is None else str(e)
                equal=es==c or (col in numeric and es!='' and c!='' and Decimal(es)==Decimal(c))
                if not equal:
                    if col=='USD_AMOUNT':mismatch.append({'source_row':count+1,'excel_usd_amount':float(e),'raw_csv_usd_amount':float(c),'absolute_difference':abs(float(e)-float(c)),'relative_difference':float(abs(Decimal(es)-Decimal(c))/max(abs(Decimal(es)),abs(Decimal(c))))})
                    else:other[col]+=1
            if count%200000==0:print('Workbook reconciliation rows:',count,flush=True)
    wb.close();p.check('Workbook/raw full population',count==N);p.check('No other original field differences',sum(other.values())==0);p.check('Reproduced 22 amount mismatches',len(mismatch)==22)
    m=pd.DataFrame(mismatch).merge(p.df[['source_row','amount','currency','route','participants','fx','party','labeled']],on='source_row',validate='one_to_one').rename(columns={'amount':'cleaned_usd_amount_num'})
    # Decimal differences retain the exact cent-level comparison convention.
    m['absolute_difference']=[float(abs(Decimal(str(a))-Decimal(str(b)))) for a,b in zip(m.excel_usd_amount,m.raw_csv_usd_amount)]
    p.check('Cleaned amounts match raw at mismatched rows',np.array_equal(m.cleaned_usd_amount_num,m.raw_csv_usd_amount))
    p.save(m,'workbook_raw_amount_mismatches.csv')
    before=p.df.amount.to_numpy().copy();after=before.copy();after[m.source_row.to_numpy(dtype=int)-2]=m.excel_usd_amount
    records=[]
    def add(scope,a,b):
        for stat in ['mean','median','P90','P95','P99']:
            f=(lambda v:float(np.mean(v))) if stat=='mean' else ((lambda v:float(np.median(v))) if stat=='median' else (lambda v:float(np.quantile(v,int(stat[1:])/100))))
            v,w=f(a),f(b);records.append({'scope':scope,'statistic':stat,'n':len(a),'csv_amount_value':v,'excel_amount_value':w,'absolute_change':abs(w-v),'relative_change':abs(w-v)/abs(v) if v else 0})
    add('ALL',before,after)
    for currency,idx in p.df.groupby('currency',observed=True).indices.items():add(str(currency),before[idx],after[idx])
    bands=[-np.inf,100,1000,10000,100000,np.inf];changes=int((pd.cut(before,bands).codes!=pd.cut(after,bands).codes).sum())
    sensitivity=p.save(pd.DataFrame(records),'amount_mismatch_sensitivity.csv')
    globalrows=sensitivity.loc[sensitivity.scope.eq('ALL')]
    immaterial=changes==0 and globalrows.relative_change.max()<1e-8 and sensitivity.relative_change.max()<1e-8
    summary=p.save(pd.DataFrame([{'n':count,'original_fields':len(header),'mismatched_amounts':len(m),'other_original_field_differences':sum(other.values()),'max_absolute_difference_usd':m.absolute_difference.max(),'max_relative_difference':m.relative_difference.max(),'amount_band_changes':changes,'max_summary_relative_change':sensitivity.relative_change.max(),'immaterial_under_declared_1e_8_summary_tolerance':immaterial}]),'source_reconciliation_summary.csv')
    p.check('Sensitivity population retained',len(before)==len(after)==N)
    statement=f'''# Source authority statement\n\nPhase 1 decision: {'RAW_CSV_CANONICAL_FOR_COMPUTATION' if immaterial else 'SOURCE_AUTHORITY_REQUIRES_REVIEW'}.\n\nThe original workbook remains the organizer-delivered source; raw CSV is the preserved computational export, and cleaned CSV preserves its original fields. All {count:,} rows and 21 fields were compared; {len(m)} USD_AMOUNT differences and {sum(other.values())} other-field differences were found. Maximum amount difference: USD {m.absolute_difference.max():.2f}; maximum relative amount difference: {m.relative_difference.max():.12g}. No source was changed.\n\nSensitivity changed {changes} fixed amount-band assignments. Maximum relative change across calculated global/currency summaries was {sensitivity.relative_change.max():.12g}. The declared materiality criterion is no band changes and all summary relative changes below 1e-8; this is an analytical numerical tolerance, not an official accounting threshold. The full sensitivity table is retained. The user explicitly authorized raw CSV computational authority if this impact is immaterial. This decision does not assert workbook/export exact equality or identify the export discrepancy cause.\n\nMismatch rows contain competition transaction information and remain only in ignored outputs/tables/source_reconciliation; do not commit, publish or upload them. Hashes are retained in the phase completion manifest.\n'''
    (p.root/'docs/source_authority_statement.md').write_text(statement,encoding='utf-8')
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(m.absolute_difference,bins=10);ax.set(title='Workbook/export amount differences: 22 mismatches; all source rows preserved',xlabel='Absolute difference (USD)',ylabel='Mismatch count');fig.tight_layout();fig.savefig(p.charts/'amount_differences.png',dpi=150);plt.close(fig)
    p.files.append(str((p.charts/'amount_differences.png').relative_to(p.root)))
    return summary,sensitivity,m


def segment_rates(p,d,groups):
    outputs=[]
    for threshold in [300,900,1800]:
        base=float(d.duration.gt(threshold).mean())
        for col in groups:
            z=d.assign(slow=d.duration.gt(threshold).astype(int)).groupby(col,observed=True).agg(n=('source_row','size'),slow_count=('slow','sum')).reset_index().rename(columns={col:'segment'})
            z['dimension']=col;z['threshold_seconds']=threshold;z['slow_rate']=z.slow_count/z.n;z['baseline_slow_rate']=base;z['difference_pp']=100*(z.slow_rate-base);z['rate_ratio']=z.slow_rate/base
            lo,hi=wilson(z.slow_count,z.n);z['slow_rate_ci_low']=lo;z['slow_rate_ci_high']=hi
            z['reliability']=np.where(z.n>=100,'ADEQUATE_DESCRIPTIVE','SPARSE')
            outputs.append(z)
    return pd.concat(outputs,ignore_index=True)


def direct_tail(p):
    d=p.df.loc[p.df.route.eq('DIRECT')].copy();p.check('Direct population and participants',len(d)==662245 and d.participants.eq(2).all())
    model_currencies=d.currency.value_counts().head(20).index.tolist()
    d['currency_group']=d.currency.astype(str).where(d.currency.isin(model_currencies),'OTHER').astype('category')
    rates=segment_rates(p,d,['fx','currency','amount_band','party','hour','day','labeled','ordering_bic','beneficiary_bic','pair'])
    p.save(rates,'direct_segment_slow_rates.csv')
    cov=rates.loc[rates.dimension.isin(['ordering_bic','beneficiary_bic','pair'])].groupby(['dimension','threshold_seconds','reliability']).n.sum().reset_index()
    cov['direct_population']=len(d);cov['coverage']=cov.n/len(d);p.save(cov,'direct_bic_support_coverage.csv')
    # Unstable/sparse BICs are audited, not encoded as thousands of dummies.
    sample=d.sample(n=min(150000,len(d)),random_state=SEED).reset_index(drop=True)
    formula='1 + fx + C(currency_group) + log_amount + C(party) + C(hour) + C(day) + label'
    x=design(sample,formula);masks=split_masks(sample);coefs=[];metrics=[]
    for threshold in [300,900,1800]:
        target=f'IS_SLOW_{threshold}';sample[target]=sample.duration.gt(threshold).astype(int)
        fits={}
        for split,mask in masks.items():
            print('Direct model',threshold,split,int(mask.sum()),flush=True)
            m=fit(sample.loc[mask],x.loc[mask],target,True);fits[split]=m
            coefs.append(coefficients(m,split,target,int(mask.sum())))
            pred=m.predict(x.loc[mask]);y=sample.loc[mask,target];null=np.repeat(y.mean(),len(y))
            metrics.append({'threshold_seconds':threshold,'evaluation':split+'_in_sample','fit_n':int(mask.sum()),'evaluation_n':len(y),'events':int(y.sum()),'observed_rate':y.mean(),'log_loss':log_loss(y,pred),'null_log_loss':log_loss(y,null),'remaining_log_loss_fraction':log_loss(y,pred)/log_loss(y,null),'brier':brier_score_loss(y,pred),'null_brier':brier_score_loss(y,null),'auc_descriptive':roc_auc_score(y,pred),'model_columns':x.shape[1]})
        for train,test in [('random_development','random_validation'),('chronological_early','chronological_late')]:
            y=sample.loc[masks[test],target];pred=fits[train].predict(x.loc[masks[test]]);base=sample.loc[masks[train],target].mean()
            metrics.append({'threshold_seconds':threshold,'evaluation':train+'_to_'+test,'fit_n':int(masks[train].sum()),'evaluation_n':len(y),'events':int(y.sum()),'observed_rate':y.mean(),'log_loss':log_loss(y,pred),'null_log_loss':log_loss(y,np.repeat(base,len(y))),'remaining_log_loss_fraction':log_loss(y,pred)/log_loss(y,np.repeat(base,len(y))),'brier':brier_score_loss(y,pred),'null_brier':brier_score_loss(y,np.repeat(base,len(y))),'auc_descriptive':roc_auc_score(y,pred),'model_columns':x.shape[1]})
    c=p.save(pd.concat(coefs),'direct_adjusted_coefficients.csv');met=p.save(pd.DataFrame(metrics),'direct_adjustment_residual_metrics.csv')
    p.save(pd.DataFrame([{'source_direct_n':len(d),'regression_sample_n':len(sample),'seed':SEED,'formula':formula,'currency_groups':json.dumps(model_currencies),'currency_group_rule':'Top 20 by Direct population count, no outcome screening; others pooled','bic_features':'NOT_INCLUDED: conservative scope; pair n>=100 coverage5.51%; endpoint n>=100 coverage85.6% is descriptive, not evidence that bank confounding is absent','time_units':'UTC hour0-23; weekday0=Monday through6=Sunday','rate_unit':'fraction; difference_pp uses percentage points','interpretation':'Residual log-loss fraction is uncertainty remaining relative to intercept baseline, not fraction of transactions with identified causes'}]),'direct_model_design.csv')
    for col in ['fx','currency','amount_band','party','hour','day','labeled']:
        z=rates.loc[rates.dimension.eq(col)];p.check(col+' segment denominator reconciliation',bool(z.groupby('threshold_seconds').n.sum().eq(len(d)).all()))
    intervals_plot(p,c.loc[c.split.eq('full')&c.outcome.eq('IS_SLOW_900')&~c.feature.eq('Intercept')],'feature','coefficient','ci_low','ci_high','Direct >900s adjusted log-odds effects: model sample n=150,000','direct_adjusted_effects.png','Log odds coefficient; pointwise 95% CI')
    fig,ax=plt.subplots(figsize=(9,4))
    for evaluation,g in met.loc[met.evaluation.str.contains('_to_')].groupby('evaluation'):ax.plot(g.threshold_seconds,g.remaining_log_loss_fraction,marker='o',label=evaluation)
    ax.set(title='Direct tail residual uncertainty on internal holdouts; exploratory thresholds',xlabel='Slow threshold (seconds)',ylabel='Model/null log-loss ratio');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(p.charts/'direct_residual_uncertainty.png',dpi=150);plt.close(fig)
    p.files.append(str((p.charts/'direct_residual_uncertainty.png').relative_to(p.root)))
    return rates,c,met


def adjusted_duration(p):
    d=p.df.copy();d['IS_SLOW_900']=d.duration.gt(900).astype(int)
    model_currencies=d.currency.value_counts().head(20).index.tolist()
    d['currency_group']=d.currency.astype(str).where(d.currency.isin(model_currencies),'OTHER').astype('category')
    sample=d.sample(n=200000,random_state=SEED).reset_index(drop=True)
    formula='1 + fx + gap + participants + C(route) + C(currency_group) + log_amount + C(party)'
    x=design(sample,formula);p.check('FX and gap effects identified in model design',{'fx','gap'}<=set(x))
    p.save(pd.DataFrame([{'source_n':len(d),'model_sample_n':len(sample),'seed':SEED,'currency_groups':json.dumps(model_currencies),'formula':formula,'currency_policy':'Top 20 by population count, without outcome screening; OTHER pooled','inference':'HC1 pointwise; fixed probability sample and internal partitions; no causal/external claim'}]),'adjusted_model_design.csv')
    rows=[]
    for outcome,binary in [('log_duration',False),('IS_SLOW_900',True)]:
        for split,mask in split_masks(sample).items():
            print('Duration model',outcome,split,flush=True)
            m=fit(sample.loc[mask],x.loc[mask],outcome,binary)
            c=coefficients(m,split,outcome,int(mask.sum()));rows.append(c)
    c=p.save(pd.concat(rows),'adjusted_fx_gap_models.csv')
    selected=c.loc[c.feature.isin(['fx','gap'])].copy()
    selected['effect_unit']=np.where(selected.outcome.eq('log_duration'),'log(1+duration seconds) per unit','log odds per unit')
    selected['exp_coefficient']=np.exp(selected.coefficient);selected['exp_ci_low']=np.exp(selected.ci_low);selected['exp_ci_high']=np.exp(selected.ci_high)
    selected['exp_interpretation']=np.where(selected.outcome.eq('log_duration'),'Ratio of conditional geometric(duration+1); not median','Odds ratio; not risk ratio')
    p.save(selected,'adjusted_fx_gap_effects.csv')
    matches=[];strata=['route','participants','currency_group','amount_band','party']
    for split,mask in split_masks(d).items():
        sub=d.loc[mask]
        for outcome in ['log_duration','IS_SLOW_900']:
            g,detail=supported_match(sub,sub.gap.eq(1),strata+['fx'],outcome,min_cell=20)
            matches.append(g|{'contrast':'gap 1 vs 0','split':split})
            if split=='full' and not detail.empty:p.save(detail,'gap_'+outcome+'_matched_strata.csv')
            for base in sorted(sub.fx.unique()):
                t=sub.loc[sub.fx.isin([base,base+1])]
                if t.fx.nunique()<2:continue
                r,detail=supported_match(t,t.fx.eq(base+1),strata,outcome,min_cell=20)
                matches.append(r|{'contrast':f'FX {base+1} vs {base}','split':split})
                if split=='full' and not detail.empty:p.save(detail,f'fx_{base}_{outcome}_strata.csv')
    match=p.save(pd.DataFrame(matches),'common_support_fx_gap_comparisons.csv')
    # Threshold sensitivity uses identical full regression sample.
    sensitivity=[]
    for threshold in [300,1800]:
        col=f'IS_SLOW_{threshold}';sample[col]=sample.duration.gt(threshold).astype(int)
        m=fit(sample,x,col,True);sensitivity.append(coefficients(m,'full',col,len(sample)))
    p.save(pd.concat(sensitivity),'adjusted_threshold_sensitivity.csv')
    from remaining_analysis import conditional_counterexamples
    renamed=d.rename(columns={'duration':'duration_seconds'})
    renamed['gap']=d.path_gap
    fx,gaps=conditional_counterexamples(renamed)
    p.save(fx,'fx_median_counterexamples_rechecked.csv');p.save(gaps,'gap_median_counterexamples_rechecked.csv')
    intervals_plot(p,selected.loc[selected.split.eq('full')].assign(effect_label=lambda z:z.feature+' / '+z.outcome),'effect_label','coefficient','ci_low','ci_high','Adjusted FX/gap effects: fixed sample n=200,000; model-specific units','adjusted_effects.png','Log-duration / log-odds coefficient; pointwise 95% CI')
    return selected,match,fx,gaps


def currency_bic(p):
    d=p.df.loc[p.df.route.isin(['INDIRECT','COVERED'])].copy();d['covered']=d.route.eq('COVERED').astype(int)
    p.check('Non-direct source population',len(d)==386330)
    pairs=d.groupby('pair',observed=True).agg(n=('source_row','size'),covered_n=('covered','sum'));pairs['indirect_n']=pairs.n-pairs.covered_n
    records=[]
    for cut in [0,20,50,100,500]:
        eligible=pairs.index[pairs.n.ge(cut)]
        for currency,sub in [('ALL',d),*[(c,d.loc[d.currency.eq(c)]) for c in sorted(d.currency.unique())]]:
            retained=sub.pair.isin(eligible)
            records.append({'currency':currency,'pair_min_n':cut,'unique_pairs':int(sub.loc[retained,'pair'].nunique()),'eligible_population_n':len(sub),'retained_n':int(retained.sum()),'coverage_percent':100*retained.mean()})
    p.save(pd.DataFrame(records),'bic_pair_support_coverage.csv')
    eligible=pairs.index[pairs.n.ge(20)&pairs.covered_n.ge(3)&pairs.indirect_n.ge(3)]
    sub=d.loc[d.pair.isin(eligible)].copy().reset_index(drop=True)
    p.check('Common-support frame contains both route outcomes',sub.covered.nunique()==2)
    sub['pair_code']=pd.Categorical(pd.factorize(sub.pair)[0].astype(str))
    group_support=sub.groupby('currency',observed=True).covered.agg(['size','sum'])
    estimable=[c for c in MAJOR if c in group_support.index and group_support.loc[c,'size']>=30 and group_support.loc[c,'sum']>=5 and group_support.loc[c,'size']-group_support.loc[c,'sum']>=5]
    # Pool, rather than manufacture separate coefficients for, sparse currencies.
    # Keep every row of the fixed pair frame in BOTH models. All eight original
    # currency supports remain separately reported below.
    sub['model_currency']=sub.currency.astype(str).where(sub.currency.isin(estimable),'OTHER_OR_SPARSE').astype('category')
    # Fixed common rows in both models. Pair-overlap selection changes scope;
    # neither this frame nor its conditional inference represents all payments.
    formula='1 + C(model_currency, Treatment(reference="OTHER_OR_SPARSE")) + participants + fx + log_amount + C(party)'
    xb=design(sub,formula);xa=design(sub,formula+' + C(pair_code)')
    models={};diagnostics=[]
    for name,x in [('baseline',xb),('bic_adjusted',xa)]:
        print('Currency model',name,len(sub),x.shape[1],flush=True)
        m=fit(sub,x,'covered',True)
        stable=bool(abs(m.params).max()<15 and m.bse.max()<5 and np.linalg.cond(x)<1e8)
        events_per_parameter=min(sub.covered.sum(),len(sub)-sub.covered.sum())/x.shape[1]
        diagnostics.append({'model':name,'n':len(sub),'pairs':sub.pair.nunique(),'parameters':x.shape[1],'covered_events':int(sub.covered.sum()),'events_per_parameter':events_per_parameter,'max_abs_coefficient':abs(m.params).max(),'max_standard_error':m.bse.max(),'design_condition_number':np.linalg.cond(x),'numerical_stability':stable,'inferential_reliability_screen':bool(stable and events_per_parameter>=10 and sub.pair.nunique()>=30),'uncertainty':'HC1 pointwise, fixed selected rows; pair-cluster sensitivity also reported; estimates failing reliability screens are diagnostic only'})
        models[name]=(m,x)
        p.save(coefficients(m,'full',name,len(sub)),name+'_coefficients.csv')
    diag=p.save(pd.DataFrame(diagnostics),'bic_model_diagnostics.csv')
    # Pair-cluster covariance sensitivity: 49 clusters; finite cluster concerns
    # and low events/parameter are explicit reliability limits.
    cluster={}
    for name,(m,x) in models.items():
        with threadpool_limits(limits=1):
            cm=sm.GLM(sub.covered,x,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':sub.pair_code})
        cluster[name]=cm
    rows=[]
    allstable=bool(diag.inferential_reliability_screen.all())
    for currency in MAJOR:
        mask=sub.currency.eq(currency);ref=sub.model_currency.eq('OTHER_OR_SPARSE')
        events=int(sub.loc[mask,'covered'].sum());n=int(mask.sum());other_n=int(ref.sum())
        row={'currency':currency,'support_n':n,'covered_n':events,'reference_other_n':other_n,'source_currency_n':int(d.currency.eq(currency).sum()),'bic_coverage_percent':100*n/max(1,int(d.currency.eq(currency).sum())),'common_population_n':len(sub),'bic_pairs':sub.pair.nunique(),'effect_unit':'odds ratio vs OTHER_OR_SPARSE pool; not probability ratio','interval_type':'Pointwise HC1; BH among estimable prespecified currency tests; sparse currencies retain blank effects'}
        term=f'C(model_currency, Treatment(reference="OTHER_OR_SPARSE"))[T.{currency}]'
        if term not in models['baseline'][0].params or term not in models['bic_adjusted'][0].params:
            row['status']='INSUFFICIENT_COMMON_SUPPORT';rows.append(row);continue
        for name,(m,x) in models.items():
            ci=m.conf_int().loc[term]
            row.update({name+'_log_odds':m.params[term],name+'_odds_ratio':np.exp(m.params[term]),name+'_ci_low':np.exp(ci.iloc[0]),name+'_ci_high':np.exp(ci.iloc[1]),name+'_p_value':m.pvalues[term],name+'_pair_cluster_ci_low':np.exp(cluster[name].conf_int().loc[term].iloc[0]),name+'_pair_cluster_ci_high':np.exp(cluster[name].conf_int().loc[term].iloc[1])})
        row['effect_change_log_odds']=row['bic_adjusted_log_odds']-row['baseline_log_odds']
        row['direction_stable']=np.sign(row['bic_adjusted_log_odds'])==np.sign(row['baseline_log_odds'])
        supported=n>=30 and events>=5 and n-events>=5 and other_n>=30 and row['bic_coverage_percent']>=5
        if not supported:status='INSUFFICIENT_COMMON_SUPPORT'
        elif not allstable or not row['direction_stable']:status='EFFECT_UNSTABLE'
        elif abs(row['bic_adjusted_log_odds'])<.75*abs(row['baseline_log_odds']):status='EFFECT_ATTENUATES_AFTER_BIC_CONTROL'
        else:status='EFFECT_REMAINS_AFTER_BIC_CONTROL'
        row['status']=status;rows.append(row)
    effects=pd.DataFrame(rows)
    for model in ['baseline','bic_adjusted']:
        valid=effects[model+'_p_value'].notna();effects.loc[valid,model+'_p_value_bh']=multipletests(effects.loc[valid,model+'_p_value'],method='fdr_bh')[1]
    p.save(effects,'currency_before_after_bic_effects.csv')
    matched=[]
    for currency in MAJOR:
        t=sub.loc[sub.currency.eq(currency)|sub.model_currency.eq('OTHER_OR_SPARSE')]
        r,detail=supported_match(t,t.currency.eq(currency),['participants','fx','amount_band','party','pair_code'],outcome='covered',min_cell=3)
        matched.append(r|{'currency':currency})
        if not detail.empty:p.save(detail,'currency_'+currency+'_matched_strata.csv')
    matching=p.save(pd.DataFrame(matched),'currency_pair_stratified_robustness.csv')
    p.save(pd.DataFrame([{'population_n':len(d),'selected_n':len(sub),'selected_pairs':len(eligible),'coverage_percent':100*len(sub)/len(d),'pair_selection':'n>=20 and Covered>=3 and Indirect>=3','minimum_currency_coverage_for_rule_percent':5,'comparison_reference':'OTHER_OR_SPARSE: non-prespecified plus currencies with n<30 or <5 events/non-events; all rows retained in both models','estimable_currency_levels':json.dumps(estimable),'baseline_formula':formula,'adjusted_formula':formula+' + C(pair_code)','limitation':'Selection on outcome overlap; fixed common rows; not representative of non-direct network. HC1 and cluster intervals are exploratory; unreliable screens prohibit inference.'}]),'bic_common_population_design.csv')
    plot=effects.dropna(subset=['bic_adjusted_log_odds']).copy()
    plot['log_ci_low']=np.log(plot.bic_adjusted_ci_low);plot['log_ci_high']=np.log(plot.bic_adjusted_ci_high)
    intervals_plot(p,plot,'currency','bic_adjusted_log_odds','log_ci_low','log_ci_high',f'Diagnostic only: insufficient currency/BIC common support; selected n={len(sub):,}','currency_bic_effects.png','Log odds vs OTHER_OR_SPARSE; pointwise 95% CI; not a global effect')
    return effects,matching,diag
