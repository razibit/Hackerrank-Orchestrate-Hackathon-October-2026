"""Strict format/evidence-reference checks for Ghost Data Still Exists.

This cannot establish that the inferred deletion decisions are correct.
Usage: python code/tools/validate_output.py --output output.csv
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

HEADER = ['case_id', 'deletion_status', 'steps_json']
PHASES = ('FINDING', 'REMEDIATION', 'VERIFICATION')
OPS = {
    'FINDING': [('REPORT_REMAINING_RECORD', 'PRESENT'), ('REPORT_EXPOSED_PII', 'PRESENT'),
                ('REPORT_ACTIVE_DATA_FLOW', 'ACTIVE'), ('REPORT_RESTORE_RISK', 'ACTIVE')],
    'REMEDIATION': [('DISABLE_DATA_FLOW', 'DISABLED'), ('BLOCK_RESTORE', 'BLOCKED'),
                    ('DELETE_RECORD', 'ABSENT'), ('REDACT_RECORD', 'REDACTED'),
                    ('ANONYMIZE_RECORD', 'ANONYMIZED')],
    'VERIFICATION': [('VERIFY_RECORD_ABSENT', 'ABSENT'), ('VERIFY_RECORD_PRESENT', 'PRESENT'),
                     ('VERIFY_RECORD_REDACTED', 'REDACTED'), ('VERIFY_RECORD_ANONYMIZED', 'ANONYMIZED'),
                     ('VERIFY_DATA_FLOW_DISABLED', 'DISABLED'), ('VERIFY_RESTORE_BLOCKED', 'BLOCKED')]
}
FIELDS = {'step_no', 'phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id'}
ALLOWED_STATUSES = {'COMPLETE', 'INCOMPLETE', 'NOT_APPLICABLE'}


def rows(path):
    with open(path, encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != HEADER and Path(path).name == 'output.csv':
            # Caller will perform the proper schema check; avoid misinterpreting input.
            pass
        return list(reader), list(reader.fieldnames or [])


def validate(output: Path, dataset: Path, expected_file: str = 'deletion_requests.csv'):
    problems = []
    if not output.is_file():
        return [f'Output does not exist: {output}'], Counter()
    outputs, fields = rows(output)
    if fields != HEADER:
        problems.append(f'Header must be {HEADER}, received {fields}')
    inputs, _ = rows(dataset / expected_file)
    expected_ids = [r['case_id'] for r in inputs]
    actual_ids = [r.get('case_id') for r in outputs]
    if len(outputs) != len(inputs):
        problems.append(f'Expected {len(inputs)} data rows, got {len(outputs)}')
    if len(actual_ids) != len(set(actual_ids)):
        problems.append('Duplicate case_id values')
    if set(actual_ids) != set(expected_ids):
        problems.append(f'Case IDs mismatch; missing={sorted(set(expected_ids)-set(actual_ids))[:12]}, extras={sorted(set(actual_ids)-set(expected_ids))[:12]}')
    if actual_ids != sorted(actual_ids):
        problems.append('Output case_id rows are not sorted lexicographically')
    lookup = {r['case_id']: r for r in inputs}
    file_manifest, _ = rows(dataset / 'evidence_files.csv')
    activity_rows, _ = rows(dataset / 'system_activity.csv')
    audit_rows, _ = rows(dataset / 'user_audit_log.csv')
    known_ids = {r['file_id']: r['captured_at'] for r in file_manifest}
    known_ids.update({r['activity_id']: r['event_time'] for r in activity_rows})
    known_ids.update({r['audit_id']: r['event_time'] for r in audit_rows})
    stats = Counter()
    for row in outputs:
        case = row.get('case_id', '<missing>')
        status = row.get('deletion_status')
        if status not in ALLOWED_STATUSES:
            problems.append(f'{case}: invalid deletion status {status!r}')
            continue
        stats[status] += 1
        try:
            steps = json.loads(row.get('steps_json', ''))
            if not isinstance(steps, list):
                raise ValueError('steps_json must be a JSON array')
        except (ValueError, TypeError) as exc:
            problems.append(f'{case}: invalid steps_json: {exc}')
            continue
        if status == 'NOT_APPLICABLE' and steps:
            problems.append(f'{case}: NOT_APPLICABLE must have [] steps')
        if status == 'COMPLETE' and any(s.get('phase') != 'VERIFICATION' for s in steps if isinstance(s, dict)):
            problems.append(f'{case}: COMPLETE must have only VERIFICATION steps')
        if status == 'INCOMPLETE' and not steps:
            problems.append(f'{case}: INCOMPLETE has no findings/remediation/verification')
        prev_sort = None
        for idx, step in enumerate(steps, 1):
            prefix = f'{case} step {idx}'
            if not isinstance(step, dict):
                problems.append(f'{prefix}: step must be a JSON object'); continue
            if set(step) != FIELDS:
                problems.append(f'{prefix}: expected keys {sorted(FIELDS)}; got {sorted(step)}')
            if step.get('step_no') != idx or isinstance(step.get('step_no'), bool):
                problems.append(f'{prefix}: step_no must equal {idx}')
            phase = step.get('phase')
            operation = step.get('operation')
            state = step.get('state')
            if phase not in PHASES:
                problems.append(f'{prefix}: invalid phase {phase!r}'); continue
            operations = OPS[phase]
            if (operation, state) not in operations:
                problems.append(f'{prefix}: invalid operation/state combination {operation}/{state}')
                continue
            system = step.get('system_id'); resource = step.get('resource_id')
            if not isinstance(system, str) or not system or not isinstance(resource, str) or not resource:
                problems.append(f'{prefix}: system_id and resource_id must be non-empty strings')
                continue
            sort_key = (PHASES.index(phase), operations.index((operation, state)), system, resource)
            if prev_sort is not None and sort_key < prev_sort:
                problems.append(f'{prefix}: steps out of required phase/operation/system/resource ordering')
            prev_sort = sort_key
            evidence = step.get('evidence_id')
            is_proof = phase == 'FINDING' or status == 'COMPLETE'
            if is_proof:
                if evidence not in known_ids:
                    problems.append(f'{prefix}: unknown/missing evidence ID {evidence!r}')
                elif case in lookup and known_ids[evidence] > lookup[case]['audit_at']:
                    problems.append(f'{prefix}: evidence {evidence} is newer than audit_at')
            elif evidence != '':
                problems.append(f'{prefix}: proposed action/future check must use empty evidence_id')
    return problems, stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('output.csv'))
    parser.add_argument('--dataset', type=Path, default=Path('dataset'))
    parser.add_argument('--expected-file', default='deletion_requests.csv')
    args = parser.parse_args()
    problems, stats = validate(args.output, args.dataset, args.expected_file)
    print('Status counts:', dict(stats))
    if problems:
        print(f'FAILED: {len(problems)} issue(s):')
        for problem in problems[:100]:
            print(' -', problem)
        if len(problems) > 100:
            print(f' ... and {len(problems)-100} more')
        raise SystemExit(1)
    print('PASS: structural and evidence-timestamp constraints (not semantic correctness)')


if __name__ == '__main__':
    main()
