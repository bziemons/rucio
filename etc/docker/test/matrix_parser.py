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
import json
import sys
import typing

import yaml

mapping = {'dists': 'DIST', 'python': 'PYTHON', 'suites': 'SUITE'}


def extract_mapped_list(inp: typing.Dict):
    return {mapping.get(key, key): [val] if not isinstance(val, list) else val for key, val in inp.items()}


def readobj(key: str, val: typing.Dict, exclude: typing.List, whitelist: typing.List):
    if not isinstance(val, dict):
        return str(val)
    if "id" not in val:
        raise ValueError("Missing field id in entry " + str(val))
    itemid = val["id"]
    del val["id"]

    if "blacklist" in val:
        # blacklist is an object that contains one or more entries per entry.
        # the entries are matched against the matrix
        new_exclude_dict = {mapping.get(key, key): itemid, **extract_mapped_list(val["blacklist"])}
        for blkey, v in new_exclude_dict.items():
            for vi in v[1:]:
                exclude.append({**new_exclude_dict, blkey: vi})
            new_exclude_dict[blkey] = v[0]
        exclude.append(new_exclude_dict)
        del val["blacklist"]
    if "whitelist" in val:
        whitelist.append({"key": mapping.get(key, key), "value": itemid,
                          "allowed": extract_mapped_list(val["whitelist"])})
        del val["whitelist"]

    if len(val.keys()) == 0:
        return itemid
    else:
        return itemid, val


def main():
    input_conf = dict(yaml.safe_load(sys.stdin))
    exclude = []
    whitelist = []
    mappedkeyvalues = {mapping.get(key, key): [readobj(key, val, exclude, whitelist) for val in input_conf[key]]
                       for key in input_conf.keys()}
    product_dicts = map(lambda d: functools.reduce(lambda d1, d2: {**d1, **d2}, d),
                        itertools.product(*map(lambda k: ({k[0]: v} for v in k[1]), mappedkeyvalues.items())))

    newproduct_dicts = list()
    for pdo in product_dicts:
        extraval_dict = {key: val for key, val in pdo.items() if isinstance(val, tuple)}
        statics = {key: val for key, val in pdo.items() if key not in extraval_dict}
        if len(extraval_dict) == 0:
            newproduct_dicts.append(statics)
        else:
            for extrakey, extraval in extraval_dict.items():
                normval, extra = extraval
                extra = extract_mapped_list(extra)
                for values in itertools.product(*extra.values()):
                    newproduct_dicts.append({**statics, extrakey: normval, **dict(zip(extra.keys(), values))})
    product_dicts = newproduct_dicts

    # apply whitelist
    product_dicts = filter(lambda pd: all(map(lambda wl: (wl["key"] not in pd
                                                          or wl["value"] != pd[wl["key"]]
                                                          or all(map(lambda a: (a[0] not in pd or pd[a[0]] in a[1]),
                                                                     wl["allowed"].items()))),
                                              whitelist)),
                           product_dicts)
    # apply blacklist
    product_dicts = filter(lambda pd: not any(map(lambda e: all(map(lambda kv: (kv[0] in pd and pd[kv[0]] == kv[1]),
                                                                    e.items())),
                                                  exclude)),
                           product_dicts)

    print(json.dumps(list(product_dicts)), file=sys.stdout)


if __name__ == "__main__":
    main()
