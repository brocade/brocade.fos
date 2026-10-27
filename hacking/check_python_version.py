#!/usr/bin/env python
# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

"""Verify the pinned Python version and print major.minor for ansible-test."""

import platform
import re
import sys
from pathlib import Path


def main() -> int:
    version_file = Path(__file__).resolve().parents[1] / ".python-version"
    try:
        expected = version_file.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as error:
        print(f"Cannot read {version_file}: {error}", file=sys.stderr)
        return 1

    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", expected):
        print(f"{version_file} must contain one MAJOR.MINOR.PATCH version.", file=sys.stderr)
        return 1

    actual = platform.python_version()
    if actual != expected:
        print(f"Use Python {expected}; the current interpreter is Python {actual}.", file=sys.stderr)
        return 1

    print(expected.rsplit(".", 1)[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
