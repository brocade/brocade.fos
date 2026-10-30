#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_singleton_obj
short_description: Brocade Fibre Channel generic handler for singleton object
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Update list of attributes based on module name and object name provided.

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
    attributes:
        description:
        -   Attribute key-value pairs for the singleton object identified by module_name and obj_name. Key
            names match the REST attribute names with hyphens replaced by underscores. Using hyphens may cause
            erroneous behaviour due to Ansible parsing.
        -   The specific sub-keys required depend on the obj_name value. All sub-keys listed below are
            optional and drawn from the known singleton objects in the collection. Keys not listed here may
            still be passed for singleton objects not covered by a dedicated module.
        -   Special note for brocade_security / password - old_password and new_password are supplied in plain
            text and are encoded by the module. If user_name refers to a non-admin account only new_password
            is needed.
        required: true
        type: dict
        suboptions:
            user_name:
                description:
                -   Account or local user name. Used with brocade_security password,
                    sshutil_public_key_action, and user_config objects.
                type: str
            old_password:
                description:
                -   Existing password in plain text. Used with brocade_security password object.
                type: str
            new_password:
                description:
                -   New password in plain text. Used with brocade_security password object.
                type: str
            operation:
                description:
                -   Certificate operation such as import or export. Used with brocade_security
                    security_certificate_action object.
                type: str
            certificate_entity:
                description:
                -   Certificate entity type (e.g. CSC, switch). Used with brocade_security
                    security_certificate_action object.
                type: str
            certificate_type:
                description:
                -   Certificate type (e.g. https, ldap). Used with brocade_security
                    security_certificate_action object.
                type: str
            certificate_name:
                description:
                -   Certificate file name. Used with brocade_security security_certificate_action object.
                type: str
            remote_host_ip:
                description:
                -   IP address of the remote host for file transfer. Used with security_certificate_action,
                    sshutil_public_key_action, and sec_crypto_cfg_template_action objects.
                type: str
            remote_host_port:
                description:
                -   Port number on the remote host for file transfer.
                type: int
            remote_user_name:
                description:
                -   User name on the remote host. Used with security_certificate_action,
                    sshutil_public_key_action, and sec_crypto_cfg_template_action objects.
                type: str
            remote_user_password:
                description:
                -   Password for the remote host user. Encoded automatically by the module. Not logged. Used
                    with security_certificate_action, sshutil_public_key_action, and
                    sec_crypto_cfg_template_action objects.
                type: str
            remote_directory:
                description:
                -   Directory path on the remote host. Used with security_certificate_action,
                    sshutil_public_key_action, and sec_crypto_cfg_template_action objects.
                type: str
            protocol:
                description:
                -   Transfer protocol for remote file operations (e.g. scp, sftp, ftp). Used with
                    security_certificate_action and sshutil_public_key_action objects.
                type: str
            public_key_name:
                description:
                -   SSH public key file name. Used with brocade_security sshutil_public_key_action object.
                type: str
            action:
                description:
                -   Operation to perform. Used with sshutil_public_key_action (import, export) and
                    sec_crypto_cfg_template_action (import, export, apply).
                type: str
            template_name:
                description:
                -   Crypto config template name. Used with brocade_security sec_crypto_cfg_template_action
                    object.
                type: str
            file_transfer_protocol_type:
                description:
                -   Transfer protocol for crypto template file operations (scp, sftp, ftp). Used with
                    brocade_security sec_crypto_cfg_template_action object.
                type: str
            port_group_policy_enabled:
                description:
                -   Enable or disable the port-group policy on an Access Gateway. Used with
                    brocade_access_gateway policy object.
                type: bool
            auto_policy_enabled:
                description:
                -   Enable or disable the auto policy on an Access Gateway. Used with brocade_access_gateway
                    policy object.
                type: bool
            reliability_counter:
                description:
                -   N-Port reliability counter value. Used with brocade_access_gateway n_port_settings object.
                type: int
            maps_policy:
                description:
                -   Active MAPS policy name. Used with brocade_maps maps_config object.
                type: str
            relay_ip_address:
                description:
                -   MAPS email relay server IP address. Used with brocade_maps maps_config object.
                type: str
            domain_name:
                description:
                -   MAPS email relay domain name. Used with brocade_maps maps_config object.
                type: str
            sender_address:
                description:
                -   MAPS email sender address. Used with brocade_maps maps_config object.
                type: str
            recipient_address_list:
                description:
                -   Dict containing a recipient_address list of email recipients. Used with brocade_maps
                    maps_config object.
                type: dict
            actions:
                description:
                -   Dict of MAPS actions to perform on alert. Used with brocade_maps maps_config object.
                type: dict
            chassis_user_friendly_name:
                description:
                -   User-friendly chassis name string. Used with brocade_chassis chassis object.
                type: str
            insistent_domain_id_enabled:
                description:
                -   Enable insistent domain ID feature. Used with brocade_fibrechannel_configuration fabric
                    object.
                type: bool
            preserved_domain_id_mode_enabled:
                description:
                -   Enable preserved domain ID mode. Used with brocade_fibrechannel_configuration fabric
                    object.
                type: bool
            principal_selection_enabled:
                description:
                -   Enable principal switch selection. Must be specified together with principal_priority.
                    Used with brocade_fibrechannel_configuration fabric object.
                type: bool
            principal_priority:
                description:
                -   Principal switch priority value (hex string, e.g. 0x6). Must be specified together with
                    principal_selection_enabled. Used with brocade_fibrechannel_configuration fabric object.
                type: str
            portname_mode:
                description:
                -   Port naming mode (e.g. dynamic, default). Used with brocade_fibrechannel_configuration
                    port_configuration object.
                type: str
            dynamic_portname_format:
                description:
                -   Dynamic port name format string (e.g. I.T.A.R). Used with
                    brocade_fibrechannel_configuration port_configuration object.
                type: str
            audit_enabled:
                description:
                -   Enable or disable audit logging. Used with brocade_logging audit object.
                type: bool
            severity_level:
                description:
                -   Minimum severity level for audit log events (e.g. info, warning, error, critical). Used
                    with brocade_logging audit object.
                type: str
            filter_class_list:
                description:
                -   Dict containing a filter_class list of audit filter classes (e.g. zone, security,
                    configuration, firmware, fabric, ls, cli, maps). Used with brocade_logging audit object.
                type: dict
            name:
                description:
                -   IANA time zone name (e.g. America/Chicago). Used with brocade_time time_zone object.
                type: str
            ntp_server_address:
                description:
                -   Dict containing a server_address list of NTP server IP addresses. Used with brocade_time
                    clock_server object.
                type: dict
            audit_interval:
                description:
                -   SNMP audit interval in minutes. Used with brocade_snmp system object.
                type: int
            contact:
                description:
                -   SNMP system contact string. Used with brocade_snmp system object.
                type: str
            description:
                description:
                -   SNMP system description string. Used with brocade_snmp system object.
                type: str
            encryption_enabled:
                description:
                -   Enable SNMP encryption. Used with brocade_snmp system object.
                type: bool
            informs_enabled:
                description:
                -   Enable SNMP inform notifications. Used with brocade_snmp system object.
                type: bool
            location:
                description:
                -   SNMP system physical location string. Used with brocade_snmp system object.
                type: str
            security_get_level_string:
                description:
                -   SNMP security level for GET operations (e.g. authentication-and-privacy). Used with
                    brocade_snmp system object.
                type: str
            security_set_level_string:
                description:
                -   SNMP security level for SET operations (e.g. authentication-and-privacy). Used with
                    brocade_snmp system object.
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
    - name: Change password
      brocade.fos.brocade_singleton_obj:
        credential: '{{ credential }}'
        vfid: -1
        module_name: brocade-security
        obj_name: password
        attributes:
          user_name: user
          new_password: xxxx
          old_password: yyyy
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel generic handler for singleton object
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import singleton_helper
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
        obj_name=dict(required=True, type="str"),
        # TODO: optimize with custom class
        attributes=dict(
            required=True,
            type="dict",
            options=dict(
                # brocade_security / password
                user_name=dict(required=False, type="str"),
                old_password=dict(required=False, type="str", no_log=True),
                new_password=dict(required=False, type="str", no_log=True),
                # brocade_security / security_certificate_action
                operation=dict(required=False, type="str"),
                certificate_entity=dict(required=False, type="str"),
                certificate_type=dict(required=False, type="str"),
                certificate_name=dict(required=False, type="str"),
                remote_host_ip=dict(required=False, type="str"),
                remote_host_port=dict(required=False, type="int"),
                remote_user_name=dict(required=False, type="str"),
                remote_user_password=dict(required=False, type="str", no_log=True),
                remote_directory=dict(required=False, type="str"),
                protocol=dict(required=False, type="str"),
                # brocade_security / sshutil_public_key_action
                public_key_name=dict(required=False, type="str"),
                action=dict(required=False, type="str"),
                # brocade_security / sec_crypto_cfg_template_action
                template_name=dict(required=False, type="str"),
                file_transfer_protocol_type=dict(required=False, type="str"),
                # brocade_access_gateway / policy
                port_group_policy_enabled=dict(required=False, type="bool"),
                auto_policy_enabled=dict(required=False, type="bool"),
                # brocade_access_gateway / n_port_settings
                reliability_counter=dict(required=False, type="int"),
                # brocade_maps / maps_config
                maps_policy=dict(required=False, type="str"),
                relay_ip_address=dict(required=False, type="str"),
                domain_name=dict(required=False, type="str"),
                sender_address=dict(required=False, type="str"),
                recipient_address_list=dict(required=False, type="dict"),
                actions=dict(required=False, type="dict"),
                # brocade_chassis / chassis
                chassis_user_friendly_name=dict(required=False, type="str"),
                # brocade_fibrechannel_configuration / fabric
                insistent_domain_id_enabled=dict(required=False, type="bool"),
                preserved_domain_id_mode_enabled=dict(required=False, type="bool"),
                principal_selection_enabled=dict(required=False, type="bool"),
                principal_priority=dict(required=False, type="str"),
                # brocade_fibrechannel_configuration / port_configuration
                portname_mode=dict(required=False, type="str"),
                dynamic_portname_format=dict(required=False, type="str"),
                # brocade_logging / audit
                audit_enabled=dict(required=False, type="bool"),
                severity_level=dict(required=False, type="str"),
                filter_class_list=dict(required=False, type="dict"),
                # brocade_time / time_zone
                name=dict(required=False, type="str"),
                # brocade_time / clock_server
                ntp_server_address=dict(required=False, type="dict"),
                # brocade_snmp / system
                audit_interval=dict(required=False, type="int"),
                contact=dict(required=False, type="str"),
                description=dict(required=False, type="str"),
                encryption_enabled=dict(required=False, type="bool"),
                informs_enabled=dict(required=False, type="bool"),
                location=dict(required=False, type="str"),
                security_get_level_string=dict(required=False, type="str"),
                security_set_level_string=dict(required=False, type="str"),
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
    module_name = str_to_human(input_params["module_name"])
    obj_name = str_to_human(input_params["obj_name"])
    attributes = input_params["attributes"]
    result = {"changed": False}

    singleton_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        module_name,
        obj_name,
        attributes,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
