import os
import subprocess
from pathlib import Path

import pytest

# Hardcoded locations relative to this file
THIS_DIR = Path(__file__).parent
SCRIPT_PATH = (THIS_DIR.parent / "run.sh").resolve()
MOCK_PATH = (THIS_DIR / "mocks").resolve()


def build_body(pr_nums):
    lines = ["intro", "```yaml", "pull_requests:"]
    lines += [f"  - number: {n}" for n in pr_nums]
    lines += ["```", "outro"]
    return "\n".join(lines)


def print_stdx(proc):
    # Print captured output to help debugging
    print(f"EXIT CODE: {proc.returncode}")
    print("------ STDOUT ------")
    print(proc.stdout or "<empty>")
    print("------ STDERR ------")
    print(proc.stderr or "<empty>")
    print("--------------------")


@pytest.mark.parametrize(
    "prs,addl,ltc,expected",
    [
        pytest.param([101], None, None, "bug,backport", id="ONE|no-addl|copy=ALL"),
        pytest.param(
            [101], "EXTRA", None, "EXTRA,bug,backport", id="ONE|addl=EXTRA|copy=ALL"
        ),
        pytest.param(
            [101], None, "backport", "backport", id="ONE|no-addl|copy=backport"
        ),
        pytest.param(
            [101],
            "EXTRA",
            "backport",
            "EXTRA,backport",
            id="ONE|addl=EXTRA|copy=backport",
        ),
        pytest.param(
            [101],
            None,
            "backport,bar,zzz",
            "backport",
            id="ONE|no-addl|copy=backport,bar,zzz",
        ),
        pytest.param(
            [101],
            "EXTRA",
            "backport,bar,zzz",
            "EXTRA,backport",
            id="ONE|addl=EXTRA|copy=backport,bar,zzz",
        ),
        pytest.param(
            [101, 202, 303],
            None,
            None,
            "bug,backport,docs,bar",
            id="THREE|no-addl|copy=ALL",
        ),
        pytest.param(
            [101, 202, 303],
            "EXTRA",
            None,
            "EXTRA,bug,backport,docs,bar",
            id="THREE|addl=EXTRA|copy=ALL",
        ),
        pytest.param(
            [101, 202, 303],
            None,
            "backport",
            "backport",
            id="THREE|no-addl|copy=backport",
        ),
        pytest.param(
            [101, 202, 303],
            "EXTRA",
            "backport",
            "EXTRA,backport",
            id="THREE|addl=EXTRA|copy=backport",
        ),
        pytest.param(
            [101, 202, 303],
            None,
            "backport,bar,zzz",
            "backport,bar",
            id="THREE|no-addl|copy=backport,bar,zzz",
        ),
        pytest.param(
            [101, 202, 303],
            "EXTRA",
            "backport,bar,zzz",
            "EXTRA,backport,bar",
            id="THREE|addl=EXTRA|copy=backport,bar,zzz",
        ),
    ],
)
def test_matrix(prs, addl, ltc, expected, monkeypatch, tmp_path):
    workdir = Path(tmp_path)
    logfile = workdir / "gh_calls.log"
    logfile.write_text("", encoding="utf-8")

    monkeypatch.setenv("PATH", f"{MOCK_PATH}:{os.environ.get('PATH', '')}")
    monkeypatch.setenv("MERGE_QUEUE_PR_URL", "https://example.com/repo/pull/9999")
    monkeypatch.setenv("REPOSITORY_URL", "https://example.com/repo")
    monkeypatch.setenv("MOCK_LOG_FILE", str(logfile))
    monkeypatch.setenv("MERGE_QUEUE_PR_BODY", build_body(prs))

    if addl is not None:
        monkeypatch.setenv("ADDITIONAL_LABELS", addl)

    if ltc is not None:
        monkeypatch.setenv("LABELS_TO_COPY", ltc)

    proc = subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd(),
        text=True,
    )

    if proc.returncode != 0:
        print_stdx(proc)

    assert proc.returncode == 0

    edits = [ln for ln in logfile.read_text().splitlines() if ln.startswith("EDIT|")]
    got = edits[-1].split("LABELS=", 1)[1] if edits else ""

    if got != expected:
        print_stdx(proc)

    assert got == expected
