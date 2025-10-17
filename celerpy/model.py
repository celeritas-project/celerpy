# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage models used for JSON I/O with Celeritas."""

from enum import StrEnum, auto
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


# orange/OrangeTypes.hh
class Tolerance(_Model):
    """Relative and absolute tolerance for construction and tracking."""

    rel: Annotated[float, Field(gt=0, lt=1)]
    "Relative tolerance: must be in (0, 1)"

    abs: Annotated[float, Field(gt=0)]
    "Absolute tolerance: must be greater than zero"


# corecel/Types.hh
class MemSpace(StrEnum):
    """Memory/execution space."""

    HOST = auto()  # CPU
    DEVICE = auto()  # GPU

    # Backward compatibility
    host = HOST
    device = DEVICE


# corecel/Types.hh
class UnitSystem(StrEnum):
    CGS = auto()
    SI = auto()
    CLHEP = auto()

    # Backward compatibility
    cgs = CGS
    si = SI
    clhep = CLHEP


# corecel/io/LoggerTypes.hh
class LogLevel(StrEnum):
    """Minimum verbosity level for logging."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


# celer-geo/Types.hh
class GeometryEngine(StrEnum):
    """Geometry model implementation for execution and rendering."""

    GEANT4 = auto()
    VECGEOM = auto()
    ORANGE = auto()

    # Backward compatibility
    geant4 = GEANT4
    vecgeom = VECGEOM
    orange = ORANGE


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
