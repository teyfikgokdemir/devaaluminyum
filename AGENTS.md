# Agent instructions

## Project-specific Codex instructions (2026-10-17)

### Project context
Aluminum site/archive recovery; preserve source provenance, original media and old-to-new domain URL mapping.

### Read before acting
Read README, package scripts, CI workflows, existing instructions and affected sources. Do not treat old documentation as proof of live state.

### Safe execution
- Audit/review is read-only: no edits, commits, tracking or infrastructure changes.
- Requested changes must be small, reversible and scoped. Preserve design, mobile behavior, accessibility, content, routing and working integrations.
- Do not deploy or push to the default branch unless explicitly requested; prefer reviewable feature branches and PRs.
- Keep credentials, customer data and private analytics out of code and logs. Never invent business claims or credentials.

### Review checklist
- Prioritize security, broken functionality and data integrity over cosmetic style. Cite exact affected paths/lines and severity; distinguish observation from hypothesis.
- Check applicable canonical, robots, sitemap, metadata, Open Graph, schema, links, accessibility and performance. SEO checks do not guarantee rankings.
- Check hreflang and RTL only where supported; preserve actual locale architecture.
- For forms and APIs check validation, rate limiting, errors and privacy; do not modify consent or analytics behavior without instruction.

### Verification
- Use only repository-supported checks; distinguish not run, failed and passed.
- Report separately: changed files, tests, commits, pushes, PRs, CI, deployment and live verification. Note blockers and next step.
