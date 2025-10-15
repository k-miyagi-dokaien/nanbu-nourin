#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path


DOC_PATH = Path(__file__).resolve().parents[1]
INPUT_TXT = DOC_PATH / 'sample_converted.txt'
OUTPUT_JSON = DOC_PATH / 'template.json'


def parse_overview(lines):
    keys = ["業務名", "業務場所", "工期"]
    found = {k: None for k in keys}
    for i, line in enumerate(lines[:80]):
        for k in keys:
            if k in line:
                # Try to pick value from same or next line
                val = None
                # split by common separators
                parts = re.split(r"[：:\t]", line, maxsplit=1)
                if len(parts) == 2 and parts[1].strip():
                    val = parts[1].strip()
                else:
                    # maybe next line holds value
                    if i + 1 < len(lines):
                        nxt = lines[i + 1].strip()
                        if nxt and not re.match(r"^第\s*\d+\s*条", nxt):
                            val = nxt
                if val:
                    found[k] = val
    fields = []
    for k in keys:
        fields.append({"key": k, "value": found[k] or "", "required": True})
    overview = {"type": "table", "fields": fields}
    return overview


def normalize_brackets(s: str) -> str:
    # convert various brackets to full-width parentheses used in sample
    # and strip leading/ending brackets
    s = s.strip()
    # unify brackets
    s = s.replace('（', '(').replace('）', ')')
    s = s.replace('【', '(').replace('】', ')')
    s = s.replace('〔', '(').replace('〕', ')')
    # remove surrounding parentheses
    m = re.match(r"^\((.+)\)$", s)
    if m:
        return m.group(1).strip()
    return s


def parse_articles(lines):
    # Patterns
    pat_article = re.compile(r"^第\s*([0-9]+)\s*条\s*$")
    pat_inline = re.compile(r"^第\s*([0-9]+)\s*条（(.+?)）$")

    articles = []
    cur = None
    pending_title = None

    def push_current():
        nonlocal cur
        if cur is None:
            return
        # trim body lines
        while cur['body'] and not cur['body'][-1].strip():
            cur['body'].pop()
        bodyMd = "\n".join(cur['body']).strip()
        articles.append({
            "no": cur['no'],
            "title": cur['title'] or f"条{cur['no']}",
            "optional": True if cur['no'] not in (1, 2, 22) else False,
            "bodyMd": bodyMd
        })
        cur = None

    for raw in lines:
        line = raw.rstrip()
        if not line:
            if cur:
                cur['body'].append("")
            continue

        # Inline form: "第n条（見出し）"
        m_inline = pat_inline.match(line)
        if m_inline:
            # close previous
            push_current()
            no = int(m_inline.group(1))
            title = m_inline.group(2).strip()
            cur = {"no": no, "title": title, "body": []}
            pending_title = None
            continue

        # Title line in parentheses before article line
        if re.match(r"^[（\(].+[）\)]$", line):
            pending_title = normalize_brackets(line)
            continue

        m = pat_article.match(line)
        if m:
            push_current()
            no = int(m.group(1))
            cur = {"no": no, "title": pending_title or None, "body": []}
            pending_title = None
            continue

        # Normal content line
        if cur is None:
            # ignore preface noise
            continue
        cur['body'].append(line)

    push_current()
    # Sort by article number just in case
    articles.sort(key=lambda a: a['no'])
    return articles


def build_template(lines):
    overview = parse_overview(lines)
    articles = parse_articles(lines)
    data = {
        "$schema": "https://example.local/schema/tokki.json",
        "version": "1.0",
        "meta": {
            "title": "特記仕様書",
            "agency": "沖縄県南部農林土木事務所",
            "createdAt": "",
            "source": "file"
        },
        "overview": overview,
        "articles": articles
    }
    return data


def main():
    if not INPUT_TXT.exists():
        raise SystemExit(f"Input not found: {INPUT_TXT}")
    lines = [l.rstrip('\n') for l in INPUT_TXT.read_text(encoding='utf-8', errors='ignore').splitlines()]
    data = build_template(lines)
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {OUTPUT_JSON} with {len(data['articles'])} articles")


if __name__ == '__main__':
    main()

