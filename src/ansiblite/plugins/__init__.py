# (c) 2012, Daniel Hokka Zakrisson <daniel@hozac.com>
# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com> and others
#
# Original file was part of Ansible but it was modified for Ansiblite
# needs (https://github.com/ownport/ansiblite)
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys
import warnings


from collections import defaultdict

from ansiblite import constants as C

from ansiblite.utils.display import Display
display = Display()

# Global so that all instances of a PluginLoader will share the caches
MODULE_CACHE = {}
PATH_CACHE = {}
PLUGIN_PATH_CACHE = {}


class PluginLoader:

    '''
    PluginLoader loads plugins from the configured plugin directories.

    It searches for plugins by iterating through the combined list of
    play basedirs, configured paths, and the python path.
    The first match is used.
    '''

    def __init__(self, class_name, package, config, subdir, aliases={}, required_base_class=None):

        self.class_name         = class_name
        self.base_class         = required_base_class
        self.package            = package
        self.subdir             = subdir
        self.aliases            = aliases

        if config and not isinstance(config, list):
            config = [config]
        elif not config:
            config = []

        self.config = config

        if class_name not in MODULE_CACHE:
            MODULE_CACHE[class_name] = {}
        if class_name not in PATH_CACHE:
            PATH_CACHE[class_name] = None
        if class_name not in PLUGIN_PATH_CACHE:
            PLUGIN_PATH_CACHE[class_name] = defaultdict(dict)

        self._module_cache      = MODULE_CACHE[class_name]
        self._paths             = PATH_CACHE[class_name]
        self._plugin_path_cache = PLUGIN_PATH_CACHE[class_name]

        self._extra_dirs = []
        self._searched_paths = set()

    def get(self, name, *args, **kwargs):
        ''' instantiates a plugin of the given name using arguments '''

        if name in self.aliases:
            name = self.aliases[name]

        if name not in self._module_cache:
            self._module_cache[name] = self._load_module_source('.'.join([self.package, name]), self.class_name)

        obj = getattr(self._module_cache[name], self.class_name)
        if self.base_class:
            # The import path is hardcoded and should be the right place,
            # so we are not expecting an ImportError.
            module = __import__(self.package, fromlist=[self.base_class])
            # Check whether this obj has the required base class.
            try:
                plugin_class = getattr(module, self.base_class)
            except AttributeError:
                return None
            if not issubclass(obj, plugin_class):
                return None
        return obj

    def _load_module_source(self, name, class_name):
        if name in sys.modules:
            # See https://github.com/ansible/ansible/issues/13110
            return sys.modules[name]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            module = __import__(name, globals(), locals(), [class_name])
        return module


action_loader = PluginLoader(
    'ActionModule',
    'ansiblite.plugins.action',
    C.DEFAULT_ACTION_PLUGIN_PATH,
    'action_plugins',
    required_base_class='ActionBase',
)

cache_loader = PluginLoader(
    'CacheModule',
    'ansiblite.plugins.cache',
    C.DEFAULT_CACHE_PLUGIN_PATH,
    'cache_plugins',
)

callback_loader = PluginLoader(
    'CallbackModule',
    'ansiblite.plugins.callback',
    C.DEFAULT_CALLBACK_PLUGIN_PATH,
    'callback_plugins',
)

connection_loader = PluginLoader(
    'Connection',
    'ansiblite.plugins.connection',
    C.DEFAULT_CONNECTION_PLUGIN_PATH,
    'connection_plugins',
    aliases={'paramiko': 'paramiko_ssh'},
    required_base_class='ConnectionBase',
)

shell_loader = PluginLoader(
    'ShellModule',
    'ansiblite.plugins.shell',
    'shell_plugins',
    'shell_plugins',
)

module_loader = PluginLoader(
    '',
    'ansiblite.modules',
    C.DEFAULT_MODULE_PATH,
    'library',
)

lookup_loader = PluginLoader(
    'LookupModule',
    'ansiblite.plugins.lookup',
    C.DEFAULT_LOOKUP_PLUGIN_PATH,
    'lookup_plugins',
    required_base_class='LookupBase',
)

vars_loader = PluginLoader(
    'VarsModule',
    'ansiblite.plugins.vars',
    C.DEFAULT_VARS_PLUGIN_PATH,
    'vars_plugins',
)

filter_loader = PluginLoader(
    'FilterModule',
    'ansiblite.plugins.filter',
    C.DEFAULT_FILTER_PLUGIN_PATH,
    'filter_plugins',
)

test_loader = PluginLoader(
    'TestModule',
    'ansiblite.plugins.test',
    C.DEFAULT_TEST_PLUGIN_PATH,
    'test_plugins'
)

fragment_loader = PluginLoader(
    'ModuleDocFragment',
    'ansiblite.utils.module_docs_fragments',
    os.path.join(os.path.dirname(__file__), 'module_docs_fragments'),
    '',
)

strategy_loader = PluginLoader(
    'StrategyModule',
    'ansiblite.plugins.strategy',
    C.DEFAULT_STRATEGY_PLUGIN_PATH,
    'strategy_plugins',
    required_base_class='StrategyBase',
)

terminal_loader = PluginLoader(
    'TerminalModule',
    'ansiblite.plugins.terminal',
    'terminal_plugins',
    'terminal_plugins'
)
