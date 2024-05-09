# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
from .conf.settings import Settings

# Mypy error: see https://github.com/koxudaxi/datamodel-code-generator/issues/1870
settings = Settings()  # type: ignore[call-arg]
