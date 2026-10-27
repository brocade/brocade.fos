#!/usr/bin/env bash
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

# Copy the current working files into a temporary ansible-test collection layout.
# Print only its path so callers can use: cd "$(hacking/prepare_ansible_test.sh)"

set -euo pipefail

source_checkout_root=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)
if [[ ! -f "$source_checkout_root/galaxy.yml" ]]; then
    printf 'Cannot find galaxy.yml in %s\n' "$source_checkout_root" >&2
    exit 1
fi

test_workspace_root=$(mktemp -d)
trap 'rm -rf -- "$test_workspace_root"' ERR
test_collection_root="$test_workspace_root/ansible_collections/brocade/fos"
mkdir -p "$test_collection_root"

cd "$source_checkout_root"
git ls-files -z --cached --others --exclude-standard |
    while IFS= read -r -d '' test_source_path; do
        if [[ -e "$test_source_path" || -L "$test_source_path" ]]; then
            printf '%s\0' "$test_source_path"
        fi
    done |
    tar --null -T - -cf - |
    tar -xf - -C "$test_collection_root"

printf '%s\n' "$test_collection_root"
