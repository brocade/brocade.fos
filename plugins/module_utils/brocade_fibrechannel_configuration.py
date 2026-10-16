# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries


from __future__ import absolute_import, division, print_function

from ansible_collections.brocade.fos.plugins.module_utils.brocade_json import bsn_json_dumps
from ansible_collections.brocade.fos.plugins.module_utils.brocade_ssh import ssh_and_configure
from ansible_collections.brocade.fos.plugins.module_utils.brocade_url import (
    full_url_get,
    url_get_to_dict,
    url_patch,
    url_patch_single_object,
)
from ansible_collections.brocade.fos.plugins.module_utils.brocade_yang import human_to_yang, yang_to_human

__metaclass__ = type


"""
Brocade configuration utils
"""


REST_FABRIC = "/rest/running/brocade-fibrechannel-configuration/fabric"
REST_PORT_CONFIGURATION = "/rest/running/brocade-fibrechannel-configuration/port-configuration"
REST_SWITCH_NEW_URI = "/rest/running/brocade-fibrechannel-switch/fibrechannel-switch"


def fabric_get(login, password, fos_ip_addr, fos_version, is_https, auth, vfid, result, ssh_hostkeymust, timeout):
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

    # Fallback for preserved-domain-id-mode-enabled if still missing
    if fabric_data.get("preserved-domain-id-mode-enabled") is None:
        full_fc_switch_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_SWITCH_NEW_URI)
        rtype_switch, rdict_switch = url_get_to_dict(
            fos_ip_addr, is_https, auth, vfid, result, full_fc_switch_url, timeout
        )
        if rtype_switch == 0:
            switches = rdict_switch.get("Response", {}).get("fibrechannel-switch", [])
            if isinstance(switches, dict):
                switches = [switches]
            if switches:
                iod_enabled = switches[0].get("in-order-delivery-enabled")
                if iod_enabled is None:
                    switch_name = switches[0].get("name") or switches[0].get("wwn")
                    if switch_name:
                        # Valid instance URL as per user instruction
                        iod_url = full_fc_switch_url + "/name/" + switch_name
                        l_rtype, l_rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, iod_url, timeout)
                        if l_rtype == 0:
                            sw_inst = l_rdict.get("Response", {}).get("fibrechannel-switch", {})
                            if isinstance(sw_inst, list) and len(sw_inst) > 0:
                                sw_inst = sw_inst[0]
                            iod_enabled = sw_inst.get("in-order-delivery-enabled")

                if iod_enabled is not None:
                    fabric_data["preserved-domain-id-mode-enabled"] = str(iod_enabled).lower()

    return 0, rdict


def fabric_patch(
    login, password, fos_ip_addr, fos_version, is_https, auth, vfid, result, diff_attributes, ssh_hostkeymust, timeout
):
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
        # Handle principal-priority dependency
        selection_enabled = patch_data.get("principal-selection-enabled")
        priority = patch_data.get("principal-priority")

        # If priority is provided but selection-enabled is not, we need to know the current state
        if priority is not None and selection_enabled is None:
            full_fabric_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_FABRIC)
            rtype, rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, full_fabric_url, timeout)
            current_selection = None
            if rtype == 0:
                fabric = rdict.get("Response", {}).get("fabric", {})
                if isinstance(fabric, list) and len(fabric) > 0:
                    fabric = fabric[0]
                if isinstance(fabric, dict):
                    current_selection = fabric.get("principal-selection-enabled")

            if current_selection is None:
                # Try leaf URI
                leaf_url = full_fabric_url + "/principal-selection-enabled"
                l_rtype, l_rdict = url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, leaf_url, timeout)
                if l_rtype == 0:
                    current_selection = l_rdict.get("Response", {}).get("principal-selection-enabled")

            if current_selection is not None:
                selection_enabled = str(current_selection).lower() == "true"

        # Apply priority logic
        if selection_enabled is False:
            # If disabling principal selection, priority must be 0 and should be omitted from patch
            if priority is not None and str(priority) != "0" and str(priority) != "0x0":
                result["failed"] = True
                result["msg"] = "Principal priority must be 0 when disabling principal-selection-enabled."
                return -1
            patch_data.pop("principal-priority", None)
        elif selection_enabled is True or (selection_enabled is None and priority is not None):
            # If enabling or already enabled, normalize priority if present
            if priority is not None:
                try:
                    p_val = int(str(priority), 0)
                    if p_val == 0:
                        patch_data["principal-priority"] = "0"
                    else:
                        patch_data["principal-priority"] = "0x{:02x}".format(p_val)
                except ValueError:
                    pass  # Keep as is if not an int

        if patch_data and ("failed" not in result or not result["failed"]):
            full_fabric_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_FABRIC)
            rtype_patch = url_patch_single_object(
                fos_ip_addr, is_https, auth, vfid, result, full_fabric_url, "fabric", patch_data, timeout
            )
            if rtype_patch != 0:
                # Fallback for preserved-domain-id-mode-enabled if it failed in /fabric
                if "preserved-domain-id-mode-enabled" in patch_data:
                    iod_val = patch_data.pop("preserved-domain-id-mode-enabled")
                    # Try to patch the rest of fabric first
                    if patch_data:
                        url_patch_single_object(
                            fos_ip_addr, is_https, auth, vfid, result, full_fabric_url, "fabric", patch_data, timeout
                        )

                    # Now try fallback for IOD on fibrechannel-switch instance
                    full_fc_switch_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_SWITCH_NEW_URI)
                    rtype_switch, rdict_switch = url_get_to_dict(
                        fos_ip_addr, is_https, auth, vfid, result, full_fc_switch_url, timeout
                    )
                    if rtype_switch == 0:
                        switches = rdict_switch.get("Response", {}).get("fibrechannel-switch", [])
                        if isinstance(switches, dict):
                            switches = [switches]
                        if switches:
                            switch_name = switches[0].get("name") or switches[0].get("wwn")
                            if switch_name:
                                # Use the valid instance URL as per user instruction
                                iod_url = full_fc_switch_url + "/name/" + switch_name
                                ret_code, body = bsn_json_dumps(
                                    result, {"fibrechannel-switch": {"in-order-delivery-enabled": iod_val}}
                                )
                                if ret_code != 0:
                                    return -100
                                rtype_patch_iod = url_patch(
                                    fos_ip_addr, is_https, auth, vfid, result, iod_url, body, timeout
                                )
                                if rtype_patch_iod == 0:
                                    result["changed"] = True
                                    if "messages" not in result:
                                        result["messages"] = ""
                                    result["messages"] += "preserved-domain-id-mode-enabled updated via fallback. "
                                    return 0

                result["failed"] = True
                result["msg"] = "Failed to update fabric attributes via REST"
                return -1
            else:
                result["changed"] = True
                if "messages" not in result:
                    result["messages"] = ""
                result["messages"] += "Fabric attributes updated via REST. "
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

    return 0


def port_configuration_get(
    login, password, fos_ip_addr, fos_version, is_https, auth, vfid, result, ssh_hostkeymust, timeout
):
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

    rssh, sshstr = ssh_and_configure(
        login, password, fos_ip_addr, ssh_hostkeymust, "creditrecovmode --show", "showcommand"
    )
    if rssh == 0:
        if "Internal port credit recovery is Disabled" in sshstr:
            rdict["Response"]["port-configuration"]["credit-recovery-mode"] = "off"
        elif "Internal port credit recovery is Enabled with LrOnly" in sshstr:
            rdict["Response"]["port-configuration"]["credit-recovery-mode"] = "onLrOnly"
        elif "Internal port credit recovery is Enabled with LrThresh" in sshstr:
            rdict["Response"]["port-configuration"]["credit-recovery-mode"] = "onLrThresh"
        elif "Not supported on this platform" in sshstr:
            result["credit_recovery_mode"] = "Not supported on this platform"
        else:
            result["failed"] = True
            result["msg"] = "credit-recovery-mode returned unknown string"
            return -1, None

    return 0, rdict


def port_configuration_patch(
    login, password, fos_ip_addr, fos_version, is_https, auth, vfid, result, diff_attributes, ssh_hostkeymust, timeout
):
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

    if "credit-recovery-mode" in l_diffs:
        if l_diffs["credit-recovery-mode"] == "off":
            rssh, sshstr = ssh_and_configure(
                login, password, fos_ip_addr, ssh_hostkeymust, "creditrecovmode --cfg off", ""
            )
            if rssh != 0:
                result["failed"] = True
                result["msg"] = "Failed to set credit-recovery-mode to off. " + sshstr
            else:
                result["changed"] = True
                result["messages"] = "credit-recovery-mode set to off"
        elif l_diffs["credit-recovery-mode"] == "onLrOnly":
            rssh, sshstr = ssh_and_configure(
                login, password, fos_ip_addr, ssh_hostkeymust, "creditrecovmode --cfg onLrOnly", ""
            )
            if rssh != 0:
                result["failed"] = True
                result["msg"] = "Failed to credit-recovery-mode to onLrOnly. " + sshstr
            else:
                result["changed"] = True
                result["messages"] = "credit-recovery-mode set to onLrOnly"
        elif l_diffs["credit-recovery-mode"] == "onLrThresh":
            rssh, sshstr = ssh_and_configure(
                login, password, fos_ip_addr, ssh_hostkeymust, "creditrecovmode --cfg onLrThresh", ""
            )
            if rssh != 0:
                result["failed"] = True
                result["msg"] = "Failed to credit-recovery-mode to onLrThresh. " + sshstr
            else:
                result["changed"] = True
                result["messages"] = "credit-recovery-mode set to onLrThresh"
        else:
            result["failed"] = True
            result["msg"] = "unknown credit-recovery-mode value"
        l_diffs.pop("credit-recovery-mode")

    if len(l_diffs) == 0:
        return 0

    full_port_config_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_PORT_CONFIGURATION)

    return url_patch_single_object(
        fos_ip_addr, is_https, auth, vfid, result, full_port_config_url, "port-configuration", l_diffs, timeout
    )
