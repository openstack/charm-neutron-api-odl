import json
from charmhelpers.core.services import helpers
from charmhelpers.core.hookenv import(
    config,
)

VLAN = 'vlan'
VXLAN = 'vxlan'
GRE = 'gre'
OVERLAY_NET_TYPES = [VXLAN, GRE]


class NeutronApiSDNRelation(helpers.RelationContext):
    name = 'neutron-plugin-api-subordinate'
    interface = 'neutron-plugin-api-subordinate'

    def provide_data(self):
        # Add sections and tuples to insert values into neutron-server's
        # neutron.conf e.g.
        # principle_config = {
        #     "neutron-api": {
        #        "/etc/neutron/neutron.conf": {
        #             "sections": {
        #                 'DEFAULT': [
        #                     ('key1', 'val1')
        #                     ('key2', 'val2')
        #                 ],
        #                 'agent': [
        #                     ('key3', 'val3')
        #                 ],
        #             }
        #         }
        #     }
        # }

        principle_config = {
            "neutron-api": {
                "/etc/neutron/neutron.conf": {
                    "sections": {
                        'DEFAULT': [
                        ],
                    }
                }
            }
        }
        relation_info = {
            'neutron-plugin': 'odl',
            'core-plugin': 'neutron.plugins.ml2.plugin.Ml2Plugin',
            'neutron-plugin-config': '/etc/neutron/plugins/ml2/ml2_conf.ini',
            'service-plugins': 'router,firewall,lbaas,vpnaas,metering',
            'subordinate_configuration': json.dumps(principle_config),
        }
        return relation_info


class ODLControllerRelation(helpers.RelationContext):
    name = 'odl-controller'
    interface = 'odl-controller-api'

    def get_first_data(self):
        if self.get('odl-controller') and len(self['odl-controller']):
            return self['odl-controller'][0]
        else:
            return {}

    def get_data(self):
        super(ODLControllerRelation, self).get_data()
        first_contoller = self.get_first_data()
        # XXX Should be using a VIP (odl doesn't provide one yet) rather than
        # first nodes private-address
        self['odl_ip'] = first_contoller.get('private-address')
        self['odl_port'] = first_contoller.get('port')
        self['odl_username'] = first_contoller.get('username')
        self['odl_password'] = first_contoller.get('password')

    def is_ready(self):
        if 'password' in self.get_first_data():
            return True
        else:
            return False


class ConfigTranslation(dict):
    def __init__(self):
        self['vlan_ranges'] = config('vlan-ranges')
        self['overlay_network_type'] = self.get_overlay_network_type()
        self['security_groups'] = config('security-groups')

    def get_overlay_network_type(self):
        overlay_networks = config('overlay-network-type').split()
        for overlay_net in overlay_networks:
            if overlay_net not in OVERLAY_NET_TYPES:
                raise ValueError('Unsupported overlay-network-type %s'
                                 % overlay_net)
        return ','.join(overlay_networks)
