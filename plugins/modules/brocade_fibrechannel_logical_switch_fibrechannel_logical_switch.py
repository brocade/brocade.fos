#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "certified"}


DOCUMENTATION = r"""

module: brocade_fibrechannel_logical_switch_fibrechannel_logical_switch
short_description: Brocade Logical Switch Configuration
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Update logging audit configuration.

options:

    credential:
        description:
        -   Login information for the FOS switch REST API.
        type: dict
        required: true
        suboptions:
            fos_ip_addr:
                description:
                -   IP address or hostname of the FOS switch.
                type: str
                required: true
            fos_user_name:
                description:
                -   Switch login username.
                type: str
                required: true
            fos_password:
                description:
                -   Switch login password.
                type: str
                required: true
            https:
                description:
                -   Connection mode, supplied as a string.
                -   C(true) uses HTTPS with certificate validation.
                -   C(self) uses HTTPS without certificate validation, allowing self-signed certificates.
                -   C(false) uses unencrypted HTTP.
                type: str
                required: true
    vfid:
        description:
        -   VFID of the target switch. Use -1 for FOS without virtual fabrics enabled. For FOS with virtual
            fabrics enabled, specify a valid VFID.
        type: int
    throttle:
        description:
        -   Delay in seconds before retrying once when the switch is busy.
        type: int
    timeout:
        description:
        -   REST timeout in seconds for operations that take longer than the default timeout.
        type: int
    all_entries:
        description:
        -   Whether entries specifies the complete desired list of objects. When true, the module adds,
            updates, and deletes objects to match entries. When false, the module adds or updates the
            specified objects and preserves objects omitted from entries.
        type: bool
    logical_switches:
        description:
        -   List of logical switch data structure Supports all writable attributes exposed by the BSN
            REST API, with hyphens replaced by underscores. All of non-default switches are required. No
            default switch data should be present.
        required: true
        type: list
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
    - name: Initial logical switch configuration
      brocade.fos.brocade_fibrechannel_logical_switch_fibrechannel_logical_switch:
        credential: '{{ credential }}'
        vfid: -1
        logical_switches:
          - fabric_id: 1
            base_switch_enabled: 0
            ficon_mode_enabled: 0
            logical_isl_enabled: 1
            port_member_list:
              port_member:
                - 0/1
                - 0/2
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel Logical Switch Configuration
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
        all_entries=dict(required=False, type="bool"),
        logical_switches=dict(required=True, type="list", elements="raw"),
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
    all_entries = input_params["all_entries"]
    vfid = input_params["vfid"]
    logical_switches = input_params["logical_switches"]
    result = {"changed": False}

    list_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        "brocade_fibrechannel_logical_switch",
        "fibrechannel_logical_switch",
        logical_switches,
        all_entries,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
