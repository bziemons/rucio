#!/usr/bin/env python3
# Copyright 2018 CERN for the benefit of the ATLAS collaboration.
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

import functools
import itertools
import sys
import typing
import json

import yaml

mapping = {'dists': 'DIST', 'python': 'PYTHON', 'suites': 'SUITE'}


def readobj(key: str, val: typing.Dict, exclude: typing.List, whitelist: typing.List):
    if not isinstance(val, dict):
        return str(val)
    if "id" not in val:
        raise ValueError("Missing field id in entry " + str(val))
    if "blacklist" in val:
        new_exclude_dict = {mapping.get(key, key): val["id"],
                            **{mapping.get(k, k): v for k, v in val["blacklist"].items()}}
        for k, v in new_exclude_dict.items():
            if isinstance(v, list):
                for vi in v[1:]:
                    exclude.append({**new_exclude_dict, k: vi})
                new_exclude_dict[k] = v[0]
        exclude.append(new_exclude_dict)
    if "whitelist" in val:
        new_include_dict = {mapping.get(k, k): (v,) if not isinstance(v, list) else v for k, v in val["whitelist"].items()}
        whitelist.append({"key": mapping.get(key, key), "value": val["id"], "allowed": new_include_dict})
    return val["id"]


def main():
    input_conf = dict(yaml.safe_load(sys.stdin))
    exclude = []
    whitelist = []
    output_conf = {mapping.get(key, key): [readobj(key, val, exclude, whitelist) for val in input_conf[key]]
                   for key in input_conf.keys()}
    product_dicts = map(lambda d: functools.reduce(lambda d1, d2: {**d1, **d2}, d),
                        itertools.product(*map(lambda k: ({k[0]: v} for v in k[1]), output_conf.items())))
    product_dicts = filter(lambda pd: all(map(lambda wl: (wl["key"] not in pd
                                                          or wl["value"] != pd[wl["key"]]
                                                          or all(map(lambda a: (a[0] not in pd or pd[a[0]] in a[1]),
                                                                     wl["allowed"].items()))),
                                              whitelist)),
                           product_dicts)
    product_dicts = filter(lambda pd: not any(map(lambda e: all(map(lambda kv: (kv[0] in pd and pd[kv[0]] == kv[1]),
                                                                e.items())),
                                              exclude)),
                           product_dicts)

    print(json.dumps(list(product_dicts)), file=sys.stdout)


if __name__ == "__main__":
    main()
