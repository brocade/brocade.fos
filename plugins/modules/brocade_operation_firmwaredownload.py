# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_operation_firmwaredownload
short_description: Brocade Fibre Channel operation firmwaredownload
version_added: '2.7'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Initiate Fibre Channel firmwaredownload.

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
    firmwaredownload:
        description:
        -   Firmware parameters.
        required: true
        type: dict
        suboptions:
            host:
                description:
                -   Remote server address.
                type: str
            user_name:
                description:
                -   Remote server or switch username, as applicable to this operation.
                type: str
            password:
                description:
                -   Password used by the requested operation.
                type: str
            remote_directory:
                description:
                -   Directory on the remote server.
                type: str
            protocol:
                description:
                -   Transfer protocol supported by the FOS operation.
                type: str
            port:
                description:
                -   Remote service port.
                type: int
            stage:
                description:
                -   Whether to stage the firmware download.
                type: bool
            activate:
                description:
                -   Whether to activate staged firmware.
                type: bool
            eula_action:
                description:
                -   Action for the firmware end-user license agreement.
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
    - name: Initiate firmwaredownload
      brocade.fos.brocade_operation_firmwaredownload:
        credential: '{{ credential }}'
        vfid: -1
        firmwaredownload:
          host:
          user_name:
          password:
          remote_directory:
          protocol:
          port:
          stage:
          activate:
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import operation_helper

"""
Brocade Fibre Channel firmwaredownload initiate
"""


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
        firmwaredownload=dict(
            required=True,
            type="dict",
            options=dict(
                host=dict(type="str"),
                user_name=dict(type="str"),
                password=dict(type="str", no_log=True),
                remote_directory=dict(type="str"),
                protocol=dict(type="str"),
                port=dict(type="int"),
                stage=dict(type="bool"),
                activate=dict(type="bool"),
                eula_action=dict(type="str"),
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
    firmwaredownload = input_params["firmwaredownload"]
    result = {"changed": False}

    operation_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        "firmwaredownload",
        "firmwaredownload_parameters",
        firmwaredownload,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
