"""Evidence pre-indexer for official participant-facing dataset.

Creates local, searchable JSONL observations with file_id provenance.
This is an ingestion scaffold, NOT a deletion-audit decision engine.
PDFs use pypdf if installed; images need a separate vision interpretation stage.

Usage: python code/tools/index_evidence.py --dataset dataset --out work/evidence_index.jsonl
"""
from __future__ import annotations
import argparse, csv, json, re, sqlite3
from pathlib import Path

RESOURCE_RE = re.compile(r'\b(?:account|analytics|audit_record|backup|data_flow|export|search|support|tombstone|marketing|cache|security|telemetry|attachment)_[A-Za-z0-9_-]+\b')
TIMESTAMP_RE = re.compile(r'\b20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\b')


def iter_json_objects(value, trail=()):
    """Extract nested dictionaries likely representing resource-level observations."""
    if isinstance(value, dict):
        if any(k in value for k in ('resource_id','record_type','activity_id','user_id','customer_reference','subject_reference')):
            yield {'path':'/'.join(map(str,trail)), 'record':value}
        for k,v in value.items():
            if isinstance(v, (dict,list)):
                yield from iter_json_objects(v, trail+(k,))
    elif isinstance(value,list):
        for i,v in enumerate(value):
            yield from iter_json_objects(v,trail+(i,))


def scan_sql(path):
    con=sqlite3.connect(':memory:')
    con.row_factory=sqlite3.Row
    try:
        con.executescript(path.read_text(encoding='utf-8'))
        tables=[r[0] for r in con.execute('SELECT name FROM sqlite_master WHERE type="table"') if not r[0].startswith('sqlite_')]
        scope={r['origin_system']:r['captured_at'] for r in con.execute('SELECT * FROM snapshot_scope')} if 'snapshot_scope' in tables else {}
        for table in tables:
            if table=='snapshot_scope':
                continue
            for r in con.execute('SELECT * FROM "'+table.replace('"','""')+'"'):
                data=dict(r)
                yield {'path':table, 'record':data, 'observed_at':data.get('updated_at'), 'scope':scope}
    finally:
        con.close()


def scan_log(path):
    for lineno,line in enumerate(path.read_text(encoding='utf-8',errors='replace').splitlines(),1):
        identifiers=RESOURCE_RE.findall(line)
        if identifiers:
            ts=TIMESTAMP_RE.search(line)
            yield {'path':f'line:{lineno}', 'record':{'text':line,'resource_ids':identifiers},
                   'observed_at':ts.group(0) if ts else None}


def scan_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        yield {'path':'pdf-unparsed','record':{'note':'Install pypdf or use a PDF-aware extractor'}}
        return
    for number,page in enumerate(PdfReader(str(path)).pages,1):
        text=page.extract_text() or ''
        if text.strip():
            yield {'path':f'page:{number}', 'record':{'text':text}}


def scan_file(path):
    ext=path.suffix.lower()
    if ext=='.json':
        yield from iter_json_objects(json.loads(path.read_text(encoding='utf-8')))
    elif ext=='.sql':
        yield from scan_sql(path)
    elif ext=='.log':
        yield from scan_log(path)
    elif ext=='.pdf':
        yield from scan_pdf(path)
    elif ext=='.txt':
        for i,line in enumerate(path.read_text(encoding='utf-8',errors='replace').splitlines(),1):
            if line.strip():
                yield {'path':f'line:{i}', 'record':{'text':line}}
    elif ext in ('.png','.jpg','.jpeg'):
        yield {'path':'image-needs-vision','record':{'note':'Interpret with a vision model; do not invent image contents'}}
    else:
        yield {'path':'unsupported','record':{'note':f'Unsupported type: {ext}'}}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dataset',type=Path,default=Path('dataset'))
    p.add_argument('--out',type=Path,default=Path('work/evidence_index.jsonl'))
    a=p.parse_args()
    manifest=a.dataset/'evidence_files.csv'
    a.out.parent.mkdir(parents=True,exist_ok=True)
    total=0
    with manifest.open(encoding='utf-8',newline='') as infile, a.out.open('w',encoding='utf-8') as outfile:
        for m in csv.DictReader(infile):
            path=a.dataset/m['file_path']
            if not path.is_file():
                raise FileNotFoundError(f"Missing {m['file_id']} at {path}")
            count=0
            try:
                for obs in scan_file(path):
                    event={'file_id':m['file_id'],'file_path':m['file_path'],
                           'captured_at':m['captured_at'],'origin':m['origin'],**obs}
                    outfile.write(json.dumps(event,ensure_ascii=False,default=str)+'\n')
                    total+=1;count+=1
            except Exception as exc:
                print(f'ERROR {m["file_id"]}: {type(exc).__name__}: {exc}')
                raise
            print(f'{m["file_id"]}: {count} indexed observations')
    print(f'Wrote {total} observations to {a.out}')
    print('IMPORTANT: index observations need temporal validation, identity matching, and reliability scoring before being used as proof.')

if __name__=='__main__':
    main()
