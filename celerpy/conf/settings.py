# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global settings for Celeritas front end.

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

    # TODO: log, log_local, disable_device

    prefix_path: Optional[DirectoryPath] = None
    "Path to the Celeritas build/install directory"
