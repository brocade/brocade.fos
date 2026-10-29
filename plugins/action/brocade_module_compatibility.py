# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

"""
Supply the FOS versions tested with this collection to brocade_module_compatibility

The module runs as an AnsiballZ payload, which cannot include versioning.md, so
the release history is read here on the controller and passed as an argument.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from pathlib import Path

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase
from ansible_collections.brocade.fos.plugins.module_utils.brocade_versioning import (
    newest_fos_versions,
    parse_release_history,
)

VERSIONING_FILE = Path(__file__).resolve().parents[2] / "versioning.md"


def load_supported_fos_versions(path=VERSIONING_FILE):
    """
    Return the FOS versions tested with the newest release in versioning.md.
    """
    if not path.is_file():
        raise AnsibleActionFail(f"{path} does not exist")

    versions = newest_fos_versions(parse_release_history(path.read_text(encoding="utf-8")))
    if not versions:
        raise AnsibleActionFail(f"{path} has no release history table")
    return versions


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super().run(tmp, task_vars)

        module_args = self._task.args.copy()
        module_args["supported_fos_versions"] = load_supported_fos_versions()

        result.update(
            self._execute_module(
                module_name="brocade.fos.brocade_module_compatibility",
                module_args=module_args,
                task_vars=task_vars,
            )
        )
        return result
