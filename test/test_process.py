# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import json

from celerpy.settings import settings
from celerpy.process import launch, communicate

settings.prefix_path = Path(__file__).parent / "mock-prefix"


def communicate_json(process, inp):
    out = communicate(process, json.dumps(inp))
    if out:
        return json.loads(out)
    return None


def test_manual():
    p = launch("mock-process")
    result = communicate_json(p, "hello")
    assert result == "success"
    result = communicate_json(p, ["foo", "bar"])
    assert result == ["success", ["foo", "bar"]]
    result = communicate_json(p, None)
    assert result == "closing"
    p.wait(timeout=0.5)
    assert p.returncode == 0
    p.stdout.close()
    p.stdin.close()
    del p


def test_context():
    with launch("mock-process") as p:
        result = communicate_json(p, "hello")
        assert result == "success"
        result = communicate_json(p, ["foo", "bar"])
        assert result == ["success", ["foo", "bar"]]
        print("closing process")
        # NOTE: we don't explicitly tell the process to exit cleanly, so
        # when `input()` gets an EOFError due to the stdin pipe closing, the
        # process tries to write "closing" to `stdout`, but that pipe has
        # already been closed. I guess that also causes a BrokenPipeError in
        # the attached pipe in this process.
    print("closed process")


def test_abort():
    with launch("mock-process") as p:
        result = communicate_json(p, "hello")
        assert result == "success"
        result = communicate_json(p, "abort")
        assert result is None


def test_abort2():
    with launch("mock-process") as p:
        result = communicate_json(p, "hello")
        assert result == "success"
        p.terminate()
        result = communicate_json(p, "terminating")
