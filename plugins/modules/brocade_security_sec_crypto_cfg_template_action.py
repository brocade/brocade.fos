#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_security_sec_crypto_cfg_template_action
short_description: Brocade Fibre Channel security crypto template file actions
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Use to perform actions on the crypto template files. The module performs the action each time and is not
    idempotent.

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
    action_inputs:
        description:
        -   Action attributes.
        required: true
        type: dict
        suboptions:
            action:
                description:
                -   Operation to perform on the crypto config template.
                type: str
            template_name:
                description:
                -   Name of the crypto config template.
                type: str
            remote_host_ip:
                description:
                -   IP address of the remote host for import or export.
                type: str
            remote_user_name:
                description:
                -   User name on the remote host for import or export.
                type: str
            remote_user_password:
                description:
                -   Password for the remote host user. Not logged.
                type: str
            remote_directory:
                description:
                -   Directory path on the remote host containing or receiving the template file.
                type: str
            file_transfer_protocol_type:
                description:
                -   File transfer protocol to use for import or export.
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
    - name: Import/export/apply cfg template
      brocade.fos.brocade_security_sec_crypto_cfg_template_action:
        credential: '{{ credential }}'
        vfid: -1
        action_inputs: '{{ action_inputs }}'
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel crypto template file actions
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import singleton_helper


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
        action_inputs=dict(
            required=True,
            type="dict",
            options=dict(
                action=dict(type="str"),
                template_name=dict(type="str"),
                remote_host_ip=dict(type="str"),
                remote_user_name=dict(type="str"),
                remote_user_password=dict(type="str", no_log=True),
                remote_directory=dict(type="str"),
                file_transfer_protocol_type=dict(type="str"),
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
    action_inputs = input_params["action_inputs"]
    result = {"changed": False}

    singleton_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        "brocade_security",
        "sec_crypto_cfg_template_action",
        action_inputs,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
