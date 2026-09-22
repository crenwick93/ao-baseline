#!/usr/bin/env bash
set -eo pipefail

# Destroy all Terraform-provisioned infrastructure.
#
# Usage:
#   ./setup/scripts/teardown.sh
#
# This runs 'terraform destroy' in setup/terraform/.
# The SSH key and generated inventory are removed automatically.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../terraform"

if [[ ! -d "${TF_DIR}/.terraform" ]]; then
  echo "ERROR: Terraform not initialized. Nothing to destroy."
  exit 1
fi

echo "Destroying infrastructure in ${TF_DIR}..."
cd "${TF_DIR}"
terraform destroy "$@"
