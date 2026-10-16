# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries


from __future__ import absolute_import, division, print_function

from ansible_collections.brocade.fos.plugins.module_utils.brocade_json import bsn_json_dumps
from ansible_collections.brocade.fos.plugins.module_utils.brocade_url import (
    full_url_get,
    url_get_to_dict,
    url_patch,
    url_post,
)
from ansible_collections.brocade.fos.plugins.module_utils.brocade_yang import (
    human_to_yang,
    is_fos_version_less_than,
    to_base64,
    yang_to_human,
)

__metaclass__ = type


"""
Brocade logging utils
"""


REST_IPFILTER_RULE = "/rest/running/brocade-security/ipfilter-rule"
REST_IPFILTER_POLICY = "/rest/running/brocade-security/ipfilter-policy"
REST_USER_CONFIG = "/rest/running/brocade-security/user-config"
REST_PASSWORD = "/rest/running/brocade-security/password"


def to_fos_security_singleton(obj_name, attributes, result, fos_version=None):
    if obj_name == "sshutil_public_key_action" and is_fos_version_less_than(fos_version, 10):
        # protocol is not a valid resource attribute on FOS releases prior to v10.x
        attributes.pop("protocol", None)

    for k, _ in attributes.items():
        if obj_name == "password":
            if k == "old-password":
                attributes[k] = to_base64(attributes[k])
            if k == "new-password":
                attributes[k] = to_base64(attributes[k])

        if obj_name == "security_certificate_generate" and k == "key-size":
            # key-size is a YANG enumeration; RFC 7951 encodes enum values as
            # JSON strings, so the switch rejects a native int regardless of
            # FOS version
            attributes[k] = str(attributes[k])

        if (
            obj_name in ("security_certificate_action", "sshutil_public_key_action", "sec_crypto_cfg_template_action")
            and k == "remote-user-password"
        ):
            attributes[k] = to_base64(attributes[k])

    return 0


def to_human_ipfilter_policy(attributes):
    for k, v in attributes.items():
        if v == "true":
            attributes[k] = True
        elif v == "false":
            attributes[k] = False

    yang_to_human(attributes)


def to_fos_ipfilter_policy(attributes, result):
    human_to_yang(attributes)

    for k, v in attributes.items():
        if isinstance(v, bool):
            if v is True:
                attributes[k] = "true"
            else:
                attributes[k] = "false"

    return 0


def ipfilter_policy_get(fos_ip_addr, is_https, auth, vfid, result, timeout):
    """
    retrieve existing ipfilter policy configuration

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type struct: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :return: code to indicate failure or success
    :rtype: int
    :return: dict of ipfilter policy configurations
    :rtype: dict
    """
    full_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_IPFILTER_POLICY)

    return url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, full_url, timeout)


def ipfilter_policy_json_str(result, rules):
    body = []

    for rule in rules:
        entry = {"name": rule["name"]}
        for k, v in rule.items():
            if k != "name":
                entry[k.replace("_", "-")] = v
        body.append(entry)

    ret_code, json_str = bsn_json_dumps(result, {"ipfilter-policy": body})

    return json_str if ret_code == 0 else None


def ipfilter_policy_patch(fos_ip_addr, is_https, auth, vfid, result, policies, timeout):
    """
    update existing ip filter configurations

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type struct: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :param diff_attributes: list of attributes for update
    :type ports: dict
    :return: code to indicate failure or success
    :rtype: int
    :return: list of dict of chassis configurations
    :rtype: list
    """
    full_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_IPFILTER_POLICY)

    json_str = ipfilter_policy_json_str(result, policies)

    result["patch_ipfilter_policy_str"] = json_str

    return url_patch(fos_ip_addr, is_https, auth, vfid, result, full_url, json_str, timeout)


def user_config_json_str(result, users):
    ret_code, json_str = bsn_json_dumps(result, {"user-config": users})

    return json_str if ret_code == 0 else None


def user_config_patch(fos_ip_addr, is_https, auth, vfid, result, users, timeout):
    """
    update existing user config configurations

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type struct: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :param diff_attributes: list of attributes for update
    :type ports: dict
    :return: code to indicate failure or success
    :rtype: int
    :return: list of dict of chassis configurations
    :rtype: list
    """
    l_users = users[:]

    rest_users = []
    for l_user in l_users:
        if len(l_user) > 1:
            rest_users.append(l_user)

    if len(rest_users) == 0:
        return 0

    full_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_USER_CONFIG)

    json_str = user_config_json_str(result, rest_users)

    result["patch_user_config_str"] = json_str

    return url_patch(fos_ip_addr, is_https, auth, vfid, result, full_url, json_str, timeout)


def user_config_post(fos_ip_addr, is_https, auth, vfid, result, users, timeout):
    """
    add to ipfilter policy configurations

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type struct: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :param diff_attributes: list of attributes for update
    :type ports: dict
    :return: code to indicate failure or success
    :rtype: int
    :return: list of dict of chassis configurations
    :rtype: list
    """
    full_url, validate_certs = full_url_get(is_https, fos_ip_addr, REST_USER_CONFIG)

    json_str = user_config_json_str(result, users)

    result["post_user_config_str"] = json_str

    return url_post(fos_ip_addr, is_https, auth, vfid, result, full_url, json_str, timeout)
