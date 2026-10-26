#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_zoning_copy
short_description: Brocade Fibre Channel zoning object copy
version_added: '2.7'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   "Mimics zoneObjectCopy funcionalities. The module is used to confirm that an existing object's and the new object's
    contents match. If they do not, the new object may be created or overwritten to match the contents.\nIf an existing
    object is Target Driven Zone, the module will error out. If objects do not match in terms of type (Alias, Zone,
    or Cfg), the module will error out."

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
    object_name:
        description:
        -   Name of the object to copy from.
        required: true
        type: str
    new_name:
        description:
        -   Name of the object to copy to.
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
    - name: Copy alias
      brocade.fos.brocade_zoning_copy:
        credential: '{{ credential }}'
        vfid: -1
        object_name: old_alias
        new_name: new_alias
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel zoning object copy
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_connection import login, logout
from ansible_collections.brocade.fos.plugins.module_utils.brocade_zoning import (
    alias_delete,
    alias_get,
    alias_post,
    alias_process_diff,
    alias_process_diff_to_delete,
    cfg_delete,
    cfg_get,
    cfg_post,
    cfg_process_diff,
    cfg_process_diff_to_delete,
    zone_delete,
    zone_get,
    zone_post,
    zone_process_diff,
    zone_process_diff_to_delete,
    zoning_common,
    zoning_find_pair_common,
)


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
        object_name=dict(required=True, type="str"),
        new_name=dict(required=True, type="str"),
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
    object_name = input_params["object_name"]
    new_name = input_params["new_name"]
    result = {"changed": False}

    if vfid is None:
        vfid = 128

    ret_code, auth, fos_version = login(fos_ip_addr, fos_user_name, fos_password, https, throttle, result, timeout)
    if ret_code != 0:
        module.exit_json(**result)

    object_name_dict, new_name_dict = zoning_find_pair_common(
        module, fos_ip_addr, https, fos_version, auth, vfid, "alias", object_name, new_name, result, timeout
    )

    result["object_name_dict"] = object_name_dict
    result["new_name_dict"] = new_name_dict

    # object_name was found and new_name doesn't exist. Create one
    if len(object_name_dict) > 0:
        object_name_dict["name"] = new_name
        obj_list = [object_name_dict]
        zoning_common(
            fos_ip_addr,
            https,
            fos_version,
            auth,
            vfid,
            result,
            module,
            obj_list,
            False,
            False,
            None,
            "alias",
            alias_process_diff,
            alias_process_diff_to_delete,
            alias_get,
            alias_post,
            alias_delete,
            None,
            False,
            timeout,
        )
        ret_code = logout(fos_ip_addr, https, auth, result, timeout)
        module.exit_json(**result)

    object_name_dict, new_name_dict = zoning_find_pair_common(
        module, fos_ip_addr, https, fos_version, auth, vfid, "zone", object_name, new_name, result, timeout
    )

    result["object_name_dict"] = object_name_dict
    result["new_name_dict"] = new_name_dict

    # object_name was found and new_name doesn't exist. Create one
    if len(object_name_dict) > 0:
        if object_name_dict["zone-type"] == 2:
            result["failed"] = True
            result["msg"] = "Target created Peer Zone cannot be copied"
            ret_code = logout(fos_ip_addr, https, auth, result, timeout)
            module.exit_json(**result)

        object_name_dict["name"] = new_name
        obj_list = [object_name_dict]
        zoning_common(
            fos_ip_addr,
            https,
            fos_version,
            auth,
            vfid,
            result,
            module,
            obj_list,
            False,
            False,
            None,
            "zone",
            zone_process_diff,
            zone_process_diff_to_delete,
            zone_get,
            zone_post,
            zone_delete,
            None,
            False,
            timeout,
        )
        ret_code = logout(fos_ip_addr, https, auth, result, timeout)
        module.exit_json(**result)

    object_name_dict, new_name_dict = zoning_find_pair_common(
        module, fos_ip_addr, https, fos_version, auth, vfid, "cfg", object_name, new_name, result, timeout
    )

    result["object_name_dict"] = object_name_dict
    result["new_name_dict"] = new_name_dict

    # object_name was found and new_name doesn't exist. Create one
    if len(object_name_dict) > 0:
        object_name_dict["name"] = new_name
        obj_list = [object_name_dict]
        zoning_common(
            fos_ip_addr,
            https,
            fos_version,
            auth,
            vfid,
            result,
            module,
            obj_list,
            False,
            False,
            None,
            "cfg",
            cfg_process_diff,
            cfg_process_diff_to_delete,
            cfg_get,
            cfg_post,
            cfg_delete,
            None,
            False,
            timeout,
        )
        ret_code = logout(fos_ip_addr, https, auth, result, timeout)
        module.exit_json(**result)

    result["failed"] = True
    result["msg"] = "no such object was found"
    ret_code = logout(fos_ip_addr, https, auth, result, timeout)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
