from test_utils import CharmTestCase
from mock import patch
import vpp_data
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


FULL_AMQP = {
    'data': {
        'password': '123',
        'private-address': '10.0.0.10',
    },
    'rids': ['amqp:2'],
    'runits': ['rabbitmq-server/0'],
}

MISSING_DATA_AMQP = {
    'data': {},
    'rids': ['amqp:2'],
    'runits': ['rabbitmq-server/0'],
}

FULL_NPAPI = {
    'data': {
        'overlay-network-type': 'gre',
        'network-device-mtu': '1200',
    },
    'rids': ['neutron-plugin-api:2'],
    'runits': ['neutron-api/0'],
}

NOMTU_NPAPI = {
    'data': {
        'overlay-network-type': 'gre',
    },
    'rids': ['neutron-plugin-api:2'],
    'runits': ['neutron-api/0'],
}

MISSING_DATA_NPAPI = {
    'data': {},
    'rids': ['neutron-plugin-api:2'],
    'runits': ['neutron-api/0'],
}

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


class AMQPRelationTest(CharmTestCase):

    def setUp(self):
        super(AMQPRelationTest, self).setUp(vpp_data, TO_PATCH)
        self.config.side_effect = self.test_config.get
        self.test_config.set('debug', True)
        self.test_config.set('verbose', True)
        self.test_config.set('rabbit-user', 'neut')
        self.test_config.set('rabbit-vhost', 'os')

    def tearDown(self):
        super(AMQPRelationTest, self).tearDown()

    @patch.object(charmhelpers.contrib.openstack.context, 'config')
    @patch.object(charmhelpers.contrib.openstack.context, 'relation_get')
    @patch.object(charmhelpers.contrib.openstack.context, 'related_units')
    @patch.object(charmhelpers.contrib.openstack.context, 'relation_ids')
    @patch.object(charmhelpers.core.hookenv, 'relation_get')
    @patch.object(charmhelpers.core.hookenv, 'related_units')
    @patch.object(charmhelpers.core.hookenv, 'relation_ids')
    def get_amqprel(self, _hrids, _hrunits, _hrget, _crids, _crunits,
                    _crget, _cconfig, relinfo=None):
        _hrids.return_value = relinfo['rids']
        _crids.return_value = relinfo['rids']
        _hrunits.return_value = relinfo['runits']
        _crunits.return_value = relinfo['runits']
        self.test_relation.set(relinfo['data'])
        _hrget.side_effect = self.test_relation.get
        _crget.side_effect = self.test_relation.get
        _cconfig.side_effect = self.test_config.get
        amqp_rel = vpp_data.AMQPRelation()
        amqp_rel.get_data()
        return amqp_rel

    def test_get_data(self):
        amqp_rel = self.get_amqprel(relinfo=FULL_AMQP)
        self.assertEqual(amqp_rel['rabbitmq_password'], '123')
        self.assertEqual(amqp_rel['amqp'][0]['password'], '123')

    def test_provide_data(self):
        amqp_rel = self.get_amqprel(relinfo=FULL_AMQP)
        self.assertEqual(amqp_rel.provide_data(), {'username': 'neut',
                                                   'vhost': 'os'})

    def test_is_ready_empty_context(self):
        amqp_rel = self.get_amqprel(relinfo=MISSING_DATA_AMQP)
        self.assertEqual(amqp_rel.is_ready(), False)

    def test_is_ready_context(self):
        amqp_rel = self.get_amqprel(relinfo=FULL_AMQP)
        self.assertEqual(amqp_rel.is_ready(), True)


class NeutronApiSDNRelationTest(CharmTestCase):

    def setUp(self):
        super(NeutronApiSDNRelationTest, self).setUp(vpp_data, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(NeutronApiSDNRelationTest, self).tearDown()

    @patch.object(charmhelpers.core.hookenv, 'relation_get')
    @patch.object(charmhelpers.core.hookenv, 'related_units')
    @patch.object(charmhelpers.core.hookenv, 'relation_ids')
    def test_provide_data(self, _hrids, _hrunits, _hrget):
        sdn_relation = vpp_data.NeutronApiSDNRelation()
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


class NeutronPluginAPIRelationTest(CharmTestCase):

    def setUp(self):
        super(NeutronPluginAPIRelationTest, self).setUp(vpp_data, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(NeutronPluginAPIRelationTest, self).tearDown()

    @patch.object(charmhelpers.core.hookenv, 'relation_get')
    @patch.object(charmhelpers.core.hookenv, 'related_units')
    @patch.object(charmhelpers.core.hookenv, 'relation_ids')
    def get_apirel(self, _hrids, _hrunits, _hrget, relinfo=None):
        _hrids.return_value = relinfo['rids']
        _hrunits.return_value = relinfo['runits']
        self.test_relation.set(relinfo['data'])
        _hrget.side_effect = self.test_relation.get
        api_rel = vpp_data.NeutronPluginAPIRelation()
        api_rel.get_data()
        return api_rel

    def test_get_first_data(self):
        api_rel = self.get_apirel(relinfo=FULL_NPAPI)
        expect = {
            'network-device-mtu': '1200',
            'overlay-network-type': 'gre'
        }
        self.assertEqual(api_rel.get_first_data(), expect)

    def test_is_ready(self):
        api_rel = self.get_apirel(relinfo=FULL_NPAPI)
        self.assertEqual(api_rel.is_ready(), True)

    def test_is_ready_incomplete(self):
        api_rel = self.get_apirel(relinfo=MISSING_DATA_NPAPI)
        self.assertEqual(api_rel.is_ready(), False)

    def test_get_data(self):
        api_rel = self.get_apirel(relinfo=FULL_NPAPI)
        expect = {
            'veth_mtu': '1200',
            'network_device_mtu': '1200',
            'overlay_network_type': 'gre'
        }
        for key in expect.keys():
            self.assertEqual(api_rel[key], expect[key])

    def test_get_data_nomtu(self):
        api_rel = self.get_apirel(relinfo=NOMTU_NPAPI)
        expect = {
            'overlay_network_type': 'gre'
        }
        for key in expect.keys():
            self.assertEqual(api_rel[key], expect[key])


class ODLControllerRelationTest(CharmTestCase):

    def setUp(self):
        super(ODLControllerRelationTest, self).setUp(vpp_data, TO_PATCH)
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
        odl_rel = vpp_data.ODLControllerRelation()
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
        super(ConfigTranslationTest, self).setUp(vpp_data, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(ConfigTranslationTest, self).tearDown()

    def test_config_default(self):
        ctxt = vpp_data.ConfigTranslation()
        self.assertEqual(ctxt, {'use_syslog': False,
                                'vlan_ranges': 'physnet1:1000:2000'})

        self.test_config.set('use-syslog', True)
        ctxt = vpp_data.ConfigTranslation()
        self.assertEqual(ctxt, {'use_syslog': True,
                                'vlan_ranges': 'physnet1:1000:2000'})

        self.test_config.set('vlan-ranges', 'physnet1:1000:3000')
        ctxt = vpp_data.ConfigTranslation()
        self.assertEqual(ctxt, {'use_syslog': True,
                                'vlan_ranges': 'physnet1:1000:3000'})
