# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries


from __future__ import absolute_import, division, print_function

import time
from pathlib import Path

import ansible.module_utils.six.moves.urllib.error as urllib_error
import ansible.module_utils.urls as ansible_urls
from ansible.module_utils.common.warnings import warn
from ansible_collections.brocade.fos.plugins.module_utils.brocade_json import bsn_json_dumps, bsn_json_loads
from ansible_collections.brocade.fos.plugins.module_utils.brocade_yang import str_to_yang

__metaclass__ = type


"""
Brocade Connections utils
"""

DEFAULT_TO = 180

VF_ID = "?vf-id="
HTTP = "http://"
HTTPS = "https://"
SELF_SIGNED = "self"
HTTPS_ENABLED = "true"


ERROR_GENERIC = -1
ERROR_LIST_EMPTY = -2
ERROR_SERVER_BUSY = -3


def full_url_get(is_https, fos_ip_addr, path):
    if isinstance(is_https, bool):
        if is_https:
            return HTTPS + fos_ip_addr + str_to_yang(path), True
        else:
            return HTTP + fos_ip_addr + str_to_yang(path), False
    elif is_https.lower() == HTTPS_ENABLED:
        return HTTPS + fos_ip_addr + str_to_yang(path), True
    elif is_https.lower() == SELF_SIGNED:
        return HTTPS + fos_ip_addr + str_to_yang(path), False
    else:
        # unrecognized https value - fall back to HTTP but warn, since this
        # silently downgrades the connection from what the caller may expect
        warn(
            f"credential.https value {is_https!r} is not recognized (expected true/false/'self'); falling back to false"
        )
        return HTTP + fos_ip_addr + str_to_yang(path), False


def url_post(fos_ip_addr, is_https, auth, vfid, result, url, body, timeout):
    retcode, post_resp = url_post_resp(fos_ip_addr, is_https, auth, vfid, result, url, body, timeout)

    return retcode


def url_post_resp(fos_ip_addr, is_https, auth, vfid, result, url, body, timeout):
    """
    general function to post for a given url

    :param fos_ip_addr: fos switch ip address
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTPS or HTTP
    :type fos_password: Bool
    :param auth: return authorization struct at the time of login
    :type auth: dict
    :param result: dict to store execution results in
    :type result: dict
    :param url: full url
    :type url: str
    :param body: body to post
    :type body: str
    :return: 0 for success or -1 for failure
    :rtype: int
    """
    not_used, validate_certs = full_url_get(is_https, "", "")

    if vfid is not None and vfid != -1:
        url = url + VF_ID + str(vfid)

    edict = {}
    retval, eret, edict, post_resp = url_helper(url, body, "POST", auth, result, validate_certs, timeout)
    if retval == ERROR_GENERIC:
        if eret == ERROR_SERVER_BUSY:
            time.sleep(auth["throttle"])
            retval, eret, edict, post_resp = url_helper(url, body, "POST", auth, result, validate_certs, timeout)
            if retval == ERROR_GENERIC:
                return eret, edict
        else:
            return eret, edict

    post_resp_data = post_resp.read()
    if len(post_resp_data) == 0:
        return 0, edict

    ret_code, root_dict = bsn_json_loads(result, post_resp_data)
    if ret_code == -1:
        result["failed"] = True
        result["msg"] = "bsn_json_loads failed"
        return -100, None

    return 0, root_dict


def url_patch(fos_ip_addr, is_https, auth, vfid, result, url, body, timeout):
    """
    general function to patch for a given url

    :param fos_ip_addr: fos switch ip address
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTPS or HTTP
    :type fos_password: Bool
    :param auth: return authorization struct at the time of login
    :type auth: dict
    :param result: dict to store execution results in
    :type auth: dict
    :param url: full url
    :type url: str
    :param body: body to post
    :type body: str
    :return: 0 for success or -1 for failure
    :rtype: int
    """
    not_used, validate_certs = full_url_get(is_https, "", "")

    if vfid is not None and vfid != -1:
        url = url + VF_ID + str(vfid)

    retval, eret, edict, resp = url_helper(url, body, "PATCH", auth, result, validate_certs, timeout)
    if retval == ERROR_GENERIC:
        if eret == ERROR_SERVER_BUSY:
            time.sleep(auth["throttle"])
            retval, eret, delete, resp = url_helper(url, body, "PATCH", auth, result, validate_certs, timeout)
            if retval == ERROR_GENERIC:
                return eret
        else:
            return eret

    result["patch_resp_data"] = resp.read()

    return 0


def url_delete(fos_ip_addr, is_https, auth, vfid, result, url, body, timeout):
    """
    general function to delete for a given url

    :param fos_ip_addr: fos switch ip address
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTPS or HTTP
    :type fos_password: Bool
    :param auth: return authorization struct at the time of login
    :type auth: dict
    :param result: dict to store execution results in
    :type result: dict
    :param url: full url
    :type url: str
    :param body: body to post
    :type body: str
    :return: 0 for success or -1 for failure
    :rtype: int
    """
    not_used, validate_certs = full_url_get(is_https, "", "")

    if vfid is not None and vfid != -1:
        url = url + VF_ID + str(vfid)

    retval, eret, edict, delete_resp = url_helper(url, body, "DELETE", auth, result, validate_certs, timeout)
    if retval == ERROR_GENERIC:
        if eret == ERROR_SERVER_BUSY:
            time.sleep(auth["throttle"])
            retval, eret, delete, delete_resp = url_helper(url, body, "DELETE", auth, result, validate_certs, timeout)
            if retval == ERROR_GENERIC:
                return eret
        else:
            return eret

    return 0


messages_404 = [
    "No entries found",
    "No syslog servers are configured",
    "No entries in Name Server",
    "No ports have Trunk Area enabled",
    "No trunking Links",
    "No pause/continue configuration",
    "No Rule violations found",
    "RADIUS configuration does not exist.",
    "TACACS+ configuration does not exist.",
    "LDAP configuration does not exist.",
    "Role Map Configuration does not exist",
    "No public keys found",
    "No device was found",
]

empty_messages_400 = [
    "Not supported on this platform",
    "AG mode is not enabled",
    "Extension not supported on this platform",
    "No entries in the FDMI database",
    "No licenses installed",
    "cannot find required parameter User group",
]


def error_message_in(errs, messages):
    if isinstance(errs, list):
        return any(err["error-message"] in messages for err in errs)

    return errs["error-message"] in messages


def known_empty_message(errs):
    if isinstance(errs, list):
        for err in errs:
            if err["error-message"] in empty_messages_400:
                return True, err["error-message"]
    else:
        if errs["error-message"] in empty_messages_400:
            return True, errs["error-message"]

    return False, None


CHASSIS_NOT_READY = "Chassis is not ready for management"


def chassis_not_ready_message(errs):
    if isinstance(errs, list):
        for err in errs:
            if err["error-message"] == CHASSIS_NOT_READY:
                return True, err["error-message"]
    else:
        if errs["error-message"] in CHASSIS_NOT_READY:
            return True, errs["error-message"]

    return False, None


def url_helper(url, body, method, auth, result, validate_certs, timeout, credential=None):
    myheaders = {}
    root_dict = {}
    root_dict["errors"] = {}
    root_dict["errors"]["error"] = {}
    root_dict["errors"]["error"]["error-message"] = {}

    if credential is None:
        myheaders = {
            "Authorization": auth["auth"],
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }
    else:
        myheaders = credential

    if timeout is None:
        timeout = DEFAULT_TO

    try:
        get_resp = ansible_urls.open_url(
            url,
            body,
            headers=myheaders,
            method=method,
            timeout=timeout,
            validate_certs=validate_certs,
            follow_redirects=False,
        )
    except urllib_error.HTTPError as e:
        e_data = e.read()
        if len(e_data) > 0:
            parse_ret_code, parsed_data = bsn_json_loads(result, e_data)
            if parse_ret_code == 0:
                root_dict = parsed_data
            result[method + "_resp_data"] = root_dict
        else:
            result[method + "_resp_data"] = e_data

        if e.code == 404 and error_message_in(root_dict["errors"]["error"], messages_404):
            empty_list_resp = {}
            empty_list_resp["Response"] = {}
            base_type = Path(url).name.split("?")[0]
            empty_list_resp["Response"][base_type] = []
            return ERROR_GENERIC, 0, empty_list_resp, None

        result[method + "_url"] = url
        result[method + "_resp_code"] = e.code
        result[method + "_resp_reason"] = e.reason

        ret_val = ERROR_GENERIC
        if e.code == 405:
            ret_val = ERROR_LIST_EMPTY
        elif e.code == 503:
            is_chassis_not_ready, err_msg = chassis_not_ready_message(root_dict["errors"]["error"])
            if is_chassis_not_ready:
                result["failed"] = True
                result["msg"] = method + " failed"
            else:
                ret_val = ERROR_SERVER_BUSY
                result["failed"] = True
                result["msg"] = method + " failed"
        elif e.code == 400:
            is_known, err_msg = known_empty_message(root_dict["errors"]["error"])
            if is_known:
                result["msg"] = err_msg
                ret_val = ERROR_LIST_EMPTY
            else:
                result["failed"] = True
                result["msg"] = method + " failed"
        else:
            result["failed"] = True
            result["msg"] = method + " failed"
        return ERROR_GENERIC, ret_val, None, None
    except urllib_error.URLError as e:
        result[method + "_url"] = url
        result["failed"] = True
        result["msg"] = f"{method} failed. {e}"
        return ERROR_GENERIC, ERROR_GENERIC, None, None

    result[method + "_url"] = url

    return (
        0,
        0,
        None,
        get_resp,
    )


def url_get_to_dict(fos_ip_addr, is_https, auth, vfid, result, url, timeout):
    """
    retrieve existing url content and return dict

    :param fos_ip_addr: ip address of FOS switch
    :type fos_ip_addr: str
    :param is_https: indicate to use HTTP or HTTPS
    :type is_https: bool
    :param auth: authorization struct from login
    :type auth: dict
    :param result: dict to keep track of execution msgs
    :type result: dict
    :param url: url for FOS REST API
    :type url: str
    :return: code to indicate failure or success
    :rtype: int
    :return: list of dict of port configurations
    :rtype: list
    """
    not_used, validate_certs = full_url_get(is_https, "", "")

    if vfid is not None and vfid != -1:
        url = url + VF_ID + str(vfid)

    retval = 0
    eret = 0
    edict = {}
    get_resp = {}
    retval, eret, edict, get_resp = url_helper(url, None, "GET", auth, result, validate_certs, timeout)
    if retval == ERROR_GENERIC:
        if eret == ERROR_SERVER_BUSY:
            time.sleep(auth["throttle"])
            retval, eret, edict, get_resp = url_helper(url, None, "GET", auth, result, validate_certs, timeout)
            if retval == ERROR_GENERIC:
                return eret, edict
        else:
            return eret, edict

    data = get_resp.read()
    ret_code, root_dict = bsn_json_loads(result, data)
    if ret_code == -1:
        result["failed"] = True
        result["msg"] = "bsn_json_loads failed"
        return -100, None

    return 0, root_dict


def url_patch_single_object(fos_ip_addr, is_https, auth, vfid, result, url, obj_name, diff_attributes, timeout):
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
    :return: dict of key/value attributes of an object
    :rtype: dict
    """
    ret_code, diff_str = bsn_json_dumps(result, {obj_name: diff_attributes})
    if ret_code != 0:
        return -100

    result["url"] = url
    result["diff_str"] = diff_str

    return url_patch(fos_ip_addr, is_https, auth, vfid, result, url, diff_str, timeout)
