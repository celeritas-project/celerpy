# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

from matplotlib.colors import ListedColormap, BoundaryNorm
import collections
import numpy as np
import json
import re
from typing import Optional
from . import model
from . import process
from pathlib import Path

from tempfile import NamedTemporaryFile
from subprocess import TimeoutExpired

__all__ = ["CelerGeo"]


_re_ptr = re.compile(r"0x[0-9a-f]+")


def _register_cmaps():
    from importlib.resources import files
    from matplotlib import colormaps

    resources = files("celerpy._resources")
    cmap = ListedColormap(
        np.loadtxt(resources.joinpath("glasbey-light.txt")),
        name="glasbey_light",
    )
    try:
        colormaps.register(cmap)
    except ValueError as e:
        # Possibly duplicate?
        print(e)


UNIT_LENGTH = {
    model.UnitSystem.cgs: "cm",
    model.UnitSystem.clhep: "mm",
    model.UnitSystem.si: "m",
}


class IdMapper:
    """Map volume names to sequential indices.

    This is so that colors can be rendered consistently across
    geometry engines that have different IDs (or ID ordering) for the same
    volume names, and so the colors will stay consistent if the image is moved
    (so that new volumes "appear").
    """

    def __init__(self):
        self.id_to_volume = []
        self.volume_to_id = ReverseIndexDict(self.id_to_volume)

    def clear(self):
        self.id_to_volume.clear()
        self.volume_to_id.clear()

    def __call__(self, image: np.ndarray, volumes: list[str]):
        # Get unique list of geometry-specific volume IDs
        ids = np.unique(image)
        sentinels = []
        if ids[0] == -1:
            sentinels.append(ids[0])
            ids = ids[1:]
        assert ids.size == 0 or ids[-1] < len(volumes)

        # Map local IDs -> volumes -> resulting IDs
        local_id_map = np.empty_like(volumes, dtype=np.int32)
        local_id_map[:] = -1
        for i in ids:
            local_id_map[i] = self.volume_to_id[volumes[i]]

        mask = (image == sentinels[0]) if sentinels else None

        # Remap from old IDs to new, ignoring invalid values
        image = local_id_map[image]
        if mask is not None:
            image = np.ma.array(image, mask=mask)

        return (image, self.id_to_volume)


class CelerGeo:
    """Manage a celer-geo process with input and output.

    TODO: if we support mapping quantities other than volumes, we'll need to
    refactor.
    """

    image: Optional[model.ImageParams]
    volumes: dict[model.GeometryEngine, list[str]]

    @classmethod
    def from_filename(cls, path: Path):
        """Construct from a geometry filename and default other setup."""
        return cls(model.ModelSetup(geometry_file=path))

    def __init__(self, setup: model.ModelSetup):
        # Create the process and attach stdin/stdout pipes
        self.process = process.launch("celer-geo")
        # Model setup with actual parameters is echoed back
        self.setup = process.communicate_model(
            self.process, setup, model.ModelSetup
        )
        # Cached image
        self.image = None
        # Cached volume names
        self.volumes = {}
        # Remapped 'visited' volume names
        self.map_ids = IdMapper()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.close()

    def reset_id_map(self):
        self.map_ids.clear()

    def trace(
        self,
        image: Optional[model.ImageInput] = None,
        *,
        geometry: Optional[model.GeometryEngine] = None,
        **kwargs,
    ):
        """Trace with a geometry, memspace, etc."""
        if image is None and not self.image:
            raise RuntimeError(
                "Image specifications must be supplied for the first trace"
            )

        # Determine whether to request the list of volumes for this geometry
        volumes = None
        if geometry is not None:
            volumes = self.volumes.setdefault(geometry, [])

        with NamedTemporaryFile(suffix=".bin", mode="w+b") as f:
            inp = model.TraceInput(
                geometry=geometry,
                volumes=(not volumes),
                bin_file=Path(f.name),
                image=image,
                **kwargs,
            )
            result = process.communicate_model(
                self.process, inp, model.TraceOutput
            )
            img = f.read()

        # Cache the geometry names and ensure trace has them
        if geometry is None:
            geometry = result.trace.geometry
            assert geometry is not None
            volumes = self.volumes.setdefault(geometry, [])
        if not volumes:
            assert isinstance(volumes, list)
            assert result.volumes
            # XXX : erase pointer names (for now?)
            volumes[:] = [_re_ptr.sub("", v) for v in result.volumes]
        else:
            result.volumes = volumes

        # Reinterpret the image as a correctly shaped Numpy array
        npimg = np.frombuffer(img, dtype=np.int32).reshape(result.image.dims)
        self.image = result.image

        return (result, npimg)

    def close(self, *, timeout=0.25):
        """Cleanly exit the ray trace loop, returning run statistics if possible."""
        result = process.communicate(self.process, json.dumps(None))
        try:
            self.process.wait(timeout=timeout)
        except TimeoutExpired:
            pass
        result = result or process.close(self.process, timeout=timeout)
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            pass
        return result


class ReverseIndexDict(collections.defaultdict):
    """Manage a two-way mapping of integers and another type."""

    def __init__(self, volume_list):
        self.vlist = volume_list

    def __missing__(self, key):
        self[key] = result = len(self)
        self.vlist.append(key)
        assert len(self.vlist) == len(self)
        return result


LabeledAxis = collections.namedtuple("LabeledAxis", ["label", "lo", "hi"])
LabeledAxes = collections.namedtuple("LabeledAxes", ["x", "y"])


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
        super().__init__(bounds, len(bounds) - 1, clip=False)
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
            return super().__call__(value, clip)

        mask = np.ma.getmaskarray(value)
        invalid = value >= self.ids_to_idx.size
        value[invalid] = 0
        mask |= invalid

        result = self.ids_to_idx[value]
        result = np.ma.array(result, mask=mask)
        return result


def calc_image_axes(image: model.ImageParams):
    """Calculate label/min/max for x and y axes from an image result."""
    down = np.array(image.down)
    right = np.array(image.right)
    height = image.pixel_width * image.dims[0]
    width = image.pixel_width * image.dims[1]
    upper_left = image.origin
    lower_left = down * height + upper_left
    units = UNIT_LENGTH[image.units]

    def calc_axes(length, dir):
        for d, dimname in enumerate("xyz"):
            if 1 - abs(dir[d]) < 1e-6:
                lower = lower_left[d]
                upper = lower + length * dir[d]
                label = f"{dimname} [{units}]"
                break
        else:
            # No orthogonal axis found
            label = "Position along ({}) from {} [{}]".format(
                ",".join("{:.3f}".format(v if v != 0 else 0) for v in dir),
                lower_left,
                units,
            )
            (lower, upper) = (0, length)
        return LabeledAxis(label, lower, upper)

    return LabeledAxes(x=calc_axes(width, right), y=calc_axes(height, -down))


class Imager:
    axes: Optional[LabeledAxes] = None

    def __init__(self, celer_geo, image: model.ImageInput):
        self.celer_geo = celer_geo
        self.image = image
        self.axes = None  # Lazily update

    def __call__(
        self,
        ax,
        geometry: Optional[model.GeometryEngine] = None,
        memspace: Optional[model.MemSpace] = None,
        colorbar=None,
    ):
        (trace_output, img) = self.celer_geo.trace(
            self.image, geometry=geometry, memspace=memspace
        )
        assert trace_output.volumes is not None
        if self.axes is None:
            self.axes = calc_image_axes(trace_output.image)
        (x, y) = self.axes

        ax.set_xlabel(x.label)
        ax.set_xlim([x.lo, x.hi])
        ax.set_ylabel(y.label)
        ax.set_ylim([y.lo, y.hi])
        ax.set_title(
            "{to.trace.geometry.name} ({to.trace.memspace.name})".format(
                to=trace_output
            )
        )

        # Remap volume IDs and volume names into a persistent 0-based list
        (img, volumes) = self.celer_geo.map_ids(img, trace_output.volumes)
        norm = IdNorm(np.arange(len(volumes)))
        im = ax.imshow(
            img,
            extent=[x.lo, x.hi, y.lo, y.hi],
            interpolation="none",
            norm=norm,
            cmap="glasbey_light",
        )

        result = {"output": trace_output, "imshow": im}
        if colorbar is None:
            colorbar = len(volumes) < 128

        if colorbar:
            # Create colorbar
            bounds = norm.boundaries
            kwargs = {"ticks": bounds[:-1] + np.diff(bounds) / 2}
            if not isinstance(colorbar, bool):
                # User can specify a new axis to place the colorbar
                kwargs["cax"] = colorbar
            fig = ax.get_figure()
            cbar = fig.colorbar(im, **kwargs)
            result["colorbar"] = cbar

            # Build labels
            cbar.ax.set_yticklabels(volumes)

        return im


_register_cmaps()
