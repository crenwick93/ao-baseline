# Dependencies — EE & DE Container Images

This directory contains build definitions for the container images used by this AO project.

## Decision Environment (DE)

Used by **EDA rulebook activations**. Includes `servicenow.itsm` for the SNOW records source plugin and `ansible.eda` for event filters.

- Definition: `de/decision-environment.yml`
- Base image: `de-minimal-rhel9` (AAP 2.5)

## Execution Environment (EE)

Used by **AAP job templates**. Includes `servicenow.itsm` for incident/CR management and `ansible.controller` for controller API operations.

- Definition: `ee/execution-environment.yml`
- Base image: `ee-minimal-rhel9` (AAP 2.5)

## Building

### Prerequisites

```bash
pip install ansible-builder
podman login registry.redhat.io    # for base images
podman login your-registry         # for pushing
```

### Build both images

```bash
REGISTRY=quay.io/myorg ./dependencies/build-images.sh
```

### Build and push

```bash
REGISTRY=quay.io/myorg ./dependencies/build-images.sh --push
```

### Build individually

```bash
ansible-builder build -f dependencies/de/decision-environment.yml -t quay.io/myorg/snow-de:latest
ansible-builder build -f dependencies/ee/execution-environment.yml -t quay.io/myorg/ao-ee:latest
```

## After Building

1. Update `.env` with your DE image tag:
   ```
   DE_IMAGE=quay.io/myorg/snow-de:latest
   ```

2. Re-run CaC to update the EDA decision environment:
   ```bash
   ./ansible_deployment/scripts/cac-apply.sh
   ```

3. If using a custom EE for job templates, update the EE in AAP Controller UI or add it to `ansible_deployment/cac/vars.yml`.
