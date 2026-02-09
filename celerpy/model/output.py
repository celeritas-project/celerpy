# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Output models for results from Celeritas."""

from typing import Literal, Optional

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

from .input import TraceSetup
from .types import LogicNotation, Real3, Size2, Tolerance, UnitSystem, _Model


# geocel/rasterize/ImageData.hh: ImageParamsScalars
class ImageParams(_Model):
    origin: Real3
    "Upper left point of the image"

    down: Real3
    "Direction vector rendered as 'downward' in the image"

    right: Real3
    "Direction vector rendered as 'rightward' in the image"

    pixel_width: PositiveFloat
    "Physical size of a pixel in the image"

    dims: Size2
    "Image dimensions (width, height) in pixels"

    units: UnitSystem = Field(alias="_units")

    # TODO: max length is not used or returned by celer-geo
    # max_length: float


# ad hoc: result from a 'trace' command
class TraceOutput(_Model):
    trace: TraceSetup
    image: ImageParams
    volumes: Optional[list[str]] = None
    sizeof_int: PositiveInt


# orange/OrangeData.hh
class OrangeScalars(_Model):
    """Scalar properties of an ORANGE geometry."""

    num_univ_levels: NonNegativeInt
    "Maximum universe nesting depth"

    max_faces: NonNegativeInt
    "Maximum number of faces intersecting a surface"

    max_intersections: NonNegativeInt
    "Maximum number of surface intersections along a ray"

    max_csg_levels: NonNegativeInt
    "Maximum CSG logic tree depth"

    tol: Tolerance
    "Construction and tracking tolerance"


# orange/OrangeParamsOutput.hh
class BihSizes(_Model):
    """Bounding Interval Hierarchy tree sizes."""

    bboxes: NonNegativeInt
    inner_nodes: NonNegativeInt
    leaf_nodes: NonNegativeInt
    local_volume_ids: NonNegativeInt


# orange/OrangeParamsOutput.hh
class BihMetadata(_Model):
    """Bounding Interval Hierarchy characteristics."""

    num_finite_bboxes: list[NonNegativeInt]
    num_infinite_bboxes: list[NonNegativeInt]
    depth: list[NonNegativeInt]


# orange/OrangeParamsOutput.hh
class UniverseIndexerSizes(_Model):
    """Universe indexer sizes."""

    surfaces: NonNegativeInt
    volumes: NonNegativeInt


# orange/OrangeParamsOutput.hh
class OrangeSizes(_Model):
    """Size properties of an ORANGE geometry."""

    connectivity_records: NonNegativeInt
    daughters: NonNegativeInt
    fast_real3s: NonNegativeInt
    local_surface_ids: NonNegativeInt
    local_volume_ids: NonNegativeInt
    logic_ints: NonNegativeInt
    obz_records: NonNegativeInt
    real_ids: NonNegativeInt
    reals: NonNegativeInt
    rect_arrays: NonNegativeInt
    simple_units: NonNegativeInt
    surface_types: NonNegativeInt
    transforms: NonNegativeInt
    univ_indices: NonNegativeInt
    univ_types: NonNegativeInt
    volume_ids: NonNegativeInt
    volume_instance_ids: NonNegativeInt
    volume_records: NonNegativeInt

    bih: BihSizes
    universe_indexer: UniverseIndexerSizes


# orange/OrangeParamsOutput.hh
class OrangeParamsOutput(_Model):
    """ORANGE geometry data structure sizes and scalars."""

    _category: Literal["internal"]
    _label: Literal["orange"]
    scalars: OrangeScalars
    sizes: OrangeSizes
    bih_metadata: BihMetadata
    tracking_logic: LogicNotation


class ExceptionDump(_Model):
    """Output of an exception message when a Celeritas app fails"""

    # Output wrapper
    _category: Literal["result"]
    _label: Literal["exception"]

    # corecel/io/ExceptionOutput.cc
    type: str
    context: Optional["ExceptionDump"] = None

    # corecel/AssertIO.json.cc
    what: Optional[str]
    which: str
    condition: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None
