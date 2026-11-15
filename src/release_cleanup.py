"""Provenance and metadata helpers for final cleanup; no new model specifications."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import tempfile
import numpy as np
import pandas as pd


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def write_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')


def safe_path(root,name):
    root=Path(root).resolve();path=(root/name).resolve()
    if not path.is_relative_to(root):raise ValueError('Artifact path escapes project')
    return path


def ordered_row_hash(rows):
    return hashlib.sha256(np.asarray(rows,dtype='<i8').tobytes()).hexdigest()


def reconstruct_phase1_sample(root):
    root=Path(root);source=root/'data/cleaned/swift_payments_cleaned.csv';source_hash=digest(source)
    design_path=root/'outputs/tables/duration/adjusted/adjusted_model_design.csv'
    design=pd.read_csv(design_path).iloc[0];n=int(design.model_sample_n);seed=int(design.seed)
    completion_path=sorted((root/'outputs/phase1/04C_duration_adjusted_robustness').glob('*/completion.json'))[-1]
    completion=json.loads(completion_path.read_text(encoding='utf-8'))
    # The module was edited after the original fit. Preserve both checksums;
    # do not pretend its current whole-file hash is the historical one.
    notebook_path=root/'notebook/04C_duration_adjusted_robustness.ipynb'
    notebook=json.loads(notebook_path.read_text(encoding='utf-8'))
    executed=[cell for cell in notebook['cells'] if cell['cell_type']=='code']
    if not executed or any(cell.get('execution_count') is None for cell in executed):raise ValueError('Historical Phase1 notebook execution evidence missing')
    if completion['source_hashes'][str(source.relative_to(root))]!=source_hash:raise ValueError('Phase1 source version mismatch')
    chunks=pd.read_csv(source,usecols=['SOURCE_ROW_NUMBER'],dtype={'SOURCE_ROW_NUMBER':'int64'},chunksize=100000)
    rows=pd.concat([chunk.SOURCE_ROW_NUMBER for chunk in chunks],ignore_index=True)
    if len(rows)!=int(design.source_n) or not np.array_equal(rows,np.arange(2,len(rows)+2)):raise ValueError('Phase1 source row order is not reconstructable')
    # Series and DataFrame use the same pandas sample index selection, with
    # the identical ordered population, sample size, and historical seed.
    sample=rows.sample(n=n,random_state=seed)
    result={'SOURCE_HASH':source_hash,'SAMPLE_N':n,'SAMPLE_SEED':seed,'SOURCE_ROW_HASH':ordered_row_hash(sample.to_numpy()),'MODEL_INPUT_VERSION':'phase1 compact_v1; ordered cleaned source; pandas.sample without replacement','CREATED_BY':'src/release_cleanup.py:reconstruct_phase1_sample','SOURCE_ROW_DTYPE':'<i8','RECONSTRUCTED_FROM_HISTORICAL_DESIGN':True,'PHASE1_ANALYSIS_CODE_SHA256':completion['analysis_code_sha256'],'CURRENT_PHASE1_MODULE_SHA256':digest(root/'src/phase1_analysis.py'),'HISTORICAL_MODULE_HASH_MATCHES_CURRENT':completion['analysis_code_sha256']==digest(root/'src/phase1_analysis.py'),'RECONSTRUCTION_LIMITATION':'Historical row-hash receipt was absent; reconstructed from preserved source order, executed notebook and historical sample-size/seed design. Original and current full-module hashes are recorded separately.','PHASE1_COMPLETION':str(completion_path.relative_to(root)),'PHASE1_COMPLETION_SHA256':digest(completion_path),'PHASE1_NOTEBOOK_SHA256':digest(notebook_path),'PHASE1_MODEL_DESIGN_SHA256':digest(design_path),'PANDAS_VERSION':pd.__version__}
    target=root/'outputs/tables/duration/adjusted/fx_gap_model_sample_design.json'
    if target.exists():
        existing=json.loads(target.read_text(encoding='utf-8'))
        if any(existing[k]!=result[k] for k in ['SOURCE_HASH','SAMPLE_N','SAMPLE_SEED','SOURCE_ROW_HASH']):raise ValueError('Canonical sample identity conflicts with reconstruction')
        return existing
    write_json(target,result);return result


def verify_phase2_sample(root,sample,source_hash,seed):
    path=Path(root)/'outputs/tables/duration/adjusted/fx_gap_model_sample_design.json'
    phase1=json.loads(path.read_text(encoding='utf-8'));actual=ordered_row_hash(sample.source_row.to_numpy())
    if phase1['SOURCE_HASH']!=source_hash or phase1['SAMPLE_N']!=len(sample) or phase1['SAMPLE_SEED']!=seed or phase1['SOURCE_ROW_HASH']!=actual:raise ValueError('Phase1 and Phase2 sample row identity mismatch')
    return {'SOURCE_ROW_HASH':actual,'PHASE1_SOURCE_ROW_HASH':phase1['SOURCE_ROW_HASH'],'PHASE1_PHASE2_ROW_IDENTITY_MATCH':True,'SOURCE_HASH':source_hash,'SAMPLE_IDENTITY_ARTIFACT_SHA256':digest(path)}


def bootstrap_endpoint_pointer(root):
    root=Path(root);evidence_path=root/'outputs/tables/final_evidence/evidence_manifest.json'
    evidence=json.loads(evidence_path.read_text(encoding='utf-8'))
    entries=[(name,value) for name,value in evidence['INPUT_HASHES'].items() if Path(name).name=='conditional_endpoint_diagnostics.csv']
    if len(entries)!=1:raise ValueError('Expected one approved endpoint diagnostic artifact')
    name,value=entries[0];artifact=safe_path(root,name)
    if digest(artifact)!=value:raise ValueError('Approved endpoint artifact hash mismatch')
    source=evidence['CLEANED_CSV_SHA256'];records={}
    for record in ['source_hashes_before.json','source_hashes_after.json']:
        path=artifact.parent/record;data=json.loads(path.read_text(encoding='utf-8'))
        if data[str(Path('data/cleaned/swift_payments_cleaned.csv'))]!=source:raise ValueError('Historical audit source version mismatch')
        records[str(path.relative_to(root))]=digest(path)
    run=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    authority=root/'outputs/final_audit/endpoint_authority'/run/'audit_manifest.json'
    manifest={'RUN_ID':artifact.parent.name,'SOURCE_HASH':source,'CONDITIONAL_ENDPOINT_DIAGNOSTICS':str(artifact.relative_to(root)),'CONDITIONAL_ENDPOINT_DIAGNOSTICS_SHA256':value,'SOURCE_HASH_RECORDS':records,'ORIGINAL_EVIDENCE_MANIFEST_SHA256':digest(evidence_path)}
    write_json(authority,manifest)
    pointer={k:manifest[k] for k in ['RUN_ID','SOURCE_HASH','CONDITIONAL_ENDPOINT_DIAGNOSTICS','CONDITIONAL_ENDPOINT_DIAGNOSTICS_SHA256']}
    pointer.update({'AUDIT_MANIFEST':str(authority.relative_to(root)),'AUDIT_MANIFEST_SHA256':digest(authority)})
    write_json(root/'outputs/final_audit/current_audit.json',pointer);return pointer


def resolve_endpoint(root,source_hash):
    root=Path(root);pointer=json.loads((root/'outputs/final_audit/current_audit.json').read_text(encoding='utf-8'))
    if pointer['SOURCE_HASH']!=source_hash:raise ValueError('Canonical endpoint source hash mismatch')
    artifact=safe_path(root,pointer['CONDITIONAL_ENDPOINT_DIAGNOSTICS']);authority=safe_path(root,pointer['AUDIT_MANIFEST'])
    if not artifact.is_file() or digest(artifact)!=pointer['CONDITIONAL_ENDPOINT_DIAGNOSTICS_SHA256']:raise ValueError('Canonical endpoint artifact hash mismatch')
    if not authority.is_file() or digest(authority)!=pointer['AUDIT_MANIFEST_SHA256']:raise ValueError('Canonical endpoint audit manifest hash mismatch')
    manifest=json.loads(authority.read_text(encoding='utf-8'))
    for key in ['RUN_ID','SOURCE_HASH','CONDITIONAL_ENDPOINT_DIAGNOSTICS','CONDITIONAL_ENDPOINT_DIAGNOSTICS_SHA256']:
        if manifest[key]!=pointer[key]:raise ValueError('Canonical endpoint pointer and authority disagree: '+key)
    for name,value in manifest['SOURCE_HASH_RECORDS'].items():
        record=safe_path(root,name)
        if digest(record)!=value:raise ValueError('Audit source-hash record changed')
        if json.loads(record.read_text(encoding='utf-8'))[str(Path('data/cleaned/swift_payments_cleaned.csv'))]!=source_hash:raise ValueError('Audit recorded a different source')
    return artifact,authority,pointer


def update_marked_section(path,start_marker,end_marker,replacement):
    path=Path(path);text=path.read_text(encoding='utf-8')
    if start_marker==end_marker or text.count(start_marker)!=1 or text.count(end_marker)!=1:raise ValueError('Require exactly one distinct start and end marker')
    start=text.index(start_marker)+len(start_marker);end=text.index(end_marker)
    if start>end:raise ValueError('Report markers are reversed or overlap')
    value=text[:start]+'\n'+replacement.rstrip()+'\n'+text[end:]
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'.',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as stream:stream.write(value);stream.flush();os.fsync(stream.fileno())
        os.replace(name,path)
    finally:
        if Path(name).exists():Path(name).unlink()
