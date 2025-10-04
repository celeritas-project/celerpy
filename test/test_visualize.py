# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from celerpy import model, visualize
from celerpy.settings import LogLevel, settings

local_path = Path(__file__).parent
settings.prefix_path = local_path / "mock-prefix"

settings.prefix_path = Path(__file__).parent / "mock-prefix"
settings.log = LogLevel.debug
settings.log_local = LogLevel.warning
settings.g4org_verbose = True


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
        assert img.shape == (4, 4)
        assert img.dtype == np.int32
        (result, img) = cg.trace(geometry=model.GeometryEngine.orange)
        assert isinstance(result, model.TraceOutput)
        assert img.shape == (4, 4)
        (result, img) = cg.trace(geometry=model.GeometryEngine.geant4)
        assert isinstance(result, model.TraceOutput)
        assert img.shape == (4, 4)
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


def test_centered_image():
    centered_image = visualize.centered_image
    kwargs = dict()

    # Test case 1: Square image with x projection along -y
    result = centered_image(
        center=[0, 0, 0], xdir=[0, -1, 0], outdir=[0, 0, 1], width=2.0, **kwargs
    )
    assert result.lower_left == [-1.0, 1.0, 0.0]
    assert result.upper_right == [1.0, -1.0, 0.0]
    assert result.rightward == [0.0, -1.0, 0.0]

    # Test case 2: Rectangle image with xdir = [1, 0, 0]
    result = centered_image(
        center=[1, 0, 0],
        xdir=[1, 0, 0],
        outdir=[0, 0, -1],
        width=(2.0, 4.0),
        **kwargs,
    )
    assert result.lower_left == [0.0, 2.0, 0.0]
    assert result.upper_right == [2.0, -2.0, 0.0]
