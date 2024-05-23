# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import sys
import json
import signal

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


def read_input():
    try:
        return json.loads(input())
    except EOFError:
        log("EOF during input read")
        return None


def setup_signals():
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)
