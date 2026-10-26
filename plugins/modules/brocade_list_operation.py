#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_list_operation
short_description: Brocade Fibre Channel operation with the container input
version_added: '2.7'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Perform specified operation.

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
        -   Operation parameters.
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
    - name: Perform operation
      brocade.fos.brocade_list_operation:
        credential: '{{ credential }}'
        module_name: vrf
        vfid: -1
        entries:
          - vrfID: 28
            action: delete
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

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
