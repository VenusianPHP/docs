#!/usr/bin/env python3
"""Fail when documentation.md and the pages disagree, or a /docs/{{version}}/ link has no page."""
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
pages = {
    str(p.relative_to(root))[:-3]
    for p in root.rglob('*.md')
    if p.parent != root and '.github' not in p.parts
}
sidebar = (root / 'documentation.md').read_text()
entries = re.findall(r'\(/docs/\{\{version\}\}/([^)#\s]+)\)', sidebar)

problems = []
problems += [f'documentation.md: {e} has no page' for e in sorted(set(entries) - pages)]
problems += [f'{p}.md: not in documentation.md' for p in sorted(pages - set(entries))]
problems += [f'documentation.md: {e} listed {entries.count(e)} times' for e in sorted(set(entries)) if entries.count(e) > 1]

fence = re.compile(r'^\s*(```|~~~)')
for page in sorted(pages):
    in_fence = None
    for number, line in enumerate((root / f'{page}.md').read_text().splitlines(), 1):
        mark = fence.match(line)
        if mark:
            in_fence = None if in_fence and line.strip().startswith(in_fence) else (in_fence or mark.group(1))
            continue
        if in_fence:
            continue
        for target in re.findall(r'\]\(/docs/\{\{version\}\}/([^)#\s]+)', line):
            if target not in pages:
                problems.append(f'{page}.md:{number}: /docs/{{{{version}}}}/{target} has no page')

for problem in problems:
    print(problem)
print(f'{len(pages)} pages, {len(entries)} sidebar entries, {len(problems)} problems')
sys.exit(1 if problems else 0)
