#!/usr/bin/env python3
"""
Debug tool: Test AO approval API connectivity and discover pending approvals.

Uses AO_SA_CLIENT_ID / AO_SA_CLIENT_SECRET from .env to authenticate,
then probes the AO API for pending approvals and attempts to approve one.

Usage:
  python3 scripts/test-ao-approval-api.py
"""

import subprocess, json, sys, os

# --- Load .env ---
env = {}
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip()

AO_BASE = env.get("AO_WEBHOOK_BASE_URL", "https://ao.example.com")
CLIENT_ID = env.get("AO_SA_CLIENT_ID", "")
CLIENT_SECRET = env.get("AO_SA_CLIENT_SECRET", "")

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: AO_SA_CLIENT_ID or AO_SA_CLIENT_SECRET not set in .env")
    sys.exit(1)

print(f"AO Base URL: {AO_BASE}")
print(f"Client ID:   {CLIENT_ID[:8]}...{CLIENT_ID[-4:]}")
print()


def curl(url, method="GET", headers=None, data=None, form_data=None):
    """Simple curl wrapper."""
    cmd = ["/usr/bin/curl", "-sk", "-X", method]
    for h in (headers or []):
        cmd += ["-H", h]
    if form_data:
        cmd += ["-H", "Content-Type: application/x-www-form-urlencoded", "-d", form_data]
    elif data:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.stdout


# --- Step 1: Get OAuth2 token ---
print("=" * 60)
print("STEP 1: Authenticate with AO (client_credentials)")
print("=" * 60)

token = None
form = f"grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
endpoint = f"{AO_BASE}/api/v1/auth/token"

print(f"\n  Trying: {endpoint}")
body = curl(endpoint, method="POST", form_data=form)
try:
    resp = json.loads(body)
    if "access_token" in resp:
        token = resp["access_token"]
        print(f"  ✅ Got token! (expires_in: {resp.get('expires_in', '?')}s)")
    else:
        print(f"  ❌ {resp.get('error', resp.get('detail', body[:100]))}")
except Exception:
    if "<html" in body.lower():
        print(f"  ❌ HTML response (not a valid endpoint)")
    else:
        print(f"  ❌ {body[:120]}")

if not token:
    print("\n❌ Could not authenticate with AO. Exiting.")
    sys.exit(1)

# --- Step 2: Discover API structure ---
print("\n" + "=" * 60)
print("STEP 2: Discover AO API structure")
print("=" * 60)

auth_header = f"Authorization: Bearer {token}"

paths_to_try = [
    "/api/v1/approvals",
    "/api/v1/executions",
    "/api/v1/workflows",
]

for path in paths_to_try:
    body = curl(f"{AO_BASE}{path}", headers=[auth_header])
    try:
        resp = json.loads(body)
        status = "✅" if "unauthorized" not in body.lower() and "error" not in body.lower() else "❌"
        preview = json.dumps(resp)[:150]
        print(f"  {status} {path} -> {preview}")
    except Exception:
        if body.strip():
            print(f"  ❌ {path} -> (non-JSON) {body[:80]}")
        else:
            print(f"  ❌ {path} -> (empty)")

# --- Step 3: Check SA permissions ---
print("\n" + "=" * 60)
print("STEP 3: Check SA identity and permissions")
print("=" * 60)

body = curl(f"{AO_BASE}/api/v1/auth/me", headers=[auth_header])
try:
    me = json.loads(body)
    print(f"  SA ID:       {me.get('id')}")
    print(f"  Username:    {me.get('username')}")
except Exception:
    print(f"  auth/me: {body[:200]}")

body = curl(f"{AO_BASE}/api/v1/authz/what_can_i", headers=[auth_header])
try:
    resp = json.loads(body)
    print(f"\n  Current permissions:")
    print(f"  {json.dumps(resp, indent=2)[:600]}")
except Exception:
    print(f"  what_can_i: {body[:200]}")

# --- Step 4: Find pending approvals ---
print("\n" + "=" * 60)
print("STEP 4: List pending approvals")
print("=" * 60)

body = curl(f"{AO_BASE}/api/v1/approvals", headers=[auth_header])
try:
    approvals = json.loads(body)
    pending = [a for a in approvals.get("resources", []) if a["status"] == "pending"]
    print(f"  Total approvals: {len(approvals.get('resources', []))}")
    print(f"  Pending approvals: {len(pending)}")

    for a in pending:
        print(f"\n  Approval: {a['id']}")
        print(f"    Name:      {a['name']}")
        print(f"    Node:      {a['approval_node_id']}")
        print(f"    Exec ID:   {a['execution_id']}")
        ctx = a.get('workflow_context', {}).get('inputs', {})
        print(f"    Context:   {json.dumps(ctx)[:200]}")
except Exception:
    print(f"  {body[:200]}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
