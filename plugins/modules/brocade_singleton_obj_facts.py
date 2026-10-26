#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_singleton_obj_facts
short_description: Brocade Fibre Channel generic facts gathering for singleton objects
version_added: '2.6'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Gather Fibre Channel FOS facts for singleton objects.

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
    obj_name:
        description:
        -   YANG name for the object. Hyphens and underscores can be used interchangeably. If the YANG
            list name is xy-z, either xy-z or xy_z is acceptable.
        required: true
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
    - name: Gather device info
      brocade.fos.brocade_singleton_obj_facts:
        credential: '{{ credential }}'
        vfid: -1
        module_name: brocade-snmp
        obj_name: system
    - name: Print ansible_facts gathered
      ansible.builtin.debug:
        var: ansible_facts
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel generic facts gathering for singleton objects
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_connection import exit_after_login, login, logout
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import singleton_get, to_human_singleton
from ansible_collections.brocade.fos.plugins.module_utils.brocade_yang import str_to_human, str_to_yang


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
        obj_name=dict(required=True, type="str"),
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
    module_name = str_to_human(input_params["module_name"])
    obj_name = str_to_human(input_params["obj_name"])
    result = {"changed": False}

    if vfid is None:
        vfid = 128

    ret_code, auth, fos_version = login(fos_ip_addr, fos_user_name, fos_password, https, throttle, result, timeout)
    if ret_code != 0:
        module.exit_json(**result)

    ret_code, response = singleton_get(
        fos_user_name,
        fos_password,
        fos_ip_addr,
        module_name,
        obj_name,
        fos_version,
        https,
        auth,
        vfid,
        result,
        timeout,
    )
    if ret_code != 0:
        result["singleton_get"] = ret_code
        exit_after_login(fos_ip_addr, https, auth, result, module, timeout)

    obj = response["Response"][str_to_yang(obj_name)]

    to_human_singleton(module_name, obj_name, obj)

    result["obj"] = obj

    ret_dict = {}
    ret_dict[obj_name] = obj

    result["ansible_facts"] = ret_dict

    logout(fos_ip_addr, https, auth, result, timeout)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
