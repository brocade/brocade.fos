# Publishing the `brocade.fos` Collection to Automation Hub

This document describes how to build and publish the `brocade.fos` Ansible collection to
both a **Private (on-prem) Automation Hub** and the **Red Hat hosted Automation Hub**
(console.redhat.com).

---

## 0. Prerequisites

- `ansible-core` >= 2.15 installed (`ansible-galaxy --version`).
- Network access to the target hub.
- An API token for the target hub (see each section below for where to get it).
- The `brocade` **namespace must already exist** on the target hub and your account must be
  an owner of it. If it does not exist, an Automation Hub administrator must create it first,
  otherwise the publish will be rejected.
- The version in `galaxy.yml` must **not** already exist on the target hub — Automation Hub
  refuses to overwrite an existing version. Bump `version:` in `galaxy.yml` for every release.

---

## 1. Build the collection artifact

From the collection root (the directory containing `galaxy.yml`):

```bash
ansible-galaxy collection build --force
```

This produces a tarball named `brocade-fos-<version>.tar.gz` (e.g. `brocade-fos-2.2.0.tar.gz`).

Verify it excludes dev/local files and contains the modules:

```bash
tar tzf brocade-fos-*.tar.gz | grep -E '(\.git|\.vscode|\.claude|\.ansible-lint|ruff\.toml)'   # should print nothing
tar tzf brocade-fos-*.tar.gz | grep -c 'plugins/modules/.*\.py'                                 # module count
```

---

## 2. Configure the hub servers (`ansible.cfg`)

Create or edit an `ansible.cfg` (repo-local is fine). Define **both** servers so you can switch
between them with `--server`:

```ini
[galaxy]
# Order matters only for installs; for publish we always pass --server explicitly.
server_list = private_ah, rh_hosted_ah

# ---- Private / on-prem Automation Hub ----
[galaxy_server.private_ah]
url = https://<PRIVATE_AH_HOST>/api/galaxy/content/published/
# token is supplied via env var / CLI, NOT stored here (see below)

# ---- Red Hat hosted Automation Hub (console.redhat.com) ----
[galaxy_server.rh_hosted_ah]
url = https://console.redhat.com/api/automation-hub/content/published/
auth_url = https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token
# token is supplied via env var / CLI, NOT stored here (see below)
```

> Replace `<PRIVATE_AH_HOST>` with your Private AH hostname, e.g.
> `automation-hub.internal.example.com`. On many Private AH installs the publish repo is
> `published`; if your hub uses a different repository, adjust the path segment accordingly
> (`.../content/<repo>/`).

### Keep tokens out of git

Do **not** write tokens into a committed `ansible.cfg`. Use one of:

- Pass `--token "$TOKEN"` on the CLI (shown below), or
- Put the token in a private, git-ignored config (e.g. `~/.ansible.cfg`), or
- Use Ansible Vault / a secrets manager.

---

## 3A. Publish to a Private (on-prem) Automation Hub

1. **Get the token:** in the Private AH web UI, go to **Collections → API token** (or
   **Repo Management → API token**) and copy/generate the token.

2. **Export it and publish:**

   ```bash
   export PRIVATE_AH_TOKEN='<paste-token-here>'

   ansible-galaxy collection publish brocade-fos-<version>.tar.gz \
     --server private_ah \
     --token "$PRIVATE_AH_TOKEN"
   ```

   If your Private AH uses a self-signed certificate, add `--ignore-certs` (or set
   `validate_certs = false` under the `[galaxy_server.private_ah]` section) — only if your
   security policy permits it.

3. **Approval:** the upload usually lands in a **staging** repository and may require an admin
   to approve it before it appears under `published`. Check the AH UI → Approval / Staging.

4. **Verify install:**

   ```bash
   ansible-galaxy collection install brocade.fos -s private_ah --token "$PRIVATE_AH_TOKEN"
   ```

---

## 3B. Publish to the Red Hat hosted Automation Hub (console.redhat.com)

1. **Get the offline token:** sign in at
   <https://console.redhat.com/ansible/automation-hub/token> and generate/copy the
   **offline token** (also called the API token). This token, together with the `auth_url`
   configured above, is exchanged for a short-lived bearer token automatically.

2. **Export it and publish:**

   ```bash
   export RH_AH_TOKEN='<paste-offline-token-here>'

   ansible-galaxy collection publish brocade-fos-<version>.tar.gz \
     --server rh_hosted_ah \
     --token "$RH_AH_TOKEN"
   ```

3. **Approval:** uploads go through Red Hat's staging/certification flow. The collection appears
   under your `brocade` namespace once processing/approval completes.

4. **Verify install:**

   ```bash
   ansible-galaxy collection install brocade.fos -s rh_hosted_ah --token "$RH_AH_TOKEN"
   ```

---

## 4. Tag the release

After the release PR merges, tag the repo to match `galaxy.yml`:

```bash
git tag v<version>        # e.g. v2.2.0
git push origin v<version>
```

Keep the git tag and the `galaxy.yml` `version:` in sync for every release.

---

## Quick reference

| | Private AH | Red Hat hosted AH |
|---|---|---|
| `--server` name | `private_ah` | `rh_hosted_ah` |
| `url` | `https://<PRIVATE_AH_HOST>/api/galaxy/content/published/` | `https://console.redhat.com/api/automation-hub/content/published/` |
| `auth_url` | *(none)* | `https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token` |
| Token source | AH UI → API token | console.redhat.com → API/offline token |
| Token env var (example) | `PRIVATE_AH_TOKEN` | `RH_AH_TOKEN` |

Build once, publish the **same** `brocade-fos-<version>.tar.gz` to either hub.
