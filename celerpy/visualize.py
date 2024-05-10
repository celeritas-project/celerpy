# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import re


def _register_cmaps():
    from importlib.resources import files
    from matplotlib import colormaps

    resources = files("celerpy._resources")
    colormaps.register(
        ListedColormap(
            np.loadtxt(resources.joinpath("glasbey-light.txt")),
            name="glasbey_light",
        )
    )


_register_cmaps()


class IdNorm(BoundaryNorm):
    """Map IDs to consecutive integers for rendering.

    This provides literally a factor of 1000 speedup over using BoundaryNorm
    (when trying to plot an image with 3k compositions).
    """

    # Note: we inherit from BoundaryNorm because there's some special-casing
    # in ColorBar and possibly elsewhere

    def __init__(self, ids):
        """Give a list of unique IDs that will be remapped to their position in
        this list.
        """
        assert ids.size > 0
        fltids = np.array(ids, dtype=float)
        bounds = np.concatenate([fltids - 0.5, [fltids[-1] + 0.5]])
        super(IdNorm, self).__init__(bounds, len(bounds) - 1, clip=False)
        self.vmin = 0
        self.vmax = ids[-1]

        # Remap matids to ID index: array up to the last valid matid.
        ids_to_idx = np.zeros((ids[-1] + 1), dtype=np.int16)
        ids_to_idx[ids] = np.arange(len(ids), dtype=np.int16)
        self.ids_to_idx = ids_to_idx

    def __call__(self, value, clip=None):
        """Convert IDs to indices.

        For integer values, this is a much faster operation than the base
        class's implementation of __call__.
        """
        if not np.issubdtype(value.dtype, np.integer):
            # When rendering color bars, matplotlib passes an array of
            # floating-point midpoint values. Let the base class logic (slower
            # but compatible with the colorbar mechanics) handle it.
            return super(IdNorm, self).__call__(value, clip)

        mask = np.ma.getmaskarray(value)
        invalid = value >= self.ids_to_idx.size
        value[invalid] = 0
        mask |= invalid

        result = self.ids_to_idx[value]
        result = np.ma.array(result, mask=mask)
        return result


class PlotDims:
    def __init__(self, md):
        """Construct with image metadata"""
        self.down = np.array(md["down"])
        self.right = np.array(md["right"])
        pw = md["pixel_width"]
        dims = md["dims"]
        self.upper_left = md["origin"]
        self.width = pw * dims[1]
        self.height = pw * dims[0]
        self.units = {
            "cgs": "cm",
            "clhep": "mm",
            "si": "m",
        }[md["_units"]]

        self.lower_left = self.down * self.height + self.upper_left

    def calc_axes(self, length, dir):
        for d, dimname in enumerate("xyz"):
            if 1 - abs(dir[d]) < 1e-6:
                lower = self.lower_left[d]
                upper = lower + length * dir[d]
                label = f"{dimname} [{self.units}]"
                break
        else:
            # No orthogonal axis found
            label = "Position along ({}) from {} [{}]".format(
                ",".join("{:.3f}".format(v if v != 0 else 0) for v in dir),
                self.lower_left,
                self.units,
            )
            (lower, upper) = (0, length)
        return (label, lower, upper)


def get_ids_and_sentinels(image):
    ids = np.unique(image)
    sentinels = []
    if ids[0] == -1:
        sentinels.append(ids[0])
        ids = ids[1:]
    return (ids, sentinels)


_re_ptr = re.compile(r"0x[0-9a-f]+")


def remap_ids(ids, volumes=None):
    """Create a set of unique volume names and corresponding ID map."""
    if volumes is None:
        volumes = [str(i) for i in range(np.max(ids))]
    new_ids = np.empty_like(volumes, dtype=np.int32)
    new_ids[:] = -1

    uvolumes = {}
    for i in ids:
        v = _re_ptr.sub("", volumes[i])
        new_id = uvolumes.setdefault(v, len(uvolumes))
        new_ids[i] = new_id

    vol_names = [None] * len(uvolumes)
    for k, v in uvolumes.items():
        vol_names[v] = k

    return (new_ids, vol_names)


def load_and_plot_image(ax, out, image=None):
    assert out["sizeof_int"] == 4
    if image is None:
        image = np.fromfile(out["trace"]["bin_file"], dtype=np.int32)
    elif isinstance(image, bytes):
        image = np.frombuffer(image, dtype=np.int32)
    image = np.reshape(image, out["image"]["dims"])
    dims = PlotDims(out["image"])

    (label, left, right) = dims.calc_axes(dims.width, dims.right)
    ax.set_xlabel(label)
    ax.set_xlim([left, right])
    (label, lower, upper) = dims.calc_axes(dims.height, -dims.down)
    ax.set_ylabel(label)
    ax.set_ylim([lower, upper])

    # Get unique set of IDs inside the raytraced image
    (ids, sentinels) = get_ids_and_sentinels(image)

    (new_ids, labels) = remap_ids(ids, out.get("volumes"))

    if sentinels:
        image = np.ma.masked_where((image == sentinels[0]), image)
    # Remap from old IDs to new, ignoring invalid values
    image = new_ids[image]

    norm = IdNorm(np.arange(len(labels)))
    im = ax.imshow(
        image,
        extent=[left, right, lower, upper],
        interpolation="none",
        norm=norm,
        cmap="glasbey_light",
    )

    if len(ids) < 128:
        # Create colorbar
        bounds = norm.boundaries
        ticks = bounds[:-1] + np.diff(bounds) / 2
        fig = ax.get_figure()
        cbar = fig.colorbar(im, ticks=ticks)

        # Build labels
        cbar.ax.set_yticklabels(labels)

    return im