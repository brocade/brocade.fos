#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_scalar_operation
short_description: Brocade Fibre Channel operation with the container input
version_added: "2.0.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Perform specified operation.

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
    entries:
        description:
        -   Operation parameters. The required sub-keys depend on the value of module_name. Hyphens and
            underscores in key names are interchangeable.
        type: dict
        required: true
        suboptions:
            host:
                description:
                -   IP address or hostname of the remote server. Used for configupload, configdownload,
                    supportsave, firmwaredownload, and license (install/export) operations.
                type: str
            user_name:
                description:
                -   User name for the remote server.
                type: str
            password:
                description:
                -   Password for the remote server. The module encodes this value automatically before sending
                    to FOS. Not logged.
                type: str
            remote_directory:
                description:
                -   Directory path on the remote server.
                type: str
            protocol:
                description:
                -   Transfer protocol for the remote server (e.g. scp, sftp, ftp).
                type: str
            port:
                description:
                -   Port number for the remote server connection (1..65535).
                type: int
            config_upload_download_option:
                description:
                -   Upload or download option for configupload and configdownload operations (e.g.
                    virtual-fabric).
                type: str
            vf_id:
                description:
                -   Target VF ID for the config_upload_download_option value fabric-id, identifying which
                    logical switch's configuration to upload or download. Distinct from the top-level vfid,
                    which selects the logical switch context to log into.
                type: int
            config_input_buffer:
                description:
                -   Configuration data buffer used as input for configdownload. Copy the config_output_buffer
                    value returned by a prior configupload operation here.
                type: str
            protocol_v2:
                description:
                -   Secondary transfer protocol. Used by supportsave when a fallback protocol is needed.
                type: str
            stage:
                description:
                -   Stage the firmware without activating it. Used for firmwaredownload.
                type: bool
            activate:
                description:
                -   Activate the firmware after staging. Used for firmwaredownload.
                type: bool
            eula_action:
                description:
                -   End-user license agreement action for firmwaredownload (e.g. accept, decline).
                type: str
            action:
                description:
                -   Action to perform for license operations. One of install, remove, or export.
                type: str
            name:
                description:
                -   License key or serial number (e.g. FOS-00-0-02-11201234). Used for license install by key,
                    remove, and targeted export operations.
                type: str
            license_payload:
                description:
                -   Base64-encoded license certificate content (RFC 3414). Use only when action is install and
                    name and host are not specified.
                type: str
            usb_file_path:
                description:
                -   Relative path of the license certificate on a USB device. Used for license install from
                    USB or license export to USB file.
                type: str
            usb_directory_path:
                description:
                -   USB directory path for exporting license certificates. Used only when action is export and
                    host and license_payload are not specified.
                type: str
            remote_file:
                description:
                -   Remote file name for exporting a license certificate to a specific file on the remote
                    server.
                type: str
            message_id:
                description:
                -   Operation message ID returned by a prior async operation. Used with module_name
                    show_status to poll operation completion.
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
    - name: Perform operation
      brocade.fos.brocade_scalar_operation:
        credential: '{{ credential }}'
        module_name: configupload
        vfid: -1
        entries:
          config_upload_download_option: virtual-fabric
"""


RETURN = r"""

msg:
    description: Success message.
    returned: success
    type: str

"""


"""
Brocade Fibre Channel operation
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import operation_helper


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
        entries=dict(
            required=True,
            type="dict",
            options=dict(
                host=dict(required=False, type="str"),
                user_name=dict(required=False, type="str"),
                password=dict(required=False, type="str", no_log=True),
                remote_directory=dict(required=False, type="str"),
                protocol=dict(required=False, type="str"),
                port=dict(required=False, type="int"),
                config_upload_download_option=dict(required=False, type="str"),
                vf_id=dict(required=False, type="int"),
                config_input_buffer=dict(required=False, type="str"),
                protocol_v2=dict(required=False, type="str"),
                stage=dict(required=False, type="bool"),
                activate=dict(required=False, type="bool"),
                eula_action=dict(required=False, type="str"),
                action=dict(required=False, type="str"),
                name=dict(required=False, type="str"),
                license_payload=dict(required=False, type="str"),
                usb_file_path=dict(required=False, type="str"),
                usb_directory_path=dict(required=False, type="str"),
                remote_file=dict(required=False, type="str"),
                message_id=dict(required=False, type="str"),
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
    entries = input_params["entries"]
    result = {"changed": False}
    module_name = input_params["module_name"]

    class_name = ""
    if module_name == "configupload" or module_name == "configdownload":
        class_name = module_name + "_parameters"

    operation_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        module_name,
        class_name,
        entries,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
