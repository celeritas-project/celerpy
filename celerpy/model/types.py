# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Base types and enums for Celeritas models."""

from enum import StrEnum, auto
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    conlist,
)

Real3 = Annotated[list, conlist(float, min_length=3, max_length=3)]
Size2 = Annotated[list, conlist(int, min_length=2, max_length=2)]


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


# orange/OrangeTypes.hh
class LogicNotation(StrEnum):
    """How to inline volumes that are used only once."""

    POSTFIX = auto()
    INFIX = auto()
