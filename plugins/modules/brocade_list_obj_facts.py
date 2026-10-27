#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_list_obj_facts
short_description: Brocade Fibre Channel generic facts gathering for list objects
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Gather Fibre Channel FOS facts for objects that are defined as list in YANG.

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
    list_name:
        description:
        -   YANG name for the list object. Hyphens and underscores can be used interchangeably. If the
            YANG list name is xy-z, either xy-z or xy_z is acceptable.
        type: str
        required: true
    attributes:
        description:
        -   List of attributes for the object to match to return. Names match YANG REST attributes with
            "-" replaced with "_". If none is given, the module returns all valid entries. Using hyphens
            in the name may result in erroneous behavior based on Ansible parsing.
        type: dict
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
    - name: Gather device info
      brocade.fos.brocade_list_obj_facts:
        credential: '{{ credential }}'
        vfid: -1
        module_name: brocade-name-server
        list_name: fibrechannel-name-server
        attributes:
          port_name: '{{ wwn_to_search }}'
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
Brocade Fibre Channel gather facts
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_connection import exit_after_login, login, logout
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import list_get, to_human_list
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
        list_name=dict(required=True, type="str"),
        attributes=dict(required=False, type="dict"),
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
    list_name = str_to_human(input_params["list_name"])
    attributes = input_params["attributes"]
    result = {"changed": False}

    if vfid is None:
        vfid = 128

    ret_code, auth, fos_version = login(fos_ip_addr, fos_user_name, fos_password, https, throttle, result, timeout)
    if ret_code != 0:
        module.exit_json(**result)

    ret_code, response = list_get(
        fos_user_name,
        fos_password,
        fos_ip_addr,
        module_name,
        list_name,
        fos_version,
        https,
        auth,
        vfid,
        result,
        timeout,
    )
    if ret_code != 0:
        result["list_get"] = ret_code
        exit_after_login(fos_ip_addr, https, auth, result, module, timeout)

    obj_list = response["Response"][str_to_yang(list_name)]
    if not isinstance(obj_list, list):
        obj_list = [] if obj_list is None else [obj_list]

    to_human_list(module_name, list_name, obj_list, result)

    result["obj_list"] = obj_list

    ret_dict = {}
    ret_list = []
    for obj in obj_list:
        if attributes is None:
            ret_list.append(obj)
        else:
            matched_all = 0
            for k, v in attributes.items():
                if k in obj and str(obj[k]) == str(v):
                    matched_all = matched_all + 1

            if matched_all == len(attributes.items()):
                ret_list.append(obj)

    if attributes is None:
        result["attributes_len"] = 0
    else:
        result["attributes_len"] = len(attributes.items())
    result["ret_list"] = ret_list

    ret_dict[list_name] = ret_list

    result["ansible_facts"] = ret_dict

    logout(fos_ip_addr, https, auth, result, timeout)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
