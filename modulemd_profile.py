# -*- coding: utf-8 -*-


# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
Installation profiles for modules.

See tests for usage.

Example:
data:
  description: Fedora 26 Server                 # verbose description, to be used in Anaconda, PackageKit, etc.
  modules:
    base-runtime:                               # module name
      available-streams: [f26, f27, rawhide]    # available streams, DNF will hide other steams from list
      default-profiles:                         # override default profiles specified in modulemd; not listed here -> no change (e.g. rawhide)
        f26: [buildroot, container]
        f27: []
      default-stream: f26                       # default stream
    httpd:
      available-streams: ['2.2', '2.4']
      default-profiles: {}
      default-stream: '2.4'
    postgresql:
      available-streams: ['9.6']
      default-profiles:
        '9.6': [client, server]
      default-stream: '9.6'
  name: fedora-server                           # N part of N-V-R
  release: 26                                   # R part of N-V-R
  version: '26'                                 # V part of N-V-R
document: modulemd-profile                      # metadata/document indentifier
version: 0                                      # metadata format version


Features:
* unique identity: N-V-R
* upgrade paths:
  * fedora-server-26-1 -> fedora-server-26-2
  * fedora-server-26-1 -> fedora-server-26.1-1
  * fedora-server-26.1-1 -> fedora-server-26.2-1
  * fedora-server-26.2-1 -> fedora-server-27-1


Open questions:
* Add 'arch' field to allow per-arch defaults?
* Available steams - allow installing *any* explicitly specified module even if it's stream is not on the list?
* List of modules / streams to be installed by default?


TODO:
* validate field types
* validate values
* define NVR policy
* enforce NVR policy
* implement load() and loadd() methods
* put (possibly the latest) installation profiles into repodata
* reimplement everything in C to make it available to libdnf, createrepo_c etc.
"""

import sys
from functools import total_ordering

import yaml


class DefaultProfiles(dict):

    def add(self, stream, profile):
        self.setdefault(stream, set()).add(profile)

    def set(self, stream, profiles):
        if profiles is None:
            self.pop(stream, None)
            return
        self[stream] = set(profiles)

    def dumpd(self):
        result = {}
        for key, value in self.items():
            result[key] = sorted(value)
        return result

    def loadd(self, d):
        self.clear()
        for key, value in d.items():
            self[key] = set(value)


class ModuleDefaults(object):
    def __init__(self):
        self.module_name = None
        self.available_streams = []
        self.default_stream = None
        self.default_profiles = DefaultProfiles()

    def dump(self, *args, **kwargs):
        return yaml.dump(self.dumpd(), *args, **kwargs)

    def dumpd(self):
        assert self.default_stream and self.default_stream in self.available_streams
        data = {
            "default-stream": self.default_stream,
            "available-streams": sorted(set(self.available_streams)),
            "default-profiles": self.default_profiles.dumpd()
        }
        result = {self.module_name: data}
        return result


@total_ordering
class InstallationProfile(dict):
    def __init__(self):
        self.name = None
        self.version = None
        self.release = None
        self.description = None

    def __eq__(self, other):
        if self.name != other.name:
            raise ValueError("Can't compare installation profiles with different names")
        return self.version == other.version and self.release == other.release

    def __lt__(self, other):
        if self.name != other.name:
            raise ValueError("Can't compare installation profiles with different names")
        if self.split_version < other.split_version:
            return True
        if self.split_version > other.split_version:
            return False
        if int(self.release) < int(other.release):
            return True
        if int(self.release) < int(other.release):
            return False
        return 0

    @property
    def split_version(self):
        return [int(i) for i in self.version.split(".")]

    def add_module_defaults(self, module_defaults):
        self[module_defaults.module_name] = module_defaults

    def dump(self, *args, **kwargs):
        return yaml.dump(self.dumpd(), *args, **kwargs)

    def dumpd(self):
        data = {
            "name": self.name,
            "version": self.version,
            "release": int(self.version),
            "description": self.description,
            "modules": {},
        }

        for key, value in self.items():
            data["modules"].update(value.dumpd())

        result = {
            "document": "modulemd-profile",
            "version": 0,
            "data": data,
        }
        return result
