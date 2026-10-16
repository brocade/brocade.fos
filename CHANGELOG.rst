=========================
Brocade.Fos Release Notes
=========================

.. contents:: Topics

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

- Remove references to SNMP v1 in the documentation and playbooks since they are obsoleted from FOS 10.x.

Bugfixes
--------

- Fix majority of lint violations reported by ansible-lint for playbooks and ruff for python files.
- Fix typo in brocade_ssh.py module - https://github.com/brocade/ansible/pull/188.
- Meaningless "No start of json char found" error message when SAN switch cannot be connected to - https://github.com/brocade/ansible/issues/204.
- Replaced protocol with protocol_v2 under suppportsave playbook.
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
- Issue related to errors sometimes being ignored is fixed by throwing proper error to upper layers.
