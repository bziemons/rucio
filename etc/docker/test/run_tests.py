#!/usr/bin/env python3
# Copyright 2020 CERN for the benefit of the ATLAS collaboration.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2020

import itertools
import json
import os
import subprocess
import sys
import typing


def matches(small: typing.Dict, group: typing.Dict):
    for key in small.keys():
        if key not in group or small[key] != group[key]:
            return False
    return True


def run(*args, env=None):
    print("Running", " ".join(args), file=sys.stderr)
    if env is None:
        subprocess.run(args, check=True, stdout=sys.stderr, stderr=subprocess.STDOUT)
    else:
        subprocess.run(args, check=True, stdout=sys.stderr, stderr=subprocess.STDOUT, env=env)


def main():
    obj = json.load(sys.stdin)
    cases = (obj["matrix"], ) if isinstance(obj["matrix"], dict) else obj["matrix"]

    for case in cases:
        for image, idgroup in obj["images"].items():
            if matches(idgroup, case):
                # Running rucio
                args = ('docker', 'run', '--detach',
                        *itertools.chain(*map(lambda x: ('--env', f'{x[0]}={x[1]}'), case.items())),
                        image)
                print("Running", " ".join(args), file=sys.stderr)
                proc = subprocess.run(args, stdout=subprocess.PIPE, check=True)
                cid = proc.stdout.decode().strip()
                if not cid:
                    raise RuntimeError("Could not determine container id after docker run")

                try:
                    print("*** Starting", {**case, "IMAGE": image}, file=sys.stderr)

                    # Running install_script.sh
                    run('docker', 'exec', '-t', cid, './tools/test/install_script.sh')

                    # Running before_script.sh
                    run('../../../tools/test/before_script.sh', env={**os.environ, **case, "IMAGE": image})

                    # Running test.sh
                    run('docker', 'exec', '-t', cid, './tools/test/test.sh')
                finally:
                    print("*** Finalizing", {**case, "IMAGE": image}, file=sys.stderr)

                    run('docker', 'stop', cid)
                    run('docker', 'rm', '-v', cid)


if __name__ == "__main__":
    main()
