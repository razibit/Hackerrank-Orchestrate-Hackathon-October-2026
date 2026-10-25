import argparse, hashlib, json, sys
from collections import Counter
from pathlib import Path

def pct(n,d): return f"{n/d:.2%} ({n}/{d})" if d else f"N/A (0/{d})"
def key(step,fields): return tuple((k,json.dumps(step.get(k),sort_keys=True,ensure_ascii=False)) for k in fields)
def evaluate(rows, ids, gold_by, fields):
    status_ok=seq_ok=tp=pred_n=gold_n=field_ok=field_n=0
    cases=[]; gold_ops=Counter(); pred_ops=Counter(); field_ok_by=Counter(); field_n_by=Counter()
    for cid in sorted(ids):
        row=rows[cid]; gold=gold_by[cid]
        ps=json.loads(row['steps_json']); gs=json.loads(gold['steps_json'])
        status=(row['deletion_status']==gold['deletion_status']); order=(ps==gs)
        status_ok+=int(status); seq_ok+=int(order)
        gc=Counter(key(s,fields) for s in gs); pc=Counter(key(s,fields) for s in ps)
        hit=sum((gc&pc).values()); tp+=hit; pred_n+=len(ps); gold_n+=len(gs)
        for s in gs: gold_ops[s.get('operation','')]+=1
        for s in ps: pred_ops[s.get('operation','')]+=1
        for i in range(max(len(gs),len(ps))):
            field_n+=len(fields)
            for f in fields:
                field_n_by[f]+=1
                ok=i<len(gs) and i<len(ps) and gs[i].get(f)==ps[i].get(f)
                field_ok+=int(ok); field_ok_by[f]+=int(ok)
        cases.append({'case':cid,'status_ok':status,'sequence_ok':order,'gold_steps':len(gs),'pred_steps':len(ps),'step_tp':hit})
    op_tp=sum(min(gold_ops[o],pred_ops[o]) for o in set(gold_ops)|set(pred_ops))
    return {'status_ok':status_ok,'n':len(ids),'seq_ok':seq_ok,'tp':tp,'pred_n':pred_n,'gold_n':gold_n,'field_ok':field_ok,'field_n':field_n,'op_tp':op_tp,'pred_ops':pred_ops,'gold_ops':gold_ops,'field_ok_by':field_ok_by,'field_n_by':field_n_by,'cases':cases}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',required=True,type=Path); ap.add_argument('--dataset',required=True,type=Path)
    ap.add_argument('--baseline',required=True,type=Path); ap.add_argument('--candidate',required=True,type=Path)
    ap.add_argument('--baseline-label',default='v14'); ap.add_argument('--candidate-label',default='v15')
    ap.add_argument('--report',required=True,type=Path)
    a=ap.parse_args(); sys.path.insert(0,str(a.repo/'code'/'tools'))
    from contract import FIELDS,STEP_FIELDS,evidence_times,read_csv,validate
    hash_b=hashlib.sha256(a.baseline.read_bytes()).hexdigest(); hash_c=hashlib.sha256(a.candidate.read_bytes()).hexdigest()
    h_b,base=read_csv(a.baseline); h_c,cand=read_csv(a.candidate)
    req_h,req=read_csv(a.dataset/'sample_deletion_requests.csv'); req_by={r['case_id']:r for r in req}
    base_by={r['case_id']:r for r in base}; cand_by={r['case_id']:r for r in cand}
    problems=[]
    for label,header,rows,mapping in [(a.baseline_label,h_b,base,base_by),(a.candidate_label,h_c,cand,cand_by)]:
        if header!=FIELDS: problems.append(f'{label}: incorrect prediction header')
        if len(mapping)!=len(rows): problems.append(f'{label}: duplicate case IDs')
        if set(mapping)-set(req_by): problems.append(f'{label}: unknown request IDs')
        if not problems: problems.extend(f'{label}: {e}' for e in validate(rows,[req_by[c] for c in sorted(mapping)],evidence_times(a.dataset)))
    if problems: raise SystemExit('Contract validation failed before answer-label loading:\n'+'\n'.join(problems))
    # Public labels are opened only after both pre-existing prediction files pass validation.
    _,gold=read_csv(a.dataset/'sample_output.csv'); gold_by={r['case_id']:r for r in gold}
    common=set(base_by)&set(cand_by)&set(gold_by)
    fields=tuple(sorted(STEP_FIELDS))
    b=evaluate(base_by,common,gold_by,fields); c=evaluate(cand_by,common,gold_by,fields)
    def delta(metric):
        x=b[metric]/b['n'] if metric in ('status_ok','seq_ok') and b['n'] else (b[metric]/b['pred_n'] if metric=='tp' and b['pred_n'] else 0)
        y=c[metric]/c['n'] if metric in ('status_ok','seq_ok') and c['n'] else (c[metric]/c['pred_n'] if metric=='tp' and c['pred_n'] else 0)
        return (y-x)*100
    dpp=delta('tp')
    baseline_only=sorted(set(base_by)-common); candidate_only=sorted(set(cand_by)-common)
    gains=sum(cc['step_tp']>bb['step_tp'] for bb,cc in zip(b['cases'],c['cases']))
    losses=sum(cc['step_tp']<bb['step_tp'] for bb,cc in zip(b['cases'],c['cases']))
    same=sum(cc['step_tp']==bb['step_tp'] for bb,cc in zip(b['cases'],c['cases']))
    lines=['# Paired public-sample cross-evaluation: v14 vs v15','',
      'Both existing prediction files passed official schema and evidence-time validation before this script read `sample_output.csv`. No inference was run. Metrics below use only case IDs present in both files, so they are paired but still a selected subset.', '',
      f'- {a.baseline_label} coverage: {len(base)}/32; {a.candidate_label} coverage: {len(cand)}/32.',
      f'- Common scored cases: {len(common)}/32.',
      f'- {a.baseline_label}-only cases: {len(baseline_only)}; {a.candidate_label}-only cases: {len(candidate_only)}.',
      f'- {a.baseline_label} file SHA-256: `{hash_b}`.',f'- {a.candidate_label} file SHA-256: `{hash_c}`.','',
      '| Metric on shared cases | v14 | v15 | v15 minus v14 |','|---|---:|---:|---:|',
      f"| Status accuracy | {pct(b['status_ok'],b['n'])} | {pct(c['status_ok'],c['n'])} | {delta('status_ok'):+.2f} pp |",
      f"| Exact-step precision | {pct(b['tp'],b['pred_n'])} | {pct(c['tp'],c['pred_n'])} | {dpp:+.2f} pp |",
      f"| Exact-step recall | {pct(b['tp'],b['gold_n'])} | {pct(c['tp'],c['gold_n'])} | {(c['tp']/c['gold_n']-b['tp']/b['gold_n'])*100 if b['gold_n'] and c['gold_n'] else 0:+.2f} pp |",
      f"| Positional fields | {pct(b['field_ok'],b['field_n'])} | {pct(c['field_ok'],c['field_n'])} | {(c['field_ok']/c['field_n']-b['field_ok']/b['field_n'])*100 if b['field_n'] and c['field_n'] else 0:+.2f} pp |",
      f"| Exact ordered sequence | {pct(b['seq_ok'],b['n'])} | {pct(c['seq_ok'],c['n'])} | {delta('seq_ok'):+.2f} pp |",'',
      f"Exact-step TP changes by case: improved {gains}, regressed {losses}, unchanged {same} of {len(common)}.",'',
      '| Shared case | v14 status correct | v15 status correct | Gold steps | v14 predicted | v15 predicted | Exact-step TP v14 | Exact-step TP v15 | TP delta | Order v14 | Order v15 |','|---|---|---|---:|---:|---:|---:|---:|---:|---|---|']
    cb={x['case']:x for x in c['cases']}
    for x in b['cases']:
        y=cb[x['case']]
        lines.append(f"| {x['case']} | {'yes' if x['status_ok'] else 'no'} | {'yes' if y['status_ok'] else 'no'} | {x['gold_steps']} | {x['pred_steps']} | {y['pred_steps']} | {x['step_tp']} | {y['step_tp']} | {y['step_tp']-x['step_tp']:+d} | {'yes' if x['sequence_ok'] else 'no'} | {'yes' if y['sequence_ok'] else 'no'} |")
    lines+=['','## Operation differences on shared cases','','| Operation | Gold | v14 | v15 | v14 missing | v15 missing | v14 extra | v15 extra |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for op in sorted(set(b['gold_ops'])|set(b['pred_ops'])|set(c['pred_ops'])):
        g=b['gold_ops'][op]; bp=b['pred_ops'][op]; cp=c['pred_ops'][op]
        lines.append(f'| {op} | {g} | {bp} | {cp} | {max(0,g-bp)} | {max(0,g-cp)} | {max(0,bp-g)} | {max(0,cp-g)} |')
    lines+=['','## Interpretation','','This paired comparison distinguishes changes on the same cases from differences caused only by changing which cases resolved. It does not establish causal improvement or hidden-set performance. If few cases overlap, treat percentage-point deltas as weak evidence.']
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'WROTE {a.report}; common={len(common)}; v14_status={b["status_ok"]}/{b["n"]}; v15_status={c["status_ok"]}/{c["n"]}; errors=0')
if __name__=='__main__': main()
