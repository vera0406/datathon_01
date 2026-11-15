"""Verify a candidate in a separate process, then atomically approve its pointer."""
from pathlib import Path
from datetime import datetime,timezone
import json
import os
import subprocess
import sys
import tempfile
from release_verification import sha256


def verify_candidate(root,candidate):
    root=Path(root).resolve();candidate=Path(candidate).resolve()
    if Path(sys.executable).resolve()!=(root/'.venv/Scripts/python.exe').resolve():raise RuntimeError('Use the project virtual environment')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    receipt=root/'outputs/phase2_1/verification'/candidate.name/(stamp+'.json')
    result=subprocess.run([sys.executable,str(root/'src/release_verification.py'),'--root',str(root),'--candidate',str(candidate),'--receipt',str(receipt)],cwd=root,text=True,encoding='utf-8',capture_output=True)
    if result.returncode or not receipt.exists():raise ValueError('Independent verification rejected candidate: '+result.stdout.strip()+' '+result.stderr.strip())
    data=json.loads(receipt.read_text(encoding='utf-8'))
    if data.get('STATUS')!='PASSED':raise ValueError('Verification receipt is not PASSED')
    return receipt,data


def promote_release(root,candidate):
    root=Path(root).resolve();candidate=Path(candidate).resolve()
    data_dir=root/'dashboard/data';pointer=data_dir/'current_release.json';lock=data_dir/'.promotion.lock'
    if candidate.parent!=(data_dir/'releases').resolve():raise ValueError('Candidate must be a direct local release directory')
    token=None;temp_path=None
    try:
        # Cooperating promoters are serialized; stale or concurrent candidates
        # cannot silently overwrite an intervening approved version.
        token=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        os.write(token,str(os.getpid()).encode('ascii'));os.fsync(token)
        before=sha256(pointer) if pointer.exists() else None
        receipt,verified=verify_candidate(root,candidate)
        manifest_path=candidate/'release_manifest.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('EXPECTED_PREVIOUS_POINTER_SHA256')!=before:raise ValueError('Stale candidate: approved pointer changed since build')
        if verified['MANIFEST_SHA256']!=sha256(manifest_path):raise ValueError('Candidate manifest changed after verification')
        if verified['VERIFIER_SHA256']!=sha256(root/'src/release_verification.py'):raise ValueError('Verifier changed during promotion')
        # Keep old approval bytes before the single shared-state commit point.
        audit=root/'outputs/phase2_1/promotion'/manifest['RUN_ID'];audit.mkdir(parents=True,exist_ok=True)
        if pointer.exists():(audit/'previous_current_release.json').write_bytes(pointer.read_bytes())
        approval={'RUN_ID':manifest['RUN_ID'],'RELEASE_PATH':candidate.relative_to(root).as_posix(),'CONTRACT':(candidate/'dashboard_table_contract.csv').relative_to(root).as_posix(),'STATUS':'APPROVED','MANIFEST_SHA256':verified['MANIFEST_SHA256'],'VERIFICATION_RECEIPT':receipt.relative_to(root).as_posix(),'VERIFICATION_RECEIPT_SHA256':sha256(receipt),'PREVIOUS_POINTER_SHA256':before,'APPROVED_AT':datetime.now(timezone.utc).isoformat(),'CAVEAT':'Local verified analytical inputs; Power BI not constructed; enforce per-fact contracts'}
        fd,name=tempfile.mkstemp(prefix='.current_release.',suffix='.tmp',dir=data_dir);temp_path=Path(name)
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as stream:
            json.dump(approval,stream,indent=2);stream.flush();os.fsync(stream.fileno())
        # Recheck approved state immediately before replace, while holding lock.
        if (sha256(pointer) if pointer.exists() else None)!=before:raise ValueError('Approved pointer changed before atomic commit')
        os.replace(temp_path,pointer);temp_path=None
        return approval
    finally:
        if temp_path is not None:
            try:temp_path.unlink(missing_ok=True)
            except OSError:pass
        if token is not None:
            os.close(token)
            try:lock.unlink()
            except OSError:pass
