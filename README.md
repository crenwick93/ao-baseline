# AO Baseline Template

This is a baseline, not a finished project. Clone it, open it in Cursor, and tell Cursor what you want the project to become — a ticket enrichment workflow, certificate rotation, CVE remediation, or something else. Cursor will adapt the workflow, rulebooks, and CaC to that use case. Do that before you provision infrastructure or apply CaC. The steps below deploy whatever the project has become.

It includes the patterns most AO projects need:

- **EDA-to-AO bridge** — the universal pattern for triggering AO workflows from Event-Driven Ansible
- **ServiceNow ITSM playbooks** — action-based incident and change request management
- **AO Approval Bridge** — programmatically bridges ServiceNow CR approvals to AO approval gates
- **Configuration as Code** — full AAP Controller + EDA object definitions
- **Terraform** — EC2 + VPC + Elastic IP for demo hosts
- **GitHub integration** — commit files and raise PRs from AO workflows
- **Example AO workflow JSON** — shows all four node types (aap_job_template, agentic, switch, approval)

## Quick Start

### 1. Clone and tell Cursor what you want to build

```bash
git clone https://github.com/crenwick93/ao-baseline.git my-ao-project
cd my-ao-project
cp .env.example .env
```

Open the project in Cursor and describe the use case. For example: "Build a certificate rotation workflow that opens a ServiceNow change request, waits for approval, then commits the new cert to GitHub."

Cursor uses `.cursor/rules/project.md` and the playbooks in this repo to reshape the template for that use case: the AO workflow JSON, the EDA rulebook filters, CaC job template names, and any new playbooks. Do this before provisioning anything — the infra and CaC steps deploy whatever the project has become.

Fill in `.env` with your AAP, ServiceNow, GitHub, and (once the workflow is published) AO credentials.

### 2. Build container images (if you need a custom DE or EE)

```bash
REGISTRY=quay.io/myorg ./dependencies/build-images.sh --push
```

Set `DE_IMAGE` in `.env` to the image you pushed.

### 3. Provision infrastructure (optional)

```bash
cd setup/terraform
terraform init && terraform apply
cd ../..

./setup/scripts/setup-apply.sh
```

### 4. Install collections and apply CaC

```bash
ansible-galaxy collection install -r ansible_deployment/cac/requirements.yml
./ansible_deployment/scripts/cac-apply.sh
```

The controller project must be synced in AAP before job templates that reference its playbooks can be created. If the first CaC run fails on templates, sync the project in the AAP UI and run CaC again.

### 5. Import and publish the AO workflow

1. In the AO UI, import the workflow JSON from `ao/`
2. Configure any agentic nodes (model, MCP servers)
3. Publish the workflow
4. Copy the EDA trigger credentials into `.env`:
   - `AO_WEBHOOK_PATH`
   - `AO_WEBHOOK_CLIENT_ID`
   - `AO_WEBHOOK_CLIENT_SECRET`

### 6. Re-run CaC with real credentials

```bash
./ansible_deployment/scripts/cac-apply.sh
```

### 7. Enable the EDA activation

In AAP → EDA → Activations, restart the rulebook activation so it picks up the webhook credentials.

### 8. Test the pipeline

```bash
./scripts/test-trigger.sh
```

## Project Structure

```
ao-baseline/
├── .env.example                    # Environment template
├── ansible.cfg                     # Ansible defaults
├── ansible-navigator.yml           # Navigator config
├── group_vars/
│   └── all.yml                     # Global vars (critical_services, health_endpoint)
├── ao/
│   └── example-workflow.json       # AO workflow skeleton (all 4 node types)
├── playbooks/
│   ├── trigger_ao_workflow.yml     # EDA-to-AO bridge (OAuth2) — reuse as-is
│   ├── manage_snow_incident.yml    # All incident ops: action=create|update|resolve
│   ├── manage_snow_change_request.yml  # All CR ops: action=create|authorize|update|review|close
│   ├── bridge_ao_approval.yml     # Bridge SNOW CR approval to AO approval gate
│   └── manage_git_repo.yml        # Git ops: action=commit_file|create_pr
├── rulebooks/
│   └── example_eda_rulebook.yml   # Two rules: incident poll + CR approval bridge
├── scripts/
│   ├── test-trigger.sh            # Fire a test event to verify the pipeline
│   └── test-ao-approval-api.py    # Debug tool for AO approval API
├── ansible_deployment/
│   ├── cac/
│   │   ├── apply.yml              # CaC playbook (AAP Controller + EDA)
│   │   ├── vars.yml               # All AAP/EDA object definitions
│   │   └── requirements.yml       # Collection dependencies
│   └── scripts/
│       └── cac-apply.sh           # CaC runner script
├── dependencies/
│   ├── de/
│   │   └── decision-environment.yml  # DE build definition (EDA)
│   ├── ee/
│   │   └── execution-environment.yml # EE build definition (AAP jobs)
│   ├── build-images.sh              # Build + push both images
│   └── README.md                    # Build instructions
├── setup/
│   ├── terraform/                 # EC2 + VPC + Elastic IP
│   ├── playbooks/
│   │   └── setup_demo_host.yml    # Demo host provisioning stub
│   └── scripts/
│       ├── setup-apply.sh         # Setup runner script
│       └── teardown.sh            # Destroy Terraform infrastructure
└── .cursor/
    └── rules/
        └── project.md             # AI assistant conventions
```

## Reusable Patterns

### 1. EDA-to-AO Bridge (`trigger_ao_workflow.yml`)

The universal pattern for triggering AO workflows from EDA. Same in every AO project — never needs modification. Two HTTP calls: OAuth2 token, then POST event payload.

### 2. AO Approval Bridge (`bridge_ao_approval.yml`)

Bridges ServiceNow CR approval to AO approval gates. When a CR moves to "Implement" in SNOW, EDA detects it, triggers this playbook, which authenticates with the AO API and programmatically approves the pending workflow step.

### 3. Action-Based SNOW Playbooks

Two playbooks cover all SNOW operations, each driven by an `action` variable:

- **`manage_snow_incident.yml`** — `create` / `update` / `resolve`
- **`manage_snow_change_request.yml`** — `create` / `authorize` / `update` / `review` / `close`

AO workflow nodes call the same job template with different `action` values:

```json
{ "action": "create", "short_description": "...", "description": "..." }
{ "action": "update", "inc_sys_id": "...", "work_notes": "..." }
{ "action": "resolve", "inc_sys_id": "...", "work_notes": "..." }
```

### 4. Dual-Rule EDA Rulebook

Two rules in one activation:
1. Poll SNOW incidents → trigger AO workflow
2. Poll SNOW change requests → bridge approvals to AO

### 5. GitHub Integration (`manage_git_repo.yml`)

Commit files and raise PRs via the GitHub API. Useful for dynamic content generation (e.g. Lightspeed remediation playbooks, config changes) and change governance.

```json
{ "action": "commit_file", "file_path": "playbooks/fix.yml", "file_content": "...", "commit_message": "Add fix" }
{ "action": "commit_file", "file_path": "playbooks/fix.yml", "file_content": "...", "branch": "feature/fix" }
{ "action": "create_pr", "pr_title": "Add fix playbook", "head_branch": "feature/fix" }
```

### 6. CaC Credential Types

Four custom credential types covering all AO integration points:
- **ServiceNow** — env vars (`SN_HOST`, `SN_USERNAME`, `SN_PASSWORD`)
- **AO Webhook** — extra_vars (`webhook_base_url`, `webhook_client_id`, `webhook_client_secret`)
- **AO API** — extra_vars (`ao_sa_client_id`, `ao_sa_client_secret`, `ao_base_url`)
- **GitHub API Token** — env var (`GITHUB_TOKEN`)

## Deployment Order

Describe the use case to Cursor first so the project is customized before anything is deployed.

1. Build DE + EE images (`./dependencies/build-images.sh --push`)
2. `terraform apply` — provisions EC2
3. `setup-apply.sh` — configures demo host
4. `cac-apply.sh` — creates AAP objects (needs project synced first)
5. Import AO workflow in AO UI, configure agentic nodes, publish
6. Update `.env` with AO webhook creds, re-run `cac-apply.sh`
7. Restart EDA activation in AAP UI
8. `./scripts/test-trigger.sh` — verify the pipeline

## Reference Projects

For real-world examples built from these patterns, see the AO demo projects in the same GitHub org.
