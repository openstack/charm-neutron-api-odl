import requests
import os
import yaml
import subprocess
from functools import partial

from charmhelpers.core.sysctl import create as create_sysctl
from socket import gethostname
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler
from charmhelpers.core.hookenv import(
    INFO,
    charm_dir,
    config,
    log,
    unit_private_ip,
)
from charmhelpers.core.hugepage import hugepage_support
from charmhelpers.core.host import (
    fstab_mount,
    rsync,
    service_stop,
    user_exists,
)
from charmhelpers.fetch import (
    apt_install,
    apt_purge,
    filter_installed_packages,
)
import odl_data
from jinja2 import Environment, FileSystemLoader

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
    pkgs = []
    pkgs.extend(PACKAGES)
    if config('use-corekeeper'):
        pkgs.append('corekeeper')
    else:
        pkgs.append('apport')
    return pkgs
