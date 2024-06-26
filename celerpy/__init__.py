# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
try:
    from . import _version

    __version__ = _version.__version__
except:  # noqa: E722
    __version__ = "0.0.0-dev"
