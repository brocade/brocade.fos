# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

from ansible_collections.brocade.fos.plugins.module_utils.brocade_url import (
    full_url_get,
    url_get_to_dict,
    url_patch_single_object,
)

__metaclass__ = type


"""
Brocade chassis utils
"""


REST_CHASSIS = "/rest/running/brocade-chassis/chassis"


def chassis_get(fos_ip_addr, is_https, auth, vfid, result, timeout):
    """
    retrieve existing switch configurations

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type auth: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :return: code to indicate failure or success
    :rtype: int
    :return: dict of chassis configurations
    :rtype: dict
    """
    full_chassis_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_CHASSIS)

    rtype, rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, full_chassis_url, timeout)
    if rtype != 0:
        result["failed"] = True
        result["msg"] = "API failed to return data"
        return -1, None

    return 0, rdict


def chassis_patch(fos_ip_addr, is_https, auth, vfid, result, diff_attributes, timeout):
    """
    update existing switch configurations

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type auth: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :param diff_attributes: list of attributes for update
    :type ports: dict
    :return: code to indicate failure or success
    :rtype: int
    :return: list of dict of chassis configurations
    :rtype: list
    """
    l_diffs = diff_attributes.copy()

    if len(l_diffs) == 0:
        return 0

    full_chassis_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_CHASSIS)

    return url_patch_single_object(
        fos_ip_addr, is_https, auth, vfid, result, full_chassis_url, "chassis", l_diffs, timeout
    )
