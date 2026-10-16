#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """

module: brocade_scalar_operation
short_description: Brocade Fibre Channel operation with the container input
version_added: '2.7'
author: Broadcom BSN Ansible Team <Automation.BSN@broadcom.com>
description:
- Perform specified operation

options:
    credential:
        description:
        - Login information
        suboptions:
            fos_ip_addr:
                description:
                - IP address of the FOS switch
                required: true
                type: str
            fos_user_name:
                description:
                - Login name of FOS switch
                required: true
                type: str
            fos_password:
                description:
                - Password of FOS switch
                required: true
                type: str
            https:
                description:
                - Encryption to use. True for HTTPS, self for self-signed HTTPS,
                  or False for HTTP
                choices:
                    - True
                    - False
                    - self
                required: true
                type: str

        type: dict
        required: true
    vfid:
        description:
        - VFID of the switch. Use -1 for FOS without VF enabled or AG.
        type: int
        required: false
    throttle:
        description:
        - Throttling delay in seconds. Enables second retry on first
          failure.
        type: int
    timeout:
        description:
        - REST timeout in seconds for operations that take longer than FOS
          default value.
        type: int
    module_name:
        description:
        - Yang module name. Hyphen or underscore are used interchangebly.
          If the Yang module name is xy-z, either xy-z or xy_z are acceptable.
        required: true
        type: str
    entries:
        description:
        - Operation parameters. The required sub-keys depend on the value of
          module_name. Hyphens and underscores in key names are interchangeable.
        type: dict
        required: true
        suboptions:
            host:
                description:
                - IP address or hostname of the remote server. Used for
                  configupload, configdownload, supportsave, firmwaredownload,
                  and license (install/export) operations.
                required: false
                type: str
            user_name:
                description:
                - User name for the remote server.
                required: false
                type: str
            password:
                description:
                - Password for the remote server. The module encodes this
                  value automatically before sending to FOS. Not logged.
                required: false
                type: str
            remote_directory:
                description:
                - Directory path on the remote server.
                required: false
                type: str
            protocol:
                description:
                - Transfer protocol for the remote server (e.g. scp, sftp,
                  ftp).
                required: false
                type: str
            port:
                description:
                - Port number for the remote server connection (1..65535).
                required: false
                type: int
            config_upload_download_option:
                description:
                - Upload or download option for configupload and
                  configdownload operations (e.g. virtual-fabric).
                required: false
                type: str
            config_input_buffer:
                description:
                - Configuration data buffer used as input for configdownload.
                  Copy the config_output_buffer value returned by a prior
                  configupload operation here.
                required: false
                type: str
            protocol_v2:
                description:
                - Secondary transfer protocol. Used by supportsave when a
                  fallback protocol is needed.
                required: false
                type: str
            stage:
                description:
                - Stage the firmware without activating it. Used for
                  firmwaredownload.
                required: false
                type: bool
            activate:
                description:
                - Activate the firmware after staging. Used for
                  firmwaredownload.
                required: false
                type: bool
            eula_action:
                description:
                - End-user license agreement action for firmwaredownload
                  (e.g. accept, decline).
                required: false
                type: str
            action:
                description:
                - Action to perform for license operations. One of install,
                  remove, or export.
                choices: [install, remove, export]
                required: false
                type: str
            name:
                description:
                - License key or serial number (e.g. FOS-00-0-02-11201234).
                  Used for license install by key, remove, and targeted
                  export operations.
                required: false
                type: str
            license_payload:
                description:
                - Base64-encoded license certificate content (RFC 3414). Use
                  only when action is install and name and host are not
                  specified.
                required: false
                type: str
            usb_file_path:
                description:
                - Relative path of the license certificate on a USB device.
                  Used for license install from USB or license export to USB
                  file.
                required: false
                type: str
            usb_directory_path:
                description:
                - USB directory path for exporting license certificates. Used
                  only when action is export and host and license_payload are
                  not specified.
                required: false
                type: str
            remote_file:
                description:
                - Remote file name for exporting a license certificate to a
                  specific file on the remote server.
                required: false
                type: str
            message_id:
                description:
                - Operation message ID returned by a prior async operation.
                  Used with module_name show_status to poll operation
                  completion.
                required: false
                type: str
            vf_id:
                description:
                - Target VF ID for the config_upload_download_option value
                  fabric-id, identifying which logical switch's configuration
                  to upload or download. Distinct from the top-level vfid,
                  which selects the logical switch context to log into.
                required: false
                type: int

"""


EXAMPLES = """

  gather_facts: False

  vars:
    credential:
      fos_ip_addr: "{{fos_ip_addr}}"
      fos_user_name: user_name
      fos_password: user_password
      https: False

  tasks:

  - name: perform operation
    brocade_scalar_operation:
      credential: "{{credential}}"
      module_name: "configupload"
      vfid: -1
      entries:
        config_upload_download_option: "virtual-fabric"

"""


RETURN = """

msg:
    description: Success message
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
                ssh_hostkeymust=dict(required=False, type="bool"),
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
                user_name=dict(required=False, type="str", aliases=["user-name"]),
                password=dict(required=False, type="str", no_log=True),
                remote_directory=dict(required=False, type="str", aliases=["remote-directory"]),
                protocol=dict(required=False, type="str"),
                port=dict(required=False, type="int"),
                config_upload_download_option=dict(
                    required=False, type="str", aliases=["config-upload-download-option"]
                ),
                vf_id=dict(required=False, type="int", aliases=["vf-id"]),
                config_input_buffer=dict(required=False, type="str", aliases=["config-input-buffer"]),
                protocol_v2=dict(required=False, type="str", aliases=["protocol-v2"]),
                stage=dict(required=False, type="bool"),
                activate=dict(required=False, type="bool"),
                eula_action=dict(required=False, type="str", aliases=["eula-action"]),
                action=dict(required=False, type="str"),
                name=dict(required=False, type="str"),
                license_payload=dict(required=False, type="str", aliases=["license-payload"]),
                usb_file_path=dict(required=False, type="str", aliases=["usb-file-path"]),
                usb_directory_path=dict(required=False, type="str", aliases=["usb-directory-path"]),
                remote_file=dict(required=False, type="str", aliases=["remote-file"]),
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
    ssh_hostkeymust = True
    if "ssh_hostkeymust" in input_params["credential"]:
        ssh_hostkeymust = input_params["credential"]["ssh_hostkeymust"]
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
        ssh_hostkeymust,
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
