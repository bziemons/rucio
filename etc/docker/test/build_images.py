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

import collections
import itertools
import json
import subprocess
import sys
import uuid
from functools import partial

DIST_KEY = "DIST"
BUILD_ARG_KEYS = ["PYTHON"]
BuildArgs = collections.namedtuple('BuildArgs', BUILD_ARG_KEYS)


def main():
    matrix = json.load(sys.stdin)
    filter_build_args = partial(map,
                                lambda argdict: {arg: val for arg, val in argdict.items() if arg in BUILD_ARG_KEYS})
    make_buildargs = partial(map, lambda argdict: BuildArgs(**argdict))
    distribution_buildargs = {dist: set(make_buildargs(filter_build_args(args))) for dist, args in
                              itertools.groupby(matrix, lambda d: d[DIST_KEY])}

    images = dict()
    for dist, buildargs_list in distribution_buildargs.items():
        for buildargs in buildargs_list:
            imagetag = f'rucio:{dist}-autotest-{uuid.uuid4()}'
            args = ('docker', 'build', '--file', f'{dist}.Dockerfile', '--tag', imagetag,
                    *itertools.chain(*map(lambda x: ('--build-arg', f'{x[0]}={x[1]}'), buildargs._asdict().items())),
                    '../../..')
            print("Running", " ".join(args), file=sys.stderr)
            subprocess.run(args, stdout=sys.stderr, check=True)
            print("Finished building image", imagetag, file=sys.stderr)
            images[imagetag] = {DIST_KEY: dist, **buildargs._asdict()}
    json.dump(images, sys.stdout)


if __name__ == "__main__":
    main()
