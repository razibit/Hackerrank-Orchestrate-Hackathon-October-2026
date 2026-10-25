"""Structural validation only; does not establish factual correctness of a prediction."""
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

FIELDS = ['case_id', 'deletion_status', 'steps_json']
STEP_FIELDS = {'step_no','phase','system_id','resource_id','operation','state','evidence_id'}
OPERATIONS = [
 ('FINDING','REPORT_REMAINING_RECORD','PRESENT'),
 ('FINDING','REPORT_EXPOSED_PII','PRESENT'),
 ('FINDING','REPORT_ACTIVE_DATA_FLOW','ACTIVE'),
 ('FINDING','REPORT_RESTORE_RISK','ACTIVE'),
 ('REMEDIATION','DISABLE_DATA_FLOW','DISABLED'),
 ('REMEDIATION','BLOCK_RESTORE','BLOCKED'),
 ('REMEDIATION','DELETE_RECORD','ABSENT'),
 ('REMEDIATION','REDACT_RECORD','REDACTED'),
 ('REMEDIATION','ANONYMIZE_RECORD','ANONYMIZED'),
 ('VERIFICATION','VERIFY_RECORD_ABSENT','ABSENT'),
 ('VERIFICATION','VERIFY_RECORD_PRESENT','PRESENT'),
 ('VERIFICATION','VERIFY_RECORD_REDACTED','REDACTED'),
 ('VERIFICATION','VERIFY_RECORD_ANONYMIZED','ANONYMIZED'),
 ('VERIFICATION','VERIFY_DATA_FLOW_DISABLED','DISABLED'),
 ('VERIFICATION','VERIFY_RESTORE_BLOCKED','BLOCKED'),
]
OP = {name:(phase,state,i) for i,(phase,name,state) in enumerate(OPERATIONS)}

def read_csv(path):
 csv.field_size_limit(16*1024*1024)
 with Path(path).open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f)
  if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
   raise ValueError(f'{path}: missing or duplicate header')
  rows=list(reader)
  if any(None in row or any(v is None for v in row.values()) for row in rows):
   raise ValueError(f'{path}: malformed CSV row')
  return reader.fieldnames,rows

def instant(value):
 t=datetime.fromisoformat(value.replace('Z','+00:00'))
 if t.tzinfo is None: raise ValueError('timestamp must include timezone')
 return t

def evidence_times(dataset):
 out={}
 for name,idcol,timecol in [('evidence_files.csv','file_id','captured_at'),
 ('system_activity.csv','activity_id','event_time'),('user_audit_log.csv','audit_id','event_time')]:
  for row in read_csv(Path(dataset)/name)[1]:
   key=row[idcol]
   if key in out: raise ValueError(f'duplicate evidence identifier: {key}')
   out[key]=instant(row[timecol])
 return out

def validate(rows,requests,times):
 errors=[]
 ids=[r['case_id'] for r in rows];expected=[r['case_id'] for r in requests]
 if len(set(expected))!=len(expected): errors.append('request IDs are not unique')
 if Counter(ids)!=Counter(expected): errors.append('case coverage does not exactly match requests')
 if ids!=sorted(ids): errors.append('rows are not sorted lexicographically by case_id')
 req={r['case_id']:r for r in requests}
 for row in rows:
  cid=row['case_id'];prefix=cid+': '
  if cid not in req: continue
  status=row['deletion_status']
  if status not in {'COMPLETE','INCOMPLETE','NOT_APPLICABLE'}:
   errors.append(prefix+'invalid deletion_status');continue
  try: steps=json.loads(row['steps_json'])
  except (ValueError,TypeError): errors.append(prefix+'invalid steps_json');continue
  if not isinstance(steps,list): errors.append(prefix+'steps_json must be an array');continue
  if status=='NOT_APPLICABLE':
   if steps: errors.append(prefix+'NOT_APPLICABLE requires []')
   continue
  if not steps: errors.append(prefix+'authorized case needs evidence-backed steps')
  keys=[];phases=set()
  cutoff=instant(req[cid]['audit_at'])
  for n,s in enumerate(steps,1):
   if not isinstance(s,dict) or set(s)!=STEP_FIELDS:
    errors.append(prefix+f'step {n} must contain exactly the seven fields');continue
   if type(s['step_no']) is not int or s['step_no']!=n: errors.append(prefix+f'step {n} numbering invalid')
   if any(not isinstance(s[k],str) for k in STEP_FIELDS-{'step_no'}):
    errors.append(prefix+f'step {n} string field invalid');continue
   if not s['system_id'] or not s['resource_id']: errors.append(prefix+f'step {n} missing system/resource')
   op=OP.get(s['operation'])
   if op is None: errors.append(prefix+f'step {n} unknown operation');continue
   phase,state,rank=op;phases.add(s['phase'])
   if (s['phase'],s['state'])!=(phase,state): errors.append(prefix+f'step {n} invalid phase/state')
   keys.append((rank,s['system_id'],s['resource_id']))
   if status=='COMPLETE' and phase!='VERIFICATION': errors.append(prefix+'COMPLETE permits verification only')
   needs_evidence=phase=='FINDING' or status=='COMPLETE'
   eid=s['evidence_id']
   if needs_evidence:
    if eid not in times: errors.append(prefix+f'step {n} missing/unknown evidence ID')
    elif times[eid]>cutoff: errors.append(prefix+f'step {n} evidence is after audit_at')
   elif eid!='': errors.append(prefix+f'step {n} future work must have empty evidence_id')
  if keys!=sorted(keys): errors.append(prefix+'step order violates operation/system/resource ordering')
  if status=='INCOMPLETE' and phases!={'FINDING','REMEDIATION','VERIFICATION'}:
   errors.append(prefix+'INCOMPLETE requires findings, remediation and verification')
 return errors
