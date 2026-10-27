#!/usr/bin/env bash
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

# Validate pending changelog fragments and incorporate them into the release
# version declared in galaxy.yml. Run after updating the version in galaxy.yml.

set -euo pipefail

REPO_ROOT="$(realpath "$(dirname "${BASH_SOURCE[0]}")/..")"
cd "${REPO_ROOT}"

collection_version=$(python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["version"])')

printf '==> Linting changelog fragments...\n'
antsibull-changelog lint

printf '==> Releasing changelog for version %s...\n' "${collection_version}"
antsibull-changelog release --version "${collection_version}"
