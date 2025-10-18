# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

from celerpy import model


def test_enum_lowercase():
    # NOTE: no deprecation warning issued :'(
    result = model.GeometryEngine.geant4
    assert result == model.GeometryEngine.GEANT4

    assert model.GeometryEngine("geant4") == model.GeometryEngine.GEANT4


def test_model_setup(tmp_path: Path):
    gdml_file = tmp_path / "foo.gdml"
    gdml_file.write_text("<gdml />")
    inp_json = json.dumps(
        {
            "geometry_file": str(gdml_file),
        }
    )
    ms = model.ModelSetup.model_validate_json(inp_json)
    assert gdml_file == ms.geometry_file


def test_image_input():
    ii = model.ImageInput(
        lower_left=[-1, 0, 0], upper_right=[1, 1, 0], vertical_pixels=1024
    )
    assert ii == model.ImageInput.model_construct(
        lower_left=[-1.0, 0.0, 0.0],
        upper_right=[1.0, 1.0, 0.0],
        rightward=[1, 0, 0],
        vertical_pixels=1024,
        horizontal_divisor=None,
    )


def test_orange_stats_serialization():
    os = model.OrangeStats()
    result = json.loads(os.model_dump_json())
    assert result == {"_cmd": "orange_stats"}


def test_bih_load():
    result = model.BihSizes.model_validate_json(
        '{"bboxes":8,"inner_nodes":0,"leaf_nodes":1,"local_volume_ids":7}'
    )
    assert result == model.BihSizes(
        bboxes=8, inner_nodes=0, leaf_nodes=1, local_volume_ids=7
    )
