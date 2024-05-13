# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

# from matplotlib import pyplot as plt
import numpy as np
import pytest
from celerpy import visualize, model
from numpy.testing import assert_array_equal

from pathlib import Path

from celerpy.settings import settings

local_path = Path(__file__).parent
settings.prefix_path = local_path / "mock-prefix"


def test_CelerGeo():
    inp = local_path / "data" / "two-boxes.gdml"
    with visualize.CelerGeo.from_filename(inp) as cg:
        with pytest.raises(RuntimeError):
            cg.trace()
        (result, img) = cg.trace(
            model.ImageInput(upper_right=[1, 1, 0], vertical_pixels=4),
            geometry=model.GeometryEngine.orange,
        )
        assert isinstance(result, model.TraceOutput)
        assert len(img) == 16 * result.sizeof_int
        (result, img) = cg.trace(geometry=model.GeometryEngine.orange)
        assert isinstance(result, model.TraceOutput)
        assert len(img) == 16 * result.sizeof_int
        (result, img) = cg.trace(geometry=model.GeometryEngine.geant4)
        assert isinstance(result, model.TraceOutput)
        assert len(img) == 16 * result.sizeof_int
        result = cg.close()
        assert result


def test_ReverseIndexDict():
    to_volume = []
    to_id = visualize.ReverseIndexDict(to_volume)

    assert to_id["foo"] == 0
    assert to_id["bar"] == 1
    assert to_id["baz"] == 2
    assert to_id["foo"] == 0
    assert to_volume == ["foo", "bar", "baz"]


def test_IdMapper():
    map_ids = visualize.IdMapper()
    (img, vol) = map_ids(np.array([1, 1, 1]), ["foo", "bar"])
    assert_array_equal(img, np.array([0, 0, 0]))
    assert vol == ["bar"]

    (img, vol) = map_ids(np.array([1, 2, 1]), ["foo", "baz", "bar"])
    assert_array_equal(img, np.array([1, 0, 1]))
    assert vol == ["bar", "baz"]

    (img, vol) = map_ids(np.array([0, 1, 2]), ["bar", "foo", "baz"])
    assert_array_equal(img, np.array([0, 2, 1]))
    assert vol == ["bar", "baz", "foo"]

    (img, vol) = map_ids(np.array([-1, 0, -1]), ["foo"])
    assert_array_equal(img, np.array([2, 2, 2]))
    assert_array_equal(img.mask, [True, False, True])
    assert vol == ["bar", "baz", "foo"]
