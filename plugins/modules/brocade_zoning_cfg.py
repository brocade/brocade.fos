#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_zoning_cfg
short_description: Brocade Fibre Channel zoning cfg configuration
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Create, delete, or update cfgs. Changes are applied to FOS within a single login session that ends
    when the operation completes. If no configuration is active, cfgsave is executed before the session
    ends. If a configuration is active, cfgenable is executed for that configuration to apply any changes
    before the session ends.

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
    cfgs:
        description:
        -   List of cfgs to be created or modified. If a CFG does not exist in the current Zone Database,
            the cfg will be created with the members specified. If a CFG already exists in the current
            Zone Database, the cfg is updated to reflect the members specified. In other words, new
            members will be added and removed members will be removed. cfgs and cfgs_to_delete are
            mutually exclusive.
        type: list
        elements: raw
    members_add_only:
        description:
        -   If true, add new members and preserve existing members omitted from the list.
        type: bool
    members_remove_only:
        description:
        -   If true, remove the specified members.
        type: bool
    cfgs_to_delete:
        description:
        -   List of cfgs to be deleted. cfgs and cfgs_to_delete are mutually exclusive.
        type: list
        elements: raw
    active_cfg:
        description:
        -   Cfg to be enabled (cfg_enable) at the end. If no cfg is specified, cfgs are saved (cfg_save).
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
    cfgs:
      - name: cfg_new_1
        members:
          - zone_new_1
          - zone_new_2
      - name: newcfg2
        members:
          - zone_new_1
          - zone_new_2
      - name: newcfg3
        members:
          - zone_new_1
          - zone_new_2
    cfgs_to_delete:
      - name: newcfg2
      - name: newcfg3
  tasks:
    - name: Create cfgs
      brocade.fos.brocade_zoning_cfg:
        credential: '{{ credential }}'
        vfid: -1
        cfgs: '{{ cfgs }}'
        active_cfg: newcfg2
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""

"""
Brocade Fibre Channel zoning cfg configuration
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_connection import login, logout
from ansible_collections.brocade.fos.plugins.module_utils.brocade_zoning import (
    cfg_delete,
    cfg_get,
    cfg_post,
    cfg_process_diff,
    cfg_process_diff_to_delete,
    zoning_common,
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
        cfgs=dict(required=False, type="list", elements="raw"),
        members_add_only=dict(required=False, type="bool"),
        members_remove_only=dict(required=False, type="bool"),
        cfgs_to_delete=dict(required=False, type="list", elements="raw"),
        active_cfg=dict(required=False, type="str"),
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
    cfgs = input_params["cfgs"]
    members_add_only = input_params["members_add_only"]
    members_remove_only = input_params["members_remove_only"]
    cfgs_to_delete = input_params["cfgs_to_delete"]
    active_cfg = input_params["active_cfg"]
    result = {"changed": False}

    if vfid is None:
        vfid = 128

    ret_code, auth, fos_version = login(fos_ip_addr, fos_user_name, fos_password, https, throttle, result, timeout)
    if ret_code != 0:
        module.exit_json(**result)

    zoning_common(
        fos_ip_addr,
        https,
        fos_version,
        auth,
        vfid,
        result,
        module,
        cfgs,
        members_add_only,
        members_remove_only,
        cfgs_to_delete,
        "cfg",
        cfg_process_diff,
        cfg_process_diff_to_delete,
        cfg_get,
        cfg_post,
        cfg_delete,
        active_cfg,
        False,
        timeout,
    )

    ret_code = logout(fos_ip_addr, https, auth, result, timeout)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
