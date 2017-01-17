
from __future__ import (absolute_import, division, print_function)

import sys
import argparse

from ansiblite.test.module import run_test

__version__ = '0.0.1'

ANSIBLITE_USAGE = '''ansiblite <command> [<args>]

The list of commands:
   test        testing Ansiblite modules
   playbook    run playbook
'''


class Ansiblite(object):

    def __init__(self):

        parser = argparse.ArgumentParser(usage=ANSIBLITE_USAGE)
        parser.add_argument('-v', '--version', action='version',
                            version='v{}'.format(__version__))
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print('Unrecognized command: %s' % args.command)
            sys.exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def test(self):

        parser = argparse.ArgumentParser(usage=ANSIBLITE_USAGE, description='Testing Ansiblite modules')
        parser.add_argument('-m', '--module-name',
            dest='module_name', required=True, help="the module module to execute")
        parser.add_argument('-a', '--args',
            dest='module_args', action='append', help="module argument string")
        args = parser.parse_args(sys.argv[2:])

        run_test(args.module_name, args.module_args)

    def playbook(self):

        raise NotImplemented()
