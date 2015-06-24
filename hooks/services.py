from functools import partial
from charmhelpers.core import hookenv
from charmhelpers.core import host
from charmhelpers.core.services.base import ServiceManager
from charmhelpers.core.services import helpers
from charmhelpers.contrib.openstack.templating import os_template_dirs
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
                    template_searchpath=os_template_dirs('templates/',
                                                         release),
                    target='/etc/neutron/plugins/ml2/ml2_conf.ini',
                    on_change_action=(partial(remote_restart,
                                              'neutron-plugin-api-subordinate',
                                              'neutron-server')),
                ),
            ]
        },
    ])
    manager.manage()
