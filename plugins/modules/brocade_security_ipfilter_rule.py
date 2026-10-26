#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_security_ipfilter_rule
short_description: Brocade Fibre Channel security ipfilter rule configuration
version_added: '2.7'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Update Fibre Channel security ipfilter rule configuration.

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
    ipfilter_rules:
        description:
        -   List of IP-filter rules. Supports all writable attributes exposed by the BSN REST API, with
            hyphens replaced by underscores.
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
    - name: Ipfilter policy is created or present
      brocade.fos.brocade_security_ipfilter_policy:
        credential: '{{ credential }}'
        vfid: -1
        ipfilter_policies:
          - name: Ipv4_telnet_http
            ip_version: IPv4
    - name: Ipfilter rules are created or present
      brocade.fos.brocade_security_ipfilter_rule:
        credential: '{{ credential }}'
        vfid: -1
        ipfilter_rules:
          - policy_name: ipv4_telnet_http
            index: 1
            destination_end_port: 22
            destination_ip: any
            destination_start_port: 22
            permission: permit
            protocol: tcp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 2
            destination_end_port: 23
            destination_ip: any
            destination_start_port: 23
            permission: deny
            protocol: tcp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 3
            destination_end_port: 80
            destination_ip: any
            destination_start_port: 80
            permission: permit
            protocol: tcp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 4
            destination_end_port: 443
            destination_ip: any
            destination_start_port: 443
            permission: permit
            protocol: tcp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 5
            destination_end_port: 161
            destination_ip: any
            destination_start_port: 161
            permission: permit
            protocol: udp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 6
            destination_end_port: 123
            destination_ip: any
            destination_start_port: 123
            permission: permit
            protocol: udp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 7
            destination_end_port: 1023
            destination_ip: any
            destination_start_port: 600
            permission: permit
            protocol: tcp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 8
            destination_end_port: 1023
            destination_ip: any
            destination_start_port: 600
            permission: permit
            protocol: udp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 9
            destination_end_port: 389
            destination_ip: any
            destination_start_port: 389
            permission: permit
            protocol: tcp
            source_ip: any
            traffic_type: INPUT
          - policy_name: ipv4_telnet_http
            index: 10
            destination_end_port: 389
            destination_ip: any
            destination_start_port: 389
            permission: permit
            protocol: udp
            source_ip: any
            traffic_type: INPUT
    - name: Ipfilter policy is activated or active already
      brocade.fos.brocade_security_ipfilter_policy:
        credential: '{{ credential }}'
        vfid: -1
        active_policy: ipv4_telnet_http
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel ipfilter rule configuration
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
        ipfilter_rules=dict(required=True, type="list", elements="raw"),
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
    ipfilter_rules = input_params["ipfilter_rules"]
    result = {"changed": False}

    list_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        "brocade_security",
        "ipfilter_rule",
        ipfilter_rules,
        False,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
