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

from charmhelpers.fetch import (
    apt_install,
    filter_installed_packages,
)

from charmhelpers.contrib.openstack.utils import os_release

NEUTRON_CONF_DIR = "/etc/neutron"
NEUTRON_CONF = '%s/neutron.conf' % NEUTRON_CONF_DIR
ML2_CONF = '%s/plugins/ml2/ml2_conf.ini' % NEUTRON_CONF_DIR

# Packages to be installed by charm.
#     common: Installed everywhere
#     api: Installed on neutron-api (neutron-server) units
#     compute: Installed on nova compute nodes
#     purge: Packages to be removed

PACKAGES = ['neutron-common', 'neutron-plugin-ml2']


def install_packages(servicename):
    pkgs = determine_packages()
    if os_release('neutron-common') >= 'kilo':
        pkgs.extend(['python-networking-odl'])
    pkgs = filter_installed_packages(pkgs)
    apt_install(pkgs, fatal=True)


def determine_packages(node_type=None):
    return PACKAGES
