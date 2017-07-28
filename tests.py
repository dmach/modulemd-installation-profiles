#/usr/bin/python3
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


import unittest

import os
import sys
import copy


from modulemd_profile import InstallationProfile, ModuleDefaults


class TestBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # SERVER - 26-5
        server = InstallationProfile()
        server.name = "fedora-server"
        server.version = "26"
        server.release = 5
        server.description = "Fedora 26 Server"
        cls.server_26_5 = server

        d = ModuleDefaults()
        d.module_name = "base-runtime"
        d.available_streams.extend(["f26", "f27", "rawhide"])
        d.default_stream = "f26"
        d.default_profiles.set("f26", ["buildroot", "container"])
        d.default_profiles.set("f27", [])
        d.default_profiles.set("rawhide", None)
        server.add_module_defaults(d)

        d = ModuleDefaults()
        d.module_name = "httpd"
        d.available_streams.extend(["2.2", "2.4"])
        d.default_stream = "2.4"
        server.add_module_defaults(d)

        d = ModuleDefaults()
        d.module_name = "postgresql"
        d.available_streams.extend(["9.6"])
        d.default_stream = "9.6"
        d.default_profiles.set("9.6", ["server", "client"])
        server.add_module_defaults(d)

        cls.server_261_1 = copy.deepcopy(cls.server_26_5)
        cls.server_261_1.version = "26.1"
        cls.server_261_1.release = 1

        cls.server_261_2 = copy.deepcopy(cls.server_26_5)
        cls.server_261_2.version = "26.1"
        cls.server_261_2.release = 2

        # WORKSTATION - 26-2
        workstation = InstallationProfile()
        workstation.name = "fedora-workstation"
        workstation.version = "26"
        workstation.release = 2
        workstation.description = "Fedora 26 Workstation"
        cls.workstation_26_2 = workstation

        d = ModuleDefaults()
        d.module_name = "base-runtime"
        d.available_streams.extend(["f26", "f27", "rawhide"])
        d.default_stream = "f26"
        d.default_profiles.set("f26", ["container"])
        workstation.add_module_defaults(d)

        d = ModuleDefaults()
        d.module_name = "postgresql"
        d.available_streams.extend(["9.6"])
        d.default_stream = "9.6"
        d.default_profiles.set("9.6", ["client"])
        workstation.add_module_defaults(d)

        # WORKSTATION - 27-1
        workstation = InstallationProfile()
        workstation.name = "fedora-workstation"
        workstation.version = "27"
        workstation.release = 1
        workstation.description = "Fedora 27 Workstation"
        cls.workstation_27_1 = workstation

        d = ModuleDefaults()
        d.module_name = "base-runtime"
        d.available_streams.extend(["f27", "rawhide"])
        d.default_stream = "f27"
        workstation.add_module_defaults(d)

        d = ModuleDefaults()
        d.module_name = "postgresql"
        d.available_streams.extend(["9.6", "10.0"])
        d.default_stream = "10.0"
        d.default_profiles.set("9.6", ["client"])
        d.default_profiles.set("10.0", ["client"])
        workstation.add_module_defaults(d)

    def test_cmp_version_major(self):
        defaults = [self.workstation_26_2, self.workstation_27_1]
        latest = max(defaults)
        self.assertEqual(latest, self.workstation_27_1)

        latest = max(defaults[::-1])
        self.assertEqual(latest, self.workstation_27_1)

    def test_cmp_version_minor(self):
        defaults = [self.server_26_5, self.server_261_1]
        latest = max(defaults)
        self.assertEqual(latest, self.server_261_1)

        latest = max(defaults[::-1])
        self.assertEqual(latest, self.server_261_1)

    def test_cmp_release(self):
        defaults = [self.server_261_1, self.server_261_2]
        latest = max(defaults)
        self.assertEqual(latest, self.server_261_2)

        latest = max(defaults[::-1])
        self.assertEqual(latest, self.server_261_2)

    def test_cmp_invalid(self):
        defaults = [self.server_26_5, self.workstation_26_2]
        self.assertRaises(ValueError, max, defaults)

    def test_installation_profile(self):
        server = self.server_26_5
        self.assertEqual(server.name, "fedora-server")
        self.assertEqual(server.version, "26")
        self.assertEqual(server.release, 5)

        base = server["base-runtime"]
        self.assertEqual(base.available_streams, ["f26", "f27", "rawhide"])
        self.assertEqual(base.default_stream, "f26")

        # base-runtime will buildroot and container default profiles on f26
        f26 = base.default_profiles["f26"]
        self.assertEqual(f26, set(["buildroot", "container"]))

        # base-runtime will have no default profile on f27
        f27 = base.default_profiles["f27"]
        self.assertEqual(f27, set([]))

        # nothing overriden on rawhide
        self.assertRaises(KeyError, base.default_profiles.__getitem__, "rawhide")


if __name__ == "__main__":
    unittest.main()
