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

import json
import os
import pathlib
import subprocess
import sys


def main():
    images = json.load(sys.stdin)
    assert isinstance(images, dict), "Passed images must be a JSON object"

    images_path = pathlib.Path("images/")
    os.chdir(images_path)
    for img in images.keys():
        archive = f"{img[img.rfind(':')+1:]}.tar.xz"
        args = ("sh", "-c", f"xzcat {archive} | docker image load {img}")
        print("Running", *args, file=sys.stderr)
        subprocess.check_call(args)


if __name__ == "__main__":
    main()
