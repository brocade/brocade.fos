#!/usr/bin/env bash
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

# Run collection checks in a fresh workspace and retain each suite's log.

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage: hacking/run_checks.sh [--only NAME] [--build-collection] [--build-docs]

Run lint/header checks, all unit tests, and Ansible sanity checks.
  --only NAME         Run one check from the summary in a fresh workspace.
  --build-collection  Also build and install the artifact in the test workspace.
  --build-docs        Also build the Sphinx HTML documentation.
  -h, --help         Show this usage information.
USAGE
}

build_collection=false
build_docs=false
only_check=
while [[ $# -gt 0 ]]; do
    case "$1" in
        --only)
            if [[ -z "${2:-}" || "${2:-}" == -* ]]; then
                printf 'Option --only requires a check name.\n' >&2
                exit 2
            fi
            only_check=$2
            shift
            ;;
        --build-collection) build_collection=true ;;
        --build-docs) build_docs=true ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

# Check prerequisites before creating the workspace.
for checks_tool in python ansible-test shellcheck; do
    if ! command -v "$checks_tool" >/dev/null 2>&1; then
        printf 'Required tool not found: %s. Complete Development Setup and activate .venv.\n' "$checks_tool" >&2
        exit 2
    fi
done
checks_script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
test_python_minor=$(python "$checks_script_dir/check_python_version.py")
test_collection_root=$("$checks_script_dir/prepare_ansible_test.sh")
cd "$test_collection_root"
checks_log_dir="$test_collection_root/tests/output/run_checks"
mkdir -p "$checks_log_dir"
printf 'Test workspace: %s\nLogs: %s\n' "$test_collection_root" "$checks_log_dir"

ansible_test_options=(--venv --python "$test_python_minor" --requirements)
check_names=()
check_codes=()
overall_status=0

run_check() {
    local check_name=$1
    shift
    if [[ -n "$only_check" && "$check_name" != "$only_check" ]]; then
        return 0
    fi
    local check_code=0
    local -a pipeline_codes
    printf '\n==> %s\n' "$check_name"
    if "$@" 2>&1 | tee "$checks_log_dir/$check_name.log"; then
        check_code=0
    else
        pipeline_codes=("${PIPESTATUS[@]}")
        check_code=${pipeline_codes[0]}
        if [[ "$check_code" -eq 0 ]]; then
            check_code=${pipeline_codes[1]}
            printf 'Could not capture the %s log (exit %s).\n' "$check_name" "$check_code" >&2
        fi
    fi
    check_names+=("$check_name")
    check_codes+=("$check_code")
    if [[ "$check_code" -ne 0 ]]; then
        overall_status=1
    fi
}

# Invoked indirectly by run_check so both build commands share one result/log.
# shellcheck disable=SC2329
build_local_collection() {
    local collection_version
    collection_version=$(python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["version"])') || return "$?"
    ansible-galaxy collection build --output-path ./build --force || return "$?"
    ansible-galaxy collection install "./build/brocade-fos-${collection_version}.tar.gz" \
        --collections-path "$test_collection_root/tests/output/installed_collections" --force --offline
}

# Default suites: add, edit, or remove run_check calls here.
# Each call needs a unique log name followed by the command and its arguments.
run_check lint_header_check ansible-test integration lint_header_check "${ansible_test_options[@]}"
run_check units ansible-test units "${ansible_test_options[@]}" --num-workers 1
run_check sanity ansible-test sanity "${ansible_test_options[@]}"

# Optional build checks use the same workspace and summary.
if [[ "$build_collection" == true || "$only_check" == collection_build ]]; then
    run_check collection_build build_local_collection
fi
if [[ "$build_docs" == true || "$only_check" == documentation_build ]]; then
    run_check documentation_build bash docs/build.sh
fi

if [[ "${#check_names[@]}" -eq 0 ]]; then
    printf 'No check matched "%s". Use a check name from the summary or Default suites block.\n' "$only_check" >&2
    exit 2
fi

printf '\nCheck summary\n'
for index in "${!check_names[@]}"; do
    check_status=PASS
    if [[ "${check_codes[$index]}" -ne 0 ]]; then
        check_status=FAIL
    fi
    printf '%-22s %-4s (exit %s)\n' "${check_names[$index]}" "$check_status" "${check_codes[$index]}"
done
printf '\nWorkspace retained: %s\nLogs: %s\n' "$test_collection_root" "$checks_log_dir"
if [[ -f "$test_collection_root/docs/build/html/index.html" ]]; then
    printf 'Documentation: %s/docs/build/html/index.html\n' "$test_collection_root"
fi
if [[ "$overall_status" -ne 0 ]]; then
    printf '\nRerun failed checks individually using your current source files:\n'
    for index in "${!check_names[@]}"; do
        if [[ "${check_codes[$index]}" -ne 0 ]]; then
            printf '  '
            printf '%q ' "$checks_script_dir/run_checks.sh" --only "${check_names[$index]}"
            printf '\n'
        fi
    done
fi
exit "$overall_status"
