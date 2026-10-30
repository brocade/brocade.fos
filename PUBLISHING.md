# Publishing the `brocade.fos` Collection to Red Hat Automation Hub and Ansible Galaxy

This document describes how to build and publish the `brocade.fos` Ansible collection to
both **Ansible Galaxy** (galaxy.ansible.com) and the **Red Hat hosted Automation Hub**
(console.redhat.com).

---

## 0. Prerequisites

- `ansible-core` installed at a version allowed by `requires_ansible` in
  `meta/runtime.yml` (`ansible-galaxy --version`).
- The `brocade` namespace must already exist on Galaxy and Automation Hub, and your account
  must own it, or publication is rejected. On Galaxy, ownership is tied to your GitHub
  account; on Automation Hub, Red Hat Partner Engineering or a hub administrator manages it.

---

## 1. Set the release version and build the artifact

Before building:

1. Add the new release to the release history in [versioning.md](versioning.md),
   choosing the version number by its release criteria.
2. Set `version:` in `galaxy.yml` to that version. Neither server accepts a
   version that already exists.
3. If `python_requires` in `tests/config.yml` changed, or the collection now
   needs external Python packages, update the **Requirements** section of
   [README.md](README.md) to match. Red Hat certification requires the README
   to state the minimum Python version and any external dependencies.

   Each version file answers a different question. Change only the ones the
   release requires, and do not copy the tested versions into the support floors:

   | File and key                          | Meaning                                   | Update when                                                  |
   | ------------------------------------- | ----------------------------------------- | ------------------------------------------------------------ |
   | `galaxy.yml` `version:`               | Release version (three-part semver)       | Every release                                                |
   | `versioning.md` newest row            | FOS, ansible-core, and Python tested      | Every release                                                |
   | `meta/runtime.yml` `requires_ansible` | Minimum supported ansible-core            | Support is deliberately raised or dropped, not for new tests |
   | `tests/config.yml` `python_requires`  | Python range for controller tests         | Support is deliberately raised or dropped                    |
   | `.python-version`                     | Python used by `hacking/` and CI          | `python_requires` changes; keep it inside that range         |

   If `requires_ansible` or `python_requires` changes, also run
   `hacking/run_checks.sh` and repeat live-switch validation on the lowest and
   highest supported combinations.
4. Remove duplicate pending fragments in `changelogs/fragments/`.
5. Validate the fragments and incorporate them into the release:

   ```bash
   hacking/release_changelog.sh
   ```

6. Review the version, YAML history, generated notes, and consumed fragments:

   ```bash
   git diff -- galaxy.yml changelogs/ CHANGELOG.rst
   git diff --check HEAD
   ```

   `keep_fragments: false` in `changelogs/config.yaml` removes consumed fragments.
   Commit their deletions with `galaxy.yml`, `changelogs/changelog.yaml`, and
   `CHANGELOG.rst`. `antsibull-changelog generate` alone does not incorporate
   pending fragments.
7. Validate the changes on a FOS switch using the supported FOS releases.
8. Ensure the certification workflow passes on the PR. It runs collection
   build/import checks, production lint, and full sanity tests through Red
   Hat's Partner Certification Checker. These checks do not exercise a live
   switch, so step 7 is still required.
9. Merge the approved pull request into `main` before publishing the collection.

From the collection root (the directory containing `galaxy.yml`):

```bash
ansible-galaxy collection build --force
```

This produces a tarball named `brocade-fos-<version>.tar.gz`. Verify the artifact
before publishing: record its checksum, then install it into a temporary directory
and confirm the module documentation loads.

```bash
sha256sum brocade-fos-<version>.tar.gz
verify_dir=$(mktemp -d)
ansible-galaxy collection install ./brocade-fos-<version>.tar.gz \
  --collections-path "$verify_dir" --offline --no-deps
ANSIBLE_COLLECTIONS_PATH="$verify_dir" ansible-doc brocade.fos.brocade_facts
rm -rf "$verify_dir"
```

---

## 2. Configure the servers (`ansible.cfg`)

Create or edit an `ansible.cfg` (repo-local is fine). Define **both** servers so you can switch
between them with `--server`:

```ini
[galaxy]
# Order matters only for installs; for publish we always pass --server explicitly.
server_list = galaxy, rh_hosted_ah

# ---- Ansible Galaxy ----
[galaxy_server.galaxy]
url = https://galaxy.ansible.com/
# token is supplied via --token from Ansible Vault, NOT stored here (see below)

# ---- Red Hat hosted Automation Hub (console.redhat.com) ----
[galaxy_server.rh_hosted_ah]
url = https://console.redhat.com/api/automation-hub/content/published/
auth_url = https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token
# token is supplied via --token from Ansible Vault, NOT stored here (see below)
```

### Store tokens in Ansible Vault

Do **not** write tokens into `ansible.cfg` or anywhere in the repository. Keep each
token in an Ansible Vault encrypted file outside the checkout. Create each file once;
`ansible-vault` prompts for a new vault password and opens an editor where you paste
only the token:

```bash
mkdir -p ~/.ansible-secrets
ansible-vault create ~/.ansible-secrets/galaxy_token.vault
ansible-vault create ~/.ansible-secrets/rh_ah_token.vault
```

Each publish section below loads its token from these files into an environment
variable. Clear them when you finish:

```bash
unset GALAXY_TOKEN RH_AH_TOKEN
```

When a token is regenerated, replace it with
`ansible-vault edit ~/.ansible-secrets/<file>.vault`.

---

## 3A. Publish to Ansible Galaxy

1. **Get the token:** sign in at <https://galaxy.ansible.com> with the GitHub account that
   owns the `brocade` namespace, then open <https://galaxy.ansible.com/ui/token/> (or
   **Collections → API token**) and copy the token.

2. **Export it and publish:**

   ```bash
   export GALAXY_TOKEN="$(ansible-vault view ~/.ansible-secrets/galaxy_token.vault)"

   ansible-galaxy collection publish brocade-fos-<version>.tar.gz \
     --server galaxy \
     --token "$GALAXY_TOKEN"
   ```

   The command waits for the import to finish and fails if the import fails. Add
   `--no-wait` to return immediately and check the import log in the Galaxy UI instead.

3. **Approval:** Galaxy has no manual approval or staging step. The version is published
   once the automated import succeeds. Fix any import errors, bump `version:` in
   `galaxy.yml`, then rebuild and publish again; a published version cannot be
   re-uploaded.

4. **Verify install:**

   ```bash
   ansible-galaxy collection install brocade.fos -s galaxy
   ```

---

## 3B. Publish to the Red Hat hosted Automation Hub (console.redhat.com)

1. **Get the offline token:** sign in at
   <https://console.redhat.com/ansible/automation-hub/token> and generate/copy the
   **offline token** (also called the API token). This token, together with the `auth_url`
   configured above, is exchanged for a short-lived bearer token automatically.

2. **Export it and publish:**

   ```bash
   export RH_AH_TOKEN="$(ansible-vault view ~/.ansible-secrets/rh_ah_token.vault)"

   ansible-galaxy collection publish brocade-fos-<version>.tar.gz \
     --server rh_hosted_ah \
     --token "$RH_AH_TOKEN"
   ```

3. **Approval:** uploads go through Red Hat's staging/certification flow. The collection appears
   under `brocade` namespace once processing/approval completes.

4. **Verify install:**

   ```bash
   ansible-galaxy collection install brocade.fos -s rh_hosted_ah --token "$RH_AH_TOKEN"
   ```

---

## 4. Tag the release

After the release PR merges, tag the repo to match `galaxy.yml`:

```bash
git tag v<version>        # e.g. v1.2.3
git push origin v<version>
```

Keep the git tag and the `galaxy.yml` `version:` in sync for every release.

---

## Quick reference

|                         | Ansible Galaxy                 | Red Hat hosted AH                                                                  |
| ----------------------- | ------------------------------ | ---------------------------------------------------------------------------------- |
| `--server` name         | `galaxy`                       | `rh_hosted_ah`                                                                     |
| `url`                   | `https://galaxy.ansible.com/`  | `https://console.redhat.com/api/automation-hub/content/published/`                 |
| `auth_url`              | *(none)*                       | `https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token` |
| Token source            | galaxy.ansible.com → API token | console.redhat.com → API/offline token                                             |
| Token env var (example) | `GALAXY_TOKEN`                 | `RH_AH_TOKEN`                                                                      |
| Approval                | None (automated import)        | Red Hat staging/certification review                                               |

Build once, publish the **same** `brocade-fos-<version>.tar.gz` to both servers.
