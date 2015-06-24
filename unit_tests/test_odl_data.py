from test_utils import CharmTestCase
from mock import patch
import odl_data
import charmhelpers
import charmhelpers.core.services.helpers
import json
TO_PATCH = [
    'config',
]


def fake_context(settings):
    def outer():
        def inner():
            return settings
        return inner
    return outer


FULL_ODLCTRL = {
    'data': {
        'private-address': '10.0.0.27',
        'port': '8080',
        'username': 'odluser',
        'password': 'hardpassword',
    },
    'rids': ['odl-controller:2'],
    'runits': ['odl-controller/0'],
}

MISSING_DATA_ODLCTRL = {
    'data': {
        'private-address': '10.0.0.27',
    },
    'rids': ['odl-controller:2'],
    'runits': ['odl-controller/0'],
}


class NeutronApiSDNRelationTest(CharmTestCase):

    def setUp(self):
        super(NeutronApiSDNRelationTest, self).setUp(odl_data, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(NeutronApiSDNRelationTest, self).tearDown()

    @patch.object(charmhelpers.core.hookenv, 'relation_get')
    @patch.object(charmhelpers.core.hookenv, 'related_units')
    @patch.object(charmhelpers.core.hookenv, 'relation_ids')
    def test_provide_data(self, _hrids, _hrunits, _hrget):
        sdn_relation = odl_data.NeutronApiSDNRelation()
        expect = {
            'core-plugin': 'neutron.plugins.ml2.plugin.Ml2Plugin',
            'neutron-plugin': 'odl',
            'neutron-plugin-config': '/etc/neutron/plugins/ml2/ml2_conf.ini',
            'service-plugins': 'router,firewall,lbaas,vpnaas,metering',
        }
        provide_data = sdn_relation.provide_data()
        for key in expect.keys():
            self.assertEqual(provide_data[key], expect[key])
        # Check valid json is being passed
        principle_config = json.loads(
            provide_data['subordinate_configuration']
        )
        self.assertEqual(principle_config['neutron-api'].keys()[0],
                         '/etc/neutron/neutron.conf')


class ODLControllerRelationTest(CharmTestCase):

    def setUp(self):
        super(ODLControllerRelationTest, self).setUp(odl_data, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(ODLControllerRelationTest, self).tearDown()

    @patch.object(charmhelpers.core.hookenv, 'relation_get')
    @patch.object(charmhelpers.core.hookenv, 'related_units')
    @patch.object(charmhelpers.core.hookenv, 'relation_ids')
    def get_odlrel(self, _hrids, _hrunits, _hrget, relinfo=None):
        _hrids.return_value = relinfo['rids']
        _hrunits.return_value = relinfo['runits']
        self.test_relation.set(relinfo['data'])
        _hrget.side_effect = self.test_relation.get
        odl_rel = odl_data.ODLControllerRelation()
        odl_rel.get_data()
        return odl_rel

    def test_get_first_data(self):
        odl_rel = self.get_odlrel(relinfo=FULL_ODLCTRL)
        expect = {
            'private-address': '10.0.0.27',
            'port': '8080',
            'username': 'odluser',
            'password': 'hardpassword',
        }
        first_data = odl_rel.get_first_data()
        for key in expect.keys():
            self.assertEqual(first_data[key], expect[key])

    def test_get_data(self):
        odl_rel = self.get_odlrel(relinfo=FULL_ODLCTRL)
        expect = {
            'odl_ip': '10.0.0.27',
            'odl_port': '8080',
            'odl_username': 'odluser',
            'odl_password': 'hardpassword',
        }
        for key in expect.keys():
            self.assertEqual(odl_rel[key], expect[key])

    def test_is_ready(self):
        odl_rel = self.get_odlrel(relinfo=FULL_ODLCTRL)
        self.assertEqual(odl_rel.is_ready(), True)

    def test_is_ready_incomplete(self):
        odl_rel = self.get_odlrel(relinfo=MISSING_DATA_ODLCTRL)
        self.assertEqual(odl_rel.is_ready(), False)


class ConfigTranslationTest(CharmTestCase):

    def setUp(self):
        super(ConfigTranslationTest, self).setUp(odl_data, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(ConfigTranslationTest, self).tearDown()

    def test_config_default(self):
        ctxt = odl_data.ConfigTranslation()
        self.assertEqual(ctxt, {'use_syslog': False,
                                'vlan_ranges': 'physnet1:1000:2000',
                                'overlay_network_type': 'gre'})

        self.test_config.set('use-syslog', True)
        ctxt = odl_data.ConfigTranslation()
        self.assertEqual(ctxt, {'use_syslog': True,
                                'vlan_ranges': 'physnet1:1000:2000',
                                'overlay_network_type': 'gre'})

        self.test_config.set('vlan-ranges', 'physnet1:1000:3000')
        ctxt = odl_data.ConfigTranslation()
        self.assertEqual(ctxt, {'use_syslog': True,
                                'vlan_ranges': 'physnet1:1000:3000',
                                'overlay_network_type': 'gre'})

        self.test_config.set('overlay-network-type', 'vxlan')
        ctxt = odl_data.ConfigTranslation()
        self.assertEqual(ctxt, {'use_syslog': True,
                                'vlan_ranges': 'physnet1:1000:3000',
                                'overlay_network_type': 'vxlan'})
