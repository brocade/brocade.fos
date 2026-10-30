#!/usr/bin/env bash
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

# Build the HTML documentation with antsibull-docs sphinx-init, the flow the
# Ansible developer guide recommends for collections.
# Usage: hacking/build_docs.sh [OUTPUT_DIR]  (default: tests/output/docs)

set -euo pipefail

repo_root=$(realpath "$(dirname "${BASH_SOURCE[0]}")/..")
output_dir=$(realpath -m "${1:-$repo_root/tests/output/docs}")
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT

# antsibull-docs documents installed collections, so build and install this one.
export ANSIBLE_COLLECTIONS_PATH="$work_dir/collections"
ansible-galaxy collection build --force --output-path "$work_dir" "$repo_root" >/dev/null
ansible-galaxy collection install "$work_dir"/brocade-fos-*.tar.gz \
    --collections-path "$ANSIBLE_COLLECTIONS_PATH" --offline --no-deps >/dev/null

rm -rf "$output_dir"
mkdir -p "$output_dir"
antsibull-docs sphinx-init --use-current --squash-hierarchy --dest-dir "$output_dir" brocade.fos >/dev/null
"$output_dir/build.sh"

printf '\nDocumentation: %s\n' "$output_dir/build/html/index.html"
