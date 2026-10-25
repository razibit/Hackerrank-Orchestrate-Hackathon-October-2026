import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path

def read(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    by={r['case_id']:r for r in rows}
    return rows,by

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--v10',type=Path,required=True)
    ap.add_argument('--v12',type=Path,required=True)
    ap.add_argument('--sample-size',type=int,default=32)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()
    r10,m10=read(a.v10); r12,m12=read(a.v12)
    ids10=set(m10); ids12=set(m12); common=sorted(ids10&ids12)
    only10=sorted(ids10-ids12); only12=sorted(ids12-ids10)
    changed=[]; case_rows=[]
    for cid in common:
        x=m10[cid]; y=m12[cid]
        sx=json.loads(x['steps_json']); sy=json.loads(y['steps_json'])
        status_same=x['deletion_status']==y['deletion_status']
        steps_same=sx==sy
        field_delta=0; missing10=missing12=0
        for i in range(max(len(sx),len(sy))):
            if i>=len(sx): missing10+=1
            elif i>=len(sy): missing12+=1
            else: field_delta+=sum(sx[i].get(k)!=sy[i].get(k) for k in set(sx[i])|set(sy[i]))
        case_rows.append(f"| {cid} | {'same' if status_same else 'changed'} | {len(sx)} | {len(sy)} | {'same' if steps_same else 'changed'} | {field_delta} | {missing10} | {missing12} |")
        if not status_same or not steps_same:
            changed.append(cid)
    h10=hashlib.sha256(a.v10.read_bytes()).hexdigest(); h12=hashlib.sha256(a.v12.read_bytes()).hexdigest()
    same_bytes=a.v10.read_bytes()==a.v12.read_bytes()
    lines=['# Direct v10 versus v12 prediction comparison','',
      'This comparison reads only the two prediction CSV files; sample labels are not loaded here. Public-sample scoring is documented in the separate detailed evaluation reports.','',
      f'- v10 coverage: {len(ids10)}/{a.sample_size} ({len(ids10)/a.sample_size:.2%}).',
      f'- v12 coverage: {len(ids12)}/{a.sample_size} ({len(ids12)/a.sample_size:.2%}).',
      f'- Same case IDs: {len(common)}/{len(ids10|ids12)}; v10-only: {len(only10)}; v12-only: {len(only12)}.',
      f'- Status changed for {sum(m10[c]["deletion_status"]!=m12[c]["deletion_status"] for c in common)}/{len(common)} common cases.',
      f'- Parsed step arrays changed for {len(changed)}/{len(common)} common cases.',
      f'- Byte-identical prediction files: {same_bytes}.',
      f'- v10 SHA-256: `{h10}`.', f'- v12 SHA-256: `{h12}`.', '',
      '| Case | Status | v10 steps | v12 steps | Parsed sequence | Field value deltas | Steps missing in v10 | Steps missing in v12 |',
      '|---|---|---:|---:|---|---:|---:|---:|', *case_rows, '',
      '## Cases present in only one run','',
      '- v10 only: '+(', '.join(only10) if only10 else 'none')+'.',
      '- v12 only: '+(', '.join(only12) if only12 else 'none')+'.','',
      '## Changed cases','',
      (', '.join(changed) if changed else 'None. Every common case has the same status and parsed step sequence in v10 and v12.')]
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'WROTE {a.report}; same_bytes={same_bytes}; common_cases={len(common)}; changed_cases={len(changed)}')
if __name__=='__main__': main()
