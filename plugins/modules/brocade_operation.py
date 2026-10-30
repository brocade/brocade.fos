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
-   Run IPS operations that take a list of entries, selected by C(module_name).
-   Supported C(module_name) values are C(vrf), C(vlan), C(interface), C(staticArp), C(staticRoute),
    and C(lag) for IP storage (IPS) on a logical switch with IP storage enabled, and C(configuration)
    for traffic class configuration.
-   The module compares C(entries) with the current list on the switch and submits each change as a
    FOS operation, waiting up to about 16 minutes for each operation to complete.
-   C(staticArp), C(staticRoute), and C(lag) entries are updated by deleting and recreating them.
-   VRF C(0) and the system traffic classes C(sysTcDefault) and C(sysTcAclDeny) are never deleted.
    Entries that change C(sysTcDefault) or C(sysTcAclDeny) cause the task to fail.

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
        -   Fabric ID of the logical switch to configure. Defaults to C(128) when omitted.
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
        -   List to manage. Values are case-sensitive.
        required: true
        type: str
        choices: [vrf, vlan, interface, staticArp, staticRoute, lag, configuration]
    entries:
        description:
        -   Desired entries for the selected list. Attribute names match the YANG leaf names of that
            list, for example C(vrfID) and C(dhcpEnabled) for C(vrf).
        required: true
        type: list
        elements: raw
    all_entries:
        description:
        -   Whether C(entries) specifies the complete desired list. When true, the module adds, updates,
            and deletes entries to match C(entries). When false, the module adds or updates the specified
            entries and preserves entries omitted from C(entries).
        -   Defaults to true when omitted, so entries not listed are deleted.
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
    - name: Configure IP storage VRFs
      brocade.fos.brocade_operation:
        credential: '{{ credential }}'
        vfid: 9
        module_name: vrf
        all_entries: false
        entries:
          - vrfID: 28
          - vrfID: 33
            dhcpEnabled: true
            dhcpServer: 198.51.100.100
"""


RETURN = r"""

current_entries:
    description: Entries read from the switch before changes, excluding those deleted and recreated.
    returned: when the switch list is read
    type: list
    elements: dict
add_entries:
    description: Entries submitted for creation.
    returned: when the switch list is read
    type: list
    elements: dict
diff_entries:
    description: Changes submitted for existing entries.
    returned: when the switch list is read
    type: list
    elements: dict
delete_entries:
    description: Entries not in C(entries). They are deleted only when C(all_entries) is true.
    returned: when the switch list is read
    type: list
    elements: dict
response:
    description: Raw REST response for the current list, or an error message.
    returned: when the switch list is read
    type: raw

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
        module_name=dict(
            required=True,
            type="str",
            choices=["vrf", "vlan", "interface", "staticArp", "staticRoute", "lag", "configuration"],
        ),
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
