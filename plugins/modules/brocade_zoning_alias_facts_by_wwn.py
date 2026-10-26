#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_zoning_alias_facts_by_wwn
short_description: Brocade Fibre Channel facts gathering of zoning by WWN
version_added: '2.6'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Gather Fibre Channel FOS facts.

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
    wwn:
        description:
        -   WWN to search in the aliases within Zone DB.
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
    wwn_to_search: aa:bb:cc:dd:ee:ff:11:15
  tasks:
    - name: Gather device alias info
      brocade.fos.brocade_zoning_alias_facts_by_wwn:
        credential: '{{ credential }}'
        vfid: -1
        wwn: '{{ wwn_to_search }}'
    - name: Print device alias information matching port_name
      when: ansible_facts['alias'] is defined
      ansible.builtin.debug:
        var: ansible_facts['alias']
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel facts gathering of zoning by WWN
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_connection import exit_after_login, login, logout
from ansible_collections.brocade.fos.plugins.module_utils.brocade_zoning import defined_get


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
        wwn=dict(required=True, type="str"),
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
    wwn = input_params["wwn"]
    result = {"changed": False}

    if vfid is None:
        vfid = 128

    ret_code, auth, fos_version = login(fos_ip_addr, fos_user_name, fos_password, https, throttle, result, timeout)
    if ret_code != 0:
        module.exit_json(**result)

    ret_code, response = defined_get(fos_ip_addr, https, fos_version, auth, vfid, result, timeout)
    if ret_code != 0:
        exit_after_login(fos_ip_addr, https, auth, result, module)

    if ret_code != 0:
        exit_after_login(fos_ip_addr, https, auth, result, module)

    alias_list = []
    if "alias" in response["Response"]["defined-configuration"]:
        if isinstance(response["Response"]["defined-configuration"]["alias"], list):
            alias_list = response["Response"]["defined-configuration"]["alias"]
        else:
            alias_list = [response["Response"]["defined-configuration"]["alias"]]

    result["alias_list"] = alias_list

    ret_list = []
    for alias in alias_list:
        if "member-entry" in alias and "alias-entry-name" in alias["member-entry"]:
            if isinstance(alias["member-entry"]["alias-entry-name"], list):
                for entry in alias["member-entry"]["alias-entry-name"]:
                    if entry == wwn.lower():
                        ret_list.append(alias)
                        break
            else:
                if alias["member-entry"]["alias-entry-name"] == wwn.lower():
                    ret_list.append(alias)

    ret_dict = {}
    if len(ret_list) > 0:
        ret_dict["alias"] = ret_list

    result["ansible_facts"] = ret_dict

    logout(fos_ip_addr, https, auth, result, timeout)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
