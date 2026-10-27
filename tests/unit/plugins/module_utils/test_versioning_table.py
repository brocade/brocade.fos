# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from pathlib import Path

from ansible_collections.brocade.fos.plugins.module_utils.brocade_objects import _read_file

VERSIONING_FILE = Path(__file__).resolve().parents[4] / "versioning.md"


def test_release_history_is_parsed_newest_first():
    releases = _read_file(VERSIONING_FILE, {}, None)

    newest = next(iter(releases))
    assert newest == "v3.0.0"
    assert [fos["version"] for fos in releases[newest]["fos_versions"]] == ["v10.0.1", "v9.2.2d"]
    assert releases[newest]["ga_date"] == "November 18, 2026"
    assert "ansible-core: v2.19.8" in releases[newest]["fos_versions"][0]["tested_with"]
    assert "python: v3.12.3" in releases[newest]["fos_versions"][0]["tested_with"]


def test_multiple_fos_versions_per_release():
    releases = _read_file(VERSIONING_FILE, {}, None)

    assert [fos["version"] for fos in releases["v1.3.3"]["fos_versions"]] == ["v8.2.3d", "v9.0.1e", "v9.1.1b"]


def test_header_and_separator_rows_are_skipped():
    releases = _read_file(VERSIONING_FILE, {}, None)

    assert "brocade.fos" not in releases
    assert not any(set(key) <= set("-: ") for key in releases)
