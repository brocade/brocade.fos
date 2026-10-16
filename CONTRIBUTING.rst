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

Install the dependencies needed for development:

.. code-block:: bash

   pip install -r dev-requirements.txt

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

Documentation Conventions
=========================

When adding or updating examples, playbooks, and documentation, please ensure that no Personal Identifiable Information (PII) or real network data is included. Use the following standard placeholders:

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

Adding a changelog fragment
---------------------------

For every change that is visible to users (bug fix, new feature, deprecation,
breaking change), create a fragment file under ``changelogs/fragments/``:

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

At release time, generate the updated ``CHANGELOG.rst`` from all accumulated
fragments and bump the version in ``galaxy.yml`` first:

.. code-block:: bash

   # 1. Ensure antsibull-changelog is installed
   pip install -r dev-requirements.txt

   # 2. Release — consumes fragments and updates CHANGELOG.rst
   antsibull-changelog release --version <new-version>

   # 3. Review CHANGELOG.rst, then commit
   git add CHANGELOG.rst changelogs/changelog.yaml changelogs/fragments/
   git commit -m "Release <new-version> changelog"

Building Documentation
======================

See `docs/documentation.rst <docs/documentation.rst>`_ for instructions on
building the Sphinx documentation.
