from test_utils import CharmTestCase
import odl_utils

TO_PATCH = [
    'apt_install',
    'config',
    'filter_installed_packages',
]


class VPPUtilsTest(CharmTestCase):

    def setUp(self):
        super(VPPUtilsTest, self).setUp(odl_utils, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def tearDown(self):
        super(VPPUtilsTest, self).tearDown()

    def test_install_packages(self):
        def _filter(pkg_list):
            return pkg_list
        self.filter_installed_packages.side_effect = _filter
        odl_utils.install_packages('neutron-api')
        self.apt_install.assert_called_with(['neutron-common',
                                             'neutron-plugin-ml2'])

    def test_determine_packages(self):
        self.assertEqual(odl_utils.determine_packages(),
                         ['neutron-common', 'neutron-plugin-ml2'])
