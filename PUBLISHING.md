# Publishing the `brocade.fos` Collection to Automation Hub

This document describes how to build and publish the `brocade.fos` Ansible collection to
both a **Private (on-prem) Automation Hub** and the **Red Hat hosted Automation Hub**
(console.redhat.com).

---

## Certification process

Use the ordered checklist below to record automated checks, live-switch results,
account entitlements, and GitHub execution for the 3.0.0 major release.
Red Hat Partner Engineering reviews the staged collection for certification
before publishing it to the certified catalog.

## 0. Prerequisites

- `ansible-core` >= 2.16 installed (`ansible-galaxy --version`).
- Network access to the target hub.
- An API token for the target hub (see each section below for where to get it).
- The `brocade` **namespace must already exist** on the target hub and your account must be
  an owner of it. If it does not exist, an Automation Hub administrator must create it first;
  otherwise, publication will be rejected.
- The version in `galaxy.yml` must **not** already exist on the target hub — Automation Hub
  refuses to overwrite an existing version. Bump `version:` in `galaxy.yml` for every release.

---

## 1. Build the collection artifact

From the collection root (the directory containing `galaxy.yml`):

```bash
ansible-galaxy collection build --force
```

This produces a tarball named `brocade-fos-<version>.tar.gz` (e.g. `brocade-fos-3.0.0.tar.gz`).

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
git tag v<version>        # e.g. v3.0.0
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


## Certification validation checklist

Work through these items in order. Complete only the first unchecked item, save
its evidence, and mark its checkbox after every acceptance criterion passes.
Replace angle-bracket placeholders with your actual values before executing commands.
Stop on failure or missing access; record the error and resolve it before moving
on. The checkboxes are a human release checklist; GitHub branch protection
provides the automated merge gate. Keep credentials and unsanitized switch
responses in private evidence storage.

### 1. Confirm the source and release

- [ ] Completed: public source and release verified.

From the collection root:

```bash
git status --short
git rev-parse HEAD
gh repo view brocade/brocade.fos --json url,visibility,defaultBranchRef
```

Acceptance: the official repository resolves, is public (or the collection is
publicly available on Galaxy), the merge branch is `main`, and the reviewed
release uses version 3.0.0 with a matching changelog. Verify public
access in a signed-out browser too. If the actual merge branch differs, update
both workflow triggers before proceeding. Save the release commit identifier
and source URL; for local changes also retain the reviewed diff until committed.

### 2. Reproduce automated checks where needed

- [ ] Completed: all required automated checks passed on the release.

Prerequisites: `python` matching
[.python-version](https://github.com/brocade/brocade.fos/blob/main/.python-version),
Git, and a working Docker or Podman engine. These are development tools, not
customer execution-environment installation steps. From the collection root,
verify the interpreter and use an isolated copy in the canonical collection directory:

```bash
python --version
python -c 'import pathlib, platform; expected = pathlib.Path(".python-version").read_text().strip(); actual = platform.python_version(); assert actual == expected, f"Expected {expected}, found {actual}"'
cert_python_minor=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
cert_work=$(mktemp -d)
mkdir -p "$cert_work/ansible_collections/brocade/fos"
git ls-files -z --cached --others --exclude-standard |
  tar --null -T - -cf - |
  tar -xf - -C "$cert_work/ansible_collections/brocade/fos"
python -m venv "$cert_work/tools"
"$cert_work/tools/bin/python" -m pip install \
  ansible-core==2.16.19 ansible-lint==26.4.0 galaxy-importer==0.4.39 distlib
cd "$cert_work/ansible_collections/brocade/fos"
"$cert_work/tools/bin/ansible-lint" --offline --profile production
```

Run the checker matrix using isolated environments for each supported branch:

```bash
for core_branch in stable-2.16 stable-2.18 stable-2.20; do
  python -m venv "$cert_work/$core_branch"
  "$cert_work/$core_branch/bin/python" -m pip install \
    "https://github.com/ansible/ansible/archive/refs/heads/$core_branch.tar.gz"
  "$cert_work/$core_branch/bin/ansible-test" sanity --docker default --python "$cert_python_minor" || break
  "$cert_work/$core_branch/bin/ansible-test" units --docker default --python "$cert_python_minor" || break
done
```

For Podman, set `ANSIBLE_TEST_PREFER_PODMAN=1` before running the commands.
Verify all three branches ran; stopping on a failing branch does not pass the
matrix. The Python selector is derived from `python` rather than hard-coded.
Container images manage their own Python patch versions; save the actual
interpreter version with each certification result. For release qualification
with the exact `.python-version` interpreter, use `--venv` instead of
`--docker default` in both commands. Qualification of other Python versions
is outside the current release scope.

Run the importer with the same configuration as the checker:

```bash
cat > "$cert_work/galaxy-importer.cfg" <<'EOF'
[galaxy-importer]
CHECK_REQUIRED_TAGS=True
RUN_ANSIBLE_LINT=False
EOF
GALAXY_IMPORTER_CONFIG="$cert_work/galaxy-importer.cfg" \
  "$cert_work/tools/bin/python" -m galaxy_importer.main \
  --git-clone-path . --output-path "$cert_work"
```

Acceptance: every command exits zero; all three sanity jobs run, production lint
has no failures, regression units pass on each branch, and import succeeds. Save tool versions and full logs, including
any allowed warnings. Dependencies and versions above match checker v6.0.0;
recheck them when changing the workflow pin. Return to the original checkout
before subsequent steps. Keep `$cert_work` for evidence until release completion.

### 3. Verify GitHub Actions execution

- [ ] Completed: certification workflow passed on the release PR.

Prerequisites: push the reviewed release branch and open its PR against
`main`; GitHub Actions must be enabled and organization policy must allow the
referenced reusable workflow. The source changes remain uncommitted until the
maintainer chooses to commit and push them.

```bash
gh pr checks <PR_NUMBER> --watch
gh run list --workflow certification.yml --event pull_request --limit 5
gh run view <RUN_ID> --verbose
gh run view <RUN_ID> --log
```

Acceptance: the run belongs to the release PR, with no startup/permission
errors. Build/import, production lint, sanity and regression units on 2.16/2.18/2.20, and
**Certification required** all succeed. Save the PR URL, run URL, and job results.
A local lint result does not replace this check. Manual dispatch becomes
available after the workflow exists on the default branch.

### 4. Require successful checks before merge

- [ ] Completed: merge protection verified.

In repository **Settings > Rules > Rulesets** or **Settings > Branches**, protect
`main`, require pull requests, and require the GitHub Actions status check
**Certification required** using its exact name from the first successful run.
Require the branch to be up to date and apply the rule to the intended users,
including administrators if your release policy requires it. Avoid bypass access
for routine merges. If using merge queues, add a `merge_group` workflow trigger
before enabling the queue.

Acceptance: an unprivileged user's PR with pending/failed certification cannot
merge. Verify in a disposable PR that introduces a YAML lint violation, wait for
the failure, observe the blocked merge, then remove the violation and rerun.
Close the disposable PR without merging. Save the rule details and both run URLs.

### 5. Confirm partner access and support

- [ ] Completed: organizational prerequisites verified.

Sign in to the Red Hat account associated with the partner organization:

1. Confirm the signed Ansible Certification Appendix and partner registration.
2. Check the applicable Partner Subscription support case for active entitlement; an open
   request alone does not demonstrate activation.
3. Confirm you can upload under the hosted Hub `brocade` namespace, not merely
   view it. Check the namespace ownership/permissions with the administrator.
4. Confirm TSANet registration, co-support contacts, and the maintainer responsible
   for annual releases and at least two supported AAP/core combinations.
5. Review managed-node counting with Partner Engineering for these local REST
   connection playbooks. Record the applicable approach and any required changes.
6. Review the existing GPL-3.0-or-later/BSD-2-Clause declarations with the
   maintainer. Copyright notices are preserved; the permitted missing-GPL-header
   sanity exception is used. Any future SPDX allocation needs owner confirmation.

Acceptance: each prerequisite is confirmed. Save case/entitlement references,
namespace permission evidence, support ownership, and any license clarification
privately. Do not place API tokens in logs, issue attachments, or Git.

### 6. Run live-switch validation separately

- [ ] Completed: live compatibility results recorded by the maintainer.

Use an isolated switch/fabric, a saved configuration, REST connectivity, and an
account authorized for the chosen test. Use FOS 10.0.1 and 9.2.2d with supported
execution environments containing core 2.16 and 2.18 and `python` matching
`.python-version`. Verify `python --version` inside each environment, not only
on the host. Install the same release
tarball in each environment and record its SHA-256 checksum. Store switch
credentials using Ansible Vault or an AAP credential. Never run the destructive
example playbooks wholesale against a production fabric.

For each FOS/core combination:

1. Run `playbooks/tasks/facts.yml` against one lab host using the sample inventory
   structure and Vault-encrypted credentials:

   ```bash
   ansible-playbook -i <LAB_INVENTORY> playbooks/tasks/facts.yml \
     --limit <LAB_HOST> -e @<VAULT_FILE> --ask-vault-pass
   ```

2. Verify on the switch that a unique `cert_300_<run_id>` alias is unused.
   Add `lab_alias_name`, `lab_wwn` (a lab-only WWN), and `lab_vfid` to your private
   Vault file alongside `credential`. Create this temporary smoke playbook:

   ```bash
   cert_lab_dir=$(mktemp -d)
   cat > "$cert_lab_dir/smoke.yml" <<'YAML'
   ---
   - name: Validate disposable FOS zoning alias
     hosts: fos_switches
     gather_facts: false
     tasks:
       - name: Require an explicitly named lab object
         ansible.builtin.assert:
           that:
             - lab_alias_name is match('^cert_300_[A-Za-z0-9_]{1,50}$')
             - lab_wwn is match('^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){7}$')
         tags: [always]

       - name: Preview alias creation without writing
         brocade.fos.brocade_zoning_alias:
           credential: "{{ credential }}"
           vfid: "{{ lab_vfid | default(-1) }}"
           aliases:
             - name: "{{ lab_alias_name }}"
               members: ["{{ lab_wwn }}"]
         check_mode: true
         tags: [preview]

       - name: Exercise alias creation and idempotency
         block:
           - name: Create disposable alias
             brocade.fos.brocade_zoning_alias:
               credential: "{{ credential }}"
               vfid: "{{ lab_vfid | default(-1) }}"
               aliases:
                 - name: "{{ lab_alias_name }}"
                   members: ["{{ lab_wwn }}"]
             register: created

           - name: Repeat the same desired alias
             brocade.fos.brocade_zoning_alias:
               credential: "{{ credential }}"
               vfid: "{{ lab_vfid | default(-1) }}"
               aliases:
                 - name: "{{ lab_alias_name }}"
                   members: ["{{ lab_wwn }}"]
             register: repeated

           - name: Check creation and second-run idempotency
             ansible.builtin.assert:
               that:
                 - created.changed
                 - not repeated.changed
         always:
           - name: Clean up the disposable alias
             brocade.fos.brocade_zoning_alias:
               credential: "{{ credential }}"
               vfid: "{{ lab_vfid | default(-1) }}"
               aliases_to_delete:
                 - name: "{{ lab_alias_name }}"

       - name: Repeat deletion of the absent alias
         brocade.fos.brocade_zoning_alias:
           credential: "{{ credential }}"
           vfid: "{{ lab_vfid | default(-1) }}"
           aliases_to_delete:
             - name: "{{ lab_alias_name }}"
         register: deleted_again

       - name: Check deletion idempotency
         ansible.builtin.assert:
           that: not deleted_again.changed
   YAML
   ```

3. Preview only, then confirm on the switch that no alias was created:

   ```bash
   ansible-playbook -i <LAB_INVENTORY> "$cert_lab_dir/smoke.yml" \
     --limit <LAB_HOST> -e @<VAULT_FILE> --ask-vault-pass --tags preview
   ```

4. Run the full smoke test and verify on the switch that cleanup removed the
   alias. Require successful assertions and an unchanged repeated deletion:

   ```bash
   ansible-playbook -i <LAB_INVENTORY> "$cert_lab_dir/smoke.yml" \
     --limit <LAB_HOST> -e @<VAULT_FILE> --ask-vault-pass
   ```

5. With a separate intentionally invalid credential, run the facts test and
   require a useful failure without passwords in the captured output. Restore
   the valid credential afterward. Verify no test objects remain.

Review the playbooks before running them; this is focused smoke coverage, not
validation of every module. Firmware, password, active-zone, and disruptive
configuration operations require separately scoped lab scenarios if claimed as
validated. If a scenario fails, preserve logs, restore the lab, and keep this
item open rather than publishing an unsupported compatibility claim.

Acceptance: the selected scenarios pass for all four combinations, cleanup is
complete, and known limitations are documented. Save sanitized logs, switch model,
FOS/core/Python versions, test identifiers, commit, artifact checksum, and results
in the release validation issue. Update `versioning.rst` with completed evidence.
After verifying cleanup and saving logs, remove `$cert_lab_dir`.

### 7. Freeze and verify the artifact

- [ ] Completed: final artifact and release metadata verified.

After all fixes and documentation changes:

```bash
ansible-galaxy collection build --force
sha256sum brocade-fos-3.0.0.tar.gz
tar -tvzf brocade-fos-3.0.0.tar.gz
cert_install=$(mktemp -d)
ansible-galaxy collection install ./brocade-fos-3.0.0.tar.gz \
  --collections-path "$cert_install" --offline --no-deps
ANSIBLE_COLLECTIONS_PATH="$cert_install" \
  ansible-doc brocade.fos.brocade_facts
```

Acceptance: artifact version is 3.0.0; the changelog covers it; module discovery
works; LICENSE, BSD text, and the resolving GPL symlink are present; no caches,
binary build products, credentials, or development environments are packaged.
Re-run checks and affected live tests if the release changes. Save the final
checksum and logs, then remove the disposable installation directory.

### 8. Upload for certification review

- [ ] Completed: staged upload and Red Hat review request recorded.

Follow section 3B with the approved artifact and your privately supplied token.
Check the Hub import task for success; notify Partner Engineering through your
established channel with collection name, version, test evidence, and any known
limitations. Uploads enter staging; do not describe the collection as certified
before approval. Keep the final artifact checksum and import task identifier.

### 9. Verify approval and availability

- [ ] Completed: Red Hat approval and hosted installation verified.

After Red Hat confirms approval, use a fresh installation directory:

```bash
cert_hub_install=$(mktemp -d)
ansible-galaxy collection install brocade.fos:==3.0.0 \
  --server rh_hosted_ah --token "$RH_AH_TOKEN" \
  --collections-path "$cert_hub_install"
ANSIBLE_COLLECTIONS_PATH="$cert_hub_install" \
  ansible-doc brocade.fos.brocade_facts
```

Acceptance: the approved version is available from hosted Hub and its module
documentation loads. Save Red Hat approval and installation evidence, finalize
the release date, and tag the release as described above. Remove the temporary
installation after saving results. Review support ownership and lifecycle
coverage with each subsequent release.
