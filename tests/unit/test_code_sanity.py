# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

"""Regression tests for complete header validation and repair."""

import importlib.util
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def code_sanity():
    path = Path(__file__).resolve().parents[1] / "sanity" / "code_sanity.py"
    spec = importlib.util.spec_from_file_location("code_sanity", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def header():
    return (
        f"# Copyright 2019-{datetime.now().year} Broadcom. All rights reserved.\n"
        "# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries\n"
        "# GNU General Public License v3.0+ "
        "(see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause\n"
        "# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause\n"
    )


@pytest.mark.parametrize(
    ("filename", "preamble"),
    [
        ("module.py", ""),
        ("module.py", "#!/usr/bin/python\n"),
        ("module.py", "# -*- coding: utf-8 -*-\n"),
        ("module.py", "#!/usr/bin/python\n# -*- coding: utf-8 -*-\n"),
        ("playbook.yml", ""),
        ("playbook.yaml", "---\n"),
        ("playbook.yml", "--- # document start\n"),
    ],
)
def test_complete_header_passes_without_rewriting(code_sanity, header, tmp_path, filename, preamble):
    path = tmp_path / filename
    original = (preamble + header + "\n# Other comments stay intact.\n").encode()
    path.write_bytes(original)

    assert code_sanity.run_copyright_check(tmp_path, [Path(filename)]) == ([], 0)
    assert code_sanity.run_copyright_check(tmp_path, [Path(filename)], fix=True) == ([], 0)
    assert path.read_bytes() == original


@pytest.mark.parametrize("missing_line", range(4))
def test_each_header_line_is_required_and_repaired(code_sanity, header, tmp_path, missing_line):
    path = tmp_path / "module.py"
    incomplete = header.splitlines(keepends=True)
    del incomplete[missing_line]
    body = '\nVALUE = "Copyright 2019-2020 Broadcom"\n'
    original = "#!/usr/bin/python\n" + "".join(incomplete) + body
    path.write_text(original)

    violations, rc = code_sanity.run_copyright_check(tmp_path, [path])
    assert rc == 1
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "Error"
    assert path.read_text() == original

    fixes, rc = code_sanity.run_copyright_check(tmp_path, [path], fix=True)
    assert rc == 0
    assert len(fixes) == 1
    assert fixes[0]["violation_type"] == "Fixed"
    assert path.read_text() == "#!/usr/bin/python\n" + header + body
    assert code_sanity.run_copyright_check(tmp_path, [path]) == ([], 0)
    assert code_sanity.run_copyright_check(tmp_path, [path], fix=True) == ([], 0)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("All rights reserved.", ""),
        ("and/or its subsidiaries", "and its subsidiaries"),
        ("GNU General Public License v3.0+", "GNU General Public License v2.0"),
        ("GPL-3.0-or-later AND BSD-2-Clause", "GPL-3.0-or-later OR BSD-2-Clause"),
        ("GPL-3.0-or-later AND BSD-2-Clause", "GPL-3.0-or-later"),
    ],
)
def test_wrong_header_contents_fail_and_are_replaced(code_sanity, header, tmp_path, old, new):
    path = tmp_path / "module.py"
    body = "\nVALUE = 1\n"
    path.write_text(header.replace(old, new) + body)

    violations, rc = code_sanity.run_copyright_check(tmp_path, [path])
    assert rc == 1
    assert violations[0]["violation"] == "copyright[incomplete]"
    assert code_sanity.run_copyright_check(tmp_path, [path], fix=True)[1] == 0
    assert path.read_text() == header + body


def test_outdated_copyright_and_partial_header_are_fixed_together(code_sanity, header, tmp_path):
    path = tmp_path / "playbook.yml"
    partial = "\n".join(header.splitlines()[:2]) + "\n"
    partial = partial.replace(str(datetime.now().year), str(datetime.now().year - 1))
    path.write_text("---\n" + partial + "\n- hosts: all\n")

    violations, rc = code_sanity.run_copyright_check(tmp_path, [path])
    assert rc == 1
    assert violations[0]["violation"] == "copyright[outdated]"
    assert code_sanity.run_copyright_check(tmp_path, [path], fix=True)[1] == 0
    assert path.read_text() == "---\n" + header + "\n- hosts: all\n"


@pytest.mark.parametrize("broadcom_first", [False, True])
def test_repair_preserves_third_party_notices(code_sanity, header, tmp_path, broadcom_first):
    path = tmp_path / "module.py"
    foreign = (
        "# Copyright (c) Ansible Project\n"
        "# GNU General Public License v3.0+ (see COPYING)\n"
        "# SPDX-License-Identifier: GPL-3.0-or-later\n"
    )
    incomplete = "\n".join(header.splitlines()[:2]) + "\n"
    body = '\nVALUE = "unchanged"\n'
    comments = incomplete + "\n" + foreign if broadcom_first else foreign + "\n" + incomplete
    path.write_text(comments + body)

    assert code_sanity.run_copyright_check(tmp_path, [path], fix=True)[1] == 0
    repaired = path.read_text()
    assert repaired.startswith(header)
    assert foreign in repaired
    assert repaired.endswith(body)
    assert repaired.count("Copyright 2019-") == 1
    assert code_sanity.run_copyright_check(tmp_path, [path]) == ([], 0)


@pytest.mark.parametrize(
    "body",
    [
        'EXAMPLE = """\n{header}"""\n',
        'VALUE = "unchanged"\n\n{header}',
    ],
)
def test_header_examples_in_body_do_not_satisfy_check(code_sanity, header, tmp_path, body):
    path = tmp_path / "module.py"
    body = body.format(header=header)
    path.write_text(body)

    violations, rc = code_sanity.run_copyright_check(tmp_path, [path])
    assert rc == 1
    assert violations[0]["violation"] == "copyright[missing]"
    assert code_sanity.run_copyright_check(tmp_path, [path], fix=True)[1] == 0
    assert path.read_text() == header + "\n" + body


def test_repair_preserves_crlf_and_file_mode(code_sanity, header, tmp_path):
    path = tmp_path / "module.py"
    original = "#!/usr/bin/python\n" + header.splitlines()[0] + "\n\nVALUE = 1\n"
    path.write_bytes(original.replace("\n", "\r\n").encode())
    path.chmod(0o755)

    assert code_sanity.run_copyright_check(tmp_path, [path], fix=True)[1] == 0
    expected = "#!/usr/bin/python\n" + header + "\nVALUE = 1\n"
    assert path.read_bytes() == expected.replace("\n", "\r\n").encode()
    assert path.stat().st_mode & 0o777 == 0o755
    assert code_sanity.run_copyright_check(tmp_path, [path]) == ([], 0)


@pytest.mark.parametrize("filename", ["LICENSE", "COPYING", "LICENSES/BSD-2-Clause.txt", "guide.rst"])
def test_excluded_files_remain_untouched(code_sanity, tmp_path, filename):
    path = tmp_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Original license or documentation text.\n")

    violations, rc = code_sanity.run_copyright_check(tmp_path, [path])
    assert rc == 0
    assert violations[0]["violation"] == "copyright[excluded]"
    assert code_sanity.run_copyright_check(tmp_path, [path], fix=True) == ([], 0)
    assert path.read_text() == "Original license or documentation text.\n"


@pytest.mark.parametrize("fix", [False, True])
def test_read_errors_fail_in_both_modes(code_sanity, tmp_path, fix):
    violations, rc = code_sanity.run_copyright_check(tmp_path, [Path("missing.py")], fix=fix)
    assert rc == 1
    assert violations[0]["violation"] == "copyright[read_error]"
