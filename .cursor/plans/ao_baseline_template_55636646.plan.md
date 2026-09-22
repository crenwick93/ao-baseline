---
name: AO Baseline Template
overview: Create a reusable starter template for AO projects by extracting the common patterns from ao-ticket-enrichment and generalizing them. Removes all nginx/demo-specific code, keeps the CaC structure, EDA-to-AO bridge pattern, ServiceNow integration, Terraform base, and project scaffolding.
todos:
  - id: create-dir
    content: Create ao-baseline directory and initialize git repo
    status: pending
  - id: scaffold
    content: "Create the base files: .env.example, .gitignore, .cursorignore, ansible.cfg, ansible-navigator.yml"
    status: pending
  - id: cac
    content: Create ansible_deployment/ — generalized apply.yml, vars.yml, requirements.yml, DE, cac-apply.sh
    status: pending
  - id: playbooks
    content: "Create playbooks/ — trigger_ao_workflow.yml, manage_snow_incident.yml (create/update/resolve), manage_snow_change_request.yml (create/authorize/update/review/close), bridge_ao_approval.yml"
    status: pending
  - id: rulebook
    content: "Create rulebooks/example_eda_rulebook.yml — SNOW incident polling + CR approval bridge rules"
    status: pending
  - id: ao-example
    content: Create ao/example-workflow.json — minimal skeleton showing AO schema format
    status: pending
  - id: terraform
    content: Create setup/terraform/ — generalized main.tf, variables.tf, outputs.tf
    status: pending
  - id: setup-playbook
    content: Create setup/playbooks/setup_demo_host.yml — minimal stub with customization comments
    status: pending
  - id: docs
    content: Create README.md, REQUIREMENTS.md, group_vars/all.yml
    status: pending
  - id: cursor-rules
    content: Create .cursor/rules/project.md with baseline conventions and gotchas
    status: pending
  - id: push
    content: Push to github.com/crenwick93/ao-baseline
    status: pending
isProject: false
---

# AO Baseline Template

## What Stays (Generalized)

These are reusable across any AO project:

- **`ansible.cfg`**, **`ansible-navigator.yml`** — as-is
- **`.gitignore`**, **`.cursorignore`** — as-is
- **`.env.example`** — keep AAP, ServiceNow, AO webhook sections; remove `MONITORING_HOST_IP`; add `DEMO_HOST_IP` as generic placeholder
- **`ansible_deployment/cac/apply.yml`** — generalize the play name, keep the `SERVICENOW_*` / `SN_*` dual-lookup pattern, controller_host/oauthtoken vars, async settings, post_tasks for enabling activations
- **`ansible_deployment/cac/vars.yml`** — keep ServiceNow + AO Webhook + AO API credential types, AAP Controller credential. Job templates: AO Bridge, Manage SNOW Incident, Manage SNOW Change Request, Bridge AO Approval. EDA objects with dual-rule rulebook (incident poll + CR approval bridge). Adapted from both projects
- **`ansible_deployment/cac/requirements.yml`** — as-is
- **`ansible_deployment/ee/decision-environment.yml`** — as-is
- **`ansible_deployment/scripts/cac-apply.sh`** — generalize comments
- **`playbooks/trigger_ao_workflow.yml`** — rename play to generic "Trigger AO Workflow", keep as-is (this is the universal EDA-to-AO bridge pattern)
- **`playbooks/manage_snow_incident.yml`** — single playbook for all incident operations. Takes `action` var: `create`, `update`, `resolve`. Each action is a clearly commented block. On create: publishes `inc_sys_id` and `inc_number` via `set_stats`. On update: adds work notes wrapped in `[code]` tags, optional state change. On resolve: two-step (work notes first, then close with `close_code: "Solution provided"`). Adapted from `ao-ticket-enrichment/playbooks/update_snow_ticket.yml` and `ao-cve-remediation-scalable/playbooks/snow_open_incident.yml`
- **`playbooks/manage_snow_change_request.yml`** — single playbook for all CR operations. Takes `action` var: `create`, `authorize`, `update`, `review`, `close`. On create: builds emergency CR with justification, implementation plan, backout plan, test plan; publishes `cr_sys_id` and `cr_number` via `set_stats`. On authorize: moves CR to authorize state and requests approval. On update: adds work notes. On review: moves to review state. On close: closes CR. Adapted from `ao-cve-remediation-scalable/playbooks/snow_open_cr.yml`
- **`playbooks/bridge_ao_approval.yml`** — bridges ServiceNow CR approval to AO approval gate. Adapted from `ao-cve-remediation-scalable/playbooks/bridge_ao_approval.yml`. Authenticates with AO API via OAuth2 service account, lists pending approvals, matches by CR number in workflow_context, approves via PATCH
- **`rulebooks/example_eda_rulebook.yml`** — two rules: (1) SNOW incident polling + bridge to AO, (2) SNOW CR approval polling + bridge to AO approval gate. Adapted from `ao-cve-remediation-scalable/rulebooks/cve_response.yml`
- **`setup/terraform/`** — keep `main.tf`, `variables.tf`, `outputs.tf` but generalize tags to `ao-demo`, remove nginx-specific security group description
- **`group_vars/all.yml`** — keep with generic vars
- **`ao/example-workflow.json`** — minimal 2-node skeleton (trigger + one AAP job) showing the schema format
- **`.cursor/rules/project.md`** — rewrite for the baseline template

## What Gets Removed

These are demo-specific to the ticket enrichment project:

- `playbooks/gather_diagnostics.yml` — nginx-specific
- `playbooks/rollback_nginx_config.yml` — nginx-specific
- `scripts/break-nginx.sh` — demo-specific
- `scripts/fix-nginx.sh` — demo-specific
- `scripts/_ensure-ssh-access.sh` — can keep as utility but optional
- `setup/playbooks/setup_monitoring_stack.yml` — nginx/prometheus-specific
- `setup/playbooks/templates/*` — all nginx/prometheus/alertmanager templates
- `setup/playbooks/inventory/` — generated by terraform
- `ao/ticket-enrichment.json` — demo-specific
- `ao/ticket-enrichment-remediation.json` — demo-specific
- `DEMO_SCRIPT.md` — demo-specific
- `REQUIREMENTS.md` — replaced with generic version
- `workflow.mermaid` — replaced with generic version

## New Files

- **`README.md`** — "How to use this template" guide: clone, configure .env, terraform, setup, CaC, import AO workflow, publish, update webhook creds, re-run CaC
- **`REQUIREMENTS.md`** — generic AAP/AO/ServiceNow/AWS requirements
- **`.cursor/rules/project.md`** — baseline-specific rules: conventions, patterns, known gotchas (EDA credential path, SNOW close_code, CaC idempotency, two-pass CaC)
- **`setup/playbooks/setup_demo_host.yml`** — minimal placeholder playbook that installs a basic web server (just a stub with comments showing where to customize)
- **`setup/scripts/setup-apply.sh`** — generalized setup script

## File Structure

```
ao-baseline/
  .env.example
  .gitignore
  .cursorignore
  ansible.cfg
  ansible-navigator.yml
  README.md
  REQUIREMENTS.md
  group_vars/
    all.yml
  ao/
    example-workflow.json
  playbooks/
    trigger_ao_workflow.yml          # EDA-to-AO bridge (OAuth2) — reuse as-is
    manage_snow_incident.yml         # All incident ops: action=create|update|resolve
    manage_snow_change_request.yml   # All CR ops: action=create|authorize|update|review|close
    bridge_ao_approval.yml           # Bridge SNOW CR approval to AO approval gate
  rulebooks/
    example_eda_rulebook.yml         # Two rules: incident poll + CR approval bridge
  scripts/
    test-ao-approval-api.py          # Debug tool for AO approval API
  ansible_deployment/
    cac/
      apply.yml
      requirements.yml
      vars.yml
    ee/
      decision-environment.yml
    scripts/
      cac-apply.sh
  setup/
    terraform/
      main.tf
      variables.tf
      outputs.tf
    playbooks/
      setup_demo_host.yml
    scripts/
      setup-apply.sh
  .cursor/
    rules/
      project.md
```

## Reusable Patterns Included

### 1. EDA-to-AO Bridge (`trigger_ao_workflow.yml`)
The universal pattern for triggering AO workflows from EDA. Same in every AO project. Two HTTP calls: OAuth2 token, then POST event payload. Source: both projects.

### 2. AO Approval Bridge (`bridge_ao_approval.yml`)
Bridges ServiceNow CR approval to AO approval gates. When a CR moves to "Implement" in SNOW, EDA detects it, triggers this playbook, which authenticates with the AO API and programmatically approves the pending workflow step. Source: `ao-cve-remediation-scalable/playbooks/bridge_ao_approval.yml`.

### 3. ServiceNow ITSM Playbooks (action-based)
Two playbooks cover all SNOW operations, each driven by an `action` variable:
- **`manage_snow_incident.yml`** — `action: create` (publishes `inc_sys_id`/`inc_number` via `set_stats`), `action: update` (work notes + optional state), `action: resolve` (two-step: work notes then close with `close_code: "Solution provided"`)
- **`manage_snow_change_request.yml`** — `action: create` (emergency CR with justification, impl/backout/test plans, publishes `cr_sys_id`/`cr_number`), `action: authorize` (request approval), `action: update` (work notes), `action: review` (move to review), `action: close` (close CR)

AO workflow nodes call the same job template with different `action` values in extra_vars. Example: `{ "action": "create", "short_description": "...", "description": "..." }`

### 4. EDA Dual-Rule Rulebook
Two rules in one activation: (1) poll SNOW incidents and trigger AO workflow, (2) poll SNOW change requests and bridge approvals to AO. Source: `ao-cve-remediation-scalable/rulebooks/cve_response.yml`.

### 5. AO Workflow JSON Schema
Example workflow showing `schema_version: "2.0.0"`, `triggers` array, `nodes` with `aap_job_template` / `agentic` / `switch` / `approval` types, `edges` array with `from_port` for switch cases. Dynamic job template names via `${node.result.content.field}`.

### 6. CaC Credential Types
- **ServiceNow Credential** — injects `SN_HOST`, `SN_USERNAME`, `SN_PASSWORD` as env vars
- **AO Webhook Credential** — injects `webhook_base_url`, `webhook_client_id`, `webhook_client_secret` as extra_vars
- **AO API Credential** — service account for AO REST API (approval bridge). Injects `ao_sa_client_id`, `ao_sa_client_secret`, `ao_base_url` as extra_vars

### 7. Debug Tools
- `scripts/test-ao-approval-api.py` — probes the AO API for pending approvals, tests authentication, discovers API structure. Source: `ao-cve-remediation-scalable/scripts/test-ao-approval-api.py`.

## Key Design Decisions

- Every playbook is generalized with variable placeholders — no hardcoded demo-specific values
- The `trigger_ao_workflow.yml` bridge is identical across projects — never needs modification
- The EDA rulebook shows both incident polling and CR approval bridging as separate rules
- Terraform is minimal — just EC2 + VPC + Elastic IP + inventory generation. No application-specific setup
- The example AO workflow JSON shows all four node types (aap_job_template, agentic, switch, approval)
- CaC vars includes all three credential types and example job templates for every reusable playbook
- The `.cursor/rules/project.md` documents all gotchas discovered during development (SNOW close_code, EDA credential path, CaC idempotency, etc.)

## Reference Projects

When building from this baseline, reference these projects for real-world examples:
- `../ao-ticket-enrichment/` — simple enrichment + remediation (3-8 node workflows)
- `../ao-cve-remediation-scalable/` — complex fleet patching with parallel dev/prod paths, approval gates, dynamic job templates, SBOM diffing
