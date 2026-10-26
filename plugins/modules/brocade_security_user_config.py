#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_security_user_config
short_description: Brocade Fibre Channel security user configuration
version_added: '2.7'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Update Fibre Channel security user configuration.

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
    delete_user_configs:
        description:
        -   List of user configurations to be deleted.
        type: list
        elements: raw
    user_configs:
        description:
        -   List of user configurations. Supports all writable attributes exposed by the BSN REST API,
            with hyphens replaced by underscores.
        type: list
        elements: dict
        suboptions:
            name:
                description:
                -   License key or serial number (e.g. FOS-00-0-02-11201234). Used for license install by key,
                    remove, and targeted export operations.
                type: str
            account_enabled:
                description:
                -   Enable or disable the user account. Used with brocade_security user_config list object.
                type: bool
            password:
                description:
                -   Password used by the requested operation.
                type: str
            virtual_fabric_role_id_list:
                description:
                -   Dict containing a role_id list of virtual fabric role assignments (e.g. admin=1-128). Used
                    with brocade_security user_config list object.
                type: dict
            chassis_access_role:
                description:
                -   Chassis access role for the user account (e.g. admin). Used with brocade_security
                    user_config list object.
                type: str
            role:
                description:
                -   Switch role for the user account. Used with brocade_security user_config list object.
                type: str
            account_description:
                description:
                -   Description string for the user account. Used with brocade_security user_config list
                    object.
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
    - name: Disable root & user
      brocade.fos.brocade_security_user_config:
        credential: '{{ credential }}'
        vfid: -1
        user_configs:
          - name: User
            account_enabled: false
          - name: Root
            account_enabled: false
    - name: Add new account
      brocade.fos.brocade_security_user_config:
        credential: '{{ credential }}'
        vfid: -1
        user_configs:
          - name: Myaccount
            password: bXlwYXNzd29yZA==
            virtual_fabric_role_id_list:
              role_id:
                - admin=1-128
            chassis_access_role: admin
          - name: Youraccount
            password: bXlwYXNzd29yZA==
            virtual_fabric_role_id_list:
              role_id:
                - admin=1-128
            chassis_access_role: admin
    - name: Delete accounts
      brocade.fos.brocade_security_user_config:
        credential: '{{ credential }}'
        vfid: -1
        delete_user_configs:
          - name: Myaccount
          - name: Youraccount
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel user configuration
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import list_delete_helper, list_helper


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
        delete_user_configs=dict(required=False, type="list", elements="raw"),
        user_configs=dict(
            required=False,
            type="list",
            elements="dict",
            options=dict(
                name=dict(type="str"),
                account_enabled=dict(type="bool"),
                password=dict(type="str", no_log=True),
                virtual_fabric_role_id_list=dict(type="dict"),
                chassis_access_role=dict(type="str"),
                role=dict(type="str"),
                account_description=dict(type="str"),
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
    user_configs = input_params["user_configs"]
    delete_user_configs = input_params["delete_user_configs"]
    result = {"changed": False}

    # if delete user config is not None, then we make sure
    # the user config is not present.
    # user config creation or update does not happen at the same
    # time
    if delete_user_configs is not None:
        return list_delete_helper(
            module,
            fos_ip_addr,
            fos_user_name,
            fos_password,
            https,
            throttle,
            vfid,
            "brocade_security",
            "user_config",
            delete_user_configs,
            True,
            result,
            timeout,
        )

    list_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        "brocade_security",
        "user_config",
        user_configs,
        False,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
