# AO Baseline Template

This is a baseline, not a finished project.

1. Clone it, create your own empty GitHub repo, and point this project at it. Later commits and the `manage_git_repo.yml` playbook go to your repo, not this template.
2. Open it in Cursor and tell Cursor what you want the project to be (ticket enrichment, certificate rotation, CVE remediation, or something else).
3. Cursor rewrites this README, `.cursor/rules/project.md`, the workflow, the rulebooks, and the CaC to match that use case, and sets `GITHUB_REPO` in `.env` to your repo.
4. Then follow the new README to build images, provision infrastructure, and apply CaC.

```bash
git clone https://github.com/crenwick93/ao-baseline.git my-ao-project
cd my-ao-project
git remote set-url origin https://github.com/YOUR_ORG/YOUR_REPO.git
git push -u origin main
cp .env.example .env
```

Fill in `.env` when Cursor asks for credentials.
