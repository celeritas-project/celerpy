# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage models used for JSON I/O with Celeritas."""

from typing import Annotated, Optional
from pydantic import (
    BaseModel,
    FilePath,
    NonNegativeInt,
    PositiveInt,
    conlist,
    Field,
    PositiveFloat,
)
from enum import Enum

Real3 = Annotated[list, conlist(float, min_length=3, max_length=3)]
Size2 = Annotated[list, conlist(PositiveInt, min_length=2, max_length=2)]


# celer-geo/Types.hh
class GeometryEngine(Enum):
    orange = "orange"
    vecgeom = "vecgeom"
    geant4 = "geant4"


# corecel/Types.hh
class MemSpace(Enum):
    host = "host"
    device = "device"


# corecel/Types.hh
class UnitSystem(Enum):
    cgs = "cgs"
    si = "si"
    clhep = "clhep"


# celer-geo/GeoInput.hh
class ModelSetup(BaseModel):
    cuda_stack_size: Optional[NonNegativeInt] = None
    cuda_heap_size: Optional[NonNegativeInt] = None
    geometry_file: FilePath


# celer-geo/GeoInput.hh
class TraceSetup(BaseModel):
    geometry: Optional[GeometryEngine] = None
    memspace: Optional[MemSpace] = None
    volumes: bool = True
    bin_file: FilePath


# geocel/rasterize/Image.hh
class ImageInput(BaseModel):
    lower_left: Real3 = [0, 0, 0]
    upper_right: Real3
    rightward: Real3 = [1, 0, 0]
    vertical_pixels: NonNegativeInt
    horizontal_divisor: Optional[PositiveInt] = None


# geocel/rasterize/ImageData.hh: ImageParamsScalars
class ImageParams(BaseModel):
    origin: Real3
    down: Real3
    right: Real3
    pixel_width: PositiveFloat
    dims: Size2
    units: UnitSystem = Field(serialization_alias="_units")


# ad hoc: result from a 'trace' command
class TraceOutput(BaseModel):
    trace: TraceSetup
    image: ImageParams
