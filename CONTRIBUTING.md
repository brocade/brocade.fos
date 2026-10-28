# Contribution

Complete setup, make changes, run checks, and update the changelog. Then choose
the pull-request or release workflow. Run Bash commands from the repository root.
Replace example branch names, filenames, and changelog text.

## Development Setup

1. Create a contribution or release branch from the latest origin/main.

2. Install the Python version in `.python-version` and make it available as `python`. Verify the required Python version.

```bash
python hacking/check_python_version.py
```

3. Create and activate the development environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install development, changelog, and documentation tools.

```bash
python -m pip install -r dev-requirements.txt
```

Reactivate `.venv` in each new terminal. Other shells need their equivalent
activation command.

## Making Changes

1. Keep the contribution focused on one issue or feature.
2. Update module documentation and examples when arguments or behavior change.
   Use raw strings for `DOCUMENTATION`, `EXAMPLES`, and `RETURN`; match argument
   types, defaults, requirements, and choices to the module specification.
3. Use fully qualified names, such as `brocade.fos.brocade_facts` and
   `ansible.builtin.debug`, in examples.
4. Set new `version_added` values to the collection version introducing the
   module or option. Preserve existing introduction versions.
5. Add regression tests as `test_*.py` under `tests/unit/`. Switch connections
   must be mocked; the unit suite discovers new test files automatically.
6. Preserve existing copyright and license notices. Unrelated changes must not
   change license allocations.

### Documentation Conventions

Keep real credentials, network data, and personally identifiable information out
of examples, logs, and commits. Use these placeholders instead; IP ranges are
TEST-NET blocks from RFC 5737.

| Value             | Placeholder                                                    |
| ----------------- | -------------------------------------------------------------- |
| Switch/host IP    | `198.51.100.x`, such as `198.51.100.1`                         |
| DNS/NTP/syslog IP | `203.0.113.x`, such as `203.0.113.10`                          |
| Port WWN          | Start with `aa:bb:cc:dd:ee:ff:11:11`; increment the last octet |
| Domain            | `example.com`, `example.net`, `example.org`                    |
| Email             | `sender@example.com`, `receiver@example.com`                   |
| Credentials       | `user_name`, `user_password`, `vault_password`                 |
| Location          | `Data Center 1`, `Data Center 2`                               |
| Zone/config/alias | `zone_1`, `cfg_1`, `alias_host_1`                              |

## Running Checks and Tests

Activate the development environment, then run from the source checkout:

```bash
# Show check options, descriptions, and discovered unit test files.
hacking/run_checks.sh --list

# Run the default check suites against your current working files.
hacking/run_checks.sh
```

The list includes each unit test file and its purpose, plus commands for listing
individual cases without running them or selecting one file in a prepared
collection workspace.

The script:

1. Verifies the pinned Python version and required tools, including ShellCheck.
2. Prepares a fresh `ansible_collections/brocade/fos` workspace with your edits.
3. Runs lint/header checks, all unit tests, and Ansible sanity checks, continuing
   after a failed suite.
4. Prints each suite's exit code and the workspace/log locations. Logs are under
   `tests/output/run_checks/` in the workspace; any failure returns a nonzero exit.

On failure, copy the printed `--only <check>` command to rerun that suite without
repeating the others. Each retry uses a fresh workspace with your current edits.

Resolve failures before submitting. Edit the original checkout and rerun the
script after changes; each run creates a new workspace and keeps its results.

### Run One Unit Test File

Use a file path shown by `hacking/run_checks.sh --list`, including any
subdirectories. From the source checkout:

```bash
# Prepare a fresh workspace in the collection layout required by ansible-test.
cd "$(hacking/prepare_ansible_test.sh)"

# Run all cases in one file; replace this example path with the selected file.
ansible-test units tests/unit/test_lint_header_check.py --venv --requirements

# Return to the original source checkout.
cd -
```

### Optional Builds

```bash
# Also build/install a local collection artifact and build the documentation.
hacking/run_checks.sh --build-collection --build-docs
```

Use either flag on its own when needed. Installation, artifacts, and generated
HTML stay in the test workspace; the script prints the documentation path.
Use `hacking/run_checks.sh --help` for options.

### Adding, Editing, or Removing Tests

- **Unit cases:** add `test_*.py` files under `tests/unit/`. Edit or remove test
  functions, fixtures, and parameter cases there. The unit suite discovers them
  automatically; no runner change is needed. Add a one-line module docstring at
  the top of each file to describe it in `--list`.
- **Suites and integration targets:** add, edit, or remove `run_check` calls in
  the `Default suites` block of `hacking/run_checks.sh`. Give each suite a unique
  log name (selected by `--only`) followed by its description for `--list`.
  Keep the shared `ansible_test_options` flags. For optional suites, include
  `list_checks` in the condition so they also appear in the list.
  For a new integration target, add its files and `aliases` under
  `tests/integration/targets/<target>/`.
  Edit or remove integration cases in that target's `runme.sh` or `tasks/` files;
  remove its runner call when deleting the target.
- **Dependencies:** update `tests/integration/requirements.txt` when integration
  dependencies change; keep shared lint-tool versions aligned with
  `dev-requirements.txt`.

Example addition to the runner:

```bash
# Include a new integration target in the default run.
run_check extra_target 'Describe the new integration checks.' \
    ansible-test integration extra_target "${ansible_test_options[@]}"
```

## Changelog

Add a fragment for user-visible fixes, features, deprecations, and breaking
changes. Describe the user impact and any required playbook changes. Formatting
and internal cleanup normally need no release note.

```bash
# 1. Create a fragment. Use <pr-number>.<type>.yaml, or a descriptive filename.
# Replace the example filename and description with your change.
cat > changelogs/fragments/42.bugfixes.yaml <<'YAML'
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

bugfixes:
  - brocade_example - fix connection timeout when vfid is -1.
YAML

# 2. Validate the fragment and include it with the code change.
antsibull-changelog lint changelogs/fragments/42.bugfixes.yaml
```

Choose the fragment category:

| Type                  | Use for                                       |
| --------------------- | --------------------------------------------- |
| `major_changes`       | Significant new features                      |
| `minor_changes`       | Small improvements and new options            |
| `breaking_changes`    | Incompatible changes                          |
| `deprecated_features` | Features to be removed                        |
| `removed_features`    | Features removed this release                 |
| `security_fixes`      | Security fixes                                |
| `bugfixes`            | Bug fixes                                     |
| `known_issues`        | Unresolved issues                             |
| `trivial`             | Internal changes omitted from published notes |

Contributors leave version bumps and fragment incorporation to release managers.
For existing release notes, use the correction steps below. Release managers
continue with **Releasing**.

Edit `changelogs/changelog.yaml`, the release-history source; do not edit generated
`CHANGELOG.rst` directly. [antsibull-changelog](https://github.com/ansible-community/antsibull-changelog)
generates it, and `docs/docsite/rst/changelog.rst` includes it in the documentation.

### Correcting Existing Notes

```bash
# 1. Edit the relevant version in changelogs/changelog.yaml.
# If CHANGELOG.rst was edited directly, transfer the intended edits/deletions
# into YAML first. Reconcile matching pending fragments to prevent duplicates.

# 2. Regenerate and review; do not use release for wording corrections.
antsibull-changelog generate
git diff -- changelogs/changelog.yaml CHANGELOG.rst
git diff --check HEAD

# 3. Include the YAML source and regenerated CHANGELOG.rst in the same commit.
```

## Submitting a Pull Request

Use this path for a contribution.

### Contributor Assignment Agreement ("CAA")

Sign the appropriate CAA before your contribution can be accepted:

- [Individual contribution](https://na3.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=7af19c0f-ae97-4b56-b950-fc4796860c79)
- [Contribution on behalf of an entity](https://na3.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=f657df18-ed64-4c51-a8f2-618bbd17d355)

1. Commit only the files related to your change (no `.venv/`, test output, or
   unrelated edits), then push your branch.
2. Open a PR against `main`: describe the problem, resulting behavior, and checks.
   Include commands, tool versions, results, and any checks that could not run.
3. Fix any failures reported by the **Certification required** check on the PR.

## Releasing

Release managers: follow [PUBLISHING.md](https://github.com/brocade/brocade.fos/blob/main/PUBLISHING.md)
for the version bump, changelog release, validation, and publication.
Committing, merging, or passing CI does not publish a release.
