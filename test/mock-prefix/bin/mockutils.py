# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import json
import signal
import sys
from typing import Any

import numpy as np

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("error")


def log(*args):
    print("<child>", *args, file=sys.stderr, flush=True)


def dump(obj, file=sys.stdout):
    try:
        json.dump(obj, file)
        file.write("\n")
        file.flush()
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
