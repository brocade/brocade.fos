# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries


from __future__ import absolute_import, division, print_function

from ansible_collections.brocade.fos.plugins.module_utils.brocade_json import bsn_json_dumps
from ansible_collections.brocade.fos.plugins.module_utils.brocade_url import full_url_get, url_get_to_dict, url_patch
from ansible_collections.brocade.fos.plugins.module_utils.brocade_yang import human_to_yang, str_to_human, yang_to_human

__metaclass__ = type


"""
Brocade Fibre Channel port utils
"""


REST_FC = "/rest/running/brocade-interface/fibrechannel"
REST_FC_STATS = "/rest/running/brocade-interface/fibrechannel-statistics"


zero_one_attributes = [
    "g-port-locked",
    "e-port-disable",
    "n-port-enabled",
    "d-port-enable",
    "persistent-disable",
    "qos-enabled",
    "compression-configured",
    "encryption-enabled",
    "target-driven-zoning-enable",
    "sim-port-enabled",
    "mirror-port-enabled",
    "credit-recovery-enabled",
    "csctl-mode-enabled",
    "fault-delay-enabled",
    "vc-link-init",
    "isl-ready-mode-enabled",
    "rscn-suppression-enabled",
    "npiv-enabled",
    "npiv-flogi-logout-enabled",
    "ex-port-enabled",
    "fec-enabled",
    "via-tts-fec-enabled",
    "port-autodisable-enabled",
    "non-dfe-enabled",
    "trunk-port-enabled",
]


def to_human_fc(port_config):
    # convert real boolean strings to boolean first
    # then convert the non 0/1 integers to boolean
    # then convert the 0/1 integers to boolean
    yang_to_human(port_config)

    for k, v in port_config.items():
        if v == "true":
            port_config[k] = True
        elif v == "false":
            port_config[k] = False

    if "enabled_state" in port_config:
        if str(port_config["enabled_state"]) == "2":
            port_config["enabled_state"] = True
        else:
            port_config["enabled_state"] = False

    for attrib in zero_one_attributes:
        if str_to_human(attrib) in port_config:
            if str(port_config[str_to_human(attrib)]) == "0":
                port_config[str_to_human(attrib)] = False
            else:
                port_config[str_to_human(attrib)] = True

    if "los_tov_mode_enabled" in port_config:
        val = str(port_config["los_tov_mode_enabled"])
        if val == "0":
            port_config["los_tov_mode_enabled"] = "Disabled"
        elif val == "1":
            port_config["los_tov_mode_enabled"] = "Fixed"
        elif val == "2":
            port_config["los_tov_mode_enabled"] = "FixedAuto"

    if "long_distance" in port_config:
        val = str(port_config["long_distance"])
        if val == "0":
            port_config["long_distance"] = "Disabled"
        elif val == "1":
            port_config["long_distance"] = "L0"
        elif val == "2":
            port_config["long_distance"] = "L1"
        elif val == "3":
            port_config["long_distance"] = "L2"
        elif val == "4":
            port_config["long_distance"] = "LE"
        elif val == "5":
            port_config["long_distance"] = "L0.5"
        elif val == "6":
            port_config["long_distance"] = "LD"
        elif val == "7":
            port_config["long_distance"] = "LS"

    if "speed" in port_config:
        val = str(port_config["speed"])
        if val == "32000000000":
            port_config["speed"] = "32Gig"
        elif val == "16000000000":
            port_config["speed"] = "16Gig"
        elif val == "10000000000":
            port_config["speed"] = "10Gig"
        elif val == "8000000000":
            port_config["speed"] = "8Gig"
        elif val == "4000000000":
            port_config["speed"] = "4Gig"
        elif val == "2000000000":
            port_config["speed"] = "2Gig"
        elif val == "1000000000":
            port_config["speed"] = "1Gig"
        elif val == "0":
            port_config["speed"] = "Auto"

    if "max_speed" in port_config:
        val = str(port_config["max_speed"])
        if val == "32000000000":
            port_config["max_speed"] = "32Gig"
        elif val == "16000000000":
            port_config["max_speed"] = "16Gig"
        elif val == "10000000000":
            port_config["max_speed"] = "10Gig"
        elif val == "8000000000":
            port_config["max_speed"] = "8Gig"
        elif val == "4000000000":
            port_config["max_speed"] = "4Gig"
        elif val == "2000000000":
            port_config["max_speed"] = "2Gig"
        elif val == "1000000000":
            port_config["max_speed"] = "1Gig"
        elif val == "0":
            port_config["max_speed"] = "Auto"


def to_fos_fc(port_config, result):
    human_to_yang(port_config)

    # convert boolean to non 0/1 integer
    # convert boolean to 0/1 integer
    # leave any remaining booleans as native JSON booleans
    if "enabled-state" in port_config:
        if port_config["enabled-state"] is True:
            port_config["enabled-state"] = 2
        elif port_config["enabled-state"] is False:
            port_config["enabled-state"] = 6
        else:
            result["failed"] = True
            result["msg"] = "enabled-state converted to unknown value"
            return -1

    for attrib in zero_one_attributes:
        if attrib in port_config:
            if isinstance(port_config[attrib], bool):
                if port_config[attrib] is False:
                    port_config[attrib] = 0
                else:
                    port_config[attrib] = 1
            else:
                result["failed"] = True
                result["msg"] = attrib + " converted non-bool value"
                return -1

    """for k, v in port_config.items():
        # is-enabled-state is excluded: FOS rejects a quoted string for this
        # leaf ("Invalid input data for is-enabled-state") and wants a native
        # JSON boolean instead, same as on brocade_fibrechannel_switch.
        if k == "is-enabled-state":
            continue
        if isinstance(v, bool):
            if v is True:
                port_config[k] = "true"
            else:
                port_config[k] = "false" """

    if "los-tov-mode-enabled" in port_config:
        if port_config["los-tov-mode-enabled"] == "Disabled":
            port_config["los-tov-mode-enabled"] = 0
        elif port_config["los-tov-mode-enabled"] == "Fixed":
            port_config["los-tov-mode-enabled"] = 1
        elif port_config["los-tov-mode-enabled"] == "FixedAuto":
            port_config["los-tov-mode-enabled"] = 2
        else:
            result["failed"] = True
            result["msg"] = "los-tov-mode-enabled converted to unknown value"
            return -1

    if "long-distance" in port_config:
        if port_config["long-distance"] == "Disabled":
            port_config["long-distance"] = 0
        elif port_config["long-distance"] == "L0":
            port_config["long-distance"] = 1
        elif port_config["long-distance"] == "L1":
            port_config["long-distance"] = 2
        elif port_config["long-distance"] == "L2":
            port_config["long-distance"] = 3
        elif port_config["long-distance"] == "LE":
            port_config["long-distance"] = 4
        elif port_config["long-distance"] == "L0.5":
            port_config["long-distance"] = 5
        elif port_config["long-distance"] == "LD":
            port_config["long-distance"] = 6
        elif port_config["long-distance"] == "LS":
            port_config["long-distance"] = 7
        else:
            result["failed"] = True
            result["msg"] = "long-distance converted to unknown value"
            return -1

    if "speed" in port_config:
        if port_config["speed"] == "32Gig":
            port_config["speed"] = 32000000000
        elif port_config["speed"] == "16Gig":
            port_config["speed"] = 16000000000
        elif port_config["speed"] == "8Gig":
            port_config["speed"] = 8000000000
        elif port_config["speed"] == "10Gig":
            port_config["speed"] = 10000000000
        elif port_config["speed"] == "4Gig":
            port_config["speed"] = 4000000000
        elif port_config["speed"] == "2Gig":
            port_config["speed"] = 2000000000
        elif port_config["speed"] == "1Gig":
            port_config["speed"] = 1000000000
        elif port_config["speed"] == "Auto":
            port_config["speed"] = 0
        else:
            result["failed"] = True
            result["msg"] = "speed converted to unknown value"
            return -1

    if "max-speed" in port_config:
        if port_config["max-speed"] == "32Gig":
            port_config["max-speed"] = 32000000000
        elif port_config["max-speed"] == "16Gig":
            port_config["max-speed"] = 16000000000
        elif port_config["max-speed"] == "8Gig":
            port_config["max-speed"] = 8000000000
        elif port_config["max-speed"] == "10Gig":
            port_config["max-speed"] = 10000000000
        elif port_config["max-speed"] == "4Gig":
            port_config["max-speed"] = 4000000000
        elif port_config["max-speed"] == "2Gig":
            port_config["max-speed"] = 2000000000
        elif port_config["max-speed"] == "1Gig":
            port_config["max-speed"] = 1000000000
        elif port_config["max-speed"] == "Auto":
            port_config["max-speed"] = 0
        else:
            result["failed"] = True
            result["msg"] = "max-speed converted to unknown value"
            return -1

    return 0


def fc_port_get(fos_ip_addr, is_https, auth, vfid, result, timeout):
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
    :return: list of dict of port configurations
    :rtype: list
    """
    full_fc_port_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_FC)

    return url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, full_fc_port_url, timeout)


def fc_port_patch(fos_ip_addr, is_https, auth, vfid, result, ports, timeout):
    """
    update existing port configurations

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type auth: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :param ports: list of ports and associated attributes for update
    :type ports: list
    :return: code to indicate failure or success
    :rtype: int
    :return: list of dict of port configurations
    :rtype: list
    """
    full_fc_port_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_FC)

    body = []
    for port in ports:
        entry = {"name": port["name"]}
        for k, v in port.items():
            if k != "name":
                entry[k.replace("_", "-")] = v
        body.append(entry)

    ret_code, fc_port_str = bsn_json_dumps(result, {"fibrechannel": body})
    if ret_code != 0:
        return -100

    result["fc_port_str"] = fc_port_str

    return url_patch(fos_ip_addr, is_https, auth, vfid, result, full_fc_port_url, fc_port_str, timeout)
