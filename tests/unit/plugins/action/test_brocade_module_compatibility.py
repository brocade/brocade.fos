# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

"""Compatibility action plugin: FOS versions read from the collection's versioning.md."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from pathlib import Path

import pytest
from ansible.errors import AnsibleActionFail
from ansible_collections.brocade.fos.plugins.action.brocade_module_compatibility import (
    VERSIONING_FILE,
    load_supported_fos_versions,
)


def test_reads_versioning_file_shipped_with_collection():
    assert Path(__file__).resolve().parents[4] / "versioning.md" == VERSIONING_FILE
    assert load_supported_fos_versions() == ["v10.0.1", "v9.2.2d"]


def test_missing_versioning_file_fails(*, tmp_path):
    with pytest.raises(AnsibleActionFail, match="does not exist"):
        load_supported_fos_versions(tmp_path / "versioning.md")


def test_versioning_file_without_table_fails(*, tmp_path):
    (tmp_path / "versioning.md").write_text("# Versioning\n")

    with pytest.raises(AnsibleActionFail, match="no release history table"):
        load_supported_fos_versions(tmp_path / "versioning.md")
