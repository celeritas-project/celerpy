# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

from matplotlib import pyplot as plt
import numpy as np


def test_visualize():
    from celerpy.visualize import load_and_plot_image

    (fig, ax) = plt.subplots()
    image = np.array([[0, 0, 0], [0, 1, 0], [2, 1, 0]], dtype=np.int32)
    metadata = {
        "sizeof_int": 4,
        "image": {
            "dims": [3, 3],
            "down": [0, -1, 0],
            "right": [1, 0, 0],
            "pixel_width": 2.0,
            "origin": [10.0, 5.0, 1.0],
            "_units": "cgs",
        },
        "volumes": ["a", "b", "c"],
    }
    load_and_plot_image(ax, metadata, image.tobytes())
