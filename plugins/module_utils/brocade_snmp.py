# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause


from __future__ import absolute_import, division, print_function

__metaclass__ = type


"""
Brocade logging utils
"""


def v1_trap_patch(v1_traps):
    """
    update existing user config configurations

    :param v1_traps: list of attributes for update
    :type v1_traps: list
    :return: list of dict of chassis configurations
    :rtype: list
    """
    rest_v1_traps = []

    for l_v1_trap in v1_traps:
        if len(l_v1_trap) > 1:
            rest_v1_traps.append(l_v1_trap)

    return rest_v1_traps


def v3_trap_patch(v3_traps):
    """
    update existing user config configurations

    :param v3_traps: list of attributes for update
    :type v3_traps: list
    :return: list of dict of chassis configurations
    :rtype: list
    """
    rest_v3_traps = []

    for l_v3_trap in v3_traps:
        if len(l_v3_trap) > 1:
            rest_v3_traps.append(l_v3_trap)

    return rest_v3_traps
