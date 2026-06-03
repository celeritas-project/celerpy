# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

from celerpy.model import input as minput
from celerpy.model import output as moutput
from celerpy.model import types as mtypes


def test_enum_lowercase():
    # NOTE: no deprecation warning issued :'(
    result = mtypes.GeometryEngine.geant4
    assert result == mtypes.GeometryEngine.GEANT4

    assert mtypes.GeometryEngine("geant4") == mtypes.GeometryEngine.GEANT4


def test_model_setup(tmp_path: Path):
    gdml_file = tmp_path / "foo.gdml"
    gdml_file.write_text("<gdml />")
    inp_json = json.dumps(
        {
            "geometry_file": str(gdml_file),
        }
    )
    ms = minput.ModelSetup.model_validate_json(inp_json)
    assert gdml_file == ms.geometry_file


def test_image_input():
    ii = minput.ImageInput(
        lower_left=[-1, 0, 0], upper_right=[1, 1, 0], vertical_pixels=1024
    )
    assert ii == minput.ImageInput.model_construct(
        lower_left=[-1.0, 0.0, 0.0],
        upper_right=[1.0, 1.0, 0.0],
        rightward=[1, 0, 0],
        vertical_pixels=1024,
        horizontal_divisor=None,
    )


def test_orange_stats_serialization():
    os = minput.OrangeStats()
    result = json.loads(os.model_dump_json())
    assert result == {"_cmd": "orange_stats"}


def test_orange_output():
    # See UniversesTest
    result = moutput.OrangeParamsOutput.model_validate_json(
        '{"_category":"internal","_label":"orange","bih_metadata":{"depth":[4,3,1],"num_finite_bboxes":[4,4,1],"num_infinite_bboxes":[1,0,0]},"scalars":{"num_univ_levels":3,"max_faces":14,"max_intersections":14,"tol":{"abs":1.5e-08,"rel":1.5e-08}},"sizes":{"bih":{"bboxes":12,"internal_nodes":6,"leaf_nodes":9,"local_volume_ids":10},"connectivity_records":25,"daughters":3,"local_surface_ids":55,"local_volume_ids":21,"logic_ints":164,"obz_records":0,"real_ids":25,"reals":24,"rect_arrays":0,"simple_units":3,"surface_types":25,"transforms":3,"universe_indexer":{"surfaces":4,"volumes":4},"univ_indices":3,"univ_types":3,"volume_ids":12,"volume_instance_ids":12,"volume_records":12},"tracking_logic":"infix"}'
    )
    assert result == moutput.OrangeParamsOutput(
        scalars=moutput.OrangeScalars(
            num_univ_levels=3,
            max_faces=14,
            max_intersections=14,
            max_csg_levels=None,
            tol=moutput.Tolerance(rel=1.5e-08, abs=1.5e-08),
        ),
        sizes={
            "bih": {
                "bboxes": 12,
                "internal_nodes": 6,
                "leaf_nodes": 9,
                "local_volume_ids": 10,
            },
            "connectivity_records": 25,
            "daughters": 3,
            "local_surface_ids": 55,
            "local_volume_ids": 21,
            "logic_ints": 164,
            "obz_records": 0,
            "real_ids": 25,
            "reals": 24,
            "rect_arrays": 0,
            "simple_units": 3,
            "surface_types": 25,
            "transforms": 3,
            "universe_indexer": {"surfaces": 4, "volumes": 4},
            "univ_indices": 3,
            "univ_types": 3,
            "volume_ids": 12,
            "volume_instance_ids": 12,
            "volume_records": 12,
        },
        bih_metadata=moutput.BihMetadata(
            num_finite_bboxes=[4, 4, 1],
            num_infinite_bboxes=[1, 0, 0],
            depth=[4, 3, 1],
            structure=None,
        ),
        tracking_logic=moutput.LogicNotation.INFIX,
    )
