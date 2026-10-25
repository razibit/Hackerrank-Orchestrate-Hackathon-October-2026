"""Validate a generated CSV against the published contract and time bounds."""
import argparse
from pathlib import Path
from contract import FIELDS,read_csv,evidence_times,validate

def main():
 root=Path(__file__).resolve().parents[2]
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('output',type=Path);p.add_argument('--dataset',type=Path,default=root/'dataset')
 p.add_argument('--requests',default='deletion_requests.csv')
 args=p.parse_args()
 header,rows=read_csv(args.output)
 errors=[] if header==FIELDS else ['incorrect output header or column order']
 if not errors:
  errors+=validate(rows,read_csv(args.dataset/args.requests)[1],evidence_times(args.dataset))
 if errors:
  for error in errors: print('ERROR:',error)
  raise SystemExit(1)
 print(f'PASS: {len(rows)} rows satisfy structural checks. Evidence relevance and policy correctness still require evaluation.')
if __name__=='__main__':main()
