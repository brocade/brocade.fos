#!/usr/bin/python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""

module: brocade_fibrechannel_configuration_fabric
short_description: Brocade Fibre Channel fabric configuration
version_added: "1.3.0"
author: Broadcom BSN Ansible Team (@brocade) <Automation.BSN@broadcom.com>
description:
-   Update Fibre Channel fabric configuration.

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
    fabric:
        description:
        -   Fabric configuration attributes to set. Supports the writable attributes of the
            C(brocade-fibrechannel-configuration/fabric) REST container, with hyphens replaced by
            underscores, for example C(insistent_domain_id_enabled), C(preserved_domain_id_mode_enabled),
            C(principal_selection_enabled), and C(principal_priority).
        -   Only the specified attributes are compared with the switch and updated.
        required: true
        type: dict
notes:
-   FOS accepts C(principal_priority) only while C(principal_selection_enabled) is true. When
    C(principal_priority) is set without C(principal_selection_enabled), the module also sets
    C(principal_selection_enabled) to true in the same request. Check mode does not show this change.
-   When C(principal_selection_enabled) is set to false, C(principal_priority) is not sent, because FOS
    rejects a priority change while disabling principal selection.
-   The switch does not report C(principal_priority) while principal selection is disabled.
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
    - name: Initial fabric configuration
      register: result
      brocade.fos.brocade_fibrechannel_configuration_fabric:
        credential: '{{ credential }}'
        vfid: -1
        fabric:
          insistent_domain_id_enabled: true
          preserved_domain_id_mode_enabled: true
          principal_selection_enabled: true
          principal_priority: '0x6'
    - name: Show fabric result
      ansible.builtin.debug:
        var: result
"""


RETURN = r"""

current_attributes:
    description: Fabric attributes read from the switch before any change.
    returned: when the switch login succeeds
    type: dict
new_attributes:
    description: Fabric attributes requested by the task.
    returned: when the switch login succeeds
    type: dict
diff_attributes:
    description: Requested attributes that differ from the switch. See the notes for attributes that are not sent.
    returned: when the switch login succeeds
    type: dict
messages:
    description: Status message for the fabric update.
    returned: when fabric attributes are updated
    type: str
msg:
    description: Error message.
    returned: failure
    type: str

"""


"""
Brocade Fibre Channel fabric Configuration
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
            ),
        ),
        vfid=dict(required=False, type="int"),
        throttle=dict(required=False, type="int"),
        timeout=dict(required=False, type="int"),
        fabric=dict(required=True, type="dict"),
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
    fabric = input_params["fabric"]
    result = {"changed": False}

    singleton_helper(
        module,
        fos_ip_addr,
        fos_user_name,
        fos_password,
        https,
        throttle,
        vfid,
        "brocade_fibrechannel_configuration",
        "fabric",
        fabric,
        result,
        timeout,
    )


if __name__ == "__main__":
    main()
