# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from celerpy.settings import settings

settings.prefix_path = Path(__file__).parent / "mock-prefix"


def test_mock_manual():
    from celerpy.process import Process

    p = Process("mock-process")
    assert not p.child.poll()
    result = p.communicate("hello")
    assert result == "success"
    result = p.communicate(["foo", "bar"])
    assert result == ["success", ["foo", "bar"]]
    result = p.close()
    assert result == "closing"


def test_mock_context():
    from celerpy.process import Process

    with Process("mock-process") as p:
        result = p.communicate("hello")
        assert result == "success"
        result = p.communicate(["foo", "bar"])
        assert result == ["success", ["foo", "bar"]]


def test_mock_abort():
    from celerpy.process import Process

    with Process("mock-process") as p:
        result = p.communicate("hello")
        assert result == "success"
        result = p.communicate("abort")
        assert result is None
