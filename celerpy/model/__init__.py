# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage models used for JSON I/O with Celeritas.

This module re-exports all models from the individual modules for backward
compatibility. For new code, prefer importing from the specific modules:
- celerpy.types: Base types, enums, and type aliases
- celerpy.input: Command and input models
- celerpy.output: Output and result models
"""

from . import input, output, types
from .input import (
    ImageInput,
    ModelSetup,
    OrangeConversionOptions,
    TraceInput,
    TraceSetup,
)
from .types import (
    GeometryEngine,
    LogLevel,
    MemSpace,
    UnitSystem,
)

__all__ = [
    "input",
    "output",
    "types",
    "ImageInput",
    "ModelSetup",
    "OrangeConversionOptions",
    "TraceInput",
    "TraceSetup",
    "GeometryEngine",
    "LogLevel",
    "MemSpace",
    "UnitSystem",
]
