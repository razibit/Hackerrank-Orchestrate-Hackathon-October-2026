import argparse, csv, hashlib, json, sys
from collections import Counter
from pathlib import Path


def pct(n, d):
    return f"{n/d:.2%} ({n}/{d})" if d else f"N/A (0/{d})"

def canonical(step, fields):
    return tuple((key, json.dumps(step.get(key), sort_keys=True, ensure_ascii=False)) for key in fields)

def list_counter(counter, labels):
    return ", ".join(f"{labels.get(key, key)} x{count}" for key, count in sorted(counter.items()) if count) or "none"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo', required=True, type=Path)
    ap.add_argument('--dataset', required=True, type=Path)
    ap.add_argument('--predictions', required=True, type=Path)
    ap.add_argument('--report', required=True, type=Path)
    args=ap.parse_args()
    sys.path.insert(0, str(args.repo/'code'/'tools'))
    from contract import FIELDS, STEP_FIELDS, evidence_times, read_csv, validate

    pred_header, pred=read_csv(args.predictions)
    _, gold=read_csv(args.dataset/'sample_output.csv')
    _, requests=read_csv(args.dataset/'sample_deletion_requests.csv')
    gold_by={row['case_id']:row for row in gold}
    pred_by={row['case_id']:row for row in pred}
    request_by={row['case_id']:row for row in requests}
    predicted_ids=set(pred_by)
    matched_requests=[request_by[cid] for cid in predicted_ids if cid in request_by]
    contract_errors=[] if pred_header==FIELDS else ['incorrect predictions header']
    if len(pred_by)!=len(pred): contract_errors.append('duplicate prediction case IDs')
    if predicted_ids-set(gold_by): contract_errors.append('unknown prediction case IDs')
    if predicted_ids-set(request_by): contract_errors.append('prediction case ID has no matching request')
    contract_errors += validate(pred, matched_requests, evidence_times(args.dataset))

    fields=tuple(sorted(STEP_FIELDS))
    score_ids=sorted(predicted_ids & set(gold_by))
    all_ids=sorted(gold_by)
    missing_ids=sorted(set(all_ids)-predicted_ids)
    status_ok=0; sequence_ok=0; exact_tp=0; predicted_steps=0; gold_steps=0
    field_ok=0; field_total=0
    field_counts=Counter(); field_totals=Counter()
    operation_gold=Counter(); operation_pred=Counter()
    per_case=[]; details=[]
    for cid in score_ids:
        pr=pred_by[cid]; gr=gold_by[cid]
        ps=json.loads(pr['steps_json']); gs=json.loads(gr['steps_json'])
        status_match=pr['deletion_status']==gr['deletion_status']
        seq_match=ps==gs
        status_ok+=int(status_match); sequence_ok+=int(seq_match)
        gc=Counter(canonical(s, fields) for s in gs); pc=Counter(canonical(s, fields) for s in ps)
        tp=sum((gc&pc).values()); exact_tp+=tp
        predicted_steps+=len(ps); gold_steps+=len(gs)
        for s in gs: operation_gold[s.get('operation','')]+=1
        for s in ps: operation_pred[s.get('operation','')]+=1
        positional_case_ok=0; positional_case_total=max(len(gs),len(ps))*len(fields)
        position_notes=[]
        for i in range(max(len(gs),len(ps))):
            if i>=len(gs):
                position_notes.append(f"step {i+1}: extra prediction ({ps[i].get('operation','?')})")
                field_total+=len(fields); positional_case_total+=0
                for key in fields: field_totals[key]+=1
                continue
            if i>=len(ps):
                position_notes.append(f"step {i+1}: missing prediction ({gs[i].get('operation','?')})")
                field_total+=len(fields); positional_case_total+=0
                for key in fields: field_totals[key]+=1
                continue
            different=[]
            for key in fields:
                field_totals[key]+=1; field_total+=1
                equal=gs[i].get(key)==ps[i].get(key)
                field_ok+=int(equal); positional_case_ok+=int(equal)
                field_counts[key]+=int(equal)
                if not equal: different.append(key)
            if different:
                position_notes.append(f"step {i+1}: {', '.join(different)}")
        per_case.append((cid,status_match,len(gs),len(ps),tp,seq_match,positional_case_ok,positional_case_total))
        if not status_match or not seq_match:
            go=Counter(s.get('operation','') for s in gs); po=Counter(s.get('operation','') for s in ps)
            missing_ops=go-po; extra_ops=po-go
            lines=[f"### {cid}", f"- Status: gold `{gr['deletion_status']}`; prediction `{pr['deletion_status']}` ({'match' if status_match else 'mismatch'}).",
                   f"- Step counts: gold {len(gs)}, prediction {len(ps)}; exact full-step matches {tp}; sequence {'matches' if seq_match else 'differs'}.",
                   f"- Gold-only operations: {list_counter(missing_ops, {})}.", f"- Prediction-only operations: {list_counter(extra_ops, {})}."]
            if position_notes: lines.append('- Positional differences: ' + '; '.join(position_notes) + '.')
            details.extend(lines)

    op_rows=[]
    for op in sorted(set(operation_gold)|set(operation_pred)):
        g=operation_gold[op]; p=operation_pred[op]; tp=min(g,p)
        op_rows.append(f"| {op or '(blank)'} | {g} | {p} | {tp} | {g-tp} | {p-tp} | {pct(tp,p)} | {pct(tp,g)} |")
    status_rows=[]
    for st in sorted(set(r['deletion_status'] for r in pred)|set(gold_by[c]['deletion_status'] for c in score_ids)):
        pc=sum(r['deletion_status']==st for r in pred)
        gc=sum(gold_by[c]['deletion_status']==st for c in score_ids)
        status_rows.append(f"| {st} | {gc} | {pc} |")
    case_rows=[f"| {cid} | {gold_by[cid]['deletion_status']} | {pred_by[cid]['deletion_status']} | {gn} | {pn} | {tp} | {'yes' if seq_match else 'no'} | {pct(fo,ft)} |" for cid,status_match,gn,pn,tp,seq_match,fo,ft in per_case]
    field_rows=[f"| {key} | {field_counts[key]} | {field_totals[key]} | {pct(field_counts[key],field_totals[key])} |" for key in sorted(fields)]
    op_tp=sum(min(operation_gold[x],operation_pred[x]) for x in set(operation_gold)|set(operation_pred))
    op_precision=pct(op_tp,sum(operation_pred.values())); op_recall=pct(op_tp,sum(operation_gold.values()))
    digest=hashlib.sha256(args.predictions.read_bytes()).hexdigest()
    lines=[
      '# v12 checkpointed public-sample evaluation', '',
      '## Scope and coverage', '',
      'The v12 process exited without producing the final `predictions.csv`. This report scores only its existing checkpointed `partial_predictions.csv`; no checkpoint rows were promoted to a final output.',
      f'- Public sample size: {len(all_ids)} cases.', f'- Checkpointed predictions: {len(pred)}/{len(all_ids)} ({len(pred)/len(all_ids):.2%}).',
      f'- Missing prediction rows: {len(missing_ids)} (not scored as empty predictions).',
      f'- Resolved-row evaluation denominator: {len(score_ids)} cases; these metrics are selection-biased.',
      f'- Prediction SHA-256: `{digest}`.', '',
      '## Status, exact steps, positions, and order', '',
      f'- Status accuracy on checkpointed rows: {pct(status_ok,len(score_ids))}.',
      f'- Exact full-step multiset precision: {pct(exact_tp,predicted_steps)}.',
      f'- Exact full-step multiset recall: {pct(exact_tp,gold_steps)}.',
      f'- Positional field accuracy (all seven fields; absent/extra steps count as seven errors): {pct(field_ok,field_total)}.',
      f'- Exact ordered sequence accuracy: {pct(sequence_ok,len(score_ids))}.',
      '- Full 32-case accuracy is unavailable because 22 cases have no prediction row.', '',
      '### Status counts on the scored rows', '', '| Status | Gold | Prediction |','|---|---:|---:|',*status_rows,'',
      '### Positional field breakdown', '', '| Field | Correct | Compared | Accuracy |','|---|---:|---:|---:|',*field_rows,'',
      '## Operation counts on the scored rows', '',
      f'- Operation-only multiset precision: {op_precision}.', f'- Operation-only multiset recall: {op_recall}.',
      '| Operation | Gold | Prediction | Matched | Missing | Extra | Precision | Recall |','|---|---:|---:|---:|---:|---:|---:|---:|',*op_rows,'',
      '## Case-level comparison', '',
      '| Case | Gold status | Predicted status | Gold steps | Predicted steps | Exact full-step matches | Exact sequence | Positional fields |','|---|---|---|---:|---:|---:|---|---:|',*case_rows,'',
      'All predicted cases have some status or sequence mismatch: '+(', '.join(cid for cid,sm,_,_,_,seq,_,_ in per_case if not sm or not seq) or 'none')+'.',
      'Cases with no checkpointed prediction (not scored): '+(', '.join(missing_ids) or 'none')+'.', '',
      '### Mismatch details', '', *(details or ['No case-level mismatches among supplied rows.']), '',
      '## Contract validity', '',
      ('PASS: official contract validation succeeded for the checkpointed rows and their matching sample requests/evidence times.' if not contract_errors else 'FAIL: '+ '; '.join(contract_errors)),
      'The official `validate_output.py` full-request invocation rejects a partial file for coverage mismatch; a separate invocation against the matching 10-request subset passed. Neither result implies complete sample coverage.', '',
      '## Limitations', '', 'Public sample only; no hidden-target accuracy claim. Checkpointed rows remain diagnostic and are not a finalized submission.'
    ]
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'WROTE {args.report}')
    print(f'COVERAGE {len(pred)}/{len(all_ids)}; STATUS {status_ok}/{len(score_ids)}; EXACT_STEPS {exact_tp}/{predicted_steps} precision, {exact_tp}/{gold_steps} recall; FIELD {field_ok}/{field_total}; ORDER {sequence_ok}/{len(score_ids)}; CONTRACT_ERRORS {len(contract_errors)}')

if __name__=='__main__': main()



