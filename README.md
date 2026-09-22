# AO Baseline Template

Reusable starter template for **Automation Orchestrator (AO)** projects. Provides all the common patterns extracted from real-world AO demos:

- **EDA-to-AO bridge** — the universal pattern for triggering AO workflows from Event-Driven Ansible
- **ServiceNow ITSM playbooks** — action-based incident and change request management
- **AO Approval Bridge** — programmatically bridges ServiceNow CR approvals to AO approval gates
- **Configuration as Code** — full AAP Controller + EDA object definitions
- **Terraform** — EC2 + VPC + Elastic IP for demo hosts
- **Example AO workflow JSON** — shows all four node types (aap_job_template, agentic, switch, approval)

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_ORG/ao-baseline.git my-ao-project
cd my-ao-project
cp .env.example .env
# Edit .env with your AAP, ServiceNow, and AO credentials
```

### 2. Provision infrastructure (optional)

```bash
cd setup/terraform
terraform init && terraform apply
cd ../..

# Configure the demo host
./setup/scripts/setup-apply.sh
```

### 3. Install collections and apply CaC

```bash
ansible-galaxy collection install -r ansible_deployment/cac/requirements.yml
./ansible_deployment/scripts/cac-apply.sh
```

### 4. Import AO workflow

1. In the AO UI, import `ao/example-workflow.json`
2. Configure any agentic nodes (model, MCP servers)
3. Publish the workflow
4. Copy the EDA trigger credentials to `.env`:
   - `AO_WEBHOOK_PATH`
   - `AO_WEBHOOK_CLIENT_ID`
   - `AO_WEBHOOK_CLIENT_SECRET`

### 5. Re-run CaC with real credentials

```bash
./ansible_deployment/scripts/cac-apply.sh
```

### 6. Enable EDA activation

In AAP → EDA → Activations, restart the rulebook activation to pick up the updated webhook credentials.

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
│   └── bridge_ao_approval.yml     # Bridge SNOW CR approval to AO approval gate
├── rulebooks/
│   └── example_eda_rulebook.yml   # Two rules: incident poll + CR approval bridge
├── scripts/
│   └── test-ao-approval-api.py    # Debug tool for AO approval API
├── ansible_deployment/
│   ├── cac/
│   │   ├── apply.yml              # CaC playbook (AAP Controller + EDA)
│   │   ├── vars.yml               # All AAP/EDA object definitions
│   │   └── requirements.yml       # Collection dependencies
│   ├── ee/
│   │   └── decision-environment.yml  # DE build definition
│   └── scripts/
│       └── cac-apply.sh           # CaC runner script
├── setup/
│   ├── terraform/                 # EC2 + VPC + Elastic IP
│   ├── playbooks/
│   │   └── setup_demo_host.yml    # Demo host provisioning stub
│   └── scripts/
│       └── setup-apply.sh         # Setup runner script
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

### 5. CaC Credential Types

Three custom credential types covering all AO integration points:
- **ServiceNow** — env vars (`SN_HOST`, `SN_USERNAME`, `SN_PASSWORD`)
- **AO Webhook** — extra_vars (`webhook_base_url`, `webhook_client_id`, `webhook_client_secret`)
- **AO API** — extra_vars (`ao_sa_client_id`, `ao_sa_client_secret`, `ao_base_url`)

## Deployment Order

1. `terraform apply` — provisions EC2
2. `setup-apply.sh` — configures demo host
3. `cac-apply.sh` — creates AAP objects (needs project synced first)
4. Import AO workflow in AO UI, configure agentic nodes, publish
5. Update `.env` with AO webhook creds, re-run `cac-apply.sh`
6. Restart EDA activation in AAP UI

## Reference Projects

For real-world examples built from these patterns:

- [`ao-ticket-enrichment`](https://github.com/crenwick93/ao-ticket-enrichment) — Simple enrichment + remediation (EDA-to-AO bridge, SNOW integration, Terraform)
- [`ao-cve-remediation-scalable`](https://github.com/crenwick93/ao-cve-remediation-scalable) — Complex fleet patching (approval bridge, CR governance, dynamic job templates)
