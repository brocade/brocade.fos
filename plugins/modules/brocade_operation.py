#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_operation
short_description: Brocade IPS operations
version_added: "2.0.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Perform IPS operations for list of objects based on module name and list name provided.

options:
    credential:
        description:
        -   Login information.
        suboptions:
            fos_ip_addr:
                description:
                -   IP address of the FOS switch.
                required: true
                type: str
            fos_user_name:
                description:
                -   Login name for the FOS switch.
                required: true
                type: str
            fos_password:
                description:
                -   Password for the FOS switch.
                required: true
                type: str
            https:
                description:
                -   Connection mode, supplied as a string.
                -   C(true) uses HTTPS with certificate validation.
                -   C(self) uses HTTPS without certificate validation, allowing self-signed certificates.
                -   C(false) uses unencrypted HTTP.
                required: true
                type: str
        type: dict
        required: true
    vfid:
        description:
        -   VFID of the switch. Use -1 for FOS without VF enabled or AG.
        type: int
    throttle:
        description:
        -   Delay in seconds before retrying once when the switch is busy.
        type: int
    timeout:
        description:
        -   REST timeout in seconds for operations that take longer than the FOS default timeout.
        type: int
    module_name:
        description:
        -   YANG module name. Hyphens and underscores can be used interchangeably. If the YANG module
            name is xy-z, either xy-z or xy_z is acceptable.
        required: true
        type: str
    entries:
        description:
        -   List of objects. The name of each attribute within each entry should match the YANG name
            except that hyphens are replaced with underscores. Using hyphens in the name may result in
            erroneous behavior based on Ansible parsing.
        required: true
        type: list
        elements: raw
    all_entries:
        description:
        -   Whether entries specifies the complete desired list of objects. When true, the module adds,
            updates, and deletes objects to match entries. When false, the module adds or updates the
            specified objects and preserves objects omitted from entries.
        type: bool
"""


EXAMPLES = r"""
- name: Manage Brocade FOS resources
  hosts: fos_switches
  gather_facts: false
  vars:
    credential:
      fos_ip_addr: '{{ fos_ip_addr }}'
      fos_user_name: user_name
      fos_password: user_password
      https: "false"
  tasks:
    - name: List object example
      brocade.fos.brocade_list_obj:
        credential: '{{ credential }}'
        vfid: -1
        module_name: brocade-snmp
        list_name: v3-account
        all_entries: false
        entries:
          - index: 1
            community_name: new name
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel Yang list processor
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import list_operation_helper


def main():
    """
    Main function
    """

    argument_spec = dict(
        credential=dict(
            required=True,
            type="dict",
            options=dict(
                fos_ip_addr=dict(required=True, type="str"),
                fos_user_name=dict(required=True, type="str"),
                fos_password=dict(required=True, type="str", no_log=True),
                https=dict(required=True, type="str"),
            ),
        ),
        vfid=dict(required=False, type="int"),
        throttle=dict(required=False, type="int"),
        timeout=dict(required=False, type="int"),
        module_name=dict(required=True, type="str"),
        entries=dict(required=True, type="list", elements="raw"),
        all_entries=dict(required=False, type="bool"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    input_params = module.params

    # Set up state variables
    fos_ip_addr = input_params["credential"]["fos_ip_addr"]
    fos_user_name = input_params["credential"]["fos_user_name"]
    fos_password = input_params["credential"]["fos_password"]
    https = input_params["credential"]["https"]
    throttle = input_params["throttle"]
    timeout = input_params["timeout"]
    vfid = input_params["vfid"]
    entries = input_params["entries"]
    all_entries = input_params["all_entries"]
    result = {"changed": False}
    module_name = input_params["module_name"]
    list_name = ""

    if module_name == "vrf":
        module_name = "ipStorage"
        list_name = "vrf"
    elif module_name == "vlan":
        module_name = "ipStorage"
        list_name = "vlan"
    elif module_name == "interface":
        module_name = "ipStorage"
        list_name = "interface"
    elif module_name == "staticArp":
        module_name = "ipStorage"
        list_name = "staticArp"
    elif module_name == "staticRoute":
        module_name = "ipStorage"
        list_name = "staticRoute"
    elif module_name == "lag":
        module_name = "ipStorage"
        list_name = "lag"
    elif module_name == "configuration":
        module_name = "trafficClass"
        list_name = "configuration"

    list_operation_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        module_name,
        list_name,
        entries,
        all_entries,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
