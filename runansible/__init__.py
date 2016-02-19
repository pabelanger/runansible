# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import shutil
import subprocess
import tempfile

import pbr.version

from runansible import rundir

__version__ = pbr.version.VersionInfo('runansible').version_string()


class AnsibleRunner(object):

    def __init__(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(self.git_root)
        self.ansible_root = os.path.join(self.root, 'ansible')
        os.makedirs(self.ansible_root)
        self.inventory = os.path.join(self.ansible_root, 'inventory')
        self.playbook = os.path.join(self.ansible_root, 'playbook')
        self.config = os.path.join(self.ansible_root, 'ansible.cfg')

    def __enter__(self):
        return self

    def __exit__(self, etype, value, tb):
        shutil.rmtree(self.root)

    def add_dir(self, dirname):
        os.makedirs(os.path.join(self.root, dirname))

    def write_playbook(self, playbook_content):
        with open(self.playbook, 'w') as playbook:
            playbook.write(playbook_content)

    def copy_playbook(self, playbook_path):
        shutil.copy(playbook_path, self.playbook)

    def prepare_files(self, hostlist):
        with open(self.inventory, 'w') as inventory:
            for host_name, host_vars in hostlist:
                inventory.write(host_name)
                inventory.write(' ')
                for k, v in host_vars.items():
                    inventory.write('%s=%s' % (k, v))
                inventory.write('\n')
        with open(self.config, 'w') as config:
            config.write('[defaults]\n')
            config.write('hostfile = %s\n' % self.inventory)

    def run(self):
        proc = subprocess.Popen(
            ['ansible-playbook', self.playbook],
            cwd=self.ansible_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (out, err) = proc.communicate()
        ret = proc.wait()
        if ret == 0:
            return 'SUCCESS'
        else:
            return 'FAILURE'
