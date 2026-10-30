=========================
Brocade.Fos Release Notes
=========================

.. contents:: Topics

v3.0.0
======

Release Summary
---------------

Major release that removes the SSH transport and Paramiko dependency in favor of the FOS REST API, updates module argument documentation and examples, and adds certification and regression-test workflows. See Major Changes for incompatible changes.

Major Changes
-------------

- Removed the SSH transport and ``paramiko`` dependency; all modules now use the FOS REST API only. Remove ``ssh_hostkeymust``, ``telnet_timeout``, and ``credit_recovery_mode`` from existing playbooks.
- Replace hyphens with underscores in nested firmwaredownload, supportsave, and scalar-operation parameter names (for example, ``user-name`` becomes ``user_name``).
- Switch FOS REST requests and responses from XML to JSON, removing the ``xmltodict`` dependency.

Minor Changes
-------------

- Add the Red Hat Partner Certification Checker v6.0.0 workflow for pull requests and main-branch pushes, with a required-check aggregation job.
- Update Automation Hub installation, support, release, and ordered manual-validation instructions.

Bugfixes
--------

- brocade_operation_show_status, brocade_operation_firmwaredownload and other modules - preserve native JSON types from FOS REST responses instead of stringifying them, fixing numeric/boolean payload round-trips (for example show-status message-id polling failing with "unknown-attribute").

v2.2.0
======

Release Summary
---------------

Deprecate galaxy branch and convert master to galaxy instead.

v2.1.0
======

Minor Changes
-------------

- Add code_sanity.py script to validate the codebase for lint violations.
- Add support for license operations - https://github.com/brocade/ansible/issues/134.
- Remove zoning_to_yaml.py utility script to resolve deprecated dependencies.

Removed Features (previously deprecated)
----------------------------------------

- Remove references to SNMP v1 in the documentation and playbooks because they are obsolete in FOS 10.x.

Bugfixes
--------

- Fix the majority of lint violations reported by ansible-lint for playbooks and Ruff for Python files.
- Fix typo in brocade_ssh.py module - https://github.com/brocade/ansible/pull/188.
- Meaningless "No start of json char found" error message when SAN switch cannot be connected to - https://github.com/brocade/ansible/issues/204.
- Replaced protocol with protocol_v2 in the supportsave playbook.
- vfid with no defined-configuration causes brocade_facts.py to crash - https://github.com/brocade/ansible/issues/203.

Known Issues
------------

- brocade_fibrechannel_configuration/fabric URI refactoring needs to be handled correctly.

v2.0.2
======

Bugfixes
--------

- Modify firmwaredownload.yml to handle potential timing issues seen under certain conditions.

v2.0.1
======

Bugfixes
--------

- Handle PATCH requests that do not change anything appropriately - https://github.com/brocade/ansible/issues/180.
- Modify firmwaredownload.yml to handle potential timing issues seen under certain conditions.
- brocade_facts https broken in release 2.0.0 - https://github.com/brocade/ansible/issues/170.
- brocade_security_certificate_action import cert fails - https://github.com/brocade/ansible/issues/149.

v2.0.0
======

Major Changes
-------------

- A new module brocade_operation is introduced.
- Configupload and configdownload support added via new module brocade_scalar_operation.
- Unified Storage Fabric (USF) functionality is supported using the new module brocade_operation — VRF, VLAN, ARP, Interface, StaticRoute, Lag, and TrafficClass operations.

Minor Changes
-------------

- Documentation updated in playbook to mention renaming of telnet_timeout to shell_timeout.
- Masked logging of the password mentioned in the credentials of the playbook.
- shebang updated from python3 to python to support latest Python version.

Bugfixes
--------

- Corrected typo in logical switch playbook by removing syslog.
- Fix errors that were sometimes ignored by propagating them to higher layers.
