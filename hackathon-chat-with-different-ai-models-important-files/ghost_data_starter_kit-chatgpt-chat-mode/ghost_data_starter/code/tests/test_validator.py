import unittest
from code.tools.validate_output import OPS, PHASES, FIELDS
from code.tools.evaluate_samples import evaluate

class TestContract(unittest.TestCase):
    def test_operation_states_unique(self):
        all_ops = [op for entries in OPS.values() for op,_ in entries]
        self.assertEqual(len(all_ops),len(set(all_ops)))
        self.assertEqual(len(all_ops),15)
    def test_all_phases_supported(self):
        self.assertEqual(set(PHASES),set(OPS))
        self.assertEqual(len(FIELDS),7)
    def test_metrics_exact_case(self):
        s={'phase':'VERIFICATION','system_id':'a','resource_id':'b','operation':'VERIFY_RECORD_ABSENT','state':'ABSENT','evidence_id':'evidence_01'}
        result=evaluate({'case_a':('COMPLETE',[s])},{'case_a':('COMPLETE',[s])})
        self.assertEqual(result['exact_case_accuracy'],1.0)
        self.assertEqual(result['step_f1'],1.0)

if __name__=='__main__':
    unittest.main()

class TestFullValidator(unittest.TestCase):
    def make_dataset(self,dirpath):
        import csv
        from pathlib import Path
        d=Path(dirpath)
        def write(name,header,row):
            with (d/name).open('w',encoding='utf-8',newline='') as f:
                w=csv.writer(f);w.writerow(header);w.writerow(row)
        write('deletion_requests.csv', ['case_id','email','requested_at','reported_status','reported_at','audit_at','request_text'],
              ['case_001','test@example.test','2026-01-01T00:00:00Z','COMPLETE','2026-01-01T00:00:00Z','2026-01-02T00:00:00Z','Delete my account'])
        write('evidence_files.csv',['file_id','file_path','origin','captured_at'], ['evidence_01','a.txt','x','2026-01-01T00:00:00Z'])
        write('system_activity.csv',['activity_id','event_time'],['activity_01','2026-01-01T00:00:00Z'])
        write('user_audit_log.csv',['audit_id','event_time'],['audit_01','2026-01-01T00:00:00Z'])
        return d
    def test_valid_complete(self):
        import csv,json,tempfile
        from pathlib import Path
        from code.tools.validate_output import validate,HEADER
        with tempfile.TemporaryDirectory() as temp:
            d=self.make_dataset(temp)
            with (d/'output.csv').open('w',newline='',encoding='utf-8') as f:
                w=csv.writer(f);w.writerow(HEADER)
                step={'step_no':1,'phase':'VERIFICATION','system_id':'account_service','resource_id':'account_001',
                      'operation':'VERIFY_RECORD_ABSENT','state':'ABSENT','evidence_id':'evidence_01'}
                w.writerow(['case_001','COMPLETE',json.dumps([step])])
            errors,stats=validate(d/'output.csv',d)
            self.assertEqual(errors,[])
            self.assertEqual(stats['COMPLETE'],1)
    def test_future_evidence_rejected(self):
        import csv,json,tempfile
        from pathlib import Path
        from code.tools.validate_output import validate,HEADER
        with tempfile.TemporaryDirectory() as temp:
            d=self.make_dataset(temp)
            (d/'evidence_files.csv').write_text('file_id,file_path,origin,captured_at\nevidence_01,a.txt,x,2026-01-03T00:00:00Z\n')
            with (d/'output.csv').open('w',newline='',encoding='utf-8') as f:
                w=csv.writer(f);w.writerow(HEADER)
                step={'step_no':1,'phase':'VERIFICATION','system_id':'account_service','resource_id':'account_001',
                      'operation':'VERIFY_RECORD_ABSENT','state':'ABSENT','evidence_id':'evidence_01'}
                w.writerow(['case_001','COMPLETE',json.dumps([step])])
            errors,_=validate(d/'output.csv',d)
            self.assertTrue(any('newer than audit_at' in e for e in errors))
