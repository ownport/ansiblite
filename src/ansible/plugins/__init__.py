# (c) 2012, Daniel Hokka Zakrisson <daniel@hozac.com>
# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com> and others
#
# This file is part of Ansible
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

import glob
import imp
import inspect
import os
import os.path
import sys
import warnings

from collections import defaultdict

from ansible import constants as C
from ansible.utils.unicode import to_unicode

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

# Global so that all instances of a PluginLoader will share the caches
MODULE_CACHE = {}
PATH_CACHE = {}
PLUGIN_CACHE = {}

def get_all_plugin_loaders():
    return [(name, obj) for (name, obj) in inspect.getmembers(sys.modules[__name__]) if isinstance(obj, PluginLoader)]

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

        if config and isinstance(config, list):
            config = config[0]
        elif not config:
            config = ''
        self.config = config

        if not class_name in MODULE_CACHE:
            MODULE_CACHE[class_name] = {}
        if not class_name in PLUGIN_CACHE:
            PLUGIN_CACHE[class_name] = defaultdict(dict)

        self._module_cache      = MODULE_CACHE[class_name]
        self._plugin_cache      = PLUGIN_CACHE[class_name]

    def __setstate__(self, data):
        '''
        Deserializer.
        '''

        class_name = data.get('class_name')
        package    = data.get('package')
        config     = data.get('config')
        aliases    = data.get('aliases')
        base_class = data.get('base_class')

        PATH_CACHE[class_name] = data.get('PATH_CACHE')
        PLUGIN_CACHE[class_name] = data.get('PLUGIN_CACHE')

        self.__init__(class_name, package, config, None, aliases, base_class)

    def __getstate__(self):
        '''
        Serializer.
        '''

        return dict(
            class_name        = self.class_name,
            base_class        = self.base_class,
            package           = self.package,
            config            = self.config,
            aliases           = self.aliases,
            PATH_CACHE        = PATH_CACHE[self.class_name],
            PLUGIN_CACHE      = PLUGIN_CACHE[self.class_name],
        )

    def add_directory(self, directory, with_subdir=False):
        ''' Adds an additional directory to the search path '''
        pass

    def find_modules(self):
        ''' returns package modules '''

        modules = MODULES.get(self.package, None)
        if not modules:
            return {}
        return modules

    def find_plugins(self):

        plugins = PLUGINS.get(self.package, None)
        if not plugins:
            return {}
        return plugins

    def find_plugin(self, name, mod_type=''):
        ''' Find a plugin named name '''

        path = self.find_plugins().get(name, None) or self.find_modules().get(name, None)
        if not path:
            display.warning('Cannot find the plugin/module "%s" in the package "%s"' % (name, self.package))
            return None

        if path in self._module_cache:
            return path

        try:
            self._module_cache[path] = __import__(path, globals(), locals(), ['*',])
            return path
        except (ImportError, ValueError), err:
            error_msg = "ansible.plugins._init__.py::find_plugin(name=%s, mod_type=%s), "
            error_msg += "path: %s, error message: %s"
            display.error(error_msg % (name, mod_type, path, err))
            return None


    def has_plugin(self, name):
        ''' Checks if a plugin named name exists '''

        return self.find_plugin(name) is not None

    __contains__ = has_plugin

    def get(self, name, *args, **kwargs):
        ''' instantiates a plugin of the given name using arguments '''

        class_only = kwargs.pop('class_only', False)
        if name in self.aliases:
            name = self.aliases[name]

        path = self.find_plugin(name)
        if path is None:
            return None

        obj = getattr(self._module_cache[path], self.class_name)
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

        if not class_only:
            obj = obj(*args, **kwargs)

        return obj

    def all(self, *args, **kwargs):
        ''' instantiates all plugins with the same arguments '''

        path_only = kwargs.pop('path_only', False)
        class_only = kwargs.pop('class_only', False)

        for name, path in self.find_plugins().items():

            if path_only:
                yield path
                continue

            if path not in self._module_cache:
                self._module_cache[path] = __import__(path, globals(), locals(), ['*',])

            try:
                obj = getattr(self._module_cache[path], self.class_name)
            except AttributeError as e:
                display.warning("Skipping plugin (%s) as it seems to be invalid: %s" % (path, to_unicode(e)))

            if self.base_class:
                # The import path is hardcoded and should be the right place,
                # so we are not expecting an ImportError.
                module = __import__(self.package, fromlist=[self.base_class])
                # Check whether this obj has the required base class.
                try:
                   plugin_class = getattr(module, self.base_class)
                except AttributeError:
                   continue
                if not issubclass(obj, plugin_class):
                   continue

            if not class_only:
                obj = obj(*args, **kwargs)

            # set extra info on the module, in case we want it later
            setattr(obj, '_original_path', path)
            yield obj

action_loader = PluginLoader(
    'ActionModule',
    'ansible.plugins.action',
    C.DEFAULT_ACTION_PLUGIN_PATH,
    'action_plugins',
    required_base_class='ActionBase',
)

cache_loader = PluginLoader(
    'CacheModule',
    'ansible.plugins.cache',
    C.DEFAULT_CACHE_PLUGIN_PATH,
    'cache_plugins',
)

callback_loader = PluginLoader(
    'CallbackModule',
    'ansible.plugins.callback',
    C.DEFAULT_CALLBACK_PLUGIN_PATH,
    'callback_plugins',
)

connection_loader = PluginLoader(
    'Connection',
    'ansible.plugins.connection',
    C.DEFAULT_CONNECTION_PLUGIN_PATH,
    'connection_plugins',
    aliases={'paramiko': 'paramiko_ssh'},
    required_base_class='ConnectionBase',
)

shell_loader = PluginLoader(
    'ShellModule',
    'ansible.plugins.shell',
    'shell_plugins',
    'shell_plugins',
)

module_loader = PluginLoader(
    '',
    'ansible.modules',
    C.DEFAULT_MODULE_PATH,
    'library',
)

lookup_loader = PluginLoader(
    'LookupModule',
    'ansible.plugins.lookup',
    C.DEFAULT_LOOKUP_PLUGIN_PATH,
    'lookup_plugins',
    required_base_class='LookupBase',
)

vars_loader = PluginLoader(
    'VarsModule',
    'ansible.plugins.vars',
    C.DEFAULT_VARS_PLUGIN_PATH,
    'vars_plugins',
)

filter_loader = PluginLoader(
    'FilterModule',
    'ansible.plugins.filter',
    C.DEFAULT_FILTER_PLUGIN_PATH,
    'filter_plugins',
)

test_loader = PluginLoader(
    'TestModule',
    'ansible.plugins.test',
    C.DEFAULT_TEST_PLUGIN_PATH,
    'test_plugins'
)

fragment_loader = PluginLoader(
    'ModuleDocFragment',
    'ansible.utils.module_docs_fragments',
    os.path.join(os.path.dirname(__file__), 'module_docs_fragments'),
    '',
)

strategy_loader = PluginLoader(
    'StrategyModule',
    'ansible.plugins.strategy',
    C.DEFAULT_STRATEGY_PLUGIN_PATH,
    'strategy_plugins',
    required_base_class='StrategyBase',
)

MODULES = {
    'ansible.modules': {
        # commands
        'command': 'ansible.modules.commands.command',
        'shell': 'ansible.modules.commands.shell',
        # system
        'ping': 'ansible.modules.system.ping',
        'setup': 'ansible.modules.system.setup',
        # utilities/helper
        'meta': 'ansible.modules.utilities.helper.meta',
    },

}

PLUGINS = {

    'ansible.plugins.action': {
        'normal': 'ansible.plugins.action.normal',
    },
    'ansible.plugins.cache': {
        'memory': 'ansible.plugins.cache.memory',
    },
    'ansible.plugins.callback': {
        'default': 'ansible.plugins.callback.default',
    },
    'ansible.plugins.connection': {
        'local': 'ansible.plugins.connection.local',
    },
    'ansible.plugins.shell': {
        'sh': 'ansible.plugins.shell.sh',
    },
    'ansible.plugins.strategy': {
        'debug': 'ansible.plugins.strategy.debug',
        'linear': 'ansible.plugins.strategy.linear',
    }
}
