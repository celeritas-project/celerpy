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


class CelerGeo:
    """Manage a celer-geo process with input and output."""

    volumes: dict[model.GeometryEngine, list[str]]
    image: Optional[model.ImageInput]

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
        # Cached volume names
        self.volumes = {}
        # Last image input
        self.image = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.close()

    def trace(
        self,
        image: Optional[model.ImageInput] = None,
        geometry: Optional[model.GeometryEngine] = None,
        memspace: Optional[model.MemSpace] = None,
        **kwargs,
    ):
        """Trace with a geometry, memspace, etc."""
        if image is None:
            if not self.image:
                raise RuntimeError(
                    "Image specifications must be supplied for the first trace"
                )
            image = self.image

        # Determine whether to request the list of volumes for this geometry
        volumes = None
        if geometry is not None:
            volumes = self.volumes.setdefault(geometry, [])

        with NamedTemporaryFile(suffix=".bin", mode="w+b") as f:
            inp = model.TraceInput(
                geometry=geometry,
                memspace=memspace,
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

        # Cache the last run image
        self.image = image

        return (result, img)

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

    def __call__(self, image, volumes: list[str]):
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


_register_cmaps()
