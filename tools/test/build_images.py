#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020-2021 CERN
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
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2020-2021
# - Mayank Sharma <mayank.sharma@cern.ch>, 2021
# - Martin Barisits <martin.barisits@cern.ch>, 2021

import argparse
import asyncio
import collections
import io
import itertools
import json
import os
import pathlib
import sys
import traceback
from asyncio.subprocess import STDOUT, PIPE
from functools import partial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Tuple, Dict, Optional, Iterable, Any, Awaitable
    from io import TextIOBase

# mostly for checking the version in automated scripts, similar to sys.version_info
VERSION: "Tuple[int]" = (2,)

DIST_KEY = "DIST"
BUILD_ARG_KEYS = ["PYTHON", "IMAGE_IDENTIFIER"]
BuildArgs = collections.namedtuple('BuildArgs', BUILD_ARG_KEYS)
IMAGE_BUILD_COUNT_LIMIT = 20


def format_args(program, *args):
    return f"{program} {' '.join(map(lambda a: repr(a) if ' ' in a else a, args))}".rstrip()


def imagetag(
    dist: str,
    buildargs: "Dict[str, str]",
    image_identifier: str,
    branch: "Optional[str]" = None,
    cache_repo: "Optional[str]" = None,
) -> str:

    buildargs_tags = '-'.join(map(lambda it: str(it[0]).lower() + str(it[1]).lower(), buildargs.items()))
    if buildargs_tags:
        buildargs_tags = '-' + buildargs_tags
    if branch:
        branch = str(branch).lstrip('refs/heads/')
        if branch.startswith('release-'):
            image_identifier += '-' + branch.lstrip('release-').lower()
    tag = f'rucio-{image_identifier}:{dist.lower()}{buildargs_tags}'
    if cache_repo:
        tag = cache_repo.lower() + '/' + tag
    return tag


async def build_image(
    name: str,
    dockerfile: str,
    build_context: str,
    buildargs: "Dict[str, str]",
    use_podman: bool,
    cache_repo: str,
    no_cache: bool,
    containerfiles_dir: "os.PathLike",
    push_cache: bool,
    verbose: bool,
    logfile: "TextIOBase" = sys.stderr,
) -> None:

    cache_args = ()
    if no_cache:
        cache_args = ('--no-cache', '--pull-always' if use_podman else '--pull')
    elif cache_repo:
        args = ('docker', 'pull', name)
        print("Running", format_args(*args), file=logfile, flush=True)
        if verbose:
            print("Running", format_args(*args), file=sys.stderr, flush=True)
        try:
            await async_tailed_run(args=args, verbose=verbose, logfile=logfile)
        except Exception:
            traceback.print_exc(file=logfile)
            if verbose:
                traceback.print_exc(limit=12, file=sys.stderr)
                sys.stderr.flush()
        cache_args = ('--cache-from', name)

    buildfile = pathlib.Path(containerfiles_dir) / dockerfile
    buildargs = map(lambda x: ('--build-arg', f'{x[0]}={x[1]}'), buildargs.items())
    args = (
        'docker',
        'build',
        *cache_args,
        '--file',
        str(buildfile),
        '--tag',
        name,
        *itertools.chain.from_iterable(buildargs),
        build_context,
    )
    print("Running", format_args('docker', *args), file=logfile, flush=True)
    if verbose:
        print("Running", format_args('docker', *args), file=sys.stderr, flush=True)
    await async_tailed_run(args=args, verbose=verbose, logfile=logfile)
    print("Finished building image", name, file=logfile, flush=True)

    if push_cache:
        args = ('docker', 'push', name)
        print("Running", " ".join(args), file=logfile, flush=True)
        if verbose:
            print("Running", " ".join(args), file=sys.stderr, flush=True)
        await async_tailed_run(args=args, verbose=verbose, logfile=logfile)


async def async_tailed_run(args: "Iterable[str]", verbose: bool, logfile: "TextIOBase") -> None:
    proc = await asyncio.create_subprocess_exec(*args, stdout=PIPE, stderr=STDOUT)
    output = await proc.stdout.readline()
    while output:
        logfile.write(output.decode('utf-8', errors='replace'))
        if verbose:
            sys.stderr.write(output.decode('utf-8', errors='replace'))
            sys.stderr.flush()
        output = await proc.stdout.readline()
    await proc.wait()


def output_version():
    print("Rucio tool: build_images.py, copyright 2020-2021 CERN, version", '.'.join(map(str, VERSION)))
    sys.exit(0)


def test_version(args):
    try:
        parsed_version = tuple(map(int, str(args.version_test).split('.')))
    except ValueError:
        print("Cannot parse version:", args.version_test)
        sys.exit(1)

    if parsed_version <= VERSION:
        sys.exit(0)
    else:
        sys.exit(1)


async def wrap_build(
    name: str,
    dist: str,
    buildargs: "BuildArgs",
    filtered_buildargs: "Dict[str, str]",
    script_args: "argparse.Namespace",
) -> "Dict[str, Any]":

    use_podman = 'USE_PODMAN' in os.environ and os.environ['USE_PODMAN'] == '1'
    memlog = io.StringIO()
    error, dockerfile, build_context = None, None, None
    try:
        if buildargs.IMAGE_IDENTIFIER == 'integration-test' and buildargs.PYTHON == '3.6':
            dockerfile = 'Dockerfile'
            build_context = str(script_args.buildfiles_dir)
        elif buildargs.IMAGE_IDENTIFIER == 'autotest':
            dockerfile = f'{dist}.Dockerfile'
            build_context = '.'
        else:
            error = "Error defining build arguments from " + str(buildargs)

        if not error:
            await build_image(
                name=name,
                dockerfile=dockerfile,
                build_context=build_context,
                buildargs=filtered_buildargs,
                use_podman=use_podman,
                cache_repo=script_args.cache_repo,
                no_cache=script_args.build_no_cache,
                containerfiles_dir=script_args.buildfiles_dir,
                push_cache=script_args.push_cache,
                verbose=script_args.verbose,
                logfile=memlog,
            )
    except Exception as e:
        error = e
    return {'name': name, 'log': memlog, 'error': error}


async def join_builds(build_futures: "List[Awaitable[Dict[str, Any]]]"):
    for future in asyncio.as_completed(build_futures):
        wrapper_result = await future

        sys.stderr.write(f"\nbuild '{wrapper_result['name']}' output:\n")
        sys.stderr.writelines(wrapper_result['log'].readlines())
        bufferend = wrapper_result['log'].read()
        if bufferend:
            sys.stderr.write(bufferend)
            if bufferend[-1] != "\n":
                sys.stderr.write("%\n")
        sys.stderr.flush()
        wrapper_result['log'].close()

        if wrapper_result['error']:
            error = wrapper_result['error']
            print(
                f"building '{wrapper_result['name']}' errored with "
                f"{traceback.format_exception_only(error.__class__, error)}",
                file=sys.stderr,
                flush=True,
            )
        else:
            print(f"building '{wrapper_result['name']}' complete", file=sys.stderr, flush=True)


def main():
    loop = asyncio.get_event_loop()

    parser = argparse.ArgumentParser(description='Build images according to the test matrix read from stdin.')
    parser.add_argument('buildfiles_dir', metavar='build directory', type=str, default='.',
                        help='the directory of Dockerfiles')
    parser.add_argument('-o', '--output', dest='output', type=str, choices=['list', 'dict'], default='dict',
                        help='the output of this command')
    parser.add_argument('-n', '--build-no-cache', dest='build_no_cache', action='store_true',
                        help='build images without cache')
    parser.add_argument('-r', '--cache-repo', dest='cache_repo', type=str, default='ghcr.io/rucio/rucio',
                        help='use the following cache repository, like ghcr.io/USER/REPO')
    parser.add_argument('-p', '--push-cache', dest='push_cache', action='store_true',
                        help='push the images to the cache repo')
    parser.add_argument('-b', '--branch', dest='branch', type=str, default='master',
                        help='the branch used to build the images from (used for the image name)')
    parser.add_argument('--version', dest='version', action='store_true',
                        help='returns the version and exits')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='increases output verbosity')
    parser.add_argument('--version-test', dest='version_test', type=str, required=False,
                        help='tests if the scripts version is equal or higher than the given version and exits with '
                             'code 0 if true, 1 otherwise')
    script_args = parser.parse_args()

    if script_args.version:
        output_version()
    elif script_args.version_test:
        test_version(script_args)

    matrix = json.load(sys.stdin)
    matrix = (matrix,) if isinstance(matrix, dict) else matrix

    filter_build_args = partial(
        map, lambda argdict: {arg: val for arg, val in argdict.items() if arg in BUILD_ARG_KEYS}
    )
    make_buildargs = partial(map, lambda argdict: BuildArgs(**argdict))
    dist_buildargs_generators = map(
        lambda t: ((t[0], ba) for ba in set(make_buildargs(filter_build_args(t[1])))),
        itertools.groupby(matrix, lambda d: d[DIST_KEY]),
    )
    flattened_dist_buildargs: "List[Tuple[str, BuildArgs]]" = list(
        itertools.chain.from_iterable(dist_buildargs_generators)
    )

    if len(flattened_dist_buildargs) >= IMAGE_BUILD_COUNT_LIMIT:
        print(
            f"Won't build {len(flattened_dist_buildargs)} images (> {IMAGE_BUILD_COUNT_LIMIT}).\n"
            f"Either there was a problem with the test matrix or the limit should be increased.",
            file=sys.stderr,
        )
        sys.exit(2)

    build_futures = list()
    images = dict()
    for dist, buildargs in flattened_dist_buildargs:
        filtered_buildargs = buildargs._asdict()
        del filtered_buildargs['IMAGE_IDENTIFIER']
        name = imagetag(
            dist=dist,
            buildargs=filtered_buildargs,
            image_identifier=buildargs.IMAGE_IDENTIFIER,
            branch=script_args.branch,
            cache_repo=script_args.cache_repo,
        )
        if script_args.verbose:
            print(f"starting build for tag '{name}'", file=sys.stderr, flush=True)
        build_futures.append(asyncio.ensure_future(wrap_build(name, dist, buildargs, filtered_buildargs, script_args)))
        images[name] = {DIST_KEY: dist, **buildargs._asdict()}

    loop.run_until_complete(join_builds(build_futures))

    if script_args.output == 'dict':
        json.dump(images, sys.stdout)
    elif script_args.output == 'list':
        json.dump(list(images.keys()), sys.stdout)


if __name__ == "__main__":
    main()
