#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_module_compatibility
short_description: Check brocade.fos compatibility with a FOS switch
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Check whether the FOS version running on the switch is one of the FOS versions tested with the
    installed brocade.fos release, as listed in the release history in C(versioning.md).
-   The task fails when the switch FOS version is not listed. Any suffix after an underscore in the
    switch FOS version is ignored.
-   The module's action plugin reads C(versioning.md) from the installed collection on the controller,
    so no configuration is needed.

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
        -   Virtual fabric ID. Use -1 when virtual fabrics are not enabled.
        type: int
    throttle:
        description:
        -   Delay in seconds before retrying once when the switch is busy.
        type: int
    timeout:
        description:
        -   REST timeout in seconds for operations that take longer than the FOS default timeout.
        type: int
    supported_fos_versions:
        description:
        -   FOS versions to accept.
        -   Set automatically by the action plugin from C(versioning.md); any value in the task is replaced.
        type: list
        elements: str
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
    - name: Module compatibility check
      brocade.fos.brocade_module_compatibility:
        credential: '{{ credential }}'
"""


RETURN = r"""

response:
    description: Result of the compatibility check.
    returned: when the switch login succeeds
    type: str
    sample: Module(s) are compatible with the given switch
switchversion:
    description: FOS version reported by the switch.
    returned: when the switch login succeeds
    type: str
    sample: v9.2.2d
switchversionansible:
    description: FOS versions tested with the installed brocade.fos release.
    returned: when the switch login succeeds
    type: list
    elements: str
    sample: ["v10.0.1", "v9.2.2d"]
msg:
    description: Error message when the switch login or version query fails.
    returned: failure
    type: str

"""


"""
Brocade Module compatibility check
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import module_compatibility_helper


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
        supported_fos_versions=dict(required=False, type="list", elements="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    input_params = module.params
    supported_fos_versions = input_params["supported_fos_versions"]
    if supported_fos_versions is None:
        module.fail_json(msg="supported_fos_versions is not set; run this module through its action plugin")

    # Set up state variables
    fos_ip_addr = input_params["credential"]["fos_ip_addr"]
    fos_user_name = input_params["credential"]["fos_user_name"]
    fos_password = input_params["credential"]["fos_password"]
    https = input_params["credential"]["https"]
    throttle = input_params["throttle"]
    timeout = input_params["timeout"]
    result = {"changed": False}

    module_compatibility_helper(
        module, fos_ip_addr, fos_user_name, fos_password, https, throttle, supported_fos_versions, result, timeout
    )


if __name__ == "__main__":
    main()
