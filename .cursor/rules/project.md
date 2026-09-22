# AO Baseline Template — Project Rules

## What This Project Is

A reusable starter template for AO (Automation Orchestrator) projects. Provides the common patterns for AO automation: EDA-to-AO bridge, ServiceNow ITSM playbooks, AO approval bridge, CaC structure, Terraform base, and project scaffolding.

When building a new AO project, clone this repo, customize the playbooks/workflow for your use case, and update CaC vars.

## Capabilities — What This Template Can Do

This template provides reusable playbooks for AO workflows. Action-based playbooks take an `action` variable; single-purpose playbooks do one thing:

| Playbook | Job Template | Actions | What It Does |
|---|---|---|---|
| `trigger_ao_workflow.yml` | AO Workflow Bridge | n/a (single purpose) | EDA-to-AO bridge — triggers AO workflows from EDA |
| `manage_snow_incident.yml` | Manage SNOW Incident | `create`, `update`, `resolve` | Full incident lifecycle in ServiceNow |
| `manage_snow_change_request.yml` | Manage SNOW Change Request | `create`, `authorize`, `update`, `review`, `close` | Full CR lifecycle in ServiceNow |
| `bridge_ao_approval.yml` | Bridge AO Approval | n/a (single purpose) | Bridges SNOW CR approval to AO approval gate |
| `manage_git_repo.yml` | Manage Git Repo | `commit_file`, `create_pr` | Commit files and raise PRs via GitHub API |

All action-based playbooks follow the same pattern: pass `action` + parameters as extra_vars.

## Key Technical Decisions

### Environment Variables
- ServiceNow vars support both `SERVICENOW_*` and `SN_*` naming (`apply.yml` has fallback lookups)
- `DEMO_HOST_IP` is the generic placeholder for the demo EC2 host IP
- AO webhook credentials (`AO_WEBHOOK_PATH`, `AO_WEBHOOK_CLIENT_ID`, `AO_WEBHOOK_CLIENT_SECRET`) come from AO after publishing the workflow
- AO API service account (`AO_SA_CLIENT_ID`, `AO_SA_CLIENT_SECRET`) are for the approval bridge — separate from webhook creds

### ServiceNow PDI Gotchas
- `close_code` must be `"Solution provided"` (not `"Solved (Permanently)"` — confirmed via API on Washington DC PDI)
- Resolving an incident is a two-step operation: add work notes first, then resolve (single call gets rejected)
- Work notes must be wrapped in `[code]...[/code]` tags for proper HTML rendering in SNOW
- AI output should use HTML formatting (`<h3>`, `<p>`, `<ul>`, `<code>`, `<pre style="white-space: pre-wrap;">`)

### AO Workflow JSON Format
- Uses `schema_version: "2.0.0"`, `triggers` array, `edges` array, `${var}` syntax
- Node types: `aap_job_template`, `agentic`, `switch`, `approval`
- AAP job nodes use `parameters.job_template_name` and `parameters.extra_vars`
- Agentic nodes use `parameters.prompt` and `parameters.model`
- AI output is at `${node.result.content.field}` when using response schema, or `${node.result.content}` for raw text
- Switch conditions: `${node.result.content.field} == 'value'`
- Approval nodes use `from_port: "approved"` on outgoing edges

### EDA Gotchas
- EDA activations must NOT have event streams attached if using `servicenow.itsm.records` source from the rulebook
- The EDA controller credential needs host URL with `/api/controller/` path suffix (AAP 2.5+)
- The `webhook_path` is passed from EDA activation extra_vars → rulebook → bridge job → AO trigger
- EDA activation can't be updated by CaC while running — disable/re-enable in AAP UI
- CR approval bridge: `event.state == '-1'` is the Implement state in ServiceNow

### CaC Gotchas
- CaC cannot overwrite encrypted credential fields that already exist — delete the credential first or edit in AAP UI
- The controller project must be synced in AAP before CaC can create job templates referencing its playbooks
- The EDA project must also be synced separately for rulebook activations
- Two-pass CaC: first run creates objects with placeholder creds, second run (after AO publish) updates with real creds
- Uses `set -a; source .env; set +a` pattern for loading env vars (not `export $(grep | xargs)`)

### Action-Based Playbook Pattern
- `manage_snow_incident.yml` — `action: create|update|resolve`
- `manage_snow_change_request.yml` — `action: create|authorize|update|review|close`
- `manage_git_repo.yml` — `action: commit_file|create_pr`
- AO workflow nodes call the same job template with different `action` values in extra_vars
- The `create`/`commit_file`/`create_pr` actions publish identifiers via `set_stats` — subsequent nodes reference them as `${node.artifacts.field}`

### GitHub Integration
- Uses GitHub REST API (Contents API for commits, Pulls API for PRs)
- `GITHUB_TOKEN` is injected as env var by the "GitHub API Token" credential type
- `GITHUB_REPO` is set in `.env` and read by playbooks via `lookup('env', ...)`
- `commit_file` action: creates or updates a file, supports branching (auto-creates branch if needed)
- `create_pr` action: opens a PR from `head_branch` to `base_branch` (default: main)
- Publishes `commit_sha`/`file_url` or `pr_number`/`pr_url` via `set_stats`
- File content is base64-encoded automatically — pass raw content in `file_content`

### Infrastructure
- Terraform provisions EC2 + VPC + Elastic IP in eu-west-1
- SSH key is generated by Terraform at `setup/terraform/demo-key.pem`
- Ansible inventory is auto-generated at `setup/playbooks/inventory/hosts.yml`

### Container Images
- DE and EE build definitions live in `dependencies/de/` and `dependencies/ee/`
- `dependencies/build-images.sh` builds both with `ansible-builder` and optionally pushes
- The DE image tag is configured via `DE_IMAGE` env var — CaC reads it in `apply.yml`
- Base images require `podman login registry.redhat.io`

## Scripts
- `./dependencies/build-images.sh` — builds DE + EE container images
- `./setup/scripts/setup-apply.sh` — configures demo host
- `./setup/scripts/teardown.sh` — destroys Terraform infrastructure
- `./ansible_deployment/scripts/cac-apply.sh` — applies all AAP/EDA objects
- `./scripts/test-trigger.sh` — fires a test event to verify the EDA-to-AO pipeline
- `./scripts/test-ao-approval-api.py` — debug tool for AO approval API

## Deployment Order
1. Build DE + EE images (`./dependencies/build-images.sh --push`)
2. `terraform apply` (provisions EC2)
3. `setup-apply.sh` (installs application on demo host)
4. `cac-apply.sh` (creates AAP objects — needs project synced first)
5. Import AO workflow in AO UI, configure agentic nodes, publish
6. Update `.env` with AO webhook creds, re-run `cac-apply.sh`
7. Restart EDA activation in AAP UI
