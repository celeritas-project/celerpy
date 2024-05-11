# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage models used for JSON I/O with Celeritas."""

from typing import Annotated, Optional
from pydantic import BaseModel, FilePath, NonNegativeInt, PositiveInt, conlist
from enum import Enum

Real3 = Annotated[list, conlist(float, min_length=3, max_length=3)]


class GeometryEngine(Enum):
    orange = "orange"
    vecgeom = "vecgeom"
    geant4 = "geant4"


class MemSpace(Enum):
    host = "host"
    device = "device"


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


# informal:
class TraceOutput(BaseModel):
    pass
