============
Contribution
============

Contributors must sign and submit a CAA before a contribution can be
accepted. Two CAAs are available, one for individual contributions and
one for contributions made on behalf of an entity, e.g., an employer.
Select the appropriate link below to electronically execute a CAA.

Contributor Assignment Agreement ("CAA")
========================================

CAA - Individual:
https://na3.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=7af19c0f-ae97-4b56-b950-fc4796860c79

CAA - Entity:
https://na3.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=f657df18-ed64-4c51-a8f2-618bbd17d355

Development Setup
=================

Start from a clone of this repository. Create a branch from the current
``main`` branch for your contribution. Run the commands below from the
repository root.

Install the Python version recorded in ``.python-version`` and make it available
as ``python``. Verify the version before creating an isolated environment:

.. code-block:: bash

   python --version
   python -c 'import pathlib, platform; expected = pathlib.Path(".python-version").read_text().strip(); assert platform.python_version() == expected, f"Expected Python {expected}"'
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -r dev-requirements.txt

The activation command above is for Bash. Use the equivalent activation command
for your shell. Reactivate this environment in each new terminal before running
the development tools. ``.venv/`` is ignored by Git.

Building a Local Collection
===========================

With the development environment activated, build the collection from the
repository root:

.. code-block:: bash

   ansible-galaxy collection build --output-path ./build --force

The artifact is written to ``build/brocade-fos-<version>.tar.gz``, where
``<version>`` is the value in ``galaxy.yml``. Replace that placeholder when
installing the artifact:

.. code-block:: bash

   ansible-galaxy collection install "./build/brocade-fos-<version>.tar.gz" --force

Rebuild and reinstall after changing source files to update the installed
collection. The ``--force`` options replace an existing build artifact and
installed collection with the same version. ``build/`` is ignored by Git.
Follow ``PUBLISHING.md`` for release artifact validation and publication.

Making Changes
==============

Keep each contribution focused on one issue or feature. Update the relevant
module documentation and examples when changing arguments or behavior. Add or
update regression tests under ``tests/unit/`` when changing behavior that can
be tested without a switch.

For module documentation:

* Use raw triple-quoted strings for ``DOCUMENTATION``, ``EXAMPLES``, and ``RETURN``.
* Keep documented argument types, defaults, requirements, and choices consistent
  with the module's argument specification.
* Use fully qualified module names, such as ``brocade.fos.brocade_facts``, in
  examples. Use ``ansible.builtin.`` for built-in modules.
* For new modules or options, set ``version_added`` to the collection version
  that first provides them, not the Ansible version. Do not change existing
  introduction versions merely because the collection is being released again.
* Follow the placeholder conventions below and keep credentials out of examples,
  logs, and commits.

Preserve existing copyright and license notices. A copyright notice identifies
ownership; it does not assign a license. Do not change license allocations as
part of an unrelated fix.

Running Code Sanity Checks
==========================

Before submitting a contribution, run sanity checks to validate your
changes:

.. code-block:: bash

   # Validate the entire repository
   python tests/sanity/code_sanity.py

   # Validate specific files or directories
   python tests/sanity/code_sanity.py --path path/to/file.py

For full usage details run ``python tests/sanity/code_sanity.py -h``.

The local runner checks Ruff, Ansible Lint, and copyright notices. It is not a
replacement for ``ansible-test`` sanity and unit tests. Its ``--fix`` option
modifies files; inspect the resulting diff before keeping those changes.
Logs are written under ``tests/sanity/`` and are ignored by Git.

Run ``git diff --check`` to check whitespace. For the canonical collection
directory layout, the sanity/unit matrix, and build/import checks, follow
``PUBLISHING.md`` under "Certification validation checklist", item 2.
Retain the command, tool versions, results, and any environment limitation when
reporting validation in a pull request.

The certification workflow in ``.github/workflows/certification.yml`` runs on
pull requests targeting ``main``. Review the "Certification required" result
and its dependent jobs. Local checks and CI do not validate live-switch behavior;
changes requiring a switch need separately scoped lab validation as described
in ``PUBLISHING.md``.

Running Unit Tests
==================

Run unit tests with ``ansible-test``, which is supplied by
``ansible-core``. Activate the development environment described above and
verify that ``ansible --version`` and ``ansible-test --version`` are available.
Use the Python version in ``.python-version``.

``ansible-test`` requires the collection to be located under
``ansible_collections/brocade/fos``. From the repository root, create an isolated
copy of the current tracked and untracked, non-ignored files:

.. code-block:: bash

   cert_python_minor=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
   unit_work=$(mktemp -d)
   mkdir -p "$unit_work/ansible_collections/brocade/fos"
   git ls-files -z --cached --others --exclude-standard |
     tar --null -T - -cf - |
     tar -xf - -C "$unit_work/ansible_collections/brocade/fos"
   cd "$unit_work/ansible_collections/brocade/fos"

Run the focused module regression tests:

.. code-block:: bash

   ansible-test units tests/unit/plugins/modules/test_module_regressions.py \
     --venv --python "$cert_python_minor" --requirements --num-workers 1

The file currently contains five test cases covering operation parameter
handling, fact gathering in check mode, and preservation of nested zoning
values. Connections and switch operations are mocked; no switch credentials
or lab hardware are required. The ``--requirements`` option installs test
dependencies and may require network access.

Run the copyright-header regression tests for the local sanity runner:

.. code-block:: bash

   ansible-test units tests/unit/test_code_sanity.py \
     --venv --python "$cert_python_minor" --requirements --num-workers 1

These tests use temporary files to check header validation and repair,
including preservation of preambles, third-party notices, line endings, and
file permissions.

To run the entire unit suite in the same collection copy:

.. code-block:: bash

   ansible-test units --venv --python "$cert_python_minor" --requirements --num-workers 1

Expect a zero exit status and no failed tests. Retain failure output and the
Ansible/Python versions when reporting problems. Results are written under
``tests/output/`` in the temporary collection copy. Return to your original
checkout after testing, preserve any needed results, and remove the temporary
directory when finished. Recreate the copy after editing source files; rerunning
tests in an old copy does not validate new edits.

These commands exercise the ``ansible-core`` version in the activated
environment. Use the matrix procedure in ``PUBLISHING.md`` for release
qualification across all configured core branches. Commit unit-test source
with the corresponding code changes; do not commit generated test output.

Documentation Conventions
=========================

When adding or updating examples, playbooks, and documentation, please ensure that no personally identifiable information (PII) or real network data is included. Use the following standard placeholders:

* **IP Addresses**: Use standard TEST-NET documentation blocks (RFC 5737).

  * Switches/Hosts: ``198.51.100.x`` (e.g., ``198.51.100.1``, ``198.51.100.2``)
  * Servers (DNS, NTP, Syslog, etc.): ``203.0.113.x`` (e.g., ``203.0.113.10``)

* **Port WWNs (PWWN)**: Use dummy values starting with ``aa:bb:cc:dd:ee:ff:11:11`` and increment the last octet as needed.
* **Domain Names**: Use ``example.com``, ``example.net``, or ``example.org``.
* **Emails**: Use ``sender@example.com`` or ``receiver@example.com``.
* **Credentials**:

  * Usernames: ``user_name``
  * Passwords: ``user_password``
  * Vault Passwords: ``vault_password``

* **Locations**: Use generic terms like ``Data Center 1`` or ``Data Center 2``.
* **Zone/Config Names**: Use generic names like ``zone_1``, ``cfg_1``, ``alias_host_1``.

Changelog
=========

This project uses `antsibull-changelog <https://github.com/ansible-community/antsibull-changelog>`_
to manage ``CHANGELOG.rst``. Do **not** edit ``CHANGELOG.rst`` directly.

How the files relate
--------------------

* ``changelogs/fragments/*.yaml`` contains pending notes for individual changes.
* ``changelogs/changelog.yaml`` stores the accumulated release history. The
  release command incorporates pending fragments into this file.
* The root ``CHANGELOG.rst`` is generated from that release history. Commit it
  so release notes can be read on GitHub and included in the published collection.
* ``docs/docsite/rst/changelog.rst`` is a documentation-site wrapper that includes
  the root ``CHANGELOG.rst``. It does not contain another copy of the descriptions
  and normally needs no change when release notes change.

Maintain each description in its YAML source, then generate the RST output.
Editing only the generated RST causes the next generation to overwrite the edit.

Adding a changelog fragment
---------------------------

For every change that is visible to users (bug fix, new feature, deprecation,
breaking change), create a fragment file under ``changelogs/fragments/``:

Use ``<pr-number>.<type>.yaml`` when the PR number is known. Before then, a
descriptive filename such as ``fix-facts-check-mode.bugfixes.yaml`` is sufficient.
Describe the effect on users. For incompatible changes, explain what users must
change in their playbooks. Routine formatting and internal cleanup generally do
not need a user-facing release note.

.. code-block:: bash

   # Filename convention: <pr-number>.<type>.yaml
   # Types: major_changes, minor_changes, breaking_changes,
   #         deprecated_features, removed_features, security_fixes,
   #         bugfixes, known_issues, trivial

   # Example for a bugfix (PR #42):
   cat > changelogs/fragments/42.bugfix.yaml << 'EOF'
   bugfixes:
     - brocade_example - fix connection timeout when vfid is -1.
   EOF

Validate the fragment before submitting it:

.. code-block:: bash

   antsibull-changelog lint changelogs/fragments/42.bugfix.yaml

Replace the example path with your fragment's path. Commit the fragment with
the code change. Contributors normally leave release history and version bumps
to the release maintainer; running ``generate`` alone does not incorporate a
pending fragment into a release.

Fragment types
--------------

+------------------------------+---------------------------------------+
| Type                         | Use for                               |
+==============================+=======================================+
| ``major_changes``            | Significant new features              |
+------------------------------+---------------------------------------+
| ``minor_changes``            | Small improvements, new options       |
+------------------------------+---------------------------------------+
| ``breaking_changes``         | Incompatible changes                  |
+------------------------------+---------------------------------------+
| ``deprecated_features``      | Features to be removed in future      |
+------------------------------+---------------------------------------+
| ``removed_features``         | Features removed this release         |
+------------------------------+---------------------------------------+
| ``security_fixes``           | Security-related fixes                |
+------------------------------+---------------------------------------+
| ``bugfixes``                 | Bug fixes                             |
+------------------------------+---------------------------------------+
| ``known_issues``             | Known issues not yet fixed            |
+------------------------------+---------------------------------------+
| ``trivial``                  | Internal changes not shown in docs    |
+------------------------------+---------------------------------------+

Generating the changelog (release managers only)
-------------------------------------------------

Before generating a release, review the pending fragments and remove duplicates
of changes already recorded for that release. Bump the version in ``galaxy.yml``
first, then run:

.. code-block:: bash

   # Validate pending fragments
   antsibull-changelog lint

   # Replace <new-version> with the version in galaxy.yml
   antsibull-changelog release --version <new-version>

   # Review the source, output, and consumed fragments
   git diff -- galaxy.yml changelogs/ CHANGELOG.rst
   git diff --check

The configuration in ``changelogs/config.yaml`` sets ``keep_fragments: false``:
the release command consumes fragments and removes them after storing their
entries in the release history. Review those deletions before committing.
Commit ``galaxy.yml``, ``changelogs/changelog.yaml``, ``CHANGELOG.rst``, and the
consumed fragment deletions together. Follow ``PUBLISHING.md`` for release
validation, artifact review, publication, and tagging.

Correcting existing release notes
---------------------------------

To revise notes already incorporated into a release, edit the appropriate
entry under that version in ``changelogs/changelog.yaml``. Then run:

.. code-block:: bash

   antsibull-changelog generate
   git diff -- changelogs/changelog.yaml CHANGELOG.rst
   git diff --check

Commit the YAML source and regenerated ``CHANGELOG.rst`` together. Do not run
``release`` merely to correct wording. If the same entry remains in a pending
fragment, reconcile it so a later release does not add a duplicate or restore
outdated text.

If someone has edited ``CHANGELOG.rst`` directly, first transfer the intended
edits into the YAML source, including any deleted entries. Only then regenerate
and check that those edits were preserved.

Building Documentation
======================

See `docs/documentation.rst <docs/documentation.rst>`_ for instructions on
building the Sphinx documentation.

With the development environment activated, run:

.. code-block:: bash

   bash docs/build.sh

The script builds and installs the collection in a temporary collection path,
generates module documentation, and builds HTML with Sphinx. Open
``docs/build/html/index.html`` to inspect the result. Generated output under
``docs/rst/`` and ``docs/build/`` and collection tarballs are ignored by Git;
do not commit them. The root ``CHANGELOG.rst`` is intentionally committed even
though it is generated.

Submitting a Pull Request
=========================

Before opening a pull request against ``main``:

#. Complete the applicable CAA above.
#. Review ``git status --short`` and both staged and unstaged diffs. Include
   only the files intended for the contribution.
#. Run the relevant local checks and tests. Build documentation when changing
   documentation or embedded module examples, and inspect the output.
#. Add and lint a changelog fragment when the change needs a release note.
   For corrections to existing notes, commit the source and generated output
   together as described above.
#. Run ``git diff --check``, then commit and push your contribution branch.
#. Open a PR describing the problem, the resulting behavior, and validation.
   Identify checks that could not run and explain why.
#. Review the certification workflow results and resolve failures before merge.

Repository maintainers review and merge contributions. Committing a change or
passing CI does not publish a collection release.
