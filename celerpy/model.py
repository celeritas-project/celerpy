# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage models used for JSON I/O with Celeritas."""

from enum import Enum
from typing import Annotated, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FilePath,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
    conlist,
)

Real3 = Annotated[list, conlist(float, min_length=3, max_length=3)]
Size2 = Annotated[list, conlist(PositiveInt, min_length=2, max_length=2)]


class _Model(BaseModel):
    """Base settings for Celeritas models.

    Note that attribute docstrings require Pydantic 2.7 or higher.
    """

    model_config = ConfigDict(use_attribute_docstrings=True)


# celer-geo/Types.hh
class GeometryEngine(Enum):
    """Geometry model implementation for execution and rendering."""

    geant4 = "geant4"
    vecgeom = "vecgeom"
    orange = "orange"


# corecel/Types.hh
class MemSpace(Enum):
    """Memory/execution space."""

    host = "host"  # CPU
    device = "device"  # GPU


# corecel/Types.hh
class UnitSystem(Enum):
    cgs = "cgs"
    si = "si"
    clhep = "clhep"


# celer-geo/GeoInput.hh
class ModelSetup(_Model):
    cuda_stack_size: Optional[NonNegativeInt] = None
    cuda_heap_size: Optional[NonNegativeInt] = None

    geometry_file: FilePath
    "Path to the GDML input file"


# celer-geo/GeoInput.hh
class TraceSetup(_Model):
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


# geocel/rasterize/ImageData.hh: ImageParamsScalars
class ImageParams(_Model):
    origin: Real3
    "Upper left point of the image"

    down: Real3
    "Direction vector rendered as 'downward' in the image"

    right: Real3
    "Direction vector rendered as 'rightward' in the image"

    pixel_width: PositiveFloat
    "Size of a pixel in the image"

    dims: Size2
    "Size of a pixel in the generated image"

    units: UnitSystem = Field(alias="_units")

    # TODO: max length is not used or returned by celer-geo
    # max_length: float


# ad hoc: input to a 'trace' command
class TraceInput(TraceSetup):
    image: Optional[ImageInput] = None
    "Reuse the existing image"


# ad hoc: result from a 'trace' command
class TraceOutput(_Model):
    trace: TraceSetup
    image: ImageParams
    volumes: Optional[list[str]] = None
    sizeof_int: PositiveInt


class ExceptionDump(_Model):
    """Output of an exception message when a Celeritas app fails"""

    _category: Literal["result"]
    _label: Literal["exception"]
    type: str
    condition: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None
    which: Optional[str] = None
    context: Optional["ExceptionDump"] = None
