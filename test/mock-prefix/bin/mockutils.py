# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import json
import os
import signal
import sys
from typing import Any

import numpy as np

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("error")


def osprint(*args, sep=" ", end="\n", file=sys.stdout, flush=True):
    """Print using the low-level os interfaces rather than python file buffers.

    This prevents "reentrant call" errors if a signal is caught during print.
    """
    s = sep.join(map(str, args)) + end
    os.write(file.fileno(), s.encode())
    if flush:
        file.flush()


def log(*args):
    osprint("<child>", *args, file=sys.stderr)


def dump(obj):
    try:
        osprint(json.dumps(obj))
    except BrokenPipeError as e:
        log(e)


def terminate(signum, frame):
    log("caught signal", signum)
    dump("terminating")
    sys.exit(signum)


def read_input() -> Any:
    try:
        return json.loads(input())
    except EOFError:
        log("EOF during input read")
        return None


def setup_signals():
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)


def expect_trace(expected_inp, expected_outp):
    expected_inp = json.loads(expected_inp)
    expected_outp = json.loads(expected_outp)
    log("expecting input...")
    inp = read_input()
    if inp is None:
        log("exiting early due to missing input")
        sys.exit(1)
    log("...read input")
    bin_file = inp.pop("bin_file")
    if inp != expected_inp:
        raise RuntimeError(f"Unexpected output: got {json.dumps(inp)!r}")

    with open(bin_file, "wb") as f:
        f.write(np.zeros([4, 4], dtype=np.int32).tobytes())

    log("writing output...")
    expected_outp["trace"]["bin_file"] = bin_file
    dump(expected_outp)
