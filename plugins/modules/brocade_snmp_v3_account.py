#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_snmp_v3_account
short_description: Brocade Fibre Channel SNMP v3 account configuration
version_added: '2.7'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Update Fibre Channel SNMP v3 account.

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
    v3_accounts:
        description:
        -   List of v3 accounts to be updated. Supports all writable attributes exposed by the BSN REST
            API, with hyphens replaced by underscores.
        required: true
        type: list
        elements: dict
        suboptions:
            index:
                description:
                -   Primary key for SNMP v1_account and v1_trap list objects.
                type: int
            authentication_protocol:
                description:
                -   SNMPv3 authentication protocol (e.g. sha512). Used with brocade_snmp v3_account list
                    object.
                type: str
            manager_engine_id:
                description:
                -   SNMPv3 manager engine ID. Used with brocade_snmp v3_account list object.
                type: str
            privacy_protocol:
                description:
                -   SNMPv3 privacy protocol (e.g. aes128). Used with brocade_snmp v3_account list object.
                type: str
            user_name:
                description:
                -   Remote server or switch username, as applicable to this operation.
                type: str
            user_group:
                description:
                -   SNMPv3 user group. Used with brocade_snmp v3_account list object.
                type: str
            authentication_password:
                description:
                -   SNMPv3 authentication password. Not logged. Used with brocade_snmp v3_account list object.
                type: str
            privacy_password:
                description:
                -   SNMPv3 privacy password. Not logged. Used with brocade_snmp v3_account list object.
                type: str
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
    - name: Snmp v3 accounts
      brocade.fos.brocade_snmp_v3_account:
        credential: '{{ credential }}'
        vfid: -1
        v3_accounts:
          - index: 1
            authentication_protocol: sha512
            manager_engine_id: 00:00:00:00:00:00:00:00:00
            privacy_protocol: aes128
            user_name: asc-test
          - index: 2
            authentication_protocol: sha512
            manager_engine_id: 00:00:00:00:00:00:00:00:00
            privacy_protocol: aes128
            user_name: snmpadmin2
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel SNMP v3 account configuration
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import list_helper


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
        v3_accounts=dict(
            required=True,
            type="list",
            elements="dict",
            options=dict(
                index=dict(type="int"),
                authentication_protocol=dict(type="str"),
                manager_engine_id=dict(type="str"),
                privacy_protocol=dict(type="str"),
                user_name=dict(type="str"),
                user_group=dict(type="str"),
                authentication_password=dict(type="str", no_log=True),
                privacy_password=dict(type="str", no_log=True),
            ),
        ),
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
    v3_accounts = input_params["v3_accounts"]
    result = {"changed": False}

    list_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        "brocade_snmp",
        "v3_account",
        v3_accounts,
        False,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
