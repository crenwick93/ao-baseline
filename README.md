# AO Baseline Template

This is a baseline, not a finished project.

1. Clone it and open it in Cursor.
2. Tell Cursor what you want the project to be (ticket enrichment, certificate rotation, CVE remediation, or something else).
3. Cursor rewrites this README, `.cursor/rules/project.md`, the workflow, the rulebooks, and the CaC to match that use case.
4. Then follow the new README to build images, provision infrastructure, and apply CaC.

```bash
git clone https://github.com/crenwick93/ao-baseline.git my-ao-project
cd my-ao-project
cp .env.example .env
```

Fill in `.env` when Cursor asks for credentials.
