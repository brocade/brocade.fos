#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Created with antsibull-docs 2.24.0

set -e

SCRIPT_DIR="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
pushd "${SCRIPT_DIR}"
COLLECTIONS_PATH=$(mktemp -d)
trap '{ popd; unset ANSIBLE_COLLECTIONS_PATH; rm -rf "${COLLECTIONS_PATH}"; }' EXIT

# Build and install the collection so antsibull-docs can discover it
VERSION=$(grep '^version:' "${REPO_ROOT}/galaxy.yml" | awk '{print $2}')
printf '\n==> Building collection brocade.fos %s...\n' "${VERSION}"
ansible-galaxy collection build --force "${REPO_ROOT}"
printf '\n==> Installing collection to %s...\n' "${COLLECTIONS_PATH}"
export ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_PATH}"
ansible-galaxy collection install "brocade-fos-${VERSION}.tar.gz" \
    -p "${COLLECTIONS_PATH}" --force

# Create collection documentation
printf '\n==> Generating RST documentation with antsibull-docs...\n'
mkdir -p rst
chmod og-w rst  # antsibull-docs wants that directory only readable by itself
antsibull-docs \
    --config-file antsibull-docs.cfg \
    collection \
    --cleanup everything \
    --use-current \
    --squash-hierarchy \
    --dest-dir rst \
    brocade.fos

# Build Sphinx site
printf '\n==> Building Sphinx HTML site...\n'
sphinx-build -M html rst build -c . -W -T --keep-going
printf '\n==> Done. Open docs/build/html/index.html to view the documentation.\n'
