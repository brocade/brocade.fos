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
Brocade configuration utils
"""


REST_FABRIC = "/rest/running/brocade-fibrechannel-configuration/fabric"
REST_PORT_CONFIGURATION = "/rest/running/brocade-fibrechannel-configuration/port-configuration"


def fabric_get(fos_ip_addr, is_https, auth, vfid, result, timeout):
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
    :return: dict of fabric configurations
    :rtype: dict
    """
    full_fabric_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_FABRIC)

    rtype, rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, full_fabric_url, timeout)
    if rtype != 0:
        # If /fabric container is not found, initialize rdict to empty Response
        if rtype == -2 or rtype == -1:  # ERROR_LIST_EMPTY or ERROR_GENERIC
            rdict = {"Response": {"fabric": {}}}
        else:
            result["failed"] = True
            result["msg"] = "API failed to return data"
            return -1, None

    if not isinstance(rdict, dict) or "Response" not in rdict:
        rdict = {"Response": {"fabric": {}}}
    if "fabric" not in rdict["Response"]:
        rdict["Response"]["fabric"] = {}

    # If fabric is a list (e.g. from 404 empty list response), convert to dict
    if isinstance(rdict["Response"]["fabric"], list):
        if len(rdict["Response"]["fabric"]) > 0:
            rdict["Response"]["fabric"] = rdict["Response"]["fabric"][0]
        else:
            rdict["Response"]["fabric"] = {}

    fabric_data = rdict["Response"]["fabric"]

    # List of attributes we want to retrieve from /fabric
    fabric_attrs = [
        "principal-selection-enabled",
        "principal-priority",
        "insistent-domain-id-enabled",
        "preserved-domain-id-mode-enabled",
    ]

    for attr in fabric_attrs:
        val = fabric_data.get(attr)
        if val is None:
            # Try individual leaf URI if missing from container
            leaf_url = full_fabric_url + "/" + attr
            l_rtype, l_rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, leaf_url, timeout)
            if l_rtype == 0:
                val = l_rdict.get("Response", {}).get(attr)

        if val is not None:
            if attr in [
                "principal-selection-enabled",
                "insistent-domain-id-enabled",
                "preserved-domain-id-mode-enabled",
            ]:
                fabric_data[attr] = str(val).lower()
            elif attr == "principal-priority":
                try:
                    p_val = int(str(val), 0)
                    if p_val == 0:
                        fabric_data[attr] = "0"
                    else:
                        fabric_data[attr] = "0x{:02x}".format(p_val)
                except ValueError:
                    fabric_data[attr] = str(val)

    return 0, rdict


def fabric_patch(fos_ip_addr, is_https, auth, vfid, result, diff_attributes, timeout):
    """
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
    :return: dict of fabric configurations
    :rtype: dict
    """
    l_diffs = diff_attributes.copy()

    # Ensure fabric boolean attributes stay native JSON booleans. FOS rejects a
    # quoted "true"/"false" string for these leaves ("Invalid input data for
    # <attr>") and wants a real boolean instead - confirmed for
    # insistent-domain-id-enabled, preserved-domain-id-mode-enabled, and
    # principal-selection-enabled.
    bool_attrs = ["preserved-domain-id-mode-enabled", "insistent-domain-id-enabled", "principal-selection-enabled"]
    for attr in bool_attrs:
        if attr in l_diffs and isinstance(l_diffs[attr], str):
            l_diffs[attr] = l_diffs[attr].lower() == "true"

    # Attributes that belong to the /fabric container
    fabric_container_attrs = [
        "principal-selection-enabled",
        "principal-priority",
        "insistent-domain-id-enabled",
        "preserved-domain-id-mode-enabled",
    ]

    patch_data = {}
    for attr in fabric_container_attrs:
        if attr in l_diffs:
            patch_data[attr] = l_diffs.pop(attr)

    # FOS rejects a principal-priority change unless principal-selection-enabled
    # is enabled; bundle it into the same PATCH so priority-only requests don't
    # depend on whatever the last-read (possibly stale) selection state was.
    if "principal-priority" in patch_data and "principal-selection-enabled" not in patch_data:
        patch_data["principal-selection-enabled"] = True

    # Conversely, FOS rejects principal-priority appearing in the same PATCH as
    # disabling principal-selection-enabled ("Principal priority cannot be set
    # while disabling principal-selection-enabled"), even when priority is 0 -
    # so drop it from this request; disabling on its own is a valid, separate change.
    if patch_data.get("principal-selection-enabled") is False and "principal-priority" in patch_data:
        patch_data.pop("principal-priority")

    if patch_data:
        full_fabric_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_FABRIC)
        rtype_patch = url_patch_single_object(
            fos_ip_addr, is_https, auth, vfid, result, full_fabric_url, "fabric", patch_data, timeout
        )
        if rtype_patch != 0:
            result["failed"] = True
            result["msg"] = "Failed to update fabric attributes via REST"
            return -1
        else:
            result["changed"] = True
            if "messages" not in result:
                result["messages"] = ""
            result["messages"] += "Fabric attributes updated via REST. "

    if len(l_diffs) > 0:
        # Handle any remaining attributes
        full_fabric_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_FABRIC)
        rtype_patch = url_patch_single_object(
            fos_ip_addr, is_https, auth, vfid, result, full_fabric_url, "fabric", l_diffs, timeout
        )
        if rtype_patch != 0:
            result["failed"] = True
            result["msg"] = "Failed to update remaining fabric attributes via REST"
            return -1
        else:
            result["changed"] = True

    return 0


def to_human_port_configuration(attributes):
    for k, v in attributes.items():
        if v == "true":
            attributes[k] = True
        elif v == "false":
            attributes[k] = False

    yang_to_human(attributes)


def to_fos_port_configuration(attributes, result):
    human_to_yang(attributes)

    for k, v in attributes.items():
        if isinstance(v, bool):
            if v is True:
                attributes[k] = "true"
            else:
                attributes[k] = "false"

    return 0


def port_configuration_get(fos_ip_addr, is_https, auth, vfid, result, timeout):
    """
    retrieve existing port configurations

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
    :return: dict of fabric configurations
    :rtype: dict
    """
    full_port_config_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_PORT_CONFIGURATION)

    rtype, rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, full_port_config_url, timeout)
    if rtype != 0:
        result["failed"] = True
        result["msg"] = "API failed to return data"
        return -1, None

    return 0, rdict


def port_configuration_patch(fos_ip_addr, is_https, auth, vfid, result, diff_attributes, timeout):
    """
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
    :return: dict of port-configuration configurations
    :rtype: dict
    """
    l_diffs = diff_attributes.copy()

    if len(l_diffs) == 0:
        return 0

    full_port_config_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_PORT_CONFIGURATION)

    return url_patch_single_object(
        fos_ip_addr, is_https, auth, vfid, result, full_port_config_url, "port-configuration", l_diffs, timeout
    )
