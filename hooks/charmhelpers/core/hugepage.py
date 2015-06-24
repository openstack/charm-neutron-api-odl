
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014-2015 Canonical Limited.
#
# This file is part of charm-helpers.
#
# charm-helpers is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3 as
# published by the Free Software Foundation.
#
# charm-helpers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with charm-helpers.  If not, see <http://www.gnu.org/licenses/>.

import yaml
from charmhelpers.core.fstab import Fstab
from charmhelpers.core.sysctl import (
    create,
)
from charmhelpers.core.host import (
    add_group,
    add_user_to_group,
    fstab_mount,
    mkdir,
)

def hugepage_support(user, group='hugetlb', nr_hugepages=256,
                     max_map_count=65536, mnt_point='/hugepages',
                     pagesize='2MB', mount=True):
    group_info = add_group(group)
    gid = group_info.gr_gid
    add_user_to_group(user, group)
    sysctl_settings = {
        'vm.nr_hugepages': nr_hugepages,
        'vm.max_map_count': max_map_count,  # 1GB
        'vm.hugetlb_shm_group': gid,
    }
    create(yaml.dump(sysctl_settings), '/etc/sysctl.d/10-hugepage.conf')
    mkdir(mnt_point, owner='root', group='root', perms=0o755, force=False)
    fstab = Fstab()
    fstab_entry = fstab.get_entry_by_attr('mountpoint', mnt_point)
    if fstab_entry:
        fstab.remove_entry(fstab_entry)
    entry = fstab.Entry('nodev', mnt_point, 'hugetlbfs',
                        'mode=1770,gid={},pagesize={}'.format(gid, pagesize), 0, 0)
    fstab.add_entry(entry)
    if mount:
        fstab_mount(mnt_point)
