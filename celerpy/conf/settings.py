# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict

from celerpy.model import LogLevel


class Settings(BaseSettings):
    """Global environment settings for Celeritas front end.

    Settings can be changed by setting environment variables such as
    ``CELER_PREFIX_PATH`` (case insensitive).

    TODO: parse config file for default unit system, etc.
    """

    model_config = SettingsConfigDict(
        env_prefix="celer_",
        validate_assignment=True,
        use_attribute_docstrings=True,
    )

    color: bool = True
    "Enable colorized terminal output"

    disable_device: bool = False
    "Disable GPU execution even if available"

    g4org_export: Optional[str] = None
    "Filename base to export converted Geant4 geometry"

    g4org_verbose: bool = False
    "Filename base to export converted Geant4 geometry"

    log: LogLevel = LogLevel.INFO
    "World log level"

    log_local: LogLevel = LogLevel.WARNING
    "Self log level"

    prefix_path: Optional[DirectoryPath] = None
    "Path to the Celeritas build/install directory"

    profiling: bool = False
    "Enable NVTX/ROCTX/Perfetto profiling"
