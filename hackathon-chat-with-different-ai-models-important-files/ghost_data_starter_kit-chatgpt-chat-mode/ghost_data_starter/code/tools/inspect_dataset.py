"""Summarize the official participant dataset, without using organizer-only files."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dataset', type=Path, default=Path('dataset'))
    args = p.parse_args()
    required = ['deletion_requests.csv', 'sample_deletion_requests.csv', 'sample_output.csv',
                'user_identities.csv', 'user_audit_log.csv', 'system_activity.csv',
                'deletion_rules.csv', 'evidence_files.csv']
    for name in required:
        path = args.dataset / name
        if not path.is_file():
            print('MISSING', path); continue
        rows, columns = read_csv(path)
        print(f'{name}: {len(rows)} rows; columns={columns}')
        if name == 'deletion_rules.csv':
            for row in rows:
                print(' ', row['data_category'], '=>', row['required_action'], '|', row['condition'])
        if name == 'sample_output.csv':
            print('  Status distribution:', dict(Counter(r['deletion_status'] for r in rows)))
            ops = Counter(step['operation'] for r in rows for step in json.loads(r['steps_json']))
            print('  Operation distribution:', dict(ops))
        if name == 'evidence_files.csv':
            print('  Evidence types:', dict(Counter(Path(r['file_path']).suffix for r in rows)))
            missing = [r['file_id'] for r in rows if not (args.dataset / r['file_path']).exists()]
            print('  Missing evidence:', missing[:10], '(total '+str(len(missing))+')')

if __name__ == '__main__':
    main()
