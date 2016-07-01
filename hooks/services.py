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

from functools import partial
from charmhelpers.core import hookenv
from charmhelpers.core.services.base import ServiceManager
from charmhelpers.core.services import helpers
from charmhelpers.contrib.openstack.templating import get_loader
from charmhelpers.contrib.openstack.utils import os_release, remote_restart

import odl_utils
import odl_data


def manage():
    config = hookenv.config()
    release = os_release('neutron-common')
    manager = ServiceManager([
        # Actions which have no prerequisites and can be rerun
        {
            'service': 'odl-setup',
            'data_ready': [
                odl_utils.install_packages,
            ],
            'provided_data': [
                odl_data.NeutronApiSDNRelation(),
            ],
        },
        {
            'service': 'api-render',
            'required_data': [
                odl_data.ODLControllerRelation(),
                config,
                odl_data.ConfigTranslation(),
            ],
            'data_ready': [
                helpers.render_template(
                    source='ml2_conf.ini',
                    template_loader=get_loader('templates/', release),
                    target='/etc/neutron/plugins/ml2/ml2_conf.ini',
                    on_change_action=(partial(remote_restart,
                                              'neutron-plugin-api-subordinate',
                                              'neutron-server')),
                ),
            ]
        },
    ])
    manager.manage()
