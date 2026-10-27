# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import copy
import importlib
from unittest.mock import Mock

import pytest
from ansible.module_utils import basic
from ansible_collections.brocade.fos.plugins.modules import brocade_facts, brocade_zoning_alias


class ModuleResultError(Exception):
    def __init__(self, *, result):
        super().__init__(result)
        self.result = result


@pytest.fixture
def module_args(*, monkeypatch):
    def exit_json(self, **result):
        raise ModuleResultError(result=result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", exit_json)

    def configure(**params):
        params["credential"] = {
            "fos_ip_addr": "192.0.2.1",
            "fos_user_name": "lab_user",
            "fos_password": "lab_secret",
            "https": "true",
        }
        monkeypatch.setattr(basic, "_load_params", lambda: copy.deepcopy(params))

    return configure


@pytest.mark.parametrize(
    "module_name, option, inputs, extra",
    [
        (
            "brocade_operation_firmwaredownload",
            "firmwaredownload",
            {"host": "192.0.2.2", "user_name": "transfer", "remote_directory": "/firmware"},
            {},
        ),
        (
            "brocade_operation_supportsave",
            "supportsave",
            {"host": "192.0.2.2", "user_name": "transfer", "remote_directory": "/support"},
            {},
        ),
        (
            "brocade_scalar_operation",
            "entries",
            {"user_name": "transfer", "remote_directory": "/config", "vf_id": 128},
            {"module_name": "configupload"},
        ),
    ],
)
def test_underscore_operation_parameters_reach_rest_helper(
    *, monkeypatch, module_args, module_name, option, inputs, extra
):
    module = importlib.import_module("ansible_collections.brocade.fos.plugins.modules." + module_name)
    module_args(**{option: inputs, **extra})
    received = {}

    def operation_helper(ansible_module, *args):
        received.update(ansible_module.params[option])
        ansible_module.exit_json(changed=False)

    monkeypatch.setattr(module, "operation_helper", operation_helper)
    with pytest.raises(ModuleResultError) as result:
        module.main()
    assert not result.value.result.get("failed", False)
    for key, value in inputs.items():
        assert received[key] == value


def test_facts_read_switch_in_check_mode(*, monkeypatch, module_args):
    module_args(gather_subset=["brocade_chassis_chassis"], _ansible_check_mode=True)
    monkeypatch.setattr(brocade_facts, "login", Mock(return_value=(0, "session", "v10.0.1")))
    getter = Mock(return_value=(0, {"Response": {"chassis": {"chassis_user_friendly_name": "lab"}}}))
    monkeypatch.setattr(brocade_facts, "singleton_get", getter)
    monkeypatch.setattr(brocade_facts, "to_human_singleton", Mock())
    logout = Mock(return_value=0)
    monkeypatch.setattr(brocade_facts, "logout", logout)

    with pytest.raises(ModuleResultError) as result:
        brocade_facts.main()

    assert result.value.result["ansible_facts"]["brocade_chassis_chassis"] == {"chassis_user_friendly_name": "lab"}
    assert not result.value.result["changed"]
    getter.assert_called_once()
    assert getter.call_args.args[3:5] == ("brocade_chassis", "chassis")
    logout.assert_called_once()


def test_zoning_lists_preserve_nested_values(*, monkeypatch, module_args):
    aliases = [{"name": "lab_alias", "members": ["10:00:00:00:00:00:00:01"]}]
    module_args(aliases=aliases)
    monkeypatch.setattr(brocade_zoning_alias, "login", Mock(return_value=(0, "session", "v10.0.1")))
    monkeypatch.setattr(brocade_zoning_alias, "logout", Mock(return_value=0))
    zoning = Mock()
    monkeypatch.setattr(brocade_zoning_alias, "zoning_common", zoning)

    with pytest.raises(ModuleResultError):
        brocade_zoning_alias.main()

    zoning.assert_called_once()
    assert zoning.call_args.args[7] == aliases
