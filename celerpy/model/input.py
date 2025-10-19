# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Input models for commands and configuration with Celeritas."""

from enum import StrEnum, auto
from typing import Literal, Optional

from pydantic import FilePath, NonNegativeInt, PositiveFloat, PositiveInt
from pydantic_core import to_json

from .types import (
    GeometryEngine,
    MemSpace,
    Real3,
    Tolerance,
    _Model,
)


# orange/g4org/Options.hh
class InlineSingletons(StrEnum):
    """How to inline volumes that are used only once."""

    NONE = auto()  # Never
    UNTRANSFORMED = auto()  # Only if not translated nor rotated
    UNROTATED = auto()  # Only if translated
    ALL = auto()  # Always


# orange/g4org/Options.hh
class OrangeConversionOptions(_Model):
    """Construction options for Geant4-to-ORANGE conversion.

    Note that most of these should never be touched when running an actual
    problem. If the length unit is changed, the resulting geometry is
    inconsistent with Geant4's scale.
    """

    # Problem scale and tolerance

    unit_length: PositiveFloat = 1.0
    "Scale factor (input unit length), customizable for unit testing"

    tol: Optional[Tolerance] = None
    "Construction and tracking tolerance (native units)"

    # Structural conversion

    explicit_interior_threshold: NonNegativeInt = 2
    "Volumes with up to this many children construct an explicit interior"

    inline_childless: bool = True
    "Forcibly inline volumes that have no children"

    inline_singletons: InlineSingletons = InlineSingletons.UNTRANSFORMED
    "Forcibly inline volumes that are only used once"

    inline_unions: bool = True
    "Forcibly copy child volumes that have union boundaries"

    remove_interior: bool = True
    "Replace 'interior' unit boundaries with 'true' and simplify"

    remove_negated_join: bool = False
    "Use DeMorgan's law to replace 'not all of' with 'any of not'"

    # Debug output

    verbose_volumes: bool = False
    "Write output about volumes being converted"

    verbose_structure: bool = False
    "Write output about proto-universes being constructed"

    objects_output_file: Optional[str] = None
    "Write converted Geant4 object structure to a JSON file"

    csg_output_file: Optional[str] = None
    "Write constructed CSG surfaces and tree to a JSON file"

    org_output_file: Optional[str] = None
    "Write final org.json to a JSON file"


# celer-geo/GeoInput.hh
class ModelSetup(_Model):
    cuda_stack_size: Optional[NonNegativeInt] = None
    cuda_heap_size: Optional[NonNegativeInt] = None

    geometry_file: FilePath
    "Path to the GDML input file"

    perfetto_file: Optional[FilePath] = None
    "Path to write Perfetto profiling output"


# celer-geo/GeoInput.hh
class TraceSetup(_Model):
    _cmd: Literal["trace"] = "trace"
    "Command name in the JSON file"

    geometry: Optional[GeometryEngine] = None
    "Geometry engine with which to perform the trace"

    memspace: Optional[MemSpace] = None
    "Whether to perform the trace on CPU or GPU"

    volumes: bool = True
    "Print a list of all volumes in the geometry"

    bin_file: FilePath
    "Specify the path to write the image binary data"


# geocel/rasterize/Image.hh
class ImageInput(_Model):
    lower_left: Real3 = [0, 0, 0]
    """Spatial coordinate of the image's lower left point"""

    upper_right: Real3
    """Spatial coordinate of the images' upper right point"""

    rightward: Real3 = [1, 0, 0]
    "Ray trace direction which points to the right in the image"

    vertical_pixels: NonNegativeInt = 512
    "Number of pixels along the y axis"

    horizontal_divisor: Optional[PositiveInt] = None
    "Increase the horizontal window to be divisible by this number"


# ad hoc: input to a 'trace' command
class TraceInput(TraceSetup):
    image: Optional[ImageInput] = None
    "Reuse the existing image"


# celer-geo/celer-geo.cc
class OrangeStats(_Model):
    def model_dump_json(self, **kwargs):
        """Override to ensure _cmd is always set to orange_stats."""
        result = self.model_dump(**kwargs)
        result["_cmd"] = "orange_stats"
        return to_json(result).decode()


# Union of available commands
Command = TraceInput | OrangeStats
