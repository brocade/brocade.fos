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
from ansible_collections.brocade.fos.plugins.module_utils.brocade_yang import human_to_yang, yang_to_human

__metaclass__ = type


"""
Brocade Fibre Channel switch utils
"""


REST_SWITCH_URI = "/rest/running/brocade-fibrechannel-switch/fibrechannel-switch"


def to_human_switch(switch_config):
    # convert all boolean strings to boolean
    # first. Then convert integer booleans
    # to boolean
    yang_to_human(switch_config)

    for k, v in switch_config.items():
        if v == "true":
            switch_config[k] = True
        elif v == "false":
            switch_config[k] = False

    if "enabled_state" in switch_config:
        if str(switch_config["enabled_state"]) == "3":
            switch_config["enabled_state"] = False
        else:
            switch_config["enabled_state"] = True


def to_fos_switch(switch_config, result):
    human_to_yang(switch_config)

    if "enabled-state" in switch_config:
        if isinstance(switch_config["enabled-state"], bool):
            if switch_config["enabled-state"] is False:
                switch_config["enabled-state"] = 3
            else:
                switch_config["enabled-state"] = 2
        else:
            result["failed"] = True
            result["msg"] = "enabled-state converted to unknown"
            return -1

    # convert the boolean to integers first
    # then convert the rest of the booleans to bool string
    for k, v in switch_config.items():
        if k == "is-enabled-state":
            continue
        if isinstance(v, bool):
            if v is True:
                switch_config[k] = "true"
            else:
                switch_config[k] = "false"

    return 0


def fc_switch_get(fos_ip_addr, is_https, auth, vfid, result, timeout):
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
    :return: dict of switch configurations
    :rtype: dict
    """
    full_fc_switch_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_SWITCH_URI)

    rtype, rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, full_fc_switch_url, timeout)

    if rtype != 0:
        result["failed"] = True
        result["msg"] = "API failed to return data"
        return -1, None

    return 0, rdict


def fc_switch_patch(fos_ip_addr, is_https, auth, vfid, result, diff_attributes, timeout):
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
    :return: dict of switch configurations
    :rtype: dict
    """
    l_diffs = diff_attributes.copy()

    # should be only key for the switch if nothing else
    if len(l_diffs) <= 1:
        return 0

    full_fc_switch_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_SWITCH_URI)

    return url_patch_single_object(
        fos_ip_addr, is_https, auth, vfid, result, full_fc_switch_url, "fibrechannel-switch", l_diffs, timeout
    )
