"""Independent read-only validation of a sealed release, with CLI receipts.

This module intentionally does not import the release builder or its checks.
It reads candidate files back from disk and recomputes invariants independently.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from release_cleanup import resolve_endpoint, ordered_row_hash

RULE_SCHEMA='RULE_ID RULE_FAMILY RULE_NAME CONDITION OUTCOME SUPPORT_COUNT SCOPE_COUNT SUPPORT_PERCENT EXCEPTION_COUNT EFFECT_SIZE EFFECT_UNIT COMPARISON_BASELINE UNCERTAINTY ADJUSTMENT_METHOD ROBUSTNESS LIMITATIONS EVIDENCE_SOURCE STATUS CONFIDENCE BUSINESS_PROBLEM POTENTIAL_APPLICATION DASHBOARD_PAGE'.split()
RULE_STATUSES={'SUPPORTED_STRUCTURAL_RULE','STRONG_STATISTICAL_PATTERN','PLAUSIBLE_GENERATING_MECHANISM','EXPLORATORY_ASSOCIATION','REJECTED_HYPOTHESIS','INSUFFICIENT_EVIDENCE'}


def validate_rules(rules,cards,manifest_count):
    if list(rules)!=RULE_SCHEMA:raise VerificationError('Canonical rule schema differs')
    if rules.RULE_ID.isna().any() or rules.RULE_ID.astype(str).str.strip().eq('').any() or not rules.RULE_ID.is_unique:raise VerificationError('Rule IDs must be unique and nonblank')
    if not set(rules.STATUS)<=RULE_STATUSES:raise VerificationError('Invalid rule status vocabulary')
    if not isinstance(manifest_count,int) or isinstance(manifest_count,bool) or len(rules)!=manifest_count:raise VerificationError('Manifest dynamic RULE_COUNT mismatch')
    if not cards.RULE_ID.is_unique or set(cards.RULE_ID)!=set(rules.RULE_ID):raise VerificationError('Evidence-card IDs differ from register')


def validate_nested(frame):
    references=['NONE','MODEL_0','MODEL_0','MODEL_2','MODEL_3','MODEL_4','MODEL_5']
    types=['BASELINE','NESTED_FROM_BASELINE','ALTERNATIVE_BASELINE']+['NESTED_EXTENSION']*4
    if list(frame.MODEL)!=[f'MODEL_{i}' for i in range(len(references))] or list(frame.REFERENCE_MODEL)!=references or list(frame.COMPARISON_TYPE)!=types:raise VerificationError('Invalid nested model reference semantics')
    if any(c in frame for c in ['INCREMENTAL_R2_VS_PREVIOUS','INCREMENTAL_MAE_IMPROVEMENT']):raise VerificationError('Legacy adjacent-model deltas remain')
    indexed=frame.set_index('MODEL')
    for row in frame.itertuples():
        if row.REFERENCE_MODEL=='NONE':
            if not pd.isna(row.DELTA_R2_VS_REFERENCE) or not pd.isna(row.DELTA_MAE_VS_REFERENCE):raise VerificationError('Baseline delta must be missing')
        else:
            ref=indexed.loc[row.REFERENCE_MODEL]
            if not np.isclose(row.DELTA_R2_VS_REFERENCE,row.R2_LOG_DURATION-ref.R2_LOG_DURATION,atol=1e-12) or not np.isclose(row.DELTA_MAE_VS_REFERENCE,ref.MAE_LOG_DURATION-row.MAE_LOG_DURATION,atol=1e-12):raise VerificationError('Reference delta arithmetic mismatch')


def technical_chart_qa(candidate,manifest,out):
    """Check image integrity only; semantic visual review remains pending."""
    candidate=Path(candidate);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    paths=[candidate/'charts'/name for name in manifest['CHART_HASHES']]
    if not paths:raise VerificationError('No PNG charts in manifest')
    canvas=Image.new('RGB',(1500,400*((len(paths)+2)//3)),'white');dimensions={}
    for i,path in enumerate(paths):
        if not path.is_file() or sha256(path)!=manifest['CHART_HASHES'][path.name]:raise VerificationError('Chart hash mismatch: '+path.name)
        with Image.open(path) as im:
            if im.format!='PNG' or min(im.size)<=0:raise VerificationError('Invalid PNG dimensions')
            dimensions[path.name]=list(im.size);im.verify()
        with Image.open(path) as im:
            thumb=im.convert('RGB');thumb.thumbnail((490,365));x=i%3*500;y=i//3*400
            canvas.paste(thumb,(x,y+20));ImageDraw.Draw(canvas).text((x+5,y+5),path.name,fill='black')
    canvas.save(out/'contact_sheet.png')
    result={'CONTACT_SHEET_GENERATED':True,'IMAGE_OPEN_CHECK':'PASSED','CHART_HASH_CHECK':'PASSED','VISUAL_REVIEW_STATUS':'PENDING_MANUAL_OR_AGENT_REVIEW','DIMENSIONS':dimensions,'CHART_HASHES':manifest['CHART_HASHES']}
    (out/'chart_qa.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return result


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


class VerificationError(ValueError):pass


def verify(root,candidate):
    root=Path(root).resolve();candidate=Path(candidate).resolve();checks=[]
    def check(name,condition):
        checks.append({'CHECK':name,'PASSED':bool(condition)})
        if not condition:raise VerificationError(name)
    check('Candidate is a direct release directory',candidate.parent==(root/'dashboard/data/releases').resolve())
    manifest_path=candidate/'release_manifest.json'
    check('Sealed manifest exists',manifest_path.is_file())
    m=json.loads(manifest_path.read_text(encoding='utf-8'))
    check('Candidate identity and state',m['RUN_ID']==candidate.name and m.get('RELEASE_STATE')=='CANDIDATE')
    required={'RUN_ID','SOURCE_CSV_SHA256','CLEANED_CSV_SHA256','EXCEL_SHA256','FILES_SHA256','CODE_HASHES','EVIDENCE_MANIFEST_SHA256','TABLE_HASHES','CHART_HASHES','TABLE_FILES','EXPECTED_PREVIOUS_POINTER_SHA256','RULE_COUNT'}
    check('Manifest required fields',required<=set(m))
    actual={p.relative_to(candidate).as_posix() for p in candidate.rglob('*') if p.is_file() and p!=manifest_path}
    check('Exact payload inventory without extras',actual==set(m['FILES_SHA256']))
    check('No release symlinks',not any(p.is_symlink() for p in candidate.rglob('*')))
    for name,value in m['FILES_SHA256'].items():
        path=candidate/name
        check('Payload safe path '+name,path.resolve().is_relative_to(candidate) and path.is_file())
        check('Payload hash '+name,sha256(path)==value)
    for name,value in m['CODE_HASHES'].items():
        check('Current release code '+name,sha256(root/name)==value)
    for name,value in [('data/raw/swift_payments_raw_export.csv',m['SOURCE_CSV_SHA256']),('data/cleaned/swift_payments_cleaned.csv',m['CLEANED_CSV_SHA256']),('data/raw/swift_umdac_datathon_2026_fictitious_payment_data.xlsx',m['EXCEL_SHA256'])]:
        check('Immutable source '+name,sha256(root/name)==value)
    evidence=root/'outputs/tables/final_evidence/evidence_manifest.json'
    check('Unchanged analytical evidence manifest',sha256(evidence)==m['EVIDENCE_MANIFEST_SHA256'])
    original=json.loads(evidence.read_text(encoding='utf-8'))
    check('Original analytical producer retained',original['CODE_SHA256']==m['EVIDENCE_PRODUCER_CODE_SHA256'])
    for name,value in original['TABLE_HASHES'].items():check('Unchanged evidence '+name,sha256(root/name)==value)
    for name,value in original['INPUT_HASHES'].items():check('Unchanged evidence input '+name,sha256(root/name)==value)
    check('CSV table inventory matches disk',set(m['TABLE_FILES'])=={p.name for p in candidate.glob('*.csv')}==set(m['TABLE_HASHES']))
    for name,value in m['TABLE_HASHES'].items():check('Table manifest hash '+name,sha256(candidate/name)==value==m['FILES_SHA256'][name])
    for name,value in m['CHART_HASHES'].items():check('Chart manifest hash '+name,sha256(candidate/'charts'/name)==value==m['FILES_SHA256']['charts/'+name])
    tables={p.stem:pd.read_csv(p) for p in candidate.glob('*.csv')}
    inventory=tables['release_table_inventory'];contract=tables['dashboard_table_contract'];relations=tables['dashboard_model_relationships'];dictionary=tables['data_dictionary']
    check('Complete unique inventory',inventory.FILE.is_unique and set(inventory.FILE)==set(m['TABLE_FILES']))
    for row in inventory.itertuples():
        z=tables[row.TABLE_NAME]
        check('Inventory rows '+row.TABLE_NAME,len(z)==row.ROWS)
        check('Inventory columns '+row.TABLE_NAME,';'.join(z.columns)==row.COLUMNS)
        check('Finite numbers '+row.TABLE_NAME,not z.select_dtypes(include='number').isin([np.inf,-np.inf]).any().any())
    facts=inventory.loc[inventory.ROLE.eq('FACT'),'TABLE_NAME'];dims=inventory.loc[inventory.ROLE.eq('DIMENSION'),'TABLE_NAME']
    check('Every fact has one contract',contract.TABLE_NAME.is_unique and set(contract.TABLE_NAME)==set(facts)==set(m['FACT_TABLES']))
    check('Dimension inventory matches manifest',set(dims)==set(m['DIMENSION_TABLES']))
    banned={'SOURCE_ROW_NUMBER','SOURCE_ROW','ORDERING_ACCOUNT','BENEFICIARY_ACCOUNT','ORDERING_BIC','BENEFICIARY_BIC','PAIR','BIC8_PATH','ORDERING_TOKENS','BENEFICIARY_TOKENS','EPOCH','EPOCH_SECONDS','DATETIME_UTC'}
    for row in contract.itertuples():
        z=tables[row.TABLE_NAME];keys=row.GRAIN.split(';')
        check('Unique nonnull grain '+row.TABLE_NAME,not z.duplicated(keys).any() and not z[keys].isna().any().any())
        check('No transaction identifiers '+row.TABLE_NAME,not set(map(str.upper,z.columns))&banned)
        measures=set(row.MEASURES.split(';'))
        check('Every measure classified '+row.TABLE_NAME,measures==set(dictionary.loc[dictionary.TABLE_NAME.eq(row.TABLE_NAME),'COLUMN']))
        allowed=set(row.ALLOWED_SLICERS.split(';'))-{'NONE'}
        actual_dims={name[3:] for name in relations.loc[relations.FACT.eq(row.TABLE_NAME),'DIMENSION']}
        check('Contract filter graph '+row.TABLE_NAME,allowed==actual_dims and not allowed&set(row.DISALLOWED_SLICERS.split(';')))
    check('Metric vocabulary',set(dictionary.METRIC_CLASS)<= {'ADDITIVE','WEIGHTED_ADDITIVE','NON_ADDITIVE','FIXED_ESTIMAND'})
    for row in relations.itertuples():
        check('Directed dimension relationship '+row.DIMENSION+' '+row.FACT,row.DIMENSION in set(dims) and row.FACT in set(facts) and row.CARDINALITY=='ONE_TO_MANY' and row.FILTER_DIRECTION=='SINGLE_DIMENSION_TO_FACT')
        dimension=tables[row.DIMENSION];fact=tables[row.FACT]
        check('Relationship key cardinality '+row.DIMENSION+' '+row.FACT,dimension[row.DIMENSION_KEY].is_unique and dimension[row.DIMENSION_KEY].notna().all() and fact[row.FACT_KEY].isin(dimension[row.DIMENSION_KEY]).all())
    n=1_048_575
    for name in ['FactRouteProfile','FactCurrencyProfile','FactPartyProfile','FactRoutingStructure','FactDurationRouteParticipant','FactDailyTotals','FactCurrencyPartyComposition']:
        check('Population reconciliation '+name,tables[name].N.sum()==n)
    check('Global portfolio population',tables['FactPortfolioOverview'].N.iloc[0]==n)
    cube=tables['FactRouteCurrencyParty'];coverage=tables['FactSuppressionCoverage'].iloc[0]
    check('Suppression accounting',cube.VISIBLE_N.ge(20).all() and cube.VISIBLE_N.sum()==coverage.VISIBLE_CUBE_N==1044210 and coverage.SUPPRESSED_N==4365 and coverage.TOTAL_SOURCE_N==n)
    check('No invented suppressed category',not cube[['ROUTING_TYPE','CURRENCY','PARTY_PAIR']].astype(str).apply(lambda s:s.str.contains('SUPPRESSED')).any().any())
    slow=tables['FactSlowPayments']
    check('Slow9 rows and denominators',len(slow)==9 and set(slow.THRESHOLD_SECONDS)=={300,900,1800} and slow.groupby('THRESHOLD_SECONDS').TOTAL_N.sum().eq(n).all())
    check('Slow rates recomputed',np.allclose(slow.SLOW_RATE_PERCENT,100*slow.SLOW_COUNT/slow.TOTAL_N))
    check('Slow rate leaders',list(slow.loc[slow.RATE_LEADER_FLAG].sort_values('THRESHOLD_SECONDS').ROUTING_TYPE)==['COVERED','INDIRECT','INDIRECT'])
    check('Direct slow volume leader',slow.loc[slow.VOLUME_LEADER_FLAG].ROUTING_TYPE.eq('DIRECT').all())
    joint=tables['FactCurrencyPartyComposition']
    check('Conditional denominators not synthesized',np.allclose(joint.P_CURRENCY_GIVEN_PARTY,joint.N/joint.PARTY_DENOMINATOR_N) and np.allclose(joint.P_PARTY_GIVEN_CURRENCY,joint.N/joint.CURRENCY_DENOMINATOR_N))
    check('Currency given Party normalizes',np.allclose(joint.groupby('PARTY_PAIR').P_CURRENCY_GIVEN_PARTY.sum(),1))
    check('Party given Currency normalizes',np.allclose(joint.groupby('CURRENCY').P_PARTY_GIVEN_CURRENCY.sum(),1))
    rules=tables['final_rule_register'];cards=tables['final_rule_evidence_cards']
    validate_rules(rules,cards,m['RULE_COUNT'])
    check('Canonical schema, IDs, statuses and dynamic rule count',True)
    status=rules.set_index('RULE_ID').STATUS
    check('Rejected and insufficient conclusions retained',status.F07==status.F08=='REJECTED_HYPOTHESIS' and status.F11==status.F12=='INSUFFICIENT_EVIDENCE')
    check('Canonical register snapshot exact',sha256(candidate/'final_rule_register.csv')==sha256(root/'outputs/rules/final_rule_register.csv')==m['CANONICAL_RULE_REGISTER_SHA256'])
    check('Evidence cards exactly1 per rule',cards.RULE_ID.is_unique and set(cards.RULE_ID)==set(rules.RULE_ID))
    for row in cards.itertuples():check('Card resolves immutable chart '+row.RULE_ID,Path(row.SOURCE_CHART).name in m['CHART_HASHES'])
    validation=tables['release_validation']
    check('Builder log agrees with manifest',len(validation)==m['VALIDATION_CHECKS_PASSED'] and validation.PASSED.eq(True).all())
    validate_nested(tables['FactDurationNestedBaselines']);check('Nested explicit references and deltas',True)
    artifact,authority,audit_pointer=resolve_endpoint(root,m['CLEANED_CSV_SHA256'])
    check('Canonical endpoint authority resolves',artifact.exists() and authority.exists())
    design=pd.read_csv(root/'outputs/tables/final_evidence/duration_nested_design.csv').iloc[0]
    sample=json.loads((root/'outputs/tables/duration/adjusted/fx_gap_model_sample_design.json').read_text(encoding='utf-8'))
    chunks=pd.read_csv(root/'data/cleaned/swift_payments_cleaned.csv',usecols=['SOURCE_ROW_NUMBER'],dtype={'SOURCE_ROW_NUMBER':'int64'},chunksize=100000)
    source_rows=pd.concat([chunk.SOURCE_ROW_NUMBER for chunk in chunks],ignore_index=True)
    reconstructed=source_rows.sample(n=sample['SAMPLE_N'],random_state=sample['SAMPLE_SEED'])
    check('Independent ordered sample identity',ordered_row_hash(reconstructed.to_numpy())==sample['SOURCE_ROW_HASH']==design.SOURCE_ROW_HASH==design.PHASE1_SOURCE_ROW_HASH and sample['SOURCE_HASH']==m['CLEANED_CSV_SHA256'] and bool(design.PHASE1_PHASE2_ROW_IDENTITY_MATCH))
    return {'STATUS':'PASSED','RUN_ID':m['RUN_ID'],'RELEASE_PATH':candidate.relative_to(root).as_posix(),'MANIFEST_SHA256':sha256(manifest_path),'VERIFIER_SHA256':sha256(Path(__file__)),'CHECKS_PASSED':len(checks),'CHECKS':checks,'VERIFIED_AT':datetime.now(timezone.utc).isoformat()}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--candidate',required=True);parser.add_argument('--receipt',required=True);args=parser.parse_args()
    root=Path(args.root).resolve();receipt=Path(args.receipt).resolve()
    if not receipt.is_relative_to(root/'outputs/phase2_1'):raise ValueError('Receipt must be in private Phase2.1 outputs')
    try:
        result=verify(root,args.candidate)
        manifest=json.loads((Path(args.candidate)/'release_manifest.json').read_text(encoding='utf-8'))
        result['TECHNICAL_CHART_QA']=technical_chart_qa(args.candidate,manifest,receipt.parent/receipt.stem)
    except Exception as error:
        result={'STATUS':'FAILED','ERROR_TYPE':type(error).__name__,'ERROR':str(error),'CANDIDATE':args.candidate,'VERIFIED_AT':datetime.now(timezone.utc).isoformat()}
    receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='CHECKS'}))
    return 0 if result['STATUS']=='PASSED' else 1


if __name__=='__main__':sys.exit(main())
