#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """

module: brocade_security_sec_crypto_template_action
short_description: Brocade Fibre Channel security crypto template file actions
version_added: '2.7'
author: Broadcom BSN Ansible Team <Automation.BSN@broadcom.com>
description:
- Use to perform actions on the crypto template files. The module
  performs the action each time and is not idempotent.

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
    action_inputs:
        description:
        - Action attributes
        required: true
        type: dict
        suboptions:
            action:
                description:
                - Operation to perform on the crypto config template
                choices:
                    - import
                    - export
                    - apply
                required: true
                type: str
            template_name:
                description:
                - Name of the crypto config template
                required: true
                type: str
            remote_host_ip:
                description:
                - IP address of the remote host for import or export
                required: false
                type: str
            remote_user_name:
                description:
                - User name on the remote host for import or export
                required: false
                type: str
            remote_user_password:
                description:
                - Password for the remote host user. Not logged.
                required: false
                type: str
            remote_directory:
                description:
                - Directory path on the remote host containing or receiving
                  the template file
                required: false
                type: str
            file_transfer_protocol_type:
                description:
                - File transfer protocol to use for import or export
                choices:
                    - scp
                    - ftp
                    - sftp
                required: false
                type: str
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

  - name: import/export/apply cfg template
    brocade_security_sec_crypto_cfg_template_action
      credential: "{{credential}}"
      vfid: -1
      action_inputs:

"""


RETURN = """

msg:
    description: Success message
    returned: success
    type: str

"""


"""
Brocade Fibre Channel crypto template file actions
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import singleton_helper


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
        action_inputs=dict(
            required=True,
            type="dict",
            options=dict(
                action=dict(type="str"),
                template_name=dict(type="str"),
                remote_host_ip=dict(type="str"),
                remote_user_name=dict(type="str"),
                remote_user_password=dict(type="str", no_log=True),
                remote_directory=dict(type="str"),
                file_transfer_protocol_type=dict(type="str"),
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
    action_inputs = input_params["action_inputs"]
    result = {"changed": False}

    singleton_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        ssh_hostkeymust,
        throttle,
        vfid,
        "brocade_security",
        "sec_crypto_cfg_template_action",
        action_inputs,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
