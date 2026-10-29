#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_list_operation
short_description: Brocade IPS operations with explicit actions
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Submit IPS operations to the switch with the entries exactly as given, selected by C(module_name).
-   Supported C(module_name) values are C(vrf), C(vlan), C(interface), C(staticArp), C(staticRoute),
    and C(lag) for IP storage (IPS) on a logical switch with IP storage enabled, and C(configuration)
    for traffic class configuration.
-   Each entry sets its operation with C(action), for example C(create) or C(delete). Unlike
    C(brocade.fos.brocade_operation), the module does not compare the entries with the switch, so
    the task always reports a change.
-   The module returns once FOS accepts the operation. To wait for it to complete, poll
    C(brocade.fos.brocade_operation_show_status) with the returned C(message_id).

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
        -   Fabric ID of the logical switch. Defaults to C(128) when omitted.
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
        -   Operation to run. One of C(vrf), C(vlan), C(interface), C(staticArp), C(staticRoute), C(lag),
            or C(configuration). Values are case-sensitive.
        required: true
        type: str
    entries:
        description:
        -   Operation entries. Each entry contains C(action) and the YANG leaf names of the operation,
            for example C(vrfID) and C(action) for C(vrf).
        type: list
        required: true
        elements: raw
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
    - name: Create IP storage VRFs
      brocade.fos.brocade_list_operation:
        credential: '{{ credential }}'
        module_name: vrf
        vfid: 5
        entries:
          - vrfID: 28
            action: create
          - vrfID: 29
            action: create
      register: result

    - name: Wait for the operation to complete
      brocade.fos.brocade_operation_show_status:
        credential: '{{ credential }}'
        vfid: 5
        show_status:
          message_id: '{{ result.operation_resp.show_status.message_id }}'
      register: status_result
      until: status_result.operation_resp.show_status.status in ["done", "delivered"]
      retries: 100
      delay: 10
"""


RETURN = r"""

input:
    description: Entries submitted to the switch, with secrets removed.
    returned: when the switch login succeeds
    type: list
    elements: dict
operation_resp:
    description: FOS response to the operation, including C(show_status.message_id) for status polling.
    returned: when the operation is submitted
    type: dict

"""


"""
Brocade Fibre Channel operation
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import operation_helper


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
    result = {"changed": False}
    module_name = input_params["module_name"]

    list_name = ""
    if module_name == "vrf":
        module_name = "ipStorageVrf"
        list_name = "ipStorageVrfParameters"
    elif module_name == "vlan":
        module_name = "ipStorageVlan"
        list_name = "ipStorageVlanParameters"
    elif module_name == "interface":
        module_name = "ipStorageInterface"
        list_name = "ipStorageInterfaceParameters"
    elif module_name == "staticArp":
        module_name = "ipStorageArp"
        list_name = "ipStorageArpParameters"
    elif module_name == "staticRoute":
        module_name = "ipStorageRoute"
        list_name = "ipStorageRouteParameters"
    elif module_name == "lag":
        module_name = "ipStorageLag"
        list_name = "ipStorageLagParameters"
    elif module_name == "configuration":
        module_name = "trafficClass"
        list_name = "trafficClassParameters"

    operation_helper(
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
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
