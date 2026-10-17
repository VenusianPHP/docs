# Agent guidelines — VenusianPHP/docs

Source for the Venusian and ScrapyardIO documentation sites. Markdown only: no build step, no frontmatter, no OKF bundle (the pages are the knowledge).

## Rules

- One page = one `.md` file under `framework/`, `surface/`, `scrapyard-io/` or `ecosystem/`. Path minus `.md` = URL after `/docs/{version}/`.
- Page opens with `# Title`, then a one-paragraph summary. Sections start at `##`.
- Two sidebars, one per site: `documentation.md` (Venusian) and `scrapyard-io.md` (ScrapyardIO: its framework, PHP IO extensions posi/ftdi, microscrap, Dept of Scrapyard Robotics). Every page has exactly one entry in exactly one of them; the entry order is the reading order (prev/next). GPIO content belongs to ScrapyardIO; Venusian's sidebar keeps only the `[GPIO]` link to it.
- Sidebar shape: `- ## Section` top level (a `##` entry may be an external link), nested `- Group` lists, page links `[Title](/docs/{{version}}/<path>)`.
- Links within a site always `/docs/{{version}}/<path>`, optional `#fragment`. A page on the other site gets its absolute unversioned URL (`https://venusian.projectsaturnstudios.com/docs/<path>` or `https://scrapyard-io.projectsaturnstudios.com/docs/<path>`). Never relative `.md` links, never a hard-coded version.
- Files that live in a package repo (LICENSE, stubs, AGENTS.md) link to that repo on GitHub.
- Branch per release line (`0.10.x`). Fixes for a line go on its branch.
- Before committing, run the link check in `.github/workflows/links.yml` locally: `python3 .github/check-links.py`.
