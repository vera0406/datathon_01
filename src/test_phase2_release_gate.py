"""Focused cleanup regression tests; execute with the project virtual environment."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
import numpy as np
import pandas as pd
from PIL import Image
from release_cleanup import digest, write_json, ordered_row_hash, resolve_endpoint, update_marked_section
from release_verification import validate_rules, validate_nested, technical_chart_qa, VerificationError

ROOT=Path(__file__).resolve().parents[1]


class CleanupGateTests(unittest.TestCase):
    def test_legacy_execution_is_blocked_without_mutation(self):
        pointer=ROOT/'dashboard/data/current_release.json';before=pointer.read_bytes()
        result=subprocess.run([sys.executable,str(ROOT/'outputs/phase2/verify_release.py')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('Deprecated verifier',result.stderr)
        self.assertEqual(before,pointer.read_bytes())

    def test_active_logic_has_no_historical_release_literal(self):
        for name in ['phase2_release','release_verification','release_promotion','release_cleanup']:
            tree=ast.parse((ROOT/'src'/(name+'.py')).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Constant) and isinstance(node.value,str):self.assertIsNone(re.search(r'20\d{6}T\d{12}Z',node.value),name)

    def test_no_literal_rule_count_validation(self):
        tree=ast.parse((ROOT/'src/release_verification.py').read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Compare) and isinstance(node.left,ast.Call) and isinstance(node.left.func,ast.Name) and node.left.func.id=='len' and node.left.args and isinstance(node.left.args[0],ast.Name) and node.left.args[0].id=='rules':
                self.assertFalse(any(isinstance(x,ast.Constant) and isinstance(x.value,int) for x in node.comparators))

    def test_rule_count_accepts_added_rule(self):
        rules=pd.read_csv(ROOT/'outputs/rules/final_rule_register.csv');cards=pd.read_csv(ROOT/'outputs/rules/final_rule_evidence_cards.csv')
        new_rule=rules.iloc[[0]].copy();new_rule['RULE_ID']='QA_ADDITIONAL_RULE'
        new_card=cards.iloc[[0]].copy();new_card['RULE_ID']='QA_ADDITIONAL_RULE'
        rules=pd.concat([rules,new_rule],ignore_index=True);cards=pd.concat([cards,new_card],ignore_index=True)
        validate_rules(rules,cards,len(rules))
        with self.assertRaises(VerificationError):validate_rules(rules,cards,len(rules)-1)

    def test_rule_blank_duplicate_status_and_cards_rejected(self):
        rules=pd.read_csv(ROOT/'outputs/rules/final_rule_register.csv');cards=pd.read_csv(ROOT/'outputs/rules/final_rule_evidence_cards.csv')
        for column,value in [('RULE_ID',' '),('RULE_ID',rules.RULE_ID.iloc[1]),('STATUS','NOT_A_STATUS')]:
            z=rules.copy();z.loc[0,column]=value
            with self.assertRaises(VerificationError):validate_rules(z,cards,len(z))
        with self.assertRaises(VerificationError):validate_rules(rules,cards.iloc[1:],len(rules))

    def test_endpoint_pointer_resolves_and_checks_source_and_hash(self):
        source=json.loads((ROOT/'outputs/final_audit/current_audit.json').read_text(encoding='utf-8'))['SOURCE_HASH']
        artifact,authority,pointer=resolve_endpoint(ROOT,source)
        self.assertEqual(digest(artifact),pointer['CONDITIONAL_ENDPOINT_DIAGNOSTICS_SHA256']);self.assertTrue(authority.exists())
        with self.assertRaises(ValueError):resolve_endpoint(ROOT,'WRONG_SOURCE')
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs/phase2_1_1') as temp:
            root=Path(temp);p=root/'outputs/final_audit/current_audit.json';copy=dict(pointer)
            copy['CONDITIONAL_ENDPOINT_DIAGNOSTICS']='bad.csv';copy['AUDIT_MANIFEST']='manifest.json'
            (root/'bad.csv').write_text('corrupt',encoding='utf-8');write_json(p,copy)
            with self.assertRaises(ValueError):resolve_endpoint(root,source)

    def test_nested_reference_metadata_and_arithmetic(self):
        table=pd.read_csv(ROOT/'outputs/tables/final_evidence/duration_nested_baselines.csv',keep_default_na=False,na_values=[''])
        validate_nested(table)
        self.assertEqual(table.loc[table.MODEL.eq('MODEL_2'),'REFERENCE_MODEL'].iloc[0],'MODEL_0')
        z=table.copy();z.loc[z.MODEL.eq('MODEL_2'),'REFERENCE_MODEL']='MODEL_1'
        with self.assertRaises(VerificationError):validate_nested(z)
        z=table.copy();z.loc[z.MODEL.eq('MODEL_4'),'DELTA_R2_VS_REFERENCE']+=1
        with self.assertRaises(VerificationError):validate_nested(z)

    def test_cross_phase_ordered_sample_hash(self):
        phase1=json.loads((ROOT/'outputs/tables/duration/adjusted/fx_gap_model_sample_design.json').read_text(encoding='utf-8'))
        phase2=pd.read_csv(ROOT/'outputs/tables/final_evidence/duration_nested_design.csv').iloc[0]
        for key in ['SOURCE_HASH','SAMPLE_N','SAMPLE_SEED','SOURCE_ROW_HASH','MODEL_INPUT_VERSION','CREATED_BY']:self.assertIn(key,phase1)
        rows=pd.Series(np.arange(2,1048575+2,dtype=np.int64)).sample(n=phase1['SAMPLE_N'],random_state=phase1['SAMPLE_SEED'])
        self.assertEqual(ordered_row_hash(rows),phase1['SOURCE_ROW_HASH']);self.assertEqual(phase1['SOURCE_ROW_HASH'],phase2.SOURCE_ROW_HASH)
        self.assertEqual(phase2.SOURCE_ROW_HASH,phase2.PHASE1_SOURCE_ROW_HASH)
        self.assertNotEqual(ordered_row_hash(rows),ordered_row_hash(rows.iloc[::-1]))

    def test_missing_duplicate_or_reversed_markers_fail_without_mutation(self):
        start='<!-- START -->';end='<!-- END -->'
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs/phase2_1_1') as temp:
            path=Path(temp)/'report.md'
            for value in ['plain text',start+' only',end+' only',start+start+end,start+end+end,end+start]:
                path.write_text(value,encoding='utf-8');before=path.read_bytes()
                with self.assertRaises(ValueError):update_marked_section(path,start,end,'new')
                self.assertEqual(before,path.read_bytes())

    def test_marked_update_preserves_outside_text(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs/phase2_1_1') as temp:
            path=Path(temp)/'report.md';path.write_text('before\n<!-- START -->old<!-- END -->\nafter',encoding='utf-8')
            update_marked_section(path,'<!-- START -->','<!-- END -->','verified result')
            self.assertEqual(path.read_text(encoding='utf-8'),'before\n<!-- START -->\nverified result\n<!-- END -->\nafter')

    def test_automated_image_qa_remains_pending(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs/phase2_1_1') as temp:
            root=Path(temp);(root/'charts').mkdir();path=root/'charts/test.png';Image.new('RGB',(8,8),'white').save(path)
            result=technical_chart_qa(root,{'CHART_HASHES':{'test.png':digest(path)}},root/'qa')
            self.assertEqual(result['VISUAL_REVIEW_STATUS'],'PENDING_MANUAL_OR_AGENT_REVIEW')
            self.assertEqual(result['IMAGE_OPEN_CHECK'],'PASSED');self.assertTrue(result['CONTACT_SHEET_GENERATED'])
            self.assertEqual(result['DIMENSIONS']['test.png'],[8,8])

    def test_automated_qa_rejects_invalid_image(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs/phase2_1_1') as temp:
            root=Path(temp);(root/'charts').mkdir();path=root/'charts/bad.png';path.write_bytes(b'not an image')
            with self.assertRaises(Exception):technical_chart_qa(root,{'CHART_HASHES':{'bad.png':digest(path)}},root/'qa')

    def test_no_active_legacy_calls_or_report_replacement(self):
        legacy=(ROOT/'outputs/phase2/verify_release.py').read_text(encoding='utf-8-sig')
        self.assertIn('DEPRECATED',legacy);self.assertNotIn('.replace(',legacy)
        self.assertNotIn('visual_review_receipt',legacy)
        self.assertNotIn('Agent visually inspected',legacy)
        for name in ['phase2_release','release_promotion','release_verification']:
            source=(ROOT/'src'/(name+'.py')).read_text(encoding='utf-8')
            self.assertNotIn('outputs/phase2/verify_release.py',source)


if __name__=='__main__':unittest.main(verbosity=2)
