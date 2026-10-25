"""Honest, labeled-sample metrics for a separately generated sample output.
Usage: python code/tools/evaluate_samples.py --prediction sample_prediction.csv
"""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path


def load(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return {r['case_id']: (r['deletion_status'], json.loads(r['steps_json'])) for r in csv.DictReader(f)}


def signature(step):
    return tuple(step.get(k) for k in ['phase','system_id','resource_id','operation','state','evidence_id'])


def evaluate(expected, predicted):
    total=len(expected); status_correct=0; seq_correct=0; exact_correct=0; field_match=0; field_total=0
    tp=fp=fn=0
    failed=[]
    for case,(truth_status,truth_steps) in expected.items():
        value=predicted.get(case)
        if value is None:
            failed.append((case,'MISSING CASE')); fn+=len(truth_steps); continue
        status,steps=value
        status_correct += status == truth_status
        a=[signature(s) for s in truth_steps]
        b=[signature(s) for s in steps]
        seq_correct += a == b
        exact_correct += status==truth_status and a==b
        ca,cb=Counter(a),Counter(b)
        shared=sum((ca & cb).values()); tp+=shared;fp+=sum((cb-ca).values());fn+=sum((ca-cb).values())
        for i in range(max(len(truth_steps),len(steps))):
            for field in ['phase','system_id','resource_id','operation','state','evidence_id']:
                field_total+=1
                if i<len(truth_steps) and i<len(steps):
                    field_match += truth_steps[i].get(field)==steps[i].get(field)
        if status!=truth_status or a!=b:
            failed.append((case, f'status={status} truth={truth_status}; step counts={len(steps)}/{len(truth_steps)}'))
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    return {'cases':total,'status_accuracy':status_correct/total if total else 0,
            'exact_case_accuracy':exact_correct/total if total else 0,
            'step_sequence_accuracy':seq_correct/total if total else 0,
            'step_precision':precision,'step_recall':recall,
            'step_f1':2*precision*recall/(precision+recall) if precision+recall else 0,
            'position_aligned_field_accuracy':field_match/field_total if field_total else 0,
            'failures':failed}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--prediction',type=Path,required=True)
    ap.add_argument('--label',type=Path,default=Path('dataset/sample_output.csv'))
    ap.add_argument('--json-report',type=Path)
    a=ap.parse_args()
    scores=evaluate(load(a.label),load(a.prediction))
    print(json.dumps(scores,indent=2))
    if a.json_report:
        a.json_report.parent.mkdir(parents=True,exist_ok=True)
        a.json_report.write_text(json.dumps(scores,indent=2),encoding='utf-8')

if __name__ == '__main__':
    main()
