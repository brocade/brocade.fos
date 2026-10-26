# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


"""
Brocade json parsing lib
"""

import json


def bsn_json_loads(result, data):
    """
    converts a FOS REST API JSON response body into a dict

    :param result: dict to keep track of execution msgs
    :type result: dict
    :param data: json data in bytes or str
    :type data: bytes or str
    :return: code to indicate failure or success
    :rtype: int
    :return: dict of data content
    :rtype: dict
    """
    try:
        ret_dict = json.loads(data)
    except json.JSONDecodeError:
        return -1, data

    return 0, ret_dict


def bsn_json_dumps(result, data):
    """
    serializes a python object into a FOS REST API JSON request body

    :param result: dict to keep track of execution msgs
    :type result: dict
    :param data: python object to serialize
    :type data: dict or list
    :return: code to indicate failure or success
    :rtype: int
    :return: json string, or None on failure
    :rtype: str
    """
    try:
        return 0, json.dumps(data)
    except (TypeError, ValueError):
        result["failed"] = True
        result["msg"] = "failed to serialize request body to json"
        return -1, None
