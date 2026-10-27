#!/usr/bin/env bash
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

set -eu

# ansible-test runs a copy of this target below the collection's tests/output/.
lint_collection_root="$PWD"
while [[ ! -f "$lint_collection_root/galaxy.yml" || ! -f "$lint_collection_root/tests/sanity/lint_header_check.py" ]]; do
    if [[ "$lint_collection_root" == / ]]; then
        echo "Cannot find the collection containing tests/sanity/lint_header_check.py" >&2
        exit 2
    fi
    lint_collection_root=$(dirname "$lint_collection_root")
done

cd "$lint_collection_root"
# Lint syntax checks use example host groups without an integration inventory.
unset ANSIBLE_HOST_PATTERN_MISMATCH
exec python tests/sanity/lint_header_check.py "$@"
