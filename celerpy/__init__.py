# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("celerpy")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

# Expose __version__ for type checkers
__all__ = ["__version__"]
