# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from test_utils import CharmTestCase
import odl_utils

TO_PATCH = [
    'apt_install',
    'filter_installed_packages',
    'os_release',
]


class VPPUtilsTest(CharmTestCase):

    def setUp(self):
        super(VPPUtilsTest, self).setUp(odl_utils, TO_PATCH)

    def tearDown(self):
        super(VPPUtilsTest, self).tearDown()

    def test_install_packages(self):
        def _filter(pkg_list):
            return pkg_list
        self.filter_installed_packages.side_effect = _filter
        self.os_release.return_value = 'icehouse'
        odl_utils.install_packages('neutron-api')
        self.apt_install.assert_called_with(['neutron-common',
                                             'neutron-plugin-ml2'],
                                            fatal=True)

    def test_install_packages_kilo(self):
        def _filter(pkg_list):
            return pkg_list
        self.filter_installed_packages.side_effect = _filter
        self.os_release.return_value = 'kilo'
        odl_utils.install_packages('neutron-api')
        self.apt_install.assert_called_with(['neutron-common',
                                             'neutron-plugin-ml2',
                                             'python-networking-odl'],
                                            fatal=True)

    def test_determine_packages(self):
        self.assertEqual(odl_utils.determine_packages(),
                         ['neutron-common', 'neutron-plugin-ml2'])
