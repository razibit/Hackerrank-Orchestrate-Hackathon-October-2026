"""Read-only inventory and starter checks; never generates predictions."""
import argparse
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path
from contract import read_csv,evidence_times,validate,FIELDS

def build_parser():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--dataset',type=Path,default=Path(__file__).resolve().parents[2]/'dataset')
 return parser

def main(argv=None):
 data=build_parser().parse_args(argv).dataset.resolve()
 expected={'deletion_requests.csv':518,'sample_deletion_requests.csv':32,
           'sample_output.csv':32,'evidence_files.csv':94}
 errors=[]
 for name in ['deletion_requests.csv','sample_deletion_requests.csv','sample_output.csv',
 'deletion_rules.csv','evidence_files.csv','user_identities.csv','user_audit_log.csv','system_activity.csv','output.csv']:
  header,rows=read_csv(data/name)
  print(f'{name}: {len(rows)} rows; columns={",".join(header)}')
  if name in expected and len(rows)!=expected[name]: errors.append(f'{name}: count differs from published snapshot')
 manifest=read_csv(data/'evidence_files.csv')[1]
 paths=[]
 for row in manifest:
  path=(data/row['file_path']).resolve()
  if not path.is_relative_to(data.resolve()):errors.append(f'{row["file_id"]}: path outside dataset')
  elif not path.is_file():errors.append(f'{row["file_id"]}: evidence file missing')
  paths.append(path)
 print('Evidence formats:',dict(sorted(Counter(p.suffix for p in paths).items())))
 samples=read_csv(data/'sample_output.csv')
 if samples[0]!=FIELDS:errors.append('sample header does not match contract')
 errors+=validate(samples[1],read_csv(data/'sample_deletion_requests.csv')[1],evidence_times(data))
 print('Sample label distribution:',dict(Counter(r['deletion_status'] for r in samples[1])))
 for module in ['pypdf','PIL','openai']:
  print(f'Optional module {module}:',bool(importlib.util.find_spec(module)))
 print('DataLab API key configured:',bool(os.environ.get('DATALAB_API_KEY','').strip()))
 for error in errors: print('ERROR:',error)
 if errors:raise SystemExit(1)
 print('PASS: files, counts, evidence paths and official sample contract validated. This preflight does not run inference.')
if __name__=='__main__':main()
