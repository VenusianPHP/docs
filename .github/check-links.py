#!/usr/bin/env python3
"""Fail when the sidebars and the pages disagree, or a /docs/{{version}}/ link has no page on its own site.

Two sites read this repository, each through its own sidebar:
documentation.md (Venusian) and scrapyard-io.md (ScrapyardIO). Every page
belongs to exactly one sidebar, and a /docs/{{version}}/ link can only reach
a page of the same site; a page on the other site is linked by its absolute URL.
"""
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
sidebars = {
    'documentation.md': 'https://venusian.projectsaturnstudios.com/docs/',
    'scrapyard-io.md': 'https://scrapyard-io.projectsaturnstudios.com/docs/',
}
pages = {
    str(p.relative_to(root))[:-3]
    for p in root.rglob('*.md')
    if p.parent != root and '.github' not in p.parts
}

problems = []
site_of = {}
entries = []
for sidebar in sidebars:
    listed = re.findall(r'\(/docs/\{\{version\}\}/([^)#\s]+)\)', (root / sidebar).read_text())
    entries += listed
    problems += [f'{sidebar}: {e} has no page' for e in sorted(set(listed) - pages)]
    problems += [f'{sidebar}: {e} listed {listed.count(e)} times' for e in sorted(set(listed)) if listed.count(e) > 1]
    for entry in set(listed) & pages:
        if entry in site_of:
            problems.append(f'{entry}: listed in both {site_of[entry]} and {sidebar}')
        site_of.setdefault(entry, sidebar)

problems += [f'{p}.md: not in any sidebar' for p in sorted(pages - set(site_of))]

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
            elif page in site_of and target in site_of and site_of[page] != site_of[target]:
                problems.append(
                    f'{page}.md:{number}: /docs/{{{{version}}}}/{target} is on the other site; '
                    f'link {sidebars[site_of[target]]}{target}'
                )

for problem in problems:
    print(problem)
print(f'{len(pages)} pages, {len(entries)} sidebar entries, {len(problems)} problems')
sys.exit(1 if problems else 0)
