
from __future__ import (absolute_import, division, print_function)

import sys
import argparse

from ansible import constants as C

from test.module import run_test
from runners import run_playbooks


__version__ = 'v2.1.4.0-1'

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

    @staticmethod
    def expand_tilde(option, opt, value, parser):
        setattr(parser.values, option.dest, os.path.expanduser(value))

    def test(self):

        parser = argparse.ArgumentParser(usage=ANSIBLITE_USAGE,
                                         description='Testing Ansiblite modules')
        parser.add_argument('-m', '--module-name',
                            dest='module_name',
                            required=True,
                            help="the module module to execute")
        parser.add_argument('-a', '--args',
                            dest='module_args',
                            action='append',
                            help="module argument string")
        args = parser.parse_args(sys.argv[2:])

        if not args.module_name:
            parser.print_help()
            sys.exit(1)

        run_test(args.module_name, args.module_args)

    def playbook(self):

        parser = argparse.ArgumentParser(usage=ANSIBLITE_USAGE,
                                         description='run Ansiblite playbooks')
        parser.add_argument('-v','--verbose', dest='verbosity', default=0,
                            action="count",
                            help="verbose mode (-vvv for more, -vvvv to enable connection debugging)")
        parser.add_argument('-p', '--playbook',
                            dest='module_playbook',
                            action='append',
                            required=True,
                            help="Ansiblite playbook")
        parser.add_argument('-i', '--inventory-file', dest='inventory',
                            help="specify inventory host path (default=%s) or comma separated host list." % C.DEFAULT_HOST_LIST,
                            default=C.DEFAULT_HOST_LIST,
                            type=str)
        parser.add_argument('--list-hosts', dest='listhosts',
                            action='store_true',
                            help='outputs a list of matching hosts; does not execute anything else')
        parser.add_argument('--list-tasks', dest='listtasks', action='store_true',
                            help="list all tasks that would be executed")
        parser.add_argument('--list-tags', dest='listtags', action='store_true',
                            help="list all available tags")
        parser.add_argument('--syntax-check', dest='syntax',
                            action='store_true',
                            help="perform a syntax check on the playbook, but do not execute it")
        parser.add_argument('-M', '--module-path', dest='module_path',
                            default=None,
                            help="specify path(s) to module library (default=%s)" % C.DEFAULT_MODULE_PATH,
                            type=str)

        args = parser.parse_args(sys.argv[2:])

        if not args.module_playbook:
            parser.print_help()
            sys.exit(1)

        run_playbooks(args.module_playbook, options=args)
