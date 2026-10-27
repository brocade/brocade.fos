# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

"""Regression tests for the lint/header runner and header validation and repair."""

import importlib.util
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def lint_header_check():
    path = Path(__file__).resolve().parents[1] / "sanity" / "lint_header_check.py"
    spec = importlib.util.spec_from_file_location("lint_header_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def lint_match():
    return {
        "check_name": "yaml[trailing-spaces]",
        "description": "Trailing spaces",
        "severity": "major",
        "location": {"path": "playbook.yml", "lines": {"begin": 1}},
    }


@pytest.fixture
def lint_process(*, lint_header_check, monkeypatch):
    def set_result(*, returncode, stdout="[]", stderr=""):
        result = subprocess.CompletedProcess(["ansible-lint"], returncode, stdout, stderr)
        monkeypatch.setattr(lint_header_check.subprocess, "run", lambda *args, **kwargs: result)

    return set_result


@pytest.fixture
def runner_repo(*, lint_header_check, monkeypatch, tmp_path, header):
    (tmp_path / "galaxy.yml").write_text(header + "namespace: brocade\nname: fos\nversion: 3.0.0\n")
    (tmp_path / ".ansible-lint").write_text("{}\n")
    monkeypatch.setattr(lint_header_check, "find_repo_root", lambda *, start: tmp_path)
    monkeypatch.setattr(lint_header_check, "setup_logging", lambda *, verbose=False: logging.getLogger(__name__))
    monkeypatch.setattr(lint_header_check, "check_dependencies", lambda *, log: {"python": "python"})
    return tmp_path


@pytest.mark.parametrize("git_metadata", [None, "directory", "file"])
def test_find_repo_root_accepts_collection_copies(*, lint_header_check, tmp_path, git_metadata):
    (tmp_path / "galaxy.yml").write_text("namespace: brocade\nname: fos\n")
    if git_metadata == "directory":
        (tmp_path / ".git").mkdir()
    elif git_metadata == "file":
        (tmp_path / ".git").write_text("gitdir: /unused/worktree\n")
    nested = tmp_path / "tests" / "integration" / "targets"
    nested.mkdir(parents=True)

    assert lint_header_check.find_repo_root(start=nested) == tmp_path


def test_cli_rejects_missing_collection_metadata(*, lint_header_check, runner_repo, monkeypatch, caplog):
    (runner_repo / "galaxy.yml").unlink()
    monkeypatch.setattr(lint_header_check.sys, "argv", ["lint_header_check.py"])

    assert lint_header_check.main() == 2
    assert "galaxy.yml is required" in caplog.text


@pytest.mark.parametrize("fix", [False, True])
@pytest.mark.parametrize("requested_path", [None, ".", "playbooks", "changelogs", "changelogs/changelog.yaml"])
def test_ansible_lint_cli_discovery_and_explicit_paths(
    *, lint_header_check, runner_repo, header, monkeypatch, fix, requested_path
):
    (runner_repo / ".ansible-lint").write_text("exclude_paths:\n  - changelogs/\n")
    files = [Path("changelogs/changelog.yaml"), Path("playbooks/main.yml"), Path("changelogs_extra/keep.yml")]
    for path in files:
        target = runner_repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(header + "\n- hosts: all\n")
    args = ["lint_header_check.py"] + (["--fix"] if fix else [])
    if requested_path:
        args.extend(["--path", str(runner_repo / requested_path)])
    monkeypatch.setattr(lint_header_check.sys, "argv", args)

    lint_calls = []

    def run_lint(cmd, **kwargs):
        assert cmd[cmd.index("-c") + 1] == str(runner_repo / ".ansible-lint")
        assert kwargs["cwd"] == runner_repo
        paths = {Path(arg).relative_to(runner_repo) for arg in cmd if arg.endswith((".yaml", ".yml"))}
        lint_calls.append(("--fix" in cmd, paths))
        return subprocess.CompletedProcess(cmd, 0, "[]", "")

    monkeypatch.setattr(lint_header_check.subprocess, "run", run_lint)
    header_calls = []
    real_header_check = lint_header_check.run_copyright_check

    def check_headers(*, repo_root, files, fix=False):
        header_calls.append((fix, set(files)))
        return real_header_check(repo_root=repo_root, files=files, fix=fix)

    monkeypatch.setattr(lint_header_check, "run_copyright_check", check_headers)

    assert lint_header_check.main() == 0
    passes = [True, False] if fix else [False]
    if requested_path in ("changelogs", "changelogs/changelog.yaml"):
        expected_lint = set()
        expected_headers = {files[0]}
    elif requested_path == "playbooks":
        expected_lint = expected_headers = {files[1]}
    else:
        expected_lint = set(files[1:]) | {Path("galaxy.yml")} if requested_path else set()
        expected_headers = set(files) | {Path("galaxy.yml")}
    expected_calls = [(mode, expected_lint) for mode in passes] if requested_path is None or expected_lint else []
    assert lint_calls == expected_calls
    assert header_calls == [(mode, expected_headers) for mode in passes]


@pytest.mark.parametrize("has_python_file", [False, True])
def test_ansible_lint_discovers_without_collected_yaml(*, lint_header_check, runner_repo, monkeypatch, has_python_file):
    if has_python_file:
        (runner_repo / "module.py").write_text("VALUE = 1\n")
    monkeypatch.setattr(lint_header_check.sys, "argv", ["lint_header_check.py", "--checks", "ansible-lint"])
    calls = []

    def run_lint(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "[]", "")

    monkeypatch.setattr(lint_header_check.subprocess, "run", run_lint)
    assert lint_header_check.main() == 0
    assert len(calls) == 1
    assert calls[0][0] == "ansible-lint"
    assert not any(arg.endswith((".py", ".yml", ".yaml")) for arg in calls[0])


@pytest.mark.parametrize("output_format", ["list", "matches", "files"])
def test_ansible_lint_violations_are_not_tool_errors(
    *, lint_header_check, lint_match, lint_process, tmp_path, output_format
):
    output = [lint_match]
    if output_format == "matches":
        output = {"matches": output}
    elif output_format == "files":
        output = {"files": {"playbook.yml": {"matches": output}}}
    lint_process(returncode=2, stdout=json.dumps(output))

    violations, rc = lint_header_check.run_ansible_lint(
        repo=tmp_path, files=[Path("playbook.yml")], fix=False, verbose=False
    )

    assert rc == 1
    assert len(violations) == 1
    assert violations[0]["violation"] == "yaml[trailing-spaces]"
    assert violations[0]["file_path"] == "playbook.yml"
    assert violations[0]["line"] == 1
    summary, rc = lint_header_check.generate_summary_log(
        ruff_violations=[],
        ruff_rc=0,
        run_ruff_check=False,
        ansible_violations=violations,
        ansible_rc=rc,
        run_ansible_lint_check=True,
        copyright_violations=[],
        copyright_rc=0,
        run_copyright=False,
    )
    assert rc == 1
    assert "FAIL" in summary
    assert "Ansible-lint exited with non-zero status" not in summary


@pytest.mark.parametrize("fix", [False, True])
@pytest.mark.parametrize("returncode", [1, 3, 5, 130])
def test_ansible_lint_tool_failures_remain_errors(
    *, lint_header_check, lint_process, tmp_path, caplog, fix, returncode
):
    lint_process(returncode=returncode, stderr="tool failure details")

    assert lint_header_check.run_ansible_lint(repo=tmp_path, files=[Path("playbook.yml")], fix=fix, verbose=False) == (
        [],
        2,
    )
    assert "tool failure details" in caplog.text


@pytest.mark.parametrize(
    ("returncode", "stdout"),
    [
        (0, "not JSON"),
        (2, "not JSON"),
        (0, ""),
        (2, ""),
        (0, "{}"),
        (0, '["not a violation object"]'),
        (0, '{"matches": {}}'),
        (2, "[]"),
    ],
)
def test_ansible_lint_unreadable_results_fail(*, lint_header_check, lint_process, tmp_path, caplog, returncode, stdout):
    lint_process(returncode=returncode, stdout=stdout)

    result = lint_header_check.run_ansible_lint(repo=tmp_path, files=[Path("playbook.yml")], fix=False, verbose=False)
    assert result == ([], 2)
    assert "Cannot read ansible-lint results" in caplog.text


@pytest.mark.parametrize("error", [FileNotFoundError(), subprocess.TimeoutExpired("ansible-lint", 300)])
def test_ansible_lint_execution_errors_fail(*, lint_header_check, monkeypatch, tmp_path, error):
    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(lint_header_check.subprocess, "run", fail)
    result = lint_header_check.run_ansible_lint(repo=tmp_path, files=[Path("playbook.yml")], fix=False, verbose=False)
    assert result == ([], 2)


def test_ansible_lint_fixed_exit_code_only_succeeds_in_fix_mode(
    *, lint_header_check, lint_match, lint_process, tmp_path
):
    lint_match["status"] = "fixed"
    lint_process(returncode=8, stdout=json.dumps([lint_match]))

    fixes, rc = lint_header_check.run_ansible_lint(repo=tmp_path, files=[Path("playbook.yml")], fix=True, verbose=False)
    assert rc == 0
    assert len(fixes) == 1
    result = lint_header_check.run_ansible_lint(repo=tmp_path, files=[Path("playbook.yml")], fix=False, verbose=False)
    assert result == ([], 2)


@pytest.mark.parametrize("fix", [False, True])
@pytest.mark.parametrize(
    ("returncode", "severity", "expected_rc"),
    [(0, None, 0), (0, "minor", 0), (2, "major", 1), (2, "minor", 1), (3, None, 2)],
)
def test_ansible_lint_cli_exit_codes(
    *, lint_header_check, lint_match, lint_process, monkeypatch, tmp_path, fix, returncode, severity, expected_rc
):
    (tmp_path / "galaxy.yml").write_text("namespace: brocade\nname: fos\nversion: 3.0.0\n")
    (tmp_path / ".ansible-lint").write_text("{}\n")
    (tmp_path / "playbook.yml").write_text("- hosts: all\n")
    monkeypatch.setattr(lint_header_check, "find_repo_root", lambda *, start: tmp_path)
    monkeypatch.setattr(lint_header_check, "setup_logging", lambda *, verbose=False: logging.getLogger(__name__))
    monkeypatch.setattr(lint_header_check, "check_dependencies", lambda *, log: {"python": "python"})
    args = ["lint_header_check.py", "--checks", "ansible-lint"] + (["--fix"] if fix else [])
    monkeypatch.setattr(lint_header_check.sys, "argv", args)
    if severity:
        lint_match["severity"] = severity
    lint_process(returncode=returncode, stdout=json.dumps([lint_match] if severity else []))

    assert lint_header_check.main() == expected_rc


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
def test_complete_header_passes_without_rewriting(*, lint_header_check, header, tmp_path, filename, preamble):
    path = tmp_path / filename
    original = (preamble + header + "\n# Other comments stay intact.\n").encode()
    path.write_bytes(original)

    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[Path(filename)]) == ([], 0)
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[Path(filename)], fix=True) == ([], 0)
    assert path.read_bytes() == original


@pytest.mark.parametrize("missing_line", range(4))
def test_each_header_line_is_required_and_repaired(*, lint_header_check, header, tmp_path, missing_line):
    path = tmp_path / "module.py"
    incomplete = header.splitlines(keepends=True)
    del incomplete[missing_line]
    body = '\nVALUE = "Copyright 2019-2020 Broadcom"\n'
    original = "#!/usr/bin/python\n" + "".join(incomplete) + body
    path.write_text(original)

    violations, rc = lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path])
    assert rc == 1
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "Error"
    assert path.read_text() == original

    fixes, rc = lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True)
    assert rc == 0
    assert len(fixes) == 1
    assert fixes[0]["violation_type"] == "Fixed"
    assert path.read_text() == "#!/usr/bin/python\n" + header + body
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path]) == ([], 0)
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True) == ([], 0)


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
def test_wrong_header_contents_fail_and_are_replaced(*, lint_header_check, header, tmp_path, old, new):
    path = tmp_path / "module.py"
    body = "\nVALUE = 1\n"
    path.write_text(header.replace(old, new) + body)

    violations, rc = lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path])
    assert rc == 1
    assert violations[0]["violation"] == "copyright[incomplete]"
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True)[1] == 0
    assert path.read_text() == header + body


def test_outdated_copyright_and_partial_header_are_fixed_together(*, lint_header_check, header, tmp_path):
    path = tmp_path / "playbook.yml"
    partial = "\n".join(header.splitlines()[:2]) + "\n"
    partial = partial.replace(str(datetime.now().year), str(datetime.now().year - 1))
    path.write_text("---\n" + partial + "\n- hosts: all\n")

    violations, rc = lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path])
    assert rc == 1
    assert violations[0]["violation"] == "copyright[outdated]"
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True)[1] == 0
    assert path.read_text() == "---\n" + header + "\n- hosts: all\n"


@pytest.mark.parametrize("broadcom_first", [False, True])
def test_repair_preserves_third_party_notices(*, lint_header_check, header, tmp_path, broadcom_first):
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

    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True)[1] == 0
    repaired = path.read_text()
    assert repaired.startswith(header)
    assert foreign in repaired
    assert repaired.endswith(body)
    assert repaired.count("Copyright 2019-") == 1
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path]) == ([], 0)


@pytest.mark.parametrize(
    "body",
    [
        'EXAMPLE = """\n{header}"""\n',
        'VALUE = "unchanged"\n\n{header}',
    ],
)
def test_header_examples_in_body_do_not_satisfy_check(*, lint_header_check, header, tmp_path, body):
    path = tmp_path / "module.py"
    body = body.format(header=header)
    path.write_text(body)

    violations, rc = lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path])
    assert rc == 1
    assert violations[0]["violation"] == "copyright[missing]"
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True)[1] == 0
    assert path.read_text() == header + "\n" + body


def test_repair_preserves_crlf_and_file_mode(*, lint_header_check, header, tmp_path):
    path = tmp_path / "module.py"
    original = "#!/usr/bin/python\n" + header.splitlines()[0] + "\n\nVALUE = 1\n"
    path.write_bytes(original.replace("\n", "\r\n").encode())
    path.chmod(0o755)

    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True)[1] == 0
    expected = "#!/usr/bin/python\n" + header + "\nVALUE = 1\n"
    assert path.read_bytes() == expected.replace("\n", "\r\n").encode()
    assert path.stat().st_mode & 0o777 == 0o755
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path]) == ([], 0)


@pytest.mark.parametrize("filename", ["LICENSE", "COPYING", "LICENSES/BSD-2-Clause.txt", "guide.rst"])
def test_excluded_files_remain_untouched(*, lint_header_check, tmp_path, filename):
    path = tmp_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Original license or documentation text.\n")

    violations, rc = lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path])
    assert rc == 0
    assert violations[0]["violation"] == "copyright[excluded]"
    assert lint_header_check.run_copyright_check(repo_root=tmp_path, files=[path], fix=True) == ([], 0)
    assert path.read_text() == "Original license or documentation text.\n"


@pytest.mark.parametrize("fix", [False, True])
def test_read_errors_fail_in_both_modes(*, lint_header_check, tmp_path, fix):
    violations, rc = lint_header_check.run_copyright_check(repo_root=tmp_path, files=[Path("missing.py")], fix=fix)
    assert rc == 1
    assert violations[0]["violation"] == "copyright[read_error]"
