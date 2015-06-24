from charmhelpers.core.hookenv import(
    INFO,
    config,
    log,
)
from charmhelpers.fetch import (
    apt_install,
    filter_installed_packages,
)

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
    pkgs = filter_installed_packages(determine_packages())
    apt_install(pkgs)


def determine_packages(node_type=None):
    return PACKAGES
