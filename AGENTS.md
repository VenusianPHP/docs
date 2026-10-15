# Agent guidelines — VenusianPHP/docs

Source for the Venusian documentation site. Markdown only: no build step, no frontmatter, no OKF bundle (the pages are the knowledge).

## Rules

- One page = one `.md` file under `framework/`, `surface/` or `ecosystem/`. Path minus `.md` = URL after `/docs/{version}/`.
- Page opens with `# Title`, then a one-paragraph summary. Sections start at `##`.
- Every page has exactly one entry in `documentation.md`; the entry order is the reading order (prev/next).
- `documentation.md` shape: `- ## Section` top level (a `##` entry may be an external link), nested `- Group` lists, page links `[Title](/docs/{{version}}/<path>)`.
- Internal links always `/docs/{{version}}/<path>`, optional `#fragment`. Never relative `.md` links, never a hard-coded version.
- Files that live in a package repo (LICENSE, stubs, AGENTS.md) link to that repo on GitHub.
- Branch per release line (`0.10.x`). Fixes for a line go on its branch.
- Before committing, run the link check in `.github/workflows/links.yml` locally: `python3 .github/check-links.py`.
