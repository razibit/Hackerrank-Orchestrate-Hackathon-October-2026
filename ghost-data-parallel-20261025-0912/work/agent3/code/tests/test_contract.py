import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from contract import validate,instant
import json

class ContractTests(unittest.TestCase):
 def setUp(self):
  self.requests=[{'case_id':'synthetic_1','audit_at':'2026-09-01T00:00:00Z'}]
  self.times={'evidence_test':instant('2026-08-31T00:00:00Z')}
 def row(self,status='COMPLETE',steps=None):
  if steps is None:steps=[{'step_no':1,'phase':'VERIFICATION','system_id':'account_service',
   'resource_id':'synthetic_account','operation':'VERIFY_RECORD_ABSENT','state':'ABSENT','evidence_id':'evidence_test'}]
  return {'case_id':'synthetic_1','deletion_status':status,'steps_json':json.dumps(steps)}
 def test_valid_complete(self):self.assertEqual(validate([self.row()],self.requests,self.times),[])
 def test_non_deletion_has_no_steps(self):
  self.assertEqual(validate([self.row('NOT_APPLICABLE',[])],self.requests,self.times),[])
  self.assertTrue(validate([self.row('NOT_APPLICABLE')],self.requests,self.times))
 def test_reject_late_evidence(self):
  self.times['evidence_test']=instant('2026-09-02T00:00:00Z')
  self.assertTrue(any('after audit_at' in e for e in validate([self.row()],self.requests,self.times)))
 def test_reject_wrong_state(self):
  r=self.row();s=json.loads(r['steps_json']);s[0]['state']='PRESENT';r['steps_json']=json.dumps(s)
  self.assertTrue(validate([r],self.requests,self.times))
 def test_reject_missing_case(self):self.assertTrue(validate([],self.requests,self.times))
 def test_reject_wrong_order(self):
  r=self.row();s=json.loads(r['steps_json']);s[0]['resource_id']='z'
  t=dict(s[0],step_no=2,resource_id='a');r['steps_json']=json.dumps(s+[t])
  self.assertTrue(any('order' in e for e in validate([r],self.requests,self.times)))
if __name__=='__main__':unittest.main()
