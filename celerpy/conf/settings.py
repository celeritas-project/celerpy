# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from pydantic import DirectoryPath, FilePath
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

    prefix_path: Optional[DirectoryPath] = None
    "Path to the Celeritas build/install directory"

    # CELER_ environment variables

    color: bool = True
    "Enable colorized terminal output"

    disable_device: bool = False
    "Disable GPU execution even if available"

    log: LogLevel = LogLevel.INFO
    "World log level"

    log_local: LogLevel = LogLevel.WARNING
    "Self log level"

    profiling: bool = False
    "Enable NVTX/ROCTX/Perfetto profiling"

    # Geant4->ORANGE conversion

    g4org_options: Optional[FilePath] = None
    "JSON file with conversion options"

    # Geant4 configuration

    g4_geo_optimize: bool = True
    "Build Geant4 tracking acceleration structures"
