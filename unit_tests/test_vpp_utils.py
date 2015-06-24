from test_utils import CharmTestCase
from mock import patch
import vpp_utils

TO_PATCH = [
    'apt_install',
    'apt_purge',
    'config',
    'filter_installed_packages',
    'user_exists',
]


class VPPUtilsTest(CharmTestCase):

    def setUp(self):
        super(VPPUtilsTest, self).setUp(vpp_utils, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(VPPUtilsTest, self).tearDown()

    def test_install_packages(self):
        def _filter(pkg_list):
            return pkg_list
        self.filter_installed_packages.side_effect = _filter
        vpp_utils.install_packages('neutron-api', 'api')
        self.apt_purge.assert_called_with([])
        self.apt_install.assert_called_with(['neutron-common', 'corekeeper'])
        vpp_utils.install_packages('neutron-api', 'compute')
        self.apt_purge.assert_called_with([])
        self.apt_install.assert_called_with(['neutron-common', 'corekeeper'])
        self.test_config.set('use-corekeeper', False)
        vpp_utils.install_packages('neutron-api', 'compute')
        self.apt_purge.assert_called_with([])
        self.apt_install.assert_called_with(['neutron-common', 'apport'])

    def test_determine_packages(self):
        self.assertEqual(vpp_utils.determine_packages(node_type='api'),
                         ['neutron-common', 'corekeeper'])
        self.assertEqual(vpp_utils.determine_packages(node_type='compute'),
                         ['neutron-common', 'corekeeper'])
        self.test_config.set('use-corekeeper', False)
        self.assertEqual(vpp_utils.determine_packages(node_type='api'),
                         ['neutron-common', 'apport'])
        self.assertEqual(vpp_utils.determine_packages(node_type='compute'),
                         ['neutron-common', 'apport'])

    @patch.object(vpp_utils, 'bug_1437891')
    def test_purge_packages(self, _bug1437891):
        def _filter(pkg_list):
            return []
        self.filter_installed_packages.side_effect = _filter
        self.test_config.set('use-corekeeper', True)
        vpp_utils.purge_packages('api')
        self.apt_purge.assert_called_with(['apport'])
        self.test_config.set('use-corekeeper', False)
        vpp_utils.purge_packages('compute')
        _bug1437891.assert_called_with()
        self.apt_purge.assert_called_with(['corekeeper'])
