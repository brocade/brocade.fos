# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

import base64

__metaclass__ = type


"""
Brocade yang utilities
"""


BASE64_PWD_ERROR = "Password can not be decoded"


def to_base64(s):
    if not isinstance(s, str):
        return BASE64_PWD_ERROR

    try:
        return base64.b64encode(s.encode("ascii")).decode("utf-8")
    except Exception:
        return BASE64_PWD_ERROR


def get_major_fos_version(fos_version):
    """
    parse a FOS version string (e.g. "v9.2.2b", "v10.0.1_bld44") into its
    major version as an int (e.g. 9, 10)
    """
    return int(fos_version.split(".", 1)[0].replace("v", ""))


def is_fos_version_less_than(fos_version, major_version):
    """
    check whether a FOS version string's major version is less than the
    given integer major version, e.g. is_fos_version_less_than("v9.2.2b", 10) -> True

    returns False if fos_version is None (version unknown)
    """
    if fos_version is None:
        return False
    return get_major_fos_version(fos_version) < major_version


def str_to_yang(istring):
    return istring.replace("_", "-")


def str_to_human(istring):
    return istring.replace("-", "_")


def is_full_human(inputs, result):
    if isinstance(inputs, list):
        for entry in inputs:
            if isinstance(entry, dict):
                for k, v in entry.items():
                    if "-" in k:
                        result["failed"] = True
                        result["msg"] = "user variable name " + k + " should not contain hyphen"
                        return False
                    elif isinstance(v, dict):
                        for k1, _v1 in v.items():
                            if "-" in k1:
                                result["failed"] = True
                                result["msg"] = "user variable name " + k1 + " should not contain hyphen"
                                return False
    elif isinstance(inputs, dict):
        for k, v in inputs.items():
            if "-" in k:
                result["failed"] = True
                result["msg"] = "user variable name " + k + " should not contain hyphen"
                return False
            elif isinstance(v, dict):
                for k1, _v1 in v.items():
                    if "-" in k1:
                        result["failed"] = True
                        result["msg"] = "user variable name " + k1 + " should not contain hyphen"
                        return False
    return True


def yang_to_human(attributes):
    yang_attributes = {}
    for k, v in attributes.items():
        if isinstance(v, dict):
            dict_v = {}
            for k1, v1 in v.items():
                if isinstance(v1, dict):
                    yang_to_human(v1)
                dict_v[str_to_human(k1)] = v1
            yang_attributes[str_to_human(k)] = dict_v
        elif isinstance(v, list):
            new_list = []
            for entry in v:
                if isinstance(entry, dict):
                    new_dict = {}
                    for k1, v1 in entry.items():
                        if isinstance(v1, dict):
                            yang_to_human(v1)
                        new_dict[str_to_human(k1)] = v1
                    new_list.append(new_dict)
                else:
                    new_list.append(entry)
            yang_attributes[str_to_human(k)] = new_list
        else:
            yang_attributes[str_to_human(k)] = v

    attributes.clear()
    for k, v in yang_attributes.items():
        attributes[k] = v


def human_to_yang(attributes):
    human_attributes = {}
    for k, v in attributes.items():
        if isinstance(v, dict):
            dict_v = {}
            for k1, v1 in v.items():
                dict_v[str_to_yang(k1)] = v1
            human_attributes[str_to_yang(k)] = dict_v
        elif isinstance(v, list):
            new_list = []
            for entry in v:
                new_dict = {}
                for k1, v1 in entry.items():
                    new_dict[str_to_yang(k1)] = v1
                new_list.append(new_dict)
            human_attributes[str_to_yang(k)] = new_list
        else:
            human_attributes[str_to_yang(k)] = v

    attributes.clear()
    for k, v in human_attributes.items():
        attributes[k] = v


def find_diff(result, yang_key, new_value, c_config, diff_attributes):
    if new_value is None:
        return
    if c_config is not None and yang_key in c_config:
        if isinstance(new_value, bool):
            if new_value != c_config[yang_key]:
                diff_attributes[yang_key] = new_value
        elif isinstance(new_value, dict):
            # if the new value is dict, just recursively
            # deal with the content
            for k, v in new_value.items():
                yang_k = k
                diff_attributes[yang_key] = {}
                find_diff(result, yang_k, v, c_config[yang_key], diff_attributes[yang_key])
            if len(diff_attributes[yang_key]) == 0:
                diff_attributes.pop(yang_key)
        elif isinstance(new_value, list):
            # if the new value is a list, compare the diff
            if c_config[yang_key] is None or len(new_value) != len(c_config[yang_key]):
                diff_attributes[yang_key] = new_value
            else:
                for nentry in new_value:
                    found = False
                    for centry in c_config[yang_key]:
                        if nentry == centry:
                            found = True
                    if not found:
                        diff_attributes[yang_key] = new_value
        else:
            if new_value != c_config[yang_key] and str(new_value) != str(c_config[yang_key]):
                diff_attributes[yang_key] = new_value
    else:
        # if the key doesn't exist in the current config
        # just mark it as different using the new vlaue
        diff_attributes[yang_key] = new_value


def generate_diff(result, c_config, n_config):
    """
    generates the diff list between current & new config

    :param result: dict to keep track of execution msgs
    :type result: dict
    :param c_config: dict of current config
    :type c_config: dict
    :param n_config: dict of new config
    :type n_config: dict
    :return: dict of diff list
    :rtype: dict
    """

    diff_attributes = {}

    if n_config is not None:
        for k, v in n_config.items():
            yang_key = k
            find_diff(result, yang_key, v, c_config, diff_attributes)

    return diff_attributes
