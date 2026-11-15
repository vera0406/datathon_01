"""Final evidence integration and local analytical release; never builds Power BI."""
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
import json
import shutil
import subprocess
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from threadpoolctl import threadpool_limits
from phase1_analysis import Phase, MAJOR, supported_match
from remaining_analysis import digest
from release_cleanup import verify_phase2_sample, resolve_endpoint

N=1_048_575
SEED=2026
SCHEMA='RULE_ID RULE_FAMILY RULE_NAME CONDITION OUTCOME SUPPORT_COUNT SCOPE_COUNT SUPPORT_PERCENT EXCEPTION_COUNT EFFECT_SIZE EFFECT_UNIT COMPARISON_BASELINE UNCERTAINTY ADJUSTMENT_METHOD ROBUSTNESS LIMITATIONS EVIDENCE_SOURCE STATUS CONFIDENCE BUSINESS_PROBLEM POTENTIAL_APPLICATION DASHBOARD_PAGE'.split()
STATUSES={'SUPPORTED_STRUCTURAL_RULE','STRONG_STATISTICAL_PATTERN','PLAUSIBLE_GENERATING_MECHANISM','EXPLORATORY_ASSOCIATION','REJECTED_HYPOTHESIS','INSUFFICIENT_EVIDENCE'}


def dump(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,default=str,allow_nan=False),encoding='utf-8')


def markdown(frame):
    d=pd.DataFrame(frame).astype(object).where(pd.notna(pd.DataFrame(frame)),'Not estimable')
    def val(x):return str(x).replace('|',' / ').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(map(val,d.columns))+' |','| '+' | '.join(['---']*len(d.columns))+' |']+['| '+' | '.join(map(val,row))+' |' for row in d.itertuples(index=False,name=None)])+'\n'


class Integration:
    def __init__(self,root):
        self.root=Path(root).resolve();self.run=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        self.private=self.root/'outputs/phase2'/self.run;self.private.mkdir(parents=True)
        self.out=self.root/'outputs/tables/final_evidence';self.charts=self.root/'outputs/charts/final_evidence'
        self.out.mkdir(parents=True,exist_ok=True);self.charts.mkdir(parents=True,exist_ok=True)
        self.inputs={};self.checks=[];self.outputs=[]
        self.source=self.root/'data/cleaned/swift_payments_cleaned.csv'
        self.source_hash=digest(self.source)
        self.raw_hash=digest(self.root/'data/raw/swift_payments_raw_export.csv')
        self.excel_hash=digest(self.root/'data/raw/swift_umdac_datathon_2026_fictitious_payment_data.xlsx')
        self.df=Phase.load(SimpleNamespace(root=self.root,source=self.source))
        self.check('Source population',len(self.df)==N)
        self.check('Source row alignment',np.array_equal(self.df.source_row,np.arange(2,N+2)))
        self.reg=self.read('outputs/rules/final_rule_register.csv')
        self.check('Canonical rule schema and unique IDs',list(self.reg)==SCHEMA and self.reg.RULE_ID.is_unique)
        self.check('Canonical statuses',set(self.reg.STATUS)<=STATUSES)
        rs=self.reg.set_index('RULE_ID').STATUS
        self.check('Phase1 conclusions preserved',rs.F11==rs.F12=='INSUFFICIENT_EVIDENCE' and rs.F07==rs.F08=='REJECTED_HYPOTHESIS')
        phase_reports=[]
        for name in ['00B_source_amount_reconciliation','04B_direct_long_tail','04C_duration_adjusted_robustness','05B_currency_bic_robustness']:
            p=sorted((self.root/'outputs/phase1'/name).glob('*/completion.json'))[-1]
            m=json.loads(p.read_text());phase_reports.append(m)
            self.inputs[str(p.relative_to(self.root))]=digest(p)
            self.check(name+' source version matches',m['source_hashes'][str(self.source.relative_to(self.root))]==self.source_hash and all(x['passed'] for x in m['checks']))

    def check(self,name,passed):
        self.checks.append({'CHECK':name,'PASSED':bool(passed)})
        assert passed,name

    def read(self,path):
        p=self.root/path;self.inputs[str(p.relative_to(self.root))]=digest(p)
        return pd.read_csv(p)

    def previous(self,phase,name):
        p=sorted((self.root/'outputs/tables/remaining'/phase).glob('*/completion.json'))[-1]
        m=json.loads(p.read_text());self.inputs[str(p.relative_to(self.root))]=digest(p)
        self.check(phase+' source version '+name,m['source_sha256']==self.source_hash)
        return self.read(str(Path(m['table_directory'])/name))

    def save(self,d,name):
        path=self.out/name
        if path.exists():shutil.copy2(path,self.private/(name+'.before'))
        d.to_csv(path,index=False,encoding='utf-8-sig');self.outputs.append(str(path.relative_to(self.root)));return d

    def chart(self,filename,title,xlabel,ylabel,draw,caption):
        fig,ax=plt.subplots(figsize=(10,5));draw(ax);ax.set(title=title,xlabel=xlabel,ylabel=ylabel)
        fig.text(.01,.01,caption,fontsize=8,wrap=True);fig.tight_layout(rect=[0,.08,1,1])
        path=self.charts/filename;fig.savefig(path,dpi=150,bbox_inches='tight');plt.close(fig)
        self.outputs.append(str(path.relative_to(self.root)));return str(path.relative_to(self.root))

    def preserved(self):
        self.check('Cleaned source unchanged',digest(self.source)==self.source_hash)
        self.check('Raw source unchanged',digest(self.root/'data/raw/swift_payments_raw_export.csv')==self.raw_hash)
        self.check('Organizer workbook unchanged',digest(self.root/'data/raw/swift_umdac_datathon_2026_fictitious_payment_data.xlsx')==self.excel_hash)

    def estimands(self):
        saved=self.previous('08_rule_validation','duration_effect_stability.csv')
        strict=saved.loc[saved.split.eq('full')&saved.contrast.eq('COVERED vs INDIRECT')].iloc[0]
        original=self.previous('08_rule_validation','prior_matched_duration_reproduction.csv').iloc[0]
        rows=[]
        for label,r,use in [('PRIMARY_MIN20',strict,'PRIMARY uncertainty-aware evidence'),('EARLIER_MIN1_SENSITIVITY',original,'SENSITIVITY ONLY; no valid singleton variance')]:
            rows.append({'ESTIMAND':label,'MATCH_REQUIREMENT':f'Minimum {int(r.min_cell_per_arm)} per route arm','MATCHED_STRATA':int(r.shared_strata),'COVERED_N':int(r.supported_treated_n),'INDIRECT_N':int(r.supported_baseline_n),'LOG_DIFFERENCE':r.adjusted_difference,'GEOMETRIC_RELATIVE_DIFFERENCE':np.expm1(r.adjusted_difference),'CI_LOW':np.expm1(r.ci_low) if pd.notna(r.ci_low) else np.nan,'CI_HIGH':np.expm1(r.ci_high) if pd.notna(r.ci_high) else np.nan,'LOG_CI_LOW':r.ci_low,'LOG_CI_HIGH':r.ci_high,'CI_UNIT':'relative geometric(duration+1) difference, fraction','INTERPRETATION':'Min-arm-weighted conditional geometric mean of duration+1; not median, causal delay or raw-second increase','DASHBOARD_USE':use,'MATCH_VARIABLES':'participants + FX + currency + party','WEIGHTING':'min(nCovered,nIndirect), normalized over eligible strata'})
        out=self.save(pd.DataFrame(rows),'covered_indirect_duration_estimands.csv')
        self.check('Primary estimand counts',strict.shared_strata==217 and strict.supported_treated_n==38017 and strict.supported_baseline_n==264393)
        self.check('Sensitivity interval not borrowed',out.loc[out.ESTIMAND.eq('EARLIER_MIN1_SENSITIVITY'),'CI_LOW'].isna().all())
        self.strict=strict;self.old_estimate=original
        return out

    def nested(self):
        # One probability sample and one heldout split; all seven models use
        # identical rows. Currency grouping is learned on training rows only.
        d=self.df.sample(n=200000,random_state=SEED).reset_index(drop=True)
        identity=verify_phase2_sample(self.root,d,self.source_hash,SEED)
        self.check('Phase1 and Phase2 ordered sample hashes match',identity['SOURCE_ROW_HASH']==identity['PHASE1_SOURCE_ROW_HASH'])
        identity_path='outputs/tables/duration/adjusted/fx_gap_model_sample_design.json'
        self.inputs[identity_path]=digest(self.root/identity_path)
        train,test=train_test_split(np.arange(len(d)),test_size=.25,random_state=SEED)
        top=d.iloc[train].currency.value_counts().head(20).index.tolist()
        d['currency_model']=d.currency.astype(str).where(d.currency.isin(top),'OTHER')
        predictors=[[],['route'],['participants'],['route','participants'],['route','participants','fx'],['route','participants','fx','currency_model'],['route','participants','fx','currency_model','log_amount','party','gap']]
        y=d.log_duration.to_numpy();rows=[]
        for i,features in enumerate(predictors):
            x=d[features].copy()
            cats=[c for c in ['route','currency_model','party'] if c in x]
            for c in cats:
                levels=sorted(x.iloc[train][c].astype(str).unique())
                self.check(f'Model{i} heldout category support {c}',set(x.iloc[test][c].astype(str))<=set(levels))
                x[c]=pd.Categorical(x[c].astype(str),categories=levels)
            if cats:x=pd.get_dummies(x,columns=cats,drop_first=True,dtype=float)
            matrix=np.column_stack([np.ones(len(d)),x.to_numpy(dtype=float)])
            with threadpool_limits(limits=1):beta=np.linalg.lstsq(matrix[train],y[train],rcond=None)[0]
            pred=matrix[test]@beta
            r2=r2_score(y[test],pred);mae=mean_absolute_error(y[test],pred)
            reference=[None,0,0,2,3,4,5][i]
            comparison=['BASELINE','NESTED_FROM_BASELINE','ALTERNATIVE_BASELINE','NESTED_EXTENSION','NESTED_EXTENSION','NESTED_EXTENSION','NESTED_EXTENSION'][i]
            label=['Intercept','Routing','Participants','Routing + Participants','Routing + Participants + FX','Routing + Participants + FX + Currency','Routing + Participants + FX + Currency + Amount + Party + Gap'][i]
            rows.append({'MODEL':f'MODEL_{i}','FEATURE_SET':label,'REFERENCE_MODEL':'NONE' if reference is None else f'MODEL_{reference}','COMPARISON_TYPE':comparison,'TRAIN_N':len(train),'TEST_N':len(test),'R2_LOG_DURATION':r2,'MAE_LOG_DURATION':mae,'RMSE_LOG_DURATION':np.sqrt(mean_squared_error(y[test],pred)),'DELTA_R2_VS_REFERENCE':r2-rows[reference]['R2_LOG_DURATION'] if reference is not None else np.nan,'DELTA_MAE_VS_REFERENCE':rows[reference]['MAE_LOG_DURATION']-mae if reference is not None else np.nan,'OUTCOME':'log1p(duration_seconds)','SAMPLE_N':len(d),'SPLIT_SEED':SEED,'NOTES':'OLS; delta MAE is reference minus current (positive means improvement). Explicit reference; M2 is not compared to M1; predictive comparison, not causal decomposition.'})
        out=self.save(pd.DataFrame(rows),'duration_nested_baselines.csv')
        self.save(pd.DataFrame([{'sample_n':len(d),'train_n':len(train),'test_n':len(test),'sample_seed':SEED,'split_seed':SEED,'training_currency_groups':json.dumps(top),'train_row_id_sha256':hashlib.sha256(d.iloc[train].source_row.to_numpy().tobytes()).hexdigest(),'test_row_id_sha256':hashlib.sha256(d.iloc[test].source_row.to_numpy().tobytes()).hexdigest(),'training_group_policy':'Top20 training currency frequencies; OTHER; no outcome screening','evaluation':'Same heldout targets and rows for all models; no raw-scale retransformation or causal variance decomposition',**identity}]),'duration_nested_design.csv')
        self.chart('duration_nested_model_performance.png','Duration baselines: explicit references; same 50,000 heldout rows','Model (reference models and feature sets in source table)','Heldout R² of log1p(seconds)',lambda ax:ax.bar(out.MODEL,out.R2_LOG_DURATION),'Train n=150,000; sample n=200,000; seed=2026. M1 and M2 reference M0; M3 references M2; subsequent models extend the previous model. No causal attribution.')
        return out

    def profiles(self):
        d=self.df
        def profile(key):
            z=d.groupby(key,observed=True).agg(N=('source_row','size'),MEAN_USD_AMOUNT=('amount','mean'),MEDIAN_USD_AMOUNT=('amount','median'),P25_USD_AMOUNT=('amount',lambda s:s.quantile(.25)),P75_USD_AMOUNT=('amount',lambda s:s.quantile(.75)),P90_USD_AMOUNT=('amount',lambda s:s.quantile(.9)),P95_USD_AMOUNT=('amount',lambda s:s.quantile(.95)),P99_USD_AMOUNT=('amount',lambda s:s.quantile(.99)),MEDIAN_DURATION=('duration','median'),P95_DURATION=('duration',lambda s:s.quantile(.95)),AMOUNT_SUM_USD=('amount','sum'),DURATION_SUM_SECONDS=('duration','sum'),LABELED_N=('label','sum')).reset_index()
            z['IQR_USD_AMOUNT']=z.P75_USD_AMOUNT-z.P25_USD_AMOUNT;z['SHARE_OF_ALL']=z.N/N
            for route in ['DIRECT','INDIRECT','COVERED']:
                count=d.loc[d.route.eq(route)].groupby(key,observed=True).size()
                z[route+'_N']=z[key].map(count).astype(float).fillna(0).astype(int)
                z[route+'_RATE']=z[route+'_N']/z.N
            z['RELIABILITY_FLAG']=np.where(z.N>=100,'ADEQUATE_DESCRIPTIVE','SPARSE')
            z=z.rename(columns={key:'CURRENCY' if key=='currency' else 'PARTY_PAIR'})
            self.check(key+' profile N',z.N.sum()==N);self.check(key+' route rates',np.allclose(z[['DIRECT_RATE','INDIRECT_RATE','COVERED_RATE']].sum(axis=1),1))
            return z
        currencies=self.save(profile('currency'),'currency_final_profile.csv');parties=self.save(profile('party'),'party_final_profile.csv')
        joint=d.groupby(['currency','party'],observed=True).size().rename('N').reset_index().rename(columns={'currency':'CURRENCY','party':'PARTY_PAIR'})
        a=joint.copy();a['PARTY_DENOMINATOR_N']=a.groupby('PARTY_PAIR',observed=True).N.transform('sum');a['P_CURRENCY_GIVEN_PARTY']=a.N/a.PARTY_DENOMINATOR_N
        b=joint.copy();b['CURRENCY_DENOMINATOR_N']=b.groupby('CURRENCY',observed=True).N.transform('sum');b['P_PARTY_GIVEN_CURRENCY']=b.N/b.CURRENCY_DENOMINATOR_N
        self.check('P(currency|party) sums to1',np.allclose(a.groupby('PARTY_PAIR',observed=True).P_CURRENCY_GIVEN_PARTY.sum(),1))
        self.check('P(party|currency) sums to1',np.allclose(b.groupby('CURRENCY',observed=True).P_PARTY_GIVEN_CURRENCY.sum(),1))
        self.save(a,'currency_given_party.csv');self.save(b,'party_given_currency.csv')
        return currencies,parties

    def same_support(self):
        d=self.df;nd=d.loc[d.route.isin(['COVERED','INDIRECT'])].copy();rows=[]
        def add(name,full,full_n,raw,n,adjusted,method,unit,note):
            rows.append(dict(EFFECT_NAME=name,FULL_POPULATION_RAW_EFFECT=float(full),FULL_POPULATION_N=int(full_n),COMMON_SUPPORT_RAW_EFFECT=float(raw),COMMON_SUPPORT_N=int(n),ADJUSTED_EFFECT=float(adjusted),ADJUSTMENT_METHOD=method,EFFECT_UNIT=unit,SUPPORT_CHANGE_NOTE=note,INTERPRETATION='Raw common-support means use empirical arm distributions; standardization changes stratum weights. Do not attribute the full change solely to confounding or causation.'))
        st=self.read('outputs/tables/duration/indirect_covered_duration_matched_strata.csv')
        st=st.loc[st.COUNT_COVERED.ge(20)&st.COUNT_INDIRECT.ge(20)]
        cr=(st.COUNT_COVERED*st.MEAN_LOG_DURATION_COVERED).sum()/st.COUNT_COVERED.sum()-(st.COUNT_INDIRECT*st.MEAN_LOG_DURATION_INDIRECT).sum()/st.COUNT_INDIRECT.sum()
        adjusted=np.average(st.LOG_DURATION_DIFFERENCE,weights=st.MATCH_WEIGHT)
        self.check('Same-support Covered point equals primary',np.isclose(adjusted,self.strict.adjusted_difference,atol=1e-10))
        add('Covered vs Indirect PRIMARY',nd.loc[nd.route.eq('COVERED'),'log_duration'].mean()-nd.loc[nd.route.eq('INDIRECT'),'log_duration'].mean(),len(nd),cr,st.COUNT_COVERED.sum()+st.COUNT_INDIRECT.sum(),adjusted,'Exact participant/FX/currency/party strata; >=20 per arm; min-arm weights','log(1+seconds)',f'{len(st)} strata; 38017 Covered and264393 Indirect retained; support and weights both change')
        st=self.previous('05_currency_party','duration_strata_USD_vs_other_USD.csv')
        cr=(st.size_1*st.mean_1).sum()/st.size_1.sum()-(st.size_0*st.mean_0).sum()/st.size_0.sum()
        usd_est=np.average(st.difference,weights=st.weight)
        add('USD vs other duration',d.loc[d.currency.eq('USD'),'log_duration'].mean()-d.loc[~d.currency.eq('USD'),'log_duration'].mean(),N,cr,st.size_1.sum()+st.size_0.sum(),usd_est,'Exact route/participants/FX/amount band/party; >=20 per arm; min-arm weights','log(1+seconds)','All currencies retained; treatment is USD; other currencies are the baseline; not a universal currency generator')
        sample=d.sample(n=200000,random_state=SEED)
        verify_phase2_sample(self.root,sample,self.source_hash,SEED)
        stored=self.read('outputs/tables/duration/adjusted/adjusted_fx_gap_effects.csv')
        for feature in ['fx','gap']:
            if feature=='fx':
                full=np.cov(d.fx,d.log_duration,ddof=0)[0,1]/np.var(d.fx)
                raw=np.cov(sample.fx,sample.log_duration,ddof=0)[0,1]/np.var(sample.fx)
            else:
                full=d.loc[d.gap.eq(1),'log_duration'].mean()-d.loc[d.gap.eq(0),'log_duration'].mean()
                raw=sample.loc[sample.gap.eq(1),'log_duration'].mean()-sample.loc[sample.gap.eq(0),'log_duration'].mean()
            adjusted=stored.loc[stored.feature.eq(feature)&stored.split.eq('full')&stored.outcome.eq('log_duration'),'coefficient'].iloc[0]
            add('Regression '+feature+' duration',full,N,raw,len(sample),adjusted,'Same fixed seed200000 rows; OLS adjusted route/participants/FX/gap/currency group/logUSD/party','log(1+seconds) per unit','Equal row weights in same-sample raw and adjusted fits; selection differs from full population. FX slope is a heterogeneous additive trend.')
        nd['covered']=nd.route.eq('COVERED').astype(float);diagnostics=[]
        for currency in MAJOR:
            treatment=nd.currency.eq(currency)
            result,detail=supported_match(nd,treatment,['participants','fx'],'covered',20)
            if detail.empty:
                diagnostics.append({'CURRENCY':currency,'STATUS':'INSUFFICIENT_COMMON_SUPPORT'});continue
            raw=(detail.size_1*detail.mean_1).sum()/detail.size_1.sum()-(detail.size_0*detail.mean_0).sum()/detail.size_0.sum()
            obs=np.dot(detail.weight,detail.mean_1);expected=np.dot(detail.weight,detail.mean_0)
            diagnostics.append({'CURRENCY':currency,'SOURCE_CURRENCY_N':int(treatment.sum()),'SOURCE_NON_DIRECT_N':len(nd),'SUPPORTED_CURRENCY_N':result['supported_treated_n'],'SUPPORTED_REFERENCE_N':result['supported_baseline_n'],'MATCHED_STRATA':result['shared_strata'],'OBSERVED_STANDARDIZED_RATE_PERCENT':100*obs,'EXPECTED_REFERENCE_RATE_PERCENT':100*expected,'DIFFERENCE_PP':100*(obs-expected),'CI_LOW_PP':result['ci_low_pp'],'CI_HIGH_PP':result['ci_high_pp'],'OBSERVED_EXPECTED_RATIO':obs/expected,'STATUS':'EXPLORATORY_ASSOCIATION','REFERENCE':'All other currencies, matched participant/FX strata','ESTIMAND':'Min-arm standardized currency-versus-rest risk difference; not legacy pooled03 residual','CAVEAT':'BIC/amount/party confounding unresolved; pointwise intervals; fixed support; not causal'})
            add('Currency '+currency+' Covered diagnostic',100*(nd.loc[treatment,'covered'].mean()-nd.loc[~treatment,'covered'].mean()),len(nd),100*raw,result['supported_treated_n']+result['supported_baseline_n'],100*(obs-expected),'Exact participant/FX shared strata; >=20 per arm; min-arm weights','percentage points','New final bridge standardizes observed and reference means on identical shared strata. Different estimand from legacy03 observed-minus-pooled-expectation; old diagnostic not mapped to final presentation.')
        self.save(pd.DataFrame(diagnostics),'currency_routing_final_diagnostics.csv')
        return self.save(pd.DataFrame(rows),'raw_vs_adjusted_same_support.csv')

    def diagnostics(self):
        held=self.previous('08_rule_validation','gap_heldout_calibration.csv');stability=self.previous('08_rule_validation','gap_parameter_stability.csv')
        dev=stability.loc[stability.split.eq('random_development')].iloc[0];full=stability.loc[stability.split.eq('full')].iloc[0]
        errors=held.development_model_error_pp
        legacy=self.read('outputs/tables/routing/advanced/gap_mechanism_model_comparison.csv').iloc[0]
        p=self.read('outputs/tables/routing/advanced/gap_mechanism_estimated_probabilities.csv').query("ROUTING_TYPE == 'ALL'").iloc[0].ESTIMATED_LINK_PROBABILITY
        summary=pd.DataFrame([
            {'MODEL':'LEGACY03_COMMON_IN_SAMPLE','FITTED_P':p,'CI_LOW':np.nan,'CI_HIGH':np.nan,'DEVELOPMENT_N':1048440,'VALIDATION_N':0,'HELDOUT_WEIGHTED_MAE_PP':np.nan,'HELDOUT_WEIGHTED_RMSE_PP':np.nan,'IN_SAMPLE_MAE_PP':legacy.WEIGHTED_MAE_PP,'IN_SAMPLE_RMSE_PP':legacy.WEIGHTED_RMSE_PP,'POPULATION_SCOPE':'Participants2-10; route×participant calibration;135 rows excluded; in-sample only'},
            {'MODEL':'FULL08_COMMON_IN_SAMPLE','FITTED_P':full.per_link_probability,'CI_LOW':full.ci_low,'CI_HIGH':full.ci_high,'DEVELOPMENT_N':int(full.n),'VALIDATION_N':0,'HELDOUT_WEIGHTED_MAE_PP':np.nan,'HELDOUT_WEIGHTED_RMSE_PP':np.nan,'IN_SAMPLE_MAE_PP':full.weighted_absolute_error_pp,'POPULATION_SCOPE':'All participants; pooled participant calibration; different grain from03'},
            {'MODEL':'FIXED_DEVELOPMENT08_HOLDOUT','FITTED_P':dev.per_link_probability,'CI_LOW':dev.ci_low,'CI_HIGH':dev.ci_high,'DEVELOPMENT_N':int(dev.n),'VALIDATION_N':int(held.n.sum()),'HELDOUT_WEIGHTED_MAE_PP':np.average(abs(errors),weights=held.n),'HELDOUT_WEIGHTED_RMSE_PP':np.sqrt(np.average(errors**2,weights=held.n)),'POPULATION_SCOPE':'Fixed development predictions on random validation; small upper-participant tail'}])
        summary['CAVEAT']='Consistent with an approximate per-link mechanism; not uniquely identified; model-based pointwise intervals; no external validation'
        self.save(summary,'gap_final_model_summary.csv')
        held=held.rename(columns={'participants':'PARTICIPANTS','n':'N','gaps':'GAP_N','observed_rate':'OBSERVED_RATE','development_model_rate':'PREDICTED_RATE','ci_low':'CI_LOW','ci_high':'CI_HIGH','small_group':'SPARSE_GROUP','development_model_error_pp':'ERROR_PP'})
        self.save(held[['PARTICIPANTS','N','GAP_N','OBSERVED_RATE','PREDICTED_RATE','CI_LOW','CI_HIGH','SPARSE_GROUP','ERROR_PP']],'gap_final_calibration.csv')
        endpoint_path,authority,pointer=resolve_endpoint(self.root,self.source_hash)
        for path in [self.root/'outputs/final_audit/current_audit.json',authority]:self.inputs[str(path.relative_to(self.root))]=digest(path)
        endpoint=self.read(endpoint_path)
        endpoint=endpoint.rename(columns=str.upper);endpoint['DIAGNOSTIC_ID']=endpoint.FAMILY+'::'+endpoint.GROUP
        self.save(endpoint,'endpoint_final_diagnostics.csv')
        adequate=endpoint.loc[~endpoint.EXPECTED_CELL_BELOW_5 & ~endpoint.SMALL_POPULATION]
        es=pd.DataFrame([{'CONDITIONAL_GROUPS':len(endpoint),'ADEQUATELY_SUPPORTED_GROUPS':len(adequate),'MAX_CRAMERS_V_SUPPORTED':adequate.CRAMERS_V.max(),'MAX_ABS_JOINT_MINUS_PRODUCT_PP_SUPPORTED':adequate.JOINT_DIFFERENCE_PP.abs().max(),'BH_SIGNIFICANT_SUPPORTED_GROUPS':int(adequate.P_VALUE_BH.lt(.05).sum()),'INTERPRETATION':'Observed endpoint mismatches are approximately consistent with independence overall and across adequately supported tested groups. Not proof of independence.','CAVEAT':'Overlapping diagnostic groups are not additive; sparse expected cells limit tests; pointwise rates and exploratory BH diagnostics'}])
        self.save(es,'endpoint_final_summary.csv')
        slow=self.read('outputs/tables/duration/slow_payment_rates_by_routing.csv').rename(columns={'TOTAL':'TOTAL_N'})
        slow['SLOW_COUNT_RANK']=slow.groupby('THRESHOLD_SECONDS').SLOW_COUNT.rank(method='min',ascending=False).astype(int)
        slow['SLOW_RATE_RANK']=slow.groupby('THRESHOLD_SECONDS').SLOW_RATE_PERCENT.rank(method='min',ascending=False).astype(int)
        slow['RATE_LEADER_FLAG']=slow.SLOW_RATE_RANK.eq(1);slow['VOLUME_LEADER_FLAG']=slow.SLOW_COUNT_RANK.eq(1)
        self.check('Nine slow route/threshold combinations',len(slow)==9 and not slow.duplicated(['ROUTING_TYPE','THRESHOLD_SECONDS']).any())
        self.check('Threshold denominators reconcile',slow.groupby('THRESHOLD_SECONDS').TOTAL_N.sum().eq(N).all())
        self.check('Slow rates correct',np.allclose(slow.SLOW_RATE_PERCENT,100*slow.SLOW_COUNT/slow.TOTAL_N))
        self.save(slow,'slow_payment_final.csv')
        for metric,filename,y in [('SLOW_RATE_PERCENT','slow_payment_rate_by_threshold.png','Slow rate (%)'),('SLOW_COUNT','slow_payment_volume_by_threshold.png','Slow transaction count')]:
            def draw(ax):
                for route,g in slow.groupby('ROUTING_TYPE'):ax.plot(g.THRESHOLD_SECONDS,g[metric],marker='o',label=route)
                ax.set_xticks([300,900,1800]);ax.legend()
            self.chart(filename,'Slow-payment rate and workload: route populations fixed at each threshold','Exploratory threshold (seconds)',y,draw,'Source n=1,048,575. Within-route denominators: Direct662,245; Indirect342,752; Covered43,578. Thresholds are not Swift SLAs; never sum across thresholds.')
        return summary,es,slow

    def evidence(self):
        estimands=self.estimands();nested=self.nested();profiles=self.profiles();bridge=self.same_support();diagnostics=self.diagnostics()
        self.rule_evidence()
        self.preserved();self.save(pd.DataFrame(self.checks),'final_evidence_validation.csv')
        manifest={'RUN_ID':self.run,'SOURCE_CSV_SHA256':self.raw_hash,'CLEANED_CSV_SHA256':self.source_hash,'EXCEL_SHA256':self.excel_hash,'CODE_SHA256':digest(Path(__file__)),'INPUT_HASHES':self.inputs,'TABLE_FILES':self.outputs,'TABLE_HASHES':{p:digest(self.root/p) for p in self.outputs},'CANONICAL_REGISTER_SHA256':digest(self.root/'outputs/rules/final_rule_register.csv'),'SCHEMA_VERSION':'2.0','GENERATED_AT':datetime.now(timezone.utc).isoformat()}
        dump(self.out/'evidence_manifest.json',manifest)
        return {'run_id':self.run,'nested_baselines':nested,'primary_estimands':estimands,'same_support':bridge,'diagnostics':diagnostics,'source_population':N,'checks_passed':len(self.checks)}

    def rule_evidence(self):
        """Presentation integration only: preserve Phase1 statistical statuses."""
        reg=self.reg.astype(object).copy();original_status=reg.set_index('RULE_ID').STATUS.copy()
        shutil.copy2(self.root/'outputs/rules/final_rule_register.csv',self.private/'final_rule_register.before.csv')
        estimate=pd.read_csv(self.out/'covered_indirect_duration_estimands.csv').iloc[0]
        mask=reg.RULE_ID.eq('F05')
        reg.loc[mask,'CONDITION']='Within217 matched participant/FX/currency/party strata; >=20 per arm'
        reg.loc[mask,'EFFECT_SIZE']=float(estimate.GEOMETRIC_RELATIVE_DIFFERENCE)
        reg.loc[mask,'EFFECT_UNIT']='Relative conditional geometric(duration+1) difference (fraction)'
        reg.loc[mask,'UNCERTAINTY']=f"Pointwise95% relative interval [{estimate.CI_LOW:.9f},{estimate.CI_HIGH:.9f}]; log interval [{estimate.LOG_CI_LOW:.9f},{estimate.LOG_CI_HIGH:.9f}]"
        reg.loc[mask,'EVIDENCE_SOURCE']='outputs/tables/final_evidence/covered_indirect_duration_estimands.csv'
        reg.loc[mask,'LIMITATIONS']='Primary min20 estimand only; earlier min1 point is sensitivity without valid singleton variance; no median/raw-second/causal claim; amount/BIC residual confounding remains.'
        reg.loc[reg.RULE_ID.eq('F11'),'RULE_NAME']='Currency-associated routing signals remain network-confounded'
        reg.loc[reg.RULE_ID.eq('F11'),'EVIDENCE_SOURCE']='outputs/tables/final_evidence/currency_routing_final_diagnostics.csv; outputs/tables/currency_party/advanced/bic_common_population_design.csv'
        reg.loc[reg.RULE_ID.eq('F11'),'LIMITATIONS']='Exploratory participant/FX-standardized currency-versus-rest diagnostics only; BIC frame2030/386330 (49pairs) is nonrepresentative; no broad independent currency effect. Phase1 extreme odds ratios are not portfolio rules.'
        reg.loc[reg.RULE_ID.eq('F12'),'RULE_NAME']='Direct residual long tail remains largely unexplained'
        self.check('No unsupported status promotion',reg.set_index('RULE_ID').STATUS.equals(original_status))
        reg.to_csv(self.root/'outputs/rules/final_rule_register.csv',index=False,encoding='utf-8-sig')
        self.inputs['outputs/rules/final_rule_register.csv']=digest(self.root/'outputs/rules/final_rule_register.csv')
        self.reg=reg
        charts={};sources={};chartmeta=[]
        def make(id,title,x,y,draw,caption,source):
            charts[id]=self.chart(id+'_evidence.png',title,x,y,draw,caption);sources[id]=source
            chartmeta.append({'RULE_ID':id,'SOURCE_TABLE':source,'SOURCE_CHART':charts[id],'POPULATION_AND_DENOMINATOR':caption,'UNIT':y,'QA_STATUS':'RENDERED_FOR_VISUAL_REVIEW','PRESENTATION_SCOPE':'Final scoped evidence only; no redundant EDA charts'})
        structural=self.previous('08_rule_validation','structural_rule_validation.csv').query("split == 'full'")
        def draw_architecture(ax):
            values=[int(structural.loc[structural.rule_id.eq(k),'exceptions'].iloc[0]) for k in ['S01','S02','S05']]
            ax.bar(['Direct→2','2→Direct','Non-direct→≥3'],values);ax.set_ylim(0,max(1,max(values)+1));ax.set_yticks([0,1])
            for i,value in enumerate(values):ax.annotate(str(value)+' exceptions',(i,value),xytext=(0,8),textcoords='offset points',ha='center')
        make('F01','Routing architecture: observed constraints, not three separate discoveries','Constraint','Exception count',draw_architecture,'Full n=1,048,575; directional scopes662,245 /662,245 /386,330; zero exceptions. Equivalent statements are merged.','outputs/tables/remaining/08_rule_validation/'+Path(self.previous_path('08_rule_validation')).name+'/structural_rule_validation.csv')
        bounds=self.read('outputs/tables/routing/advanced/fx_observed_upper_bounds.csv')
        def draw_bounds(ax):
            ax.plot(bounds.PARTICIPANT_COUNT,bounds.THEORETICAL_MAX_FX,'--',label='participants−1 bound')
            ax.scatter(bounds.PARTICIPANT_COUNT,bounds.MAX_OBSERVED_FX,label='observed maximum')
            for r in bounds.itertuples():ax.annotate('n='+str(r.RECORDS),(r.PARTICIPANT_COUNT,r.MAX_OBSERVED_FX),fontsize=7,xytext=(0,7),textcoords='offset points')
            ax.legend()
        make('F02','FX structural upper bound: full population, sparse tail retained','Participant count','FX conversion count',draw_bounds,'Full n=1,048,575; participant-specific n shown. Sparse upper groups do not always reach the bound; no records removed.','outputs/tables/routing/advanced/fx_observed_upper_bounds.csv')
        g=pd.read_csv(self.out/'gap_final_calibration.csv')
        def draw_gap(ax):
            ax.errorbar(g.PARTICIPANTS,g.OBSERVED_RATE*100,yerr=[(g.OBSERVED_RATE-g.CI_LOW)*100,(g.CI_HIGH-g.OBSERVED_RATE)*100],fmt='o',label='Observed / Wilson95%')
            ax.plot(g.PARTICIPANTS,g.PREDICTED_RATE*100,'--',label='Fixed development model')
            sparse=g.SPARSE_GROUP;ax.scatter(g.loc[sparse,'PARTICIPANTS'],g.loc[sparse,'OBSERVED_RATE']*100,c='red',marker='x',label='n<100')
            ax.set_xticks(g.PARTICIPANTS,[f'{r.PARTICIPANTS}\nn={r.N:,}' for r in g.itertuples()],rotation=45);ax.legend(fontsize=8)
        make('F03','Gap calibration: development fit evaluated without refitting on holdout','Participants / validation group n','Gap rate (%)',draw_gap,'Validation n=523,941; each group denominator is its N. Red crosses flag sparse tail; intervals are pointwise. Approximate mechanism, not identified truth.','outputs/tables/final_evidence/gap_final_calibration.csv')
        ep=pd.read_csv(self.out/'endpoint_final_diagnostics.csv');adequate=~ep.EXPECTED_CELL_BELOW_5 & ~ep.SMALL_POPULATION
        def draw_endpoint(ax):
            ax.scatter(ep.loc[adequate,'N'],ep.loc[adequate,'JOINT_DIFFERENCE_PP'],label='Adequate expected cells / n')
            ax.scatter(ep.loc[~adequate,'N'],ep.loc[~adequate,'JOINT_DIFFERENCE_PP'],marker='x',c='red',label='Sparse / unreliable chi-square')
            ax.set_xscale('log');ax.axhline(0,c='grey',ls='--');ax.legend(fontsize=8)
        make('F04','Conditional endpoint diagnostics: approximate consistency, not proof','Group n (logarithmic axis)','Joint minus marginal-product rate (pp)',draw_endpoint,'66 overlapping diagnostic groups from source n=1,048,575. Do not add group populations. Sparse groups retained and marked; BH results in source table.','outputs/tables/final_evidence/endpoint_final_diagnostics.csv')
        estimands=pd.read_csv(self.out/'covered_indirect_duration_estimands.csv')
        def draw_estimands(ax):
            ax.errorbar(100*estimate.GEOMETRIC_RELATIVE_DIFFERENCE,0,xerr=[[100*(estimate.GEOMETRIC_RELATIVE_DIFFERENCE-estimate.CI_LOW)],[100*(estimate.CI_HIGH-estimate.GEOMETRIC_RELATIVE_DIFFERENCE)]],fmt='o',label='PRIMARY min20 /95%CI')
            ax.scatter(100*estimands.iloc[1].GEOMETRIC_RELATIVE_DIFFERENCE,1,marker='D',facecolors='none',edgecolors='grey',label='Earlier sensitivity: no valid CI')
            ax.set_yticks([0,1],['217 strata','1777 strata']);ax.axvline(0,c='grey',ls='--');ax.legend(fontsize=8)
        make('F05','Covered versus Indirect: primary and earlier estimands stay separate','Conditional geometric(duration+1) relative difference (%)','Estimand / strata',draw_estimands,'PRIMARY n=38,017 Covered +264,393 Indirect; min-arm weights. Earlier n=43,430 +326,885. Not median change, causal delay or raw-second increase.','outputs/tables/final_evidence/covered_indirect_duration_estimands.csv')
        u=self.previous('05_currency_party','adjusted_duration_contrasts.csv').query("contrast == 'USD_vs_other' and min_cell_per_arm == 20").iloc[0]
        def draw_usd(ax):
            value=u.relative_geometric_duration_plus_one*100
            ax.errorbar(value,0,xerr=[[value-u.relative_ci_low*100],[u.relative_ci_high*100-value]],fmt='o');ax.axvline(0,c='grey',ls='--');ax.set_yticks([0],['USD vs other'])
        make('F06','USD adjusted duration contrast: fixed supported population','Relative geometric(duration+1) difference (%)','Contrast',draw_usd,'283 shared strata; supported n=175,439 USD +857,071 other. Adjusted route/participants/FX/amount-band/party; no causal/global-currency claim.',str(Path(self.previous_path('05_currency_party'))/'adjusted_duration_contrasts.csv'))
        fx=self.read('outputs/tables/duration/adjusted/fx_median_counterexamples_rechecked.csv');fx=fx.loc[fx.adequate]
        gap=self.read('outputs/tables/duration/adjusted/gap_median_counterexamples_rechecked.csv')
        for id,z,title in [('F07',fx,'Rejected: every adjacent FX increase has a positive median penalty'),('F08',gap,'Rejected: every path gap has a positive median penalty')]:
            counts=[int(z.difference_seconds.lt(0).sum()),int(z.difference_seconds.eq(0).sum()),int(z.difference_seconds.gt(0).sum())]
            make(id,title,'Observed conditional median direction','Comparison group count',lambda ax,c=counts:ax.bar(['Negative','Zero','Positive'],c),f'Full source n=1,048,575; {len(z)} qualifying comparisons, each >=100 per arm. Comparison populations overlap. Rejects universality, NOT every association or causal effect.','outputs/tables/duration/adjusted/'+('fx_median_counterexamples_rechecked.csv' if id=='F07' else 'gap_median_counterexamples_rechecked.csv'))
        recurrence=self.previous('06_anomaly_analysis','duplicate_label_recurrence_contrasts.csv').query("feature == 'repeat_within_86400_seconds'").iloc[0]
        def draw_recurrence(ax):
            ax.bar(['DUPLICATE_PAYMENT\nn=72','UNLABELED\nn=1,047,028'],[100*recurrence.target_rate,100*recurrence.baseline_rate]);ax.set_yscale('log')
        make('F09','Retrospective exact duplicate linkage, not fraud prediction','Observed label population','Within86400s recurrence rate (%; logarithmic axis)',draw_recurrence,'72/72 labeled duplicate rows versus18/1,047,028 unlabeled. Exact account-pair/amount/currency; future neighbors allowed; related rows challenge independence.',str(Path(self.previous_path('06_anomaly_analysis'))/'duplicate_label_recurrence_contrasts.csv'))
        token=self.previous('07_tokens','token_parser_coverage.csv')
        make('F10','Token formatting QA: recognize field openings; retain strict-block residuals','Side / delimiter','Unmatched strict-block delimiter count',lambda ax:ax.bar(['Ordering <','Beneficiary <','Ordering >','Beneficiary >'],[int(token.iloc[0].unparsed_opening_brackets),int(token.iloc[1].unparsed_opening_brackets),int(token.iloc[0].unparsed_closing_brackets),int(token.iloc[1].unparsed_closing_brackets)]),'n=1,048,575 token strings per side. Zero unrecognized field openings. Syntax coverage does not establish identity, semantics or fraud.',str(Path(self.previous_path('07_tokens'))/'token_parser_coverage.csv'))
        cur=pd.read_csv(self.out/'currency_routing_final_diagnostics.csv')
        def draw_currency(ax):
            y=np.arange(len(cur));ax.errorbar(cur.DIFFERENCE_PP,y,xerr=[cur.DIFFERENCE_PP-cur.CI_LOW_PP,cur.CI_HIGH_PP-cur.DIFFERENCE_PP],fmt='o')
            ax.set_yticks(y,[f'{r.CURRENCY} (source n={r.SOURCE_CURRENCY_N:,})' for r in cur.itertuples()]);ax.axvline(0,c='grey',ls='--')
        make('F11','Exploratory currency routing signals; bank-network confounding unresolved','Participant/FX-standardized currency-versus-rest difference (pp)','Prespecified currency',draw_currency,'Non-direct source n=386,330; min20/arm shared strata, min-arm weights, pointwise95%CI. BIC common frame only2030 rows /49pairs (0.5255%); no global independent currency rule.','outputs/tables/final_evidence/currency_routing_final_diagnostics.csv')
        residual=self.read('outputs/tables/duration/direct_tail/direct_adjustment_residual_metrics.csv');residual=residual.loc[residual.evaluation.str.contains('_to_')]
        def draw_tail(ax):
            for evaluation,z in residual.groupby('evaluation'):ax.plot(z.threshold_seconds,z.remaining_log_loss_fraction,marker='o',label=evaluation)
            ax.set_ylim(0,1.05);ax.axhline(1,c='grey',ls='--');ax.set_xticks([300,900,1800]);ax.legend(fontsize=7)
        make('F12','Direct tail: observable models leave nearly all baseline uncertainty','Exploratory slow threshold (seconds)','Heldout model/null log-loss ratio',draw_tail,'Direct population662,245; model sample150,000; evaluation n=74,625/75,000. Residual uncertainty is NOT a fraction of transactions with an identified cause.','outputs/tables/duration/direct_tail/direct_adjustment_residual_metrics.csv')
        matches=self.read('outputs/tables/duration/adjusted/common_support_fx_gap_comparisons.csv')
        z=matches.loc[matches.split.eq('full')&matches.outcome.eq('log_duration')&matches.contrast.str.startswith('FX')&matches.status.eq('ESTIMATED')]
        def draw_fx(ax):
            y=np.arange(len(z));ax.errorbar(z.adjusted_difference,y,xerr=[z.adjusted_difference-z.ci_low,z.ci_high-z.adjusted_difference],fmt='o');ax.set_yticks(y,z.contrast);ax.axvline(0,c='grey',ls='--')
        make('F13','Adjusted FX relationships differ by transition; no uniform speedup','Matched log1p(duration seconds) difference','Adjacent FX transition',draw_fx,'Source n=1,048,575; >=20 per arm; transition-specific retained N in source. Internal linear-model sample200,000; these contrasts are not causal and have different support.','outputs/tables/duration/adjusted/common_support_fx_gap_comparisons.csv')
        adjusted=self.read('outputs/tables/duration/adjusted/adjusted_fx_gap_effects.csv');r=adjusted.loc[adjusted.feature.eq('gap')&adjusted.outcome.eq('log_duration')&adjusted.split.eq('full')].iloc[0]
        q=matches.loc[matches.contrast.eq('gap 1 vs 0')&matches.outcome.eq('log_duration')&matches.split.eq('full')].iloc[0]
        def draw_weak(ax):
            vals=np.array([r.coefficient,q.adjusted_difference]);lo=np.array([r.ci_low,q.ci_low]);hi=np.array([r.ci_high,q.ci_high])
            ax.errorbar(vals,[0,1],xerr=[vals-lo,hi-vals],fmt='o');ax.set_yticks([0,1],['Adjusted OLS','Matched min20']);ax.axvline(0,c='grey',ls='--')
        make('F14','Gap adjusted duration association remains weak / unstable','Log1p(duration seconds) contrast','Specification',draw_weak,'OLS sample200,000; matched supported n=63,700 gap +840,184 no-gap (687strata). Both intervals include zero; this does not prove no effect.','outputs/tables/duration/adjusted/adjusted_fx_gap_effects.csv; outputs/tables/duration/adjusted/common_support_fx_gap_comparisons.csv')
        self.save(pd.DataFrame(chartmeta),'final_chart_quality_contract.csv')
        cards=[]
        for _,r in reg.iterrows():
            what=str(r.OUTCOME)
            if r.STATUS=='REJECTED_HYPOTHESIS':what='Rejected a universal positive observed median penalty. Did NOT reject every association, heterogeneous transition, or causal mechanism hypothesis.'
            if r.STATUS=='INSUFFICIENT_EVIDENCE':what='Unresolved: '+str(r.RULE_NAME)+'. No positive mechanism or exact-zero effect is established.'
            if r.RULE_ID=='F05':what=f'Within217 sufficiently supported matched strata, Covered showed {100*estimate.GEOMETRIC_RELATIVE_DIFFERENCE:.2f}% higher conditional geometric mean of duration+1 than Indirect under the specified matching framework.'
            if r.RULE_ID=='F11':what='Exploratory participant/FX-standardized routing differences exist; broad independent currency effects after BIC control remain unestablished. Extreme selected-frame odds ratios are not shown.'
            cards.append({'RULE_ID':r.RULE_ID,'RULE_NAME':r.RULE_NAME,'WHAT_HAPPENED':what,'UNDER_WHAT_CONDITIONS':r.CONDITION,'EFFECT_SIZE':r.EFFECT_SIZE,'RELIABILITY':str(r.UNCERTAINTY)+'; '+str(r.ROBUSTNESS),'ALTERNATIVE_EXPLANATIONS':r.LIMITATIONS,'WHY_IT_MATTERS':str(r.BUSINESS_PROBLEM)+'; proposed '+str(r.POTENTIAL_APPLICATION),'SUPPORT_N':r.SUPPORT_COUNT,'SCOPE_N':r.SCOPE_COUNT,'EFFECT_UNIT':r.EFFECT_UNIT,'STATUS':r.STATUS,'CONFIDENCE':r.CONFIDENCE,'SOURCE_TABLE':sources[r.RULE_ID],'SOURCE_CHART':charts[r.RULE_ID],'DASHBOARD_PAGE':r.DASHBOARD_PAGE,'CAVEAT':r.LIMITATIONS})
        cards=pd.DataFrame(cards);path=self.root/'outputs/rules/final_rule_evidence_cards.csv'
        if path.exists():shutil.copy2(path,self.private/(path.name+'.before'))
        cards.to_csv(path,index=False,encoding='utf-8-sig')
        text='# Final business evidence cards\n\nAll applications are proposed monitoring/QA/benchmarking uses, not demonstrated savings, speedups, fraud prevention or SLA improvements. Rejected and unresolved rows are not supported discoveries.\n\n'
        for r in cards.to_dict('records'):
            text+=f"## {r['RULE_ID']}: {r['RULE_NAME']}\n\n"+markdown([{'FIELD':k,'VALUE':v} for k,v in r.items()])+'\n'
        self.write_doc('final_rule_evidence_cards.md',text)

    def previous_path(self,phase):
        p=sorted((self.root/'outputs/tables/remaining'/phase).glob('*/completion.json'))[-1]
        return json.loads(p.read_text())['table_directory']

    def write_doc(self,name,text):
        path=self.root/'docs'/name
        if path.exists():shutil.copy2(path,self.private/(name+'.before'))
        path.write_text(text,encoding='utf-8')


class Release:
    """Versioned, immutable-on-success analytical release with filter guards."""
    def __init__(self,root):
        self.e=Integration(root);self.root=self.e.root;self.run=self.e.run
        self.evidence=self.root/'outputs/tables/final_evidence'
        manifest=json.loads((self.evidence/'evidence_manifest.json').read_text())
        # Release plumbing changes do not invalidate already approved analytical
        # evidence. Bind its original producer to the approved historical manifest.
        pointer_path=self.root/'dashboard/data/current_release.json'
        self.previous_pointer_sha256=digest(pointer_path) if pointer_path.exists() else None
        approved={}
        if pointer_path.exists():
            pointer=json.loads(pointer_path.read_text(encoding='utf-8'))
            approved=json.loads((self.root/pointer['RELEASE_PATH']/'release_manifest.json').read_text(encoding='utf-8'))
        evidence_hash=digest(self.evidence/'evidence_manifest.json')
        approved_evidence=approved.get('EVIDENCE_MANIFEST_SHA256')==evidence_hash and manifest['CODE_SHA256']==approved.get('EVIDENCE_PRODUCER_CODE_SHA256',approved.get('CODE_HASH_OR_COMMIT_IF_AVAILABLE'))
        self.e.check('Final evidence retains verified producer provenance',manifest['CLEANED_CSV_SHA256']==self.e.source_hash and (manifest['CODE_SHA256']==digest(Path(__file__)) or approved_evidence))
        self.e.check('Final evidence artifact hashes',all(digest(self.root/p)==h for p,h in manifest['TABLE_HASHES'].items()))
        self.e.check('Only canonical audited register',manifest['CANONICAL_REGISTER_SHA256']==digest(self.root/'outputs/rules/final_rule_register.csv'))
        self.evidence_manifest=manifest
        self.path=self.root/'dashboard/data/releases'/self.run;self.path.mkdir(parents=True,exist_ok=False)
        self.facts={};self.contracts=[];self.dimensions={};self.relationships=[];self.inventory=[];self.dictionary=[]
        self.classes={};self.ratios={}
        self.banned={'SOURCE_ROW_NUMBER','SOURCE_ROW','ORDERING_ACCOUNT','BENEFICIARY_ACCOUNT','ORDERING_BIC8','BENEFICIARY_BIC8','ORDERING_BIC','BENEFICIARY_BIC','PAIR','BIC8_PATH','ORDERING_TOKENS','BENEFICIARY_TOKENS','ORDERING_DETAILS','BENEFICIARY_DETAILS','EPOCH','EPOCH_SECONDS','DATETIME_UTC'}

    def read(self,name):return self.e.read('outputs/tables/final_evidence/'+name)

    def output(self,name,frame,role,load=True):
        self.e.check(name+' valid schema',frame.columns.is_unique and all(str(c).strip() for c in frame))
        self.e.check(name+' no direct identifiers',not bool(set(map(str.upper,map(str,frame.columns)))&self.banned))
        self.e.check(name+' finite numeric values',not frame.select_dtypes(include='number').isin([np.inf,-np.inf]).any().any())
        file=name+'.csv';frame.to_csv(self.path/file,index=False,encoding='utf-8-sig')
        self.inventory.append({'TABLE_NAME':name,'FILE':file,'ROLE':role,'LOAD_INTO_POWER_BI':load,'ROWS':len(frame),'COLUMNS':';'.join(frame.columns)})
        return frame

    def fact(self,name,frame,keys,dims,additive=(),ratios=None,scope='Mutually exclusive rows within this fact only',unit_note='',limitation='',source='09_dashboard_data_prep.ipynb',source_table=''):
        self.e.check(name+' unique grain',not frame.duplicated(keys).any())
        self.facts[name]=self.output(name,frame,'FACT')
        ratios=ratios or {};self.ratios[name]=ratios
        classes={}
        for c in frame:
            if c in keys or c in dims.values():continue
            if c in ratios:kind='WEIGHTED_ADDITIVE'
            elif c in additive:kind='ADDITIVE'
            elif any(w in c for w in ['MEDIAN','P25','P75','P90','P95','P99','IQR']):kind='NON_ADDITIVE'
            else:kind='FIXED_ESTIMAND'
            classes[c]=kind
            formula='Sum only within declared additive scope' if kind=='ADDITIVE' else ('Exact grain only; no median-of-medians or averaged percentiles' if kind=='NON_ADDITIVE' else ('SUM('+ratios[c][0]+')/SUM('+ratios[c][1]+') × '+str(ratios[c][2]) if kind=='WEIGHTED_ADDITIVE' else 'Select one fixed evidence row; never SUM/AVERAGE'))
            self.dictionary.append({'TABLE_NAME':name,'COLUMN':c,'METRIC_CLASS':kind,'UNIT_OR_SCOPE':unit_note or 'See field name and table contract','VALID_AGGREGATION':formula,'LIMITATION':scope})
        self.classes[name]=classes
        allowed=list(dims)
        all_dims=['Routing','Currency','Party','Threshold','Participant','FX','Rule','Date','Effect','EndpointGroup','Evaluation','TokenSide','QAMetric','QACohort','GapModel']
        self.contracts.append({'TABLE_NAME':name,'GRAIN':';'.join(keys),'PRIMARY_KEY_OR_GRAIN':';'.join(keys),'AVAILABLE_DIMENSIONS':';'.join(allowed) or 'NONE','MEASURES':';'.join(classes),'DENOMINATOR':scope,'ADDITIVE_MEASURES':';'.join(c for c,v in classes.items() if v=='ADDITIVE'),'NON_ADDITIVE_MEASURES':';'.join(c for c,v in classes.items() if v!='ADDITIVE'),'ALLOWED_SLICERS':';'.join(allowed) or 'NONE','DISALLOWED_SLICERS':';'.join(c for c in all_dims if c not in allowed),'SOURCE_NOTEBOOK':source,'SOURCE_TABLE':source_table,'LIMITATIONS':limitation+' '+scope,'UNIT_NOTE':unit_note,'EMPTY_SELECTION':'BLANK / unavailable, not a fabricated zero','FIXED_ESTIMAND_FILTERING':'Selecting evidence rows never refits models or changes their original support'})
        for dim,key in dims.items():
            assert key in frame and frame[key].notna().all(),(name,key)
            self.relationships.append({'DIMENSION':'Dim'+dim,'DIMENSION_KEY':key,'FACT':name,'FACT_KEY':key,'CARDINALITY':'ONE_TO_MANY','FILTER_DIRECTION':'SINGLE_DIMENSION_TO_FACT','ACTIVE':True})

    def build_facts(self):
        d=self.e.df
        overview=pd.DataFrame([{'PORTFOLIO_KEY':'GLOBAL','N':len(d),'AMOUNT_SUM_USD':d.amount.sum(),'DURATION_SUM_SECONDS':d.duration.sum(),'MEDIAN_DURATION_SECONDS':d.duration.median(),'P95_DURATION_SECONDS':d.duration.quantile(.95),'P99_DURATION_SECONDS':d.duration.quantile(.99),'LABELED_N':int(d.label.sum()),'GAP_N':int(d.gap.sum())}])
        self.fact('FactPortfolioOverview',overview,['PORTFOLIO_KEY'],{},['N','AMOUNT_SUM_USD','DURATION_SUM_SECONDS','LABELED_N','GAP_N'],scope='Global source n=1048575; no segment filters supported',unit_note='Transactions / USD / seconds',source_table='Canonical cleaned CSV aggregate')
        route=d.groupby('route',observed=True).agg(N=('source_row','size'),AMOUNT_SUM_USD=('amount','sum'),DURATION_SUM_SECONDS=('duration','sum'),MEDIAN_DURATION_SECONDS=('duration','median'),P90_DURATION_SECONDS=('duration',lambda x:x.quantile(.9)),P95_DURATION_SECONDS=('duration',lambda x:x.quantile(.95)),P99_DURATION_SECONDS=('duration',lambda x:x.quantile(.99)),LABELED_N=('label','sum')).reset_index().rename(columns={'route':'ROUTING_TYPE'})
        self.fact('FactRouteProfile',route,['ROUTING_TYPE'],{'Routing':'ROUTING_TYPE'},['N','AMOUNT_SUM_USD','DURATION_SUM_SECONDS','LABELED_N'],scope='Each route N; disjoint routes; exact-grain quantiles only',unit_note='Transactions / USD / seconds',source_table='Canonical cleaned CSV route aggregate')
        for name,file,key,dim in [('FactCurrencyProfile','currency_final_profile.csv','CURRENCY','Currency'),('FactPartyProfile','party_final_profile.csv','PARTY_PAIR','Party')]:
            z=self.read(file);ratios={c:('AMOUNT_SUM_USD','N',1) for c in ['MEAN_USD_AMOUNT']}
            ratios.update({c+'_RATE':(c+'_N','N',1) for c in ['DIRECT','INDIRECT','COVERED']})
            self.fact(name,z,[key],{dim:key},['N','AMOUNT_SUM_USD','DURATION_SUM_SECONDS','LABELED_N','DIRECT_N','INDIRECT_N','COVERED_N'],ratios,scope='Per-category N; SHARE_OF_ALL uses global1048575; route counts are measures, NOT route filter keys',unit_note='USD amounts; duration seconds; rates/shares fractions',limitation='Sparse category flag retained. Sum numerator/denominator for weighted means/rates; no average of stored summaries.',source='10_final_analytical_integration.ipynb',source_table='outputs/tables/final_evidence/'+file)
        a=self.read('currency_given_party.csv');b=self.read('party_given_currency.csv')
        composition=a.merge(b.drop(columns='N'),on=['CURRENCY','PARTY_PAIR'],validate='one_to_one')
        self.fact('FactCurrencyPartyComposition',composition,['CURRENCY','PARTY_PAIR'],{'Currency':'CURRENCY','Party':'PARTY_PAIR'},['N'],scope='P(currency|party) denominator is all currency rows within selected Party; P(party|currency) denominator is all Party rows within selected Currency',unit_note='Transactions; conditional probabilities fraction',limitation='Stored conditional denominators repeat: NEVER SUM. Use REMOVEFILTERS(Currency) or REMOVEFILTERS(Party) respectively when deriving ratios; stored probabilities exact cell only.',source='10_final_analytical_integration.ipynb',source_table='currency_given_party.csv; party_given_currency.csv')
        cube=d.groupby(['route','currency','party'],observed=True).agg(VISIBLE_N=('source_row','size'),AMOUNT_SUM_USD=('amount','sum'),DURATION_SUM_SECONDS=('duration','sum'),LABELED_N=('label','sum'),MEDIAN_DURATION_SECONDS=('duration','median'),P95_DURATION_SECONDS=('duration',lambda x:x.quantile(.95))).reset_index().rename(columns={'route':'ROUTING_TYPE','currency':'CURRENCY','party':'PARTY_PAIR'})
        visible=cube.loc[cube.VISIBLE_N.ge(20)].copy();suppressed=int(cube.loc[cube.VISIBLE_N.lt(20),'VISIBLE_N'].sum())
        visible['MEAN_DURATION_SECONDS']=visible.DURATION_SUM_SECONDS/visible.VISIBLE_N
        self.e.check('Cube suppression reconciles',int(visible.VISIBLE_N.sum())+suppressed==N and suppressed==4365)
        self.fact('FactRouteCurrencyParty',visible,['ROUTING_TYPE','CURRENCY','PARTY_PAIR'],{'Routing':'ROUTING_TYPE','Currency':'CURRENCY','Party':'PARTY_PAIR'},['VISIBLE_N','AMOUNT_SUM_USD','DURATION_SUM_SECONDS','LABELED_N'],ratios={'MEAN_DURATION_SECONDS':('DURATION_SUM_SECONDS','VISIBLE_N',1)} if 'MEAN_DURATION_SECONDS' in visible else {},scope='Only visible cells n>=20; denominator VISIBLE_N, not unknown full filtered population',unit_note='Transactions / USD / seconds',limitation='4365 suppressed rows are NOT in this fact and cannot be attributed to any category. Exact-cell percentiles only. Label visuals as visible cohort; filtered coverage unavailable.',source_table='Canonical cleaned CSV route/currency/party aggregate; small cells separate')
        coverage=pd.DataFrame([{'COVERAGE_KEY':'GLOBAL','TOTAL_SOURCE_N':N,'VISIBLE_CUBE_N':int(visible.VISIBLE_N.sum()),'SUPPRESSED_N':suppressed,'GLOBAL_COVERAGE_PERCENT':100*visible.VISIBLE_N.sum()/N,'FILTERED_COVERAGE_STATUS':'UNAVAILABLE: suppressed rows cannot be allocated after filters','POLICY':'Cells<20 omitted from sliceable fact; totals retained separately'}])
        self.suppression=coverage
        self.fact('FactSuppressionCoverage',coverage,['COVERAGE_KEY'],{},scope='Global coverage only; cannot filter by route/currency/party',unit_note='Transactions; global percent',limitation='Do not show this global coverage as selected-category coverage.',source_table='09 suppression accounting')
        joint=self.e.read('outputs/tables/routing/routing_participant_fx.csv').rename(columns={'PARTICIPANT_COUNT':'PARTICIPANTS','FX_COUNT':'FX','TRANSACTION_COUNT':'N'})
        self.fact('FactRoutingStructure',joint,['ROUTING_TYPE','PARTICIPANTS','FX'],{'Routing':'ROUTING_TYPE','Participant':'PARTICIPANTS','FX':'FX'},['N'],scope='Mutually exclusive route/participant/FX counts; source1048575',unit_note='Transaction count',source='03_bank_routing.ipynb',source_table='outputs/tables/routing/routing_participant_fx.csv')
        duration=self.e.read('outputs/tables/duration/duration_by_routing_and_participants.csv').rename(columns={'TRANSACTION_COUNT':'N'})
        self.fact('FactDurationRouteParticipant',duration,['ROUTING_TYPE','PARTICIPANTS'],{'Routing':'ROUTING_TYPE','Participant':'PARTICIPANTS'},['N'],scope='Each route×participant N; quantiles are non-additive exact-grain summaries',unit_note='Duration seconds; transaction N',source='04_payment_duration.ipynb',source_table='outputs/tables/duration/duration_by_routing_and_participants.csv')
        calibration=self.read('gap_final_calibration.csv')
        self.fact('FactGapCalibration',calibration,['PARTICIPANTS'],{'Participant':'PARTICIPANTS'},['N','GAP_N'],ratios={'OBSERVED_RATE':('GAP_N','N',1)},scope='Validation n523941 partitioned by participants; fixed development model predictions',unit_note='Rates fractions; residual percentage points',limitation='No route/currency/date keys. Prediction/CI is fixed for its published group; n<100 flagged.',source='08_rule_validation.ipynb; 10 integration',source_table='gap_final_calibration.csv')
        gaps=self.read('gap_final_model_summary.csv')
        self.fact('FactGapModelSummary',gaps,['MODEL'],{'GapModel':'MODEL'},scope='One fixed model/scope per row; development/validation counts are not additive across overlapping models',unit_note='Per-link probability; model errors pp',source='03/08; 10 integration',source_table='gap_final_model_summary.csv')
        endpoints=self.read('endpoint_final_diagnostics.csv')
        self.fact('FactEndpointDiagnostics',endpoints,['DIAGNOSTIC_ID'],{'EndpointGroup':'DIAGNOSTIC_ID'},scope='One fixed tested conditional group; groups and families overlap, NEVER SUM their N',unit_note='Rates fractions; joint residual pp; Cramér V',source='Final audit conditional endpoint integration',source_table='endpoint_final_diagnostics.csv')
        slow=self.read('slow_payment_final.csv')
        self.fact('FactSlowPayments',slow,['ROUTING_TYPE','THRESHOLD_SECONDS'],{'Routing':'ROUTING_TYPE','Threshold':'THRESHOLD_SECONDS'},['TOTAL_N','SLOW_COUNT'],ratios={'SLOW_RATE_PERCENT':('SLOW_COUNT','TOTAL_N',100)},scope='REQUIRE exactly one threshold before totals; source1048575 repeats across thresholds',unit_note='Seconds thresholds; transaction counts; percent',limitation='Thresholds300/900/1800 are exploratory, not Swift SLAs. Rate/volume leaders differ.',source='04_payment_duration.ipynb; 10 integration',source_table='slow_payment_final.csv')
        nested=self.read('duration_nested_baselines.csv')
        self.fact('FactDurationNestedBaselines',nested,['MODEL'],{},scope='Fixed same heldout n50000 for every model; never SUM model counts or metrics',unit_note='R²; log1p(seconds) errors',limitation='M2 replaces M1 rather than nesting it; improvements are predictive not causal decomposition.',source='10_final_analytical_integration.ipynb',source_table='duration_nested_baselines.csv')
        bridge=self.read('raw_vs_adjusted_same_support.csv')
        self.fact('FactSameSupportEffects',bridge,['EFFECT_NAME'],{},scope='One fixed effect/estimand per row; row-specific units and overlapping scopes',unit_note='EFFECT_UNIT per row',limitation='Raw full/support-restricted/standardized means use different support and/or weights; do not SUM effects or claim all change is confounding.',source='10_final_analytical_integration.ipynb',source_table='raw_vs_adjusted_same_support.csv')
        effects=self.e.read('outputs/tables/duration/adjusted/adjusted_fx_gap_effects.csv')
        effects=effects.rename(columns={'feature':'FEATURE','split':'SPLIT','outcome':'OUTCOME','coefficient':'ESTIMATE','ci_low':'CI_LOW','ci_high':'CI_HIGH','model_n':'MODEL_N','effect_unit':'EFFECT_UNIT'})
        effects['EFFECT_ID']=effects.FEATURE+'::'+effects.OUTCOME+'::'+effects.SPLIT
        self.fact('FactAdjustedDurationEffects',effects,['EFFECT_ID'],{'Effect':'EFFECT_ID'},scope='One fixed coefficient/specification/split; MODEL_N repeats and cannot be summed',unit_note='Row-specific log1p(seconds) or log odds; exp coefficients have distinct geometric/odds interpretations',limitation='Select one effect/outcome/split for cards. Model fits do not respond to transaction slicers. Binary odds ratios are not probability ratios.',source='04C_duration_adjusted_robustness.ipynb',source_table='outputs/tables/duration/adjusted/adjusted_fx_gap_effects.csv')
        cur=self.read('currency_routing_final_diagnostics.csv')
        self.fact('FactCurrencyRoutingDiagnostics',cur,['CURRENCY'],{'Currency':'CURRENCY'},scope='Fixed participant/FX-standardized currency-versus-rest contrast on shared support; each currency row has different reference and weights',unit_note='Rates percent; risk difference/CI pp; observed/reference ratio',limitation='Currency filters select evidence rows, do not refit. Bank confounding unresolved. No extreme Phase1 BIC odds ratios released.',source='10_final_analytical_integration.ipynb',source_table='currency_routing_final_diagnostics.csv')
        bic=self.e.read('outputs/tables/currency_party/advanced/currency_before_after_bic_effects.csv')[['currency','support_n','source_currency_n','bic_coverage_percent','status']].rename(columns={'currency':'CURRENCY','support_n':'SUPPORTED_N','source_currency_n':'SOURCE_CURRENCY_N','bic_coverage_percent':'COVERAGE_PERCENT','status':'STATUS'})
        self.fact('FactCurrencyBICCoverage',bic,['CURRENCY'],{'Currency':'CURRENCY'},['SUPPORTED_N','SOURCE_CURRENCY_N'],ratios={'COVERAGE_PERCENT':('SUPPORTED_N','SOURCE_CURRENCY_N',100)},scope='Per-currency non-direct source and selected pair-frame counts; eight currencies only, not full network',unit_note='Transactions; percent',limitation='Global pair-frame2030/386330 (49pairs); selected frame nonrepresentative; all currency effects insufficient.',source='05B_currency_bic_robustness.ipynb',source_table='Phase1 currency BIC coverage; coefficients deliberately excluded')
        residual=self.e.read('outputs/tables/duration/direct_tail/direct_adjustment_residual_metrics.csv').query("evaluation.str.contains('_to_')",engine='python').rename(columns={'threshold_seconds':'THRESHOLD_SECONDS','evaluation':'EVALUATION'})
        residual['ROUTING_TYPE']='DIRECT'
        self.fact('FactDirectTailResidual',residual,['THRESHOLD_SECONDS','EVALUATION'],{'Routing':'ROUTING_TYPE','Threshold':'THRESHOLD_SECONDS','Evaluation':'EVALUATION'},scope='Fixed Direct-only holdout metric per threshold×evaluation; overlapping samples, NEVER SUM counts/losses',unit_note='Log loss/Brier/ratio; source Direct662245; model sample150000',limitation='Residual loss fraction is not fraction of unexplained transactions; no reconstructed cause.',source='04B_direct_long_tail.ipynb',source_table='outputs/tables/duration/direct_tail/direct_adjustment_residual_metrics.csv')
        dates=d[['epoch','duration','label']].copy();dates['DATE_UTC']=pd.to_datetime(dates.epoch,unit='s',utc=True).dt.strftime('%Y-%m-%d')
        daily=dates.groupby('DATE_UTC').agg(N=('duration','size'),DURATION_SUM_SECONDS=('duration','sum'),LABELED_N=('label','sum')).reset_index()
        self.fact('FactDailyTotals',daily,['DATE_UTC'],{'Date':'DATE_UTC'},['N','DURATION_SUM_SECONDS','LABELED_N'],scope='One UTC date; source1048575 across mutually exclusive dates',unit_note='Transactions; seconds',limitation='No route/currency/party keys. Date slicer cannot legitimately filter facts without dates.',source_table='Canonical source UTC date aggregate')
        duplicate=self.e.previous('06_anomaly_analysis','duplicate_label_recurrence_contrasts.csv')
        qr=[]
        for r in duplicate.itertuples():
            for cohort,n,k in [('DUPLICATE_PAYMENT',r.target_n,r.target_successes),('UNLABELED',r.baseline_n,r.baseline_successes)]:qr.append({'QA_METRIC':r.feature,'QA_COHORT':cohort,'N':n,'SUCCESS_N':k,'RECURRENCE_RATE':k/n})
        self.fact('FactDuplicateQA',pd.DataFrame(qr),['QA_METRIC','QA_COHORT'],{'QAMetric':'QA_METRIC','QACohort':'QA_COHORT'},['N','SUCCESS_N'],ratios={'RECURRENCE_RATE':('SUCCESS_N','N',1)},scope='REQUIRE exactly one QA_METRIC before totals; populations repeat across features; duplicate/unlabeled-only QA frame1047100',unit_note='Transactions; retrospective recurrence fraction',limitation='Unlabeled not verified normal; future neighbors allowed; not fraud accuracy.',source='06_anomaly_analysis.ipynb',source_table='duplicate_label_recurrence_contrasts.csv')
        tokens=self.e.previous('07_tokens','token_parser_coverage.csv').rename(columns={'side':'TOKEN_SIDE','n':'N_STRINGS'})
        self.fact('FactTokenParserQA',tokens,['TOKEN_SIDE'],{'TokenSide':'TOKEN_SIDE'},['N_STRINGS','blank_n','zero_parsed_tags_n','unparsed_opening_brackets','unparsed_closing_brackets','unrecognized_field_openings','literal_value_hit_n'],scope='1048575 strings per side; adding sides yields strings, not distinct transactions',unit_note='Token string counts / structural marker counts',limitation='Mean lengths/counts fixed per side; syntax not identity, semantics or incremental predictive value.',source='07_tokens.ipynb',source_table='token_parser_coverage.csv')
        reg=self.e.reg;cards=self.e.read('outputs/rules/final_rule_evidence_cards.csv')
        self.e.check('Evidence cards canonical rule identity',set(cards.RULE_ID)==set(reg.RULE_ID) and cards.RULE_ID.is_unique)
        extra=[c for c in cards if c not in reg or c=='RULE_ID']
        rulefact=reg.merge(cards[extra],on='RULE_ID',validate='one_to_one')
        self.fact('FactRuleEvidence',rulefact,['RULE_ID'],{'Rule':'RULE_ID'},scope='Disconnected rule evidence; statuses, units and populations differ; NEVER SUM support counts or count rejected/unresolved as supported discoveries',unit_note='Rule-specific EFFECT_UNIT; conditional support meaning',source_table='outputs/rules/final_rule_register.csv; final_rule_evidence_cards.csv')

    def build_dimensions(self):
        for rel in self.relationships:
            name,key=rel['DIMENSION'],rel['DIMENSION_KEY']
            values=self.facts[rel['FACT']][key]
            if name in self.dimensions:self.dimensions[name]=pd.concat([self.dimensions[name],pd.DataFrame({key:values})],ignore_index=True).drop_duplicates()
            else:self.dimensions[name]=pd.DataFrame({key:values}).drop_duplicates()
        for name,d in self.dimensions.items():
            key=list(d)[0];d=d.sort_values(key).reset_index(drop=True)
            self.e.check(name+' unique nonnull key',d[key].is_unique and d[key].notna().all())
            if name=='DimThreshold':d['INTERPRETATION']='Exploratory seconds cut-off, not Swift SLA'
            if name=='DimRule':
                info=self.e.reg[['RULE_ID','RULE_NAME','RULE_FAMILY','STATUS','DASHBOARD_PAGE']]
                d=d.merge(info,on='RULE_ID',validate='one_to_one')
                d['SUPPORTED_FINDING_FLAG']=d.STATUS.isin(['SUPPORTED_STRUCTURAL_RULE','STRONG_STATISTICAL_PATTERN','PLAUSIBLE_GENERATING_MECHANISM'])
                d['DISCOVERY_COUNT_CAVEAT']='Status counts are evidence categories; exploratory/rejected/unresolved are not supported discoveries; logical dependencies already merged.'
            self.dimensions[name]=self.output(name,d,'DIMENSION')
        for rel in self.relationships:
            dim=self.dimensions[rel['DIMENSION']];fact=self.facts[rel['FACT']];key=rel['FACT_KEY']
            joined=fact[[key]].merge(dim[[key]],on=key,how='left',validate='many_to_one',indicator=True)
            self.e.check(rel['FACT']+'→'+rel['DIMENSION']+' cardinality',len(joined)==len(fact) and joined._merge.eq('both').all())

    def validate_filter(self,table,dimensions):
        contract=next(c for c in self.contracts if c['TABLE_NAME']==table)
        allowed=set(contract['ALLOWED_SLICERS'].split(';'))-{'NONE'}
        if not set(dimensions)<=allowed:raise ValueError('Unsupported filter for '+table+': '+str(set(dimensions)-allowed))

    def aggregate(self,table,metric,rows,operation='sum'):
        frame=self.facts[table].loc[rows]
        if table=='FactSlowPayments' and frame.THRESHOLD_SECONDS.nunique()!=1:raise ValueError('Choose exactly one exploratory threshold')
        if table=='FactDuplicateQA' and frame.QA_METRIC.nunique()!=1:raise ValueError('Choose exactly one QA metric')
        kind=self.classes[table][metric]
        if operation=='mean':raise ValueError('Unweighted mean of summaries/rates is prohibited')
        if kind=='ADDITIVE' and operation=='sum':return frame[metric].sum(min_count=1)
        if kind=='WEIGHTED_ADDITIVE' and operation=='weighted':
            numerator,denominator,mult=self.ratios[table][metric]
            return mult*frame[numerator].sum()/frame[denominator].sum() if frame[denominator].sum()>0 else np.nan
        if kind in ['NON_ADDITIVE','FIXED_ESTIMAND'] and operation=='single' and len(frame)==1:return frame[metric].iloc[0]
        raise ValueError('Invalid aggregation of '+kind+' metric '+metric)

    def validate(self):
        self.e.check('Route totals',self.facts['FactRouteProfile'].N.sum()==N)
        self.e.check('Currency totals',self.facts['FactCurrencyProfile'].N.sum()==N)
        self.e.check('Party totals',self.facts['FactPartyProfile'].N.sum()==N)
        self.e.check('Routing joint totals',self.facts['FactRoutingStructure'].N.sum()==N)
        self.e.check('Duration joint totals',self.facts['FactDurationRouteParticipant'].N.sum()==N)
        self.e.check('UTC daily totals',self.facts['FactDailyTotals'].N.sum()==N)
        self.e.check('Conditional joint totals',self.facts['FactCurrencyPartyComposition'].N.sum()==N)
        self.e.check('Visible+suppressed counts',self.facts['FactRouteCurrencyParty'].VISIBLE_N.sum()+self.suppression.SUPPRESSED_N.iloc[0]==N)
        self.e.check('Canonical release rule identity',set(self.facts['FactRuleEvidence'].RULE_ID)==set(self.e.reg.RULE_ID))
        slow=self.facts['FactSlowPayments'];selected=slow.index[slow.THRESHOLD_SECONDS.eq(300)]
        self.e.check('Weighted slow rate guard computes correct rate',np.isclose(self.aggregate('FactSlowPayments','SLOW_RATE_PERCENT',selected,'weighted'),100*slow.loc[selected,'SLOW_COUNT'].sum()/N))
        tests=[('Median of medians blocked',lambda:self.aggregate('FactRouteProfile','MEDIAN_DURATION_SECONDS',slice(None),'sum')),
            ('Average of rates blocked',lambda:self.aggregate('FactSlowPayments','SLOW_RATE_PERCENT',selected,'mean')),
            ('Repeated threshold denominators blocked',lambda:self.aggregate('FactSlowPayments','TOTAL_N',slice(None),'sum')),
            ('Unweighted mean of means blocked',lambda:self.aggregate('FactCurrencyProfile','MEAN_USD_AMOUNT',slice(None),'mean')),
            ('Fixed effects cannot sum',lambda:self.aggregate('FactAdjustedDurationEffects','ESTIMATE',slice(None),'sum')),
            ('Daily route filter blocked',lambda:self.validate_filter('FactDailyTotals',['Routing'])),
            ('Filtered suppression allocation blocked',lambda:self.validate_filter('FactSuppressionCoverage',['Currency'])),
            ('Rules cannot filter payments',lambda:self.validate_filter('FactRouteProfile',['Rule']))]
        for name,test in tests:
            rejected=False
            try:test()
            except ValueError:rejected=True
            self.e.check(name,rejected)
        cube=self.facts['FactRouteCurrencyParty'];selected=cube.index[cube.CURRENCY.eq('USD')]
        self.e.check('Allowed cube currency filter preserves visible counts',self.aggregate('FactRouteCurrencyParty','VISIBLE_N',selected)==cube.loc[selected,'VISIBLE_N'].sum())
        self.e.preserved()

    def build(self):
        self.build_facts();self.build_dimensions();self.validate()
        contracts=pd.DataFrame(self.contracts);relations=pd.DataFrame(self.relationships);dictionary=pd.DataFrame(self.dictionary)
        self.output('dashboard_table_contract',contracts,'METADATA',False)
        self.output('dashboard_model_relationships',relations,'METADATA',False)
        self.output('data_dictionary',dictionary,'METADATA',False)
        self.output('release_validation',pd.DataFrame(self.e.checks),'VALIDATION',False)
        for filename in ['final_rule_register.csv','final_rule_evidence_cards.csv']:
            source=self.root/'outputs/rules'/filename;shutil.copy2(source,self.path/filename)
            self.inventory.append({'TABLE_NAME':filename[:-4],'FILE':filename,'ROLE':'CANONICAL_EVIDENCE_SNAPSHOT','LOAD_INTO_POWER_BI':False,'ROWS':len(pd.read_csv(source)),'COLUMNS':';'.join(pd.read_csv(source,nrows=0).columns)})
        self.output('release_table_inventory',pd.DataFrame(self.inventory),'METADATA',False)
        # Include metadata-output checks too, so the exported log and manifest
        # report the same completed validation population.
        pd.DataFrame(self.e.checks).to_csv(self.path/'release_validation.csv',index=False,encoding='utf-8-sig')
        for item in self.inventory:
            if item['TABLE_NAME']=='release_validation':item['ROWS']=len(self.e.checks)
            if item['TABLE_NAME']=='release_table_inventory':item['ROWS']=len(self.inventory)
        pd.DataFrame(self.inventory).to_csv(self.path/'release_table_inventory.csv',index=False,encoding='utf-8-sig')
        # Candidates never write the approved pointer, top-level compatibility
        # contract, or historical analytical documents. Promotion is separate.
        shutil.copy2(self.root/'docs/source_authority_statement.md',self.path/'source_authority_statement.md')
        chart_folder=self.path/'charts';chart_folder.mkdir()
        for path in (self.root/'outputs/charts/final_evidence').glob('*.png'):shutil.copy2(path,chart_folder/path.name)
        csvs=sorted(self.path.glob('*.csv'))
        try:commit=subprocess.run(['git','rev-parse','HEAD'],cwd=self.root,text=True,capture_output=True,check=True).stdout.strip()
        except Exception:commit=None
        report={'RUN_ID':self.run,'SOURCE_CSV_SHA256':self.e.raw_hash,'CLEANED_CSV_SHA256':self.e.source_hash,'EXCEL_SHA256':self.e.excel_hash,'CODE_HASH_OR_COMMIT_IF_AVAILABLE':digest(Path(__file__)),'GIT_COMMIT':commit,'GENERATED_AT':datetime.now(timezone.utc).isoformat(),'TABLE_FILES':[p.name for p in csvs],'TABLE_HASHES':{p.name:digest(p) for p in csvs},'SCHEMA_VERSION':'phase2-2.0','SOURCE_POPULATION':N,'EVIDENCE_MANIFEST_SHA256':digest(self.evidence/'evidence_manifest.json'),'SOURCE_ARTIFACT_HASHES':self.evidence_manifest['INPUT_HASHES'],'CANONICAL_RULE_REGISTER_SHA256':digest(self.root/'outputs/rules/final_rule_register.csv'),'CHART_HASHES':{p.name:digest(p) for p in chart_folder.glob('*.png')},'DECISION':'READY_FOR_POWER_BI_WITH_LIMITATIONS','LIMITATIONS':['Page4 exploratory and bank-confounded; F11 insufficient','Direct mechanism unresolved; F12 insufficient','No arbitrary cross-grain slicers; follow contract','4365 suppressed rows not attributable after filters','Adjusted effects fixed estimands; no causal inference','Local competition data only; publication not authorized'],'FACT_TABLES':list(self.facts),'DIMENSION_TABLES':list(self.dimensions),'VALIDATION_CHECKS_PASSED':len(self.e.checks)}
        report.update({'SCHEMA_VERSION':'phase2-2.1.1','RULE_COUNT':len(self.e.reg),'RELEASE_STATE':'CANDIDATE','EXPECTED_PREVIOUS_POINTER_SHA256':self.previous_pointer_sha256,'EVIDENCE_PRODUCER_CODE_SHA256':self.evidence_manifest['CODE_SHA256'],'CODE_HASHES':{p:digest(self.root/p) for p in ['src/phase2_release.py','src/release_verification.py','src/release_promotion.py','src/release_cleanup.py','src/phase1_analysis.py','src/remaining_analysis.py']}})
        report['FILES_SHA256']={p.relative_to(self.path).as_posix():digest(p) for p in sorted(self.path.rglob('*')) if p.is_file()}
        # This manifest describes a sealed candidate, never approval. No shared
        # approved state changes here, including when copying/hashing fails.
        dump(self.path/'release_manifest.json',report)
        return report

    def documents(self,report):
        """Publish current decisions while retaining superseded audit text in backups."""
        release=str(self.path.relative_to(self.root));reg=self.e.reg
        pages=[
            (1,'Payment Characteristics','READY','Portfolio, currency and party profiles','Full source1048575','Global overview has no transaction slicers','Use exact-grain quantiles; no synthesized cohort medians'),
            (2,'Routing Architecture','READY','F01/F02; routing structure fact','Full source1048575','Routing/Participant/FX only on joint structure fact','Equivalent structural statements remain one rule family'),
            (3,'Path Observability','READY_WITH_LIMITATIONS','F03/F04; heldout gap and66 endpoint diagnostics','Gap validation523941; endpoint overlapping groups','Participant only for gap; endpoint group only for endpoint evidence','Approximate mechanism; not proof of independence; sparse tail flagged'),
            (4,'Currency Routing Signals and Network Confounding','READY_WITH_LIMITATIONS','F11; all eight prespecified currency diagnostics and coverage','Non-direct386330; selected BIC frame2030/49pairs','Currency selects fixed evidence rows; no model refitting','Exploratory signal only; independent global currency effect unresolved'),
            (5,'What Is Associated with Payment Duration?','READY_WITH_LIMITATIONS','F05/F06/F07/F08/F13/F14; quantiles and seven baselines','Covered primary302410; nested heldout50000; adjusted sample200000','Model effects disconnected from transaction filters','No causal, raw-median or unique variance attribution'),
            (6,'The Slow-Payment Workload','READY_WITH_LIMITATIONS','Nine route/threshold rows; F12 Direct residual diagnostics','Source1048575; Direct662245; model sample150000','Exactly one Threshold; Routing where available; residual fixed evaluation','Cut-offs are not SLAs; Direct mechanism remains unexplained'),
            (7,'Retrospective Anomaly and Token QA','READY_WITH_LIMITATIONS','Path A: F09 duplicate recurrence; F10 token parser quality','Duplicate/unlabeled QA1047100; token1048575 strings per side','QA metric/cohort and token-side filters only','Retrospective supporting QA; no fraud accuracy, token semantics or new scam mechanism'),
            (8,'Reconstructed Rules and Business Implications','READY_WITH_LIMITATIONS','Audited22-column register;14 six-question evidence cards','Rule-specific mixed and overlapping populations','Disconnected Rule selector only','Separate six statuses; rejected/unresolved are not supported discoveries')]
        readiness=pd.DataFrame(pages,columns=['PAGE','PAGE_TITLE','READINESS','EVIDENCE_READY','POPULATION_AND_DENOMINATOR','ALLOWED_FILTERS_AND_INTERACTIONS','LIMITATIONS'])
        readiness['REMAINING_ACTION']='Implement Power BI visual measures and slicer interactions according to frozen contracts; construction not performed'
        readiness['RELEASE']=release
        readiness=readiness.rename(columns={'PAGE_TITLE':'TITLE','READINESS':'STATUS','POPULATION_AND_DENOMINATOR':'DENOMINATOR','ALLOWED_FILTERS_AND_INTERACTIONS':'ALLOWED_SLICERS','LIMITATIONS':'CAVEAT'})
        questions=['What payment characteristics shape the population?','Which participant and FX constraints hold?','How observable are payment paths and endpoints?','Which currency routing signals remain network-confounded?','Which observables are associated with duration?','Where are slow-payment rates and workloads concentrated?','What retrospective label/token QA is supported?','Which rules are supported, rejected or unresolved?']
        source_tables=['FactPortfolioOverview; FactCurrencyProfile; FactPartyProfile','FactRoutingStructure','FactGapCalibration; FactEndpointDiagnostics','FactCurrencyRoutingDiagnostics; FactCurrencyBICCoverage','FactDurationRouteParticipant; FactDurationNestedBaselines; FactSameSupportEffects; FactAdjustedDurationEffects','FactSlowPayments; FactDirectTailResidual','FactDuplicateQA; FactTokenParserQA','FactRuleEvidence']
        source_charts=['Not applicable: exact profile/KPI tables','F01_evidence.png; F02_evidence.png','F03_evidence.png; F04_evidence.png','F11_evidence.png','duration_nested_model_performance.png; F05_evidence.png; F06_evidence.png; F13_evidence.png; F14_evidence.png','slow_payment_rate_by_threshold.png; slow_payment_volume_by_threshold.png; F12_evidence.png','F09_evidence.png; F10_evidence.png','; '.join(self.e.reg.RULE_ID+'_evidence.png')+'; separate statuses']
        x_dims=['Currency / Party','Routing / Participant / FX','Participant / conditional diagnostic group','Prespecified currency','Route / Participant / model / fixed estimand','Route / Threshold / Evaluation','QA metric / cohort / token side','Rule ID / Status']
        y_metrics=['N / share / amount and duration quantiles','N / structural exceptions / FX bound','Observed versus predicted gap / joint residual','Standardized Covered risk difference and BIC coverage','Duration quantiles / heldout R2 / geometric-duration contrast','Slow count / slow rate / residual log-loss ratio','Recurrence rate / parser residual count','Effect size / uncertainty / support, each rule separately']
        units=['Transactions; USD; seconds; fractions','Transactions / participant count / FX count','Fractions; pp; Cramers V','Percentage points; coverage percent','Seconds; log1p(seconds); relative geometric(duration+1) fraction','Transactions; percent; seconds; loss ratio','Retrospective fraction / string marker count','Rule-specific units; never aggregate unlike effects']
        missing=['None for descriptive scope','None for observed structural scope','Unique generator identification and independence proof unavailable','Global independent currency effect after BIC control unavailable','Causal effects and external validation unavailable','Direct-delay mechanism unresolved','Scam mechanisms and incremental token prediction outside Path A','F11/F12 unresolved; rejected hypotheses remain rejected']
        readiness['BUSINESS_QUESTION']=questions;readiness['MAIN_FINDING']=readiness.EVIDENCE_READY
        readiness['EVIDENCE_STATUS']=readiness.STATUS;readiness['SOURCE_TABLE']=source_tables;readiness['SOURCE_CHART']=source_charts
        readiness['X_DIMENSION']=x_dims;readiness['Y_METRIC']=y_metrics;readiness['UNIT']=units
        readiness['DISALLOWED_SLICERS']='Every slicer absent from the corresponding fact contract; no automatic cross-fact filtering'
        readiness['BUSINESS_APPLICATION']=['Population monitoring','Structural QA','Observability monitoring','Exploratory routing/network review','Conditional duration benchmarking','Workload prioritization; no SLA claim','Retrospective supporting QA','Evidence-led monitoring proposals']
        readiness['MISSING_EVIDENCE']=missing
        required='PAGE TITLE STATUS BUSINESS_QUESTION MAIN_FINDING EVIDENCE_STATUS SOURCE_TABLE SOURCE_CHART X_DIMENSION Y_METRIC DENOMINATOR UNIT ALLOWED_SLICERS DISALLOWED_SLICERS CAVEAT BUSINESS_APPLICATION MISSING_EVIDENCE'.split()
        readiness=readiness[required+['REMAINING_ACTION','RELEASE']]
        self.e.write_doc('dashboard_readiness_matrix.md','# Final Phase 2 dashboard readiness\n\nReadiness means analytical inputs are ready for construction, not that Power BI has been built or tested. This current matrix supersedes prior Phase 1 page labels.\n\n'+markdown(readiness))
        issue_details=[('I05','RESOLVED_IN_RELEASE','Per-fact grain/filter contract; only dimension-to-fact joins; invalid filters tested'),('I06','RESOLVED','Only audited22-column canonical register;14 IDs and six statuses; legacy register deprecated'),('I07','RESOLVED','Canonical nine-row slow table and paired rate/volume charts retain threshold reversal'),('I08','RESOLVED_WITH_SCOPE','Primary217 strata +9.93546% has own CI; earlier1777 +12.03143% sensitivity has no CI'),('I09','RESOLVED','Seven same-split baselines; no tree or incremental R² causal attribution'),('I10','RESOLVED','Full currency/party mean, median, P75/P90/P95/P99/IQR and both conditional probabilities'),('I14','RESOLVED_WITH_SCOPE','Legacy03 excludes135 rows; full08 and fixed holdout523941 are separately labelled'),('I15','RESOLVED_WITH_LIMITATIONS','66 conditional endpoint groups integrated; approximate consistency not proven independence'),('I18','RESOLVED_WITH_SCOPE','Full raw, same-support raw and adjusted bridge; selection and reweighting explicitly distinguished'),('I19','RESOLVED_BY_RESTRICTED_CONTRACT','4365 rows globally reconciled, never category-allocated; filtered full coverage unknown; quantiles exact grain only'),('I20','RESOLVED_FOR_FINAL_RELEASE','Dedicated final charts replace legacy presentation; n, units, CIs and sparse caveats; no unequal-bin histogram claim'),('I21','RESOLVED','14 complete business evidence cards linked one-to-one to canonical rule IDs')]
        issues=pd.DataFrame(issue_details,columns=['ISSUE','PHASE2_STATUS','EVIDENCE_AND_SCOPE'])
        self.e.write_doc('phase2_issue_reassessment.md','# Phase 2 issue reassessment\n\n'+markdown(issues)+'\nI01/I03/I04 remain resolved within their Phase 1 investigation scope; their hypotheses are not promoted. I02 remains analytically limited:2030/386330 records,49 supported BIC pairs. F11 and F12 remain INSUFFICIENT_EVIDENCE. I11/I12/I13 are outside Path A supporting QA; no claim of completed scam-mechanism or incremental token explanation. I16 remains exploratory with pointwise intervals. Versioned content hashes and source-bound evidence address release provenance; historical notebooks are retained.\n')
        estimands=self.read('covered_indirect_duration_estimands.csv');nested=self.read('duration_nested_baselines.csv')
        currency=self.read('currency_final_profile.csv');party=self.read('party_final_profile.csv');slow=self.read('slow_payment_final.csv')
        gap=self.read('gap_final_model_summary.csv');endpoint=self.read('endpoint_final_summary.csv')
        statuses=self.e.reg.groupby('STATUS').size().rename('RULE_COUNT').reset_index()
        residual=self.facts['FactDirectTailResidual'].rename(columns=str.upper)
        contract_text='''# Dashboard model and measure contract

Use only FACT/DIMENSION rows marked LOAD_INTO_POWER_BI in release_table_inventory.csv. Never auto-detect relationships or create fact-to-fact relationships. The supplied relationship file permits one-to-many, single-direction dimension-to-fact filtering only. Facts of different grains must not be directly merged. Turn off interactions from a slicer to every visual whose fact contract does not allow it. Date does not filter undated facts. Rule selection is disconnected from payments.

For additive measures use SUM only inside declared scope. For rates use DIVIDE(SUM(success_n), SUM(denominator_n)), multiplying by100 only for percent fields. Require HASONEVALUE(DimThreshold[THRESHOLD_SECONDS]) for slow totals/rates; otherwise return BLANK. Require exactly one QA metric for duplicate recurrence totals. Never average stored rates, odds ratios, quantiles, medians or model coefficients. Use SELECTEDVALUE for one fixed evidence row and return BLANK for multiple rows. Quantiles are available only at the published grain; hidden visual category totals must return BLANK when more than one grain row is selected. A single visible source row is not evidence that a broader multi-category quantile has been recomputed.

For P(currency|party) compute selected joint N divided by joint N after REMOVEFILTERS(DimCurrency); for P(party|currency) remove DimParty instead. Do not sum repeated denominators. Stored conditional probabilities are single published cells only. These measures answer different questions and retain the conditioning label.

The visible cube excludes cells n<20. Label all its filtered visuals 'Visible cohort (cells n>=20)'. SUM(VISIBLE_N) is not the full filtered source denominator. Global4365 suppression is a disconnected coverage fact; never allocate these rows by category or display global coverage as filtered coverage. Global source medians and full route profiles are separate exact estimands. There is no synthesized SUPPRESSED category. Empty/unsupported selections show BLANK or 'Not available', never a fabricated zero.

Release validation executes valid weighted-rate and visible-count calculations and rejects incompatible slicers, multi-threshold totals, averaged rates, median recombination and summed fixed coefficients. Power BI UI enforcement remains an implementation requirement; no report has been built.
'''
        self.e.write_doc('dashboard_data_model_contract.md',contract_text)
        sections=[('Executive Summary',f'Decision: **{report["DECISION"]}**. Immutable local analytical release: `{release}`. All {report["VALIDATION_CHECKS_PASSED"]} release checks passed. No Power BI construction, public release, commit or push was performed. Readiness is conditional on enforcing the supplied contracts in the future report.'),
            ('Files Created / Modified','Created src/phase2_release.py, notebook/10_final_analytical_integration.ipynb, final evidence tables/charts, evidence cards, this report, issue reassessment and model contract. Rebuilt notebook/09_dashboard_data_prep.ipynb and updated canonical register plus final audit/readiness/checklists. Prior versions of overwritten outputs/docs are retained under outputs/phase2/. Versioned CSV/PNG inputs, contracts, inventory, dictionary, validations and provenance manifest reside in `'+release+'`. Fresh-kernel execution receipts are recorded under outputs/phase2/execution/; completion must be assessed from those receipts, not inferred from notebook creation.'),
            ('Final Rule Register Status',markdown(statuses)+f'\n22 columns,{len(self.e.reg)} unique rule IDs. F07/F08 remain REJECTED_HYPOTHESIS; F11/F12 remain INSUFFICIENT_EVIDENCE. Architecture equivalences remain F01; FX>=2 non-direct is a consequence of F02, not another independent discovery.'),
            ('Covered vs Indirect Final Estimand',markdown(estimands)+'\nPrimary effect is conditional geometric(duration+1), not raw median or causal delay. Original1777-stratum result is sensitivity only; its missing interval is not borrowed.'),
            ('Nested Duration Explanatory Results',markdown(nested)+'\nAll models use the same200000 sampled rows,150000 training and50000 heldout. M2 is an alternative to M1; incremental explanatory gains are predictive comparisons, not causal variance decomposition.'),
            ('Currency / Party Final Descriptive Evidence',f'{len(currency)} currency categories and {len(party)} party pairs each reconcile to1048575. Both conditional-probability directions sum to1 within their explicit conditioning groups. Full amount profiles include mean, median, P75/P90/P95/P99/IQR; duration is in seconds. Currency→Covered evidence remains exploratory with bank confounding; the2030-record BIC frame covers only0.525458% of386330 non-direct transactions. Extreme BIC-frame odds ratios are deliberately excluded from final presentation. See currency_routing_final_diagnostics.csv and raw_vs_adjusted_same_support.csv.'),
            ('Gap / Endpoint Diagnostic Integration',markdown(gap)+'\n'+markdown(endpoint)+'\nHeldout calibration uses fixed development predictions. Legacy03 and full08 differ in scope and grouping. Observed endpoint mismatches are approximately consistent with independence overall and across adequately supported tested groups; this is not proof of independence.'),
            ('Slow-Payment Final Narrative',markdown(slow)+f'\nDirect has the largest slow volume at all cut-offs. Rate leader changes from Covered at300 seconds to Indirect at900/1800. Direct adjusted holdout log-loss / null-loss fraction remains {residual.REMAINING_LOG_LOSS_FRACTION.min():.9f}–{residual.REMAINING_LOG_LOSS_FRACTION.max():.9f}; this is predictive loss, not fraction of unexplained payments. F12 has no established mechanism. Thresholds are analytical, not Swift SLAs.'),
            ('Business Evidence Cards',f'All{len(self.e.reg)} canonical IDs have six-question cards and source/chart mapping in outputs/rules/final_rule_evidence_cards.csv and docs/final_rule_evidence_cards.md. Applications are proposed monitoring/QA uses, with no invented savings or causal operational gains.'),
            ('Dashboard Data Model',f'{len(self.facts)} fact tables and {len(self.dimensions)} dimensions; one-to-many single-direction relationships only; separate fixed evidence, daily aggregates, cube, full profiles and global coverage. See release_table_inventory.csv, dashboard_model_relationships.csv and dashboard_data_model_contract.md.'),
            ('Filter Compatibility','Every fact has allowed/disallowed slicers, grain, denominator and source. Currency selects published fixed currency evidence; it never refits models. Date is restricted to daily facts. Rule selectors do not filter transactions. All unsupported interactions must be disabled during Power BI construction.'),
            ('Non-Additive Metric Protections','data_dictionary.csv classifies ADDITIVE, WEIGHTED_ADDITIVE, NON_ADDITIVE and FIXED_ESTIMAND fields. Averaged rates/medians, multiple-threshold totals and summed coefficients are rejected by executable release guards. Exact-grain display only for quantiles, model estimates and confidence intervals.'),
            ('Suppression Coverage','1044210 visible +4365 globally suppressed =1048575. Suppressed transactions are never allocated to route/currency/party. Filtered cube metrics describe visible cohorts only; full filtered coverage is unknown. Global coverage is a disconnected fact.'),
            ('Final Dashboard Page Readiness',markdown(readiness)),
            ('Remaining Analytical Limitations','F11 independent currency effect and F12 Direct mechanism remain unresolved. FX associations vary across transitions and support; gap association is weak and intervals include zero. No external validation, causal claim, Swift SLA, fraud accuracy or token incremental predictive value. Page7 uses Path A retrospective QA only. Raw CSV is the canonical computational source; organizer workbook is retained as delivery source with22 immaterial amount-precision differences, not exact equality. All three source hashes remain unchanged. Detailed Phase1 evidence is preserved.'),
            ('Final Decision',report['DECISION']+'\n\nPhase2 analytical integration is complete subject to successful fresh-kernel notebook receipts and independent release hash/contract verification. No remaining analytical blocker to constructing the restricted dashboard; enforcing UI measures and slicer compatibility is mandatory. Stop here; Power BI was not constructed.')]
        self.e.write_doc('phase2_final_integration_report.md','# Phase 2 final analytical integration report\n\n'+'\n\n'.join(f'## {i}. {name}\n\n{text}' for i,(name,text) in enumerate(sections,1)))
        update='# Phase 2 final integration — current decision\n\n'+report['DECISION']+'\n\nThis section supersedes prior readiness/integration statuses; historical evidence below is retained. See phase2_final_integration_report.md, phase2_issue_reassessment.md and dashboard_readiness_matrix.md. I01/I03/I04 are not reopened. I02/F11 and F12 remain analytically limited.\n\n'+markdown(issues)+'\n'
        for name in ['final_analytical_output_audit.md','missing_analysis_checklist.md','pre_powerbi_fix_list.md']:
            p=self.root/'docs'/name;old=p.read_text(encoding='utf-8')
            marker='<!-- PHASE2_CURRENT_END -->'
            if marker in old:old=old.split(marker,1)[1].lstrip()
            self.e.write_doc(name,update+'\n'+marker+'\n\n'+old)


def build_final_evidence(root):return Integration(root).evidence()


def build_dashboard_release(root):return Release(root).build()
