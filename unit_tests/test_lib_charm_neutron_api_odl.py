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

from __future__ import absolute_import
from __future__ import print_function

import mock
import charms_openstack.test_utils as test_utils

import charm.openstack.neutron_api_odl as neutron_api_odl


class Helper(test_utils.PatchHelper):

    def setUp(self):
        super().setUp()
        self.patch_release(neutron_api_odl.IcehouseNeutronAPIODLCharm.release)


class TestCustomProperties(Helper):

    def test_overlay_net_types(self):
        config = mock.MagicMock()
        for v in ['gre', 'gre vxlan', 'vxlan']:
            config.overlay_network_type = v
            neutron_api_odl.overlay_net_types(config)
        # ensure that it fails
        with self.assertRaises(ValueError):
            config.overlay_network_type = 'fail-me'
            neutron_api_odl.overlay_net_types(config)


class TestNeutronAPIODLCharm(Helper):

    def test_all_packages(self):
        self.patch_object(neutron_api_odl.ch_utils, 'os_release')
        self.os_release.return_value = 'kilo'
        c = neutron_api_odl.KiloNeutronAPIODLCharm()
        self.assertEqual(
            c.all_packages,
            ['neutron-common', 'neutron-plugin-ml2', 'python-networking-odl'])

    def test_configure_plugin(self):
        principle_interface = mock.MagicMock()
        self.patch_object(neutron_api_odl.ch_utils, 'os_release')
        self.os_release.return_value = 'icehouse'
        c = neutron_api_odl.IcehouseNeutronAPIODLCharm()
        c.configure_plugin(principle_interface)
        config_dict = {
            'neutron-api': {
                '/etc/neutron/neutron.conf': {'sections': {'DEFAULT': []}}}}
        principle_interface.configure_plugin.assert_called_once_with(
            neutron_plugin='odl',
            core_plugin='neutron.plugins.ml2.plugin.Ml2Plugin',
            neutron_plugin_config='/etc/neutron/plugins/ml2/ml2_conf.ini',
            service_plugins='router,firewall,lbaas,vpnaas,metering',
            subordinate_configuration=config_dict)

    def test_configure_plugin_newton(self):
        principle_interface = mock.MagicMock()
        self.patch_object(neutron_api_odl.ch_utils, 'os_release')
        self.os_release.return_value = 'newton'
        c = neutron_api_odl.NewtonNeutronAPIODLCharm()
        c.configure_plugin(principle_interface)
        config_dict = {
            'neutron-api': {
                '/etc/neutron/neutron.conf': {'sections': {'DEFAULT': []}}}}
        principle_interface.configure_plugin.assert_called_once_with(
            neutron_plugin='odl',
            core_plugin='neutron.plugins.ml2.plugin.Ml2Plugin',
            neutron_plugin_config='/etc/neutron/plugins/ml2/ml2_conf.ini',
            service_plugins=('router,firewall,vpnaas,metering,'
                             'neutron_lbaas.services.loadbalancer.'
                             'plugin.LoadBalancerPluginv2'),
            subordinate_configuration=config_dict)
