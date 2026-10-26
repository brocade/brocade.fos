#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_list_obj
short_description: Brocade Fibre Channel general list processing
version_added: '2.7'
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Update Fibre Channel list of objects based on module name and list name provided.

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
        required: true
        type: str
    all_entries:
        description:
        -   Whether entries specifies the complete desired list of objects. When true, the module adds,
            updates, and deletes objects to match entries. When false, the module adds or updates the
            specified objects and preserves objects omitted from entries.
        type: bool
    entries:
        description:
        -   List of objects. Each element is a dict whose keys match the YANG attribute names with hyphens
            replaced by underscores. Using hyphens may cause erroneous behaviour due to Ansible parsing.
        -   The required attributes within each element depend on the module_name and list_name values. All
            sub-keys listed here are optional and drawn from the known list objects in the collection.
        type: list
        elements: dict
        suboptions:
            name:
                description:
                -   Primary key used by fibrechannel_switch, fabric_switch, fibrechannel,
                    fibrechannel_diagnostics, license, ipfilter_policy, user_config, maps group, rule, and
                    maps_policy list objects.
                type: str
            index:
                description:
                -   Primary key for SNMP v1_account and v1_trap list objects.
                type: int
            trap_index:
                description:
                -   Primary key for SNMP v3_trap list object.
                type: int
            fabric_id:
                description:
                -   Primary key for fibrechannel_logical_switch list object.
                type: int
            port_group_id:
                description:
                -   Primary key for brocade_access_gateway port_group list object.
                type: int
            n_port:
                description:
                -   Primary key for brocade_access_gateway n_port_map list object.
                type: str
            policy_name:
                description:
                -   Key for brocade_security ipfilter_rule list object.
                type: str
            server:
                description:
                -   Key for brocade_security radius_server, tacacs_server, ldap_server and brocade_logging
                    syslog_server list objects.
                type: str
            ldap_role:
                description:
                -   Key for brocade_security ldap_role_map list object.
                type: str
            algorithm_type:
                description:
                -   Key for brocade_security sshutil_key list object.
                type: str
            key_type:
                description:
                -   Key for brocade_security sshutil_key list object.
                type: str
            user_name:
                description:
                -   Key for brocade_security sshutil_public_key and user_config list objects.
                type: str
            message_id:
                description:
                -   Key for brocade_logging raslog list object.
                type: str
            module_id:
                description:
                -   Key for brocade_logging raslog_module list object.
                type: str
            log_type:
                description:
                -   Key for brocade_logging log_quiet_control list object.
                type: str
            group_type:
                description:
                -   Key for brocade_maps paused_cfg list object.
                type: str
            mib_name:
                description:
                -   Key for brocade_snmp mib_capability list object.
                type: str
            trap_name:
                description:
                -   Key for brocade_snmp trap_capability list object.
                type: str
            hba_id:
                description:
                -   Key for brocade_fdmi hba list object.
                type: str
            port_name:
                description:
                -   Key for brocade_fdmi port list object.
                type: str
            slot_number:
                description:
                -   Key for brocade_fru blade list object.
                type: int
            trunk_index:
                description:
                -   Key for brocade_fibrechannel_trunk trunk_area list object.
                type: int
            port_id:
                description:
                -   Key for brocade_name_server fibrechannel_name_server list object.
                type: str
            link_address:
                description:
                -   Key for ficon ficon_logical_path list object.
                type: str
            channel_image_id:
                description:
                -   Key for ficon ficon_logical_path list object.
                type: str
            dp_id:
                description:
                -   Key for brocade_interface extension_ip_interface and brocade_extension_ip_route list
                    objects.
                type: int
            ip_address:
                description:
                -   Key for brocade_interface extension_ip_interface and brocade_extension_ip_route list
                    objects.
                type: str
            ip_prefix_length:
                description:
                -   Key for brocade_extension_ip_route list object.
                type: int
            community_name:
                description:
                -   Community name string. Used with brocade_snmp v1_account list object. Not logged.
                type: str
            authentication_protocol:
                description:
                -   SNMPv3 authentication protocol (e.g. sha512). Used with brocade_snmp v3_account list
                    object.
                type: str
            manager_engine_id:
                description:
                -   SNMPv3 manager engine ID. Used with brocade_snmp v3_account list object.
                type: str
            privacy_protocol:
                description:
                -   SNMPv3 privacy protocol (e.g. aes128). Used with brocade_snmp v3_account list object.
                type: str
            user_group:
                description:
                -   SNMPv3 user group. Used with brocade_snmp v3_account list object.
                type: str
            authentication_password:
                description:
                -   SNMPv3 authentication password. Not logged. Used with brocade_snmp v3_account list object.
                type: str
            privacy_password:
                description:
                -   SNMPv3 privacy password. Not logged. Used with brocade_snmp v3_account list object.
                type: str
            host:
                description:
                -   SNMP trap destination host IP address. Used with brocade_snmp v1_trap and v3_trap list
                    objects.
                type: str
            port_number:
                description:
                -   SNMP trap destination port number. Used with brocade_snmp v1_trap and v3_trap list
                    objects.
                type: int
            trap_severity_level:
                description:
                -   SNMP trap severity level (e.g. warning). Used with brocade_snmp v1_trap and v3_trap list
                    objects.
                type: str
            informs_enabled:
                description:
                -   Enable SNMPv3 informs instead of traps. Used with brocade_snmp v3_trap list object.
                type: bool
            usm_index:
                description:
                -   SNMPv3 USM account index for the trap. Used with brocade_snmp v3_trap list object.
                type: int
            account_enabled:
                description:
                -   Enable or disable the user account. Used with brocade_security user_config list object.
                type: bool
            password:
                description:
                -   User account password (base64-encoded). Used with brocade_security user_config list
                    object. Not logged.
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
            ip_version:
                description:
                -   IP version for the ipfilter policy (IPv4 or IPv6). Used with brocade_security
                    ipfilter_policy list object.
                type: str
            destination_end_port:
                description:
                -   Destination end port for the ipfilter rule. Used with brocade_security ipfilter_rule list
                    object.
                type: int
            destination_ip:
                description:
                -   Destination IP address or any. Used with brocade_security ipfilter_rule list object.
                type: str
            destination_start_port:
                description:
                -   Destination start port for the ipfilter rule. Used with brocade_security ipfilter_rule
                    list object.
                type: int
            permission:
                description:
                -   Permit or deny action for the ipfilter rule. Used with brocade_security ipfilter_rule list
                    object.
                type: str
            protocol:
                description:
                -   Protocol for the ipfilter rule (e.g. tcp, udp). Used with brocade_security ipfilter_rule
                    list object.
                type: str
            source_ip:
                description:
                -   Source IP address or any. Used with brocade_security ipfilter_rule list object.
                type: str
            traffic_type:
                description:
                -   Traffic direction (e.g. INPUT). Used with brocade_security ipfilter_rule list object.
                type: str
            switch_role:
                description:
                -   Switch role mapped from an LDAP role. Used with brocade_security ldap_role_map list
                    object.
                type: str
            port:
                description:
                -   Syslog server port number. Used with brocade_logging syslog_server list object.
                type: int
            secure_mode:
                description:
                -   Enable TLS for the syslog server connection. Used with brocade_logging syslog_server list
                    object.
                type: bool
            actions:
                description:
                -   Dict containing an action list of MAPS alert actions (e.g. raslog). Used with brocade_maps
                    rule list object.
                type: dict
            event_severity:
                description:
                -   Severity of the MAPS rule event. Used with brocade_maps rule list object.
                type: str
            group_name:
                description:
                -   MAPS group name associated with the rule. Used with brocade_maps rule list object.
                type: str
            is_rule_on_rule:
                description:
                -   Indicates if this is a rule-on-rule type. Used with brocade_maps rule list object.
                type: bool
            logical_operator:
                description:
                -   Logical comparison operator (e.g. g for greater-than). Used with brocade_maps rule list
                    object.
                type: str
            monitoring_system:
                description:
                -   MAPS monitoring system identifier (e.g. C3TXTO). Used with brocade_maps rule list object.
                type: str
            quiet_time:
                description:
                -   Quiet time in seconds between repeat alerts. Used with brocade_maps rule list object.
                type: int
            threshold_value:
                description:
                -   Threshold value that triggers the rule. Used with brocade_maps rule list object.
                type: int
            time_base:
                description:
                -   Time base for the threshold (e.g. Min, Sec). Used with brocade_maps rule list object.
                type: str
            rule_list:
                description:
                -   Dict containing a rule list of MAPS rule names assigned to a policy. Used with
                    brocade_maps maps_policy list object.
                type: dict
            port_group_n_ports:
                description:
                -   Dict containing an n_port list of N-Port members for this port group. Used with
                    brocade_access_gateway port_group list object.
                type: dict
            port_group_f_ports:
                description:
                -   Dict containing an f_port list of F-Port members for this port group. Used with
                    brocade_access_gateway port_group list object.
                type: dict
            port_group_name:
                description:
                -   Human-readable name for the port group. Used with brocade_access_gateway port_group list
                    object.
                type: str
            configured_f_port_list:
                description:
                -   Dict containing an f_port list of configured F-Ports for this N-Port mapping. Used with
                    brocade_access_gateway n_port_map list object.
                type: dict
            static_f_port_list:
                description:
                -   Dict containing an f_port list of static F-Ports. Used with brocade_access_gateway
                    n_port_map list object.
                type: dict
            login_limit:
                description:
                -   Maximum login limit for the N-Port. Used with brocade_access_gateway n_port_map list
                    object.
                type: int
            port_member_list:
                description:
                -   Dict containing a port_member list of port members for the logical switch. Used with
                    brocade_fibrechannel_logical_switch fibrechannel_logical_switch list object.
                type: dict
    delete_entries:
        description:
        -   List of entries to be deleted. Mutually exclusive with entries. Each element should contain only
            the key attribute(s) for the list object (e.g. name, index, server, policy_name + index, etc.).
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
    - name: List object example
      brocade.fos.brocade_list_obj:
        credential: '{{ credential }}'
        vfid: -1
        module_name: brocade-snmp
        list_name: v3-account
        all_entries: false
        entries:
          - index: 1
            community_name: new name
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel Yang list processor
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import list_delete_helper, list_helper
from ansible_collections.brocade.fos.plugins.module_utils.brocade_yang import str_to_human


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
        all_entries=dict(required=False, type="bool"),
        entries=dict(
            required=False,
            type="list",
            elements="dict",
            options=dict(
                # Common key fields
                name=dict(required=False, type="str"),
                index=dict(required=False, type="int"),
                trap_index=dict(required=False, type="int"),
                fabric_id=dict(required=False, type="int"),
                port_group_id=dict(required=False, type="int"),
                n_port=dict(required=False, type="str"),
                policy_name=dict(required=False, type="str"),
                server=dict(required=False, type="str"),
                ldap_role=dict(required=False, type="str"),
                algorithm_type=dict(required=False, type="str"),
                key_type=dict(required=False, type="str"),
                user_name=dict(required=False, type="str"),
                message_id=dict(required=False, type="str"),
                module_id=dict(required=False, type="str"),
                log_type=dict(required=False, type="str"),
                group_type=dict(required=False, type="str"),
                mib_name=dict(required=False, type="str"),
                trap_name=dict(required=False, type="str"),
                hba_id=dict(required=False, type="str"),
                port_name=dict(required=False, type="str"),
                slot_number=dict(required=False, type="int"),
                trunk_index=dict(required=False, type="int"),
                port_id=dict(required=False, type="str"),
                link_address=dict(required=False, type="str"),
                channel_image_id=dict(required=False, type="str"),
                dp_id=dict(required=False, type="int"),
                ip_address=dict(required=False, type="str"),
                ip_prefix_length=dict(required=False, type="int"),
                # brocade_snmp / v1_account
                community_name=dict(required=False, type="str", no_log=True),
                # brocade_snmp / v3_account
                authentication_protocol=dict(required=False, type="str"),
                manager_engine_id=dict(required=False, type="str"),
                privacy_protocol=dict(required=False, type="str"),
                user_group=dict(required=False, type="str"),
                authentication_password=dict(required=False, type="str", no_log=True),
                privacy_password=dict(required=False, type="str", no_log=True),
                # brocade_snmp / v1_trap and v3_trap
                host=dict(required=False, type="str"),
                port_number=dict(required=False, type="int"),
                trap_severity_level=dict(required=False, type="str"),
                # brocade_snmp / v3_trap
                informs_enabled=dict(required=False, type="bool"),
                usm_index=dict(required=False, type="int"),
                # brocade_security / user_config
                account_enabled=dict(required=False, type="bool"),
                password=dict(required=False, type="str", no_log=True),
                virtual_fabric_role_id_list=dict(required=False, type="dict"),
                chassis_access_role=dict(required=False, type="str"),
                role=dict(required=False, type="str"),
                account_description=dict(required=False, type="str"),
                # brocade_security / ipfilter_policy
                ip_version=dict(required=False, type="str"),
                # brocade_security / ipfilter_rule
                destination_end_port=dict(required=False, type="int"),
                destination_ip=dict(required=False, type="str"),
                destination_start_port=dict(required=False, type="int"),
                permission=dict(required=False, type="str"),
                protocol=dict(required=False, type="str"),
                source_ip=dict(required=False, type="str"),
                traffic_type=dict(required=False, type="str"),
                # brocade_security / ldap_role_map
                switch_role=dict(required=False, type="str"),
                # brocade_logging / syslog_server
                port=dict(required=False, type="int"),
                secure_mode=dict(required=False, type="bool"),
                # brocade_maps / rule
                actions=dict(required=False, type="dict"),
                event_severity=dict(required=False, type="str"),
                group_name=dict(required=False, type="str"),
                is_rule_on_rule=dict(required=False, type="bool"),
                logical_operator=dict(required=False, type="str"),
                monitoring_system=dict(required=False, type="str"),
                quiet_time=dict(required=False, type="int"),
                threshold_value=dict(required=False, type="int"),
                time_base=dict(required=False, type="str"),
                # brocade_maps / maps_policy
                rule_list=dict(required=False, type="dict"),
                # brocade_access_gateway / port_group
                port_group_n_ports=dict(required=False, type="dict"),
                port_group_f_ports=dict(required=False, type="dict"),
                port_group_name=dict(required=False, type="str"),
                # brocade_access_gateway / n_port_map
                configured_f_port_list=dict(required=False, type="dict"),
                static_f_port_list=dict(required=False, type="dict"),
                login_limit=dict(required=False, type="int"),
                # brocade_fibrechannel_logical_switch
                port_member_list=dict(required=False, type="dict"),
            ),
        ),
        delete_entries=dict(required=False, type="list", elements="raw"),
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
    entries = input_params["entries"]
    all_entries = input_params["all_entries"]
    delete_entries = input_params["delete_entries"]
    result = {"changed": False}

    # if delete_entries is not None, then we make sure
    # the attributes listed are not present.
    # entries update does not happen at the same
    # time
    if delete_entries is not None:
        return list_delete_helper(
            module,
            fos_ip_addr,
            fos_user_name,
            fos_password,
            https,
            throttle,
            vfid,
            module_name,
            list_name,
            delete_entries,
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
        module_name,
        list_name,
        entries,
        all_entries,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
