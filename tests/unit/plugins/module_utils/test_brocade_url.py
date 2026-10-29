# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

"""Connection URL and certificate validation for each credential.https value."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.brocade.fos.plugins.module_utils import brocade_url


@pytest.fixture
def warnings(*, monkeypatch):
    messages = []
    monkeypatch.setattr(brocade_url, "warn", messages.append)
    return messages


@pytest.mark.parametrize(
    ("https", "url", "validate_certs"),
    [
        ("true", "https://198.51.100.1/rest/login", True),
        ("TRUE", "https://198.51.100.1/rest/login", True),
        ("self", "https://198.51.100.1/rest/login", False),
        ("false", "http://198.51.100.1/rest/login", False),
        ("False", "http://198.51.100.1/rest/login", False),
        (True, "https://198.51.100.1/rest/login", True),
        (False, "http://198.51.100.1/rest/login", False),
    ],
)
def test_documented_https_values_do_not_warn(*, warnings, https, url, validate_certs):
    assert brocade_url.full_url_get(https, "198.51.100.1", "/rest/login") == (url, validate_certs)
    assert warnings == []


def test_unrecognized_https_value_warns_and_uses_http(*, warnings):
    assert brocade_url.full_url_get("flase", "198.51.100.1", "/rest/login") == ("http://198.51.100.1/rest/login", False)
    assert len(warnings) == 1
    assert "'flase' is not recognized" in warnings[0]
