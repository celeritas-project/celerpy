# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath, Field
from typing import Optional


class Settings(BaseSettings):
    """Global settings for Celeritas front end.

    Settings can be changed by setting environment variables such as
    ``CELER_PREFIX_PATH`` (case insensitive).
    """

    model_config = SettingsConfigDict(
        env_prefix="celer_", validate_assignment=True
    )

    color: bool = True
    debug: bool = False
    # TODO: log, log_local, disable_device
    prefix_path: Optional[DirectoryPath] = Field(
        None, description="Path to the Celeritas build/install directory"
    )
