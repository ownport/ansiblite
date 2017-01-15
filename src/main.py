from __future__ import (absolute_import, division, print_function)

import sys
import json
import optparse

# Cleaner removes from sys.path any external libs to avoid potential
# conflicts with existing system libraries
from ansiblite.utils.pyenv import Cleaner
sys.path = Cleaner.syspath()


class Stdin():

    def read(self):
        return json.dumps(dict(ANSIBLE_MODULE_ARGS={}))


def run():

    # TODO wrap stdin & stdout

    # from pprint import pprint

    opts, args = parse()

    sys.stdin = Stdin()
    # sys.stdout = stdout

    # print help('modules')

    try:
        module = __import__(
            'ansiblite.modules.{}'.format(opts.module_path),
            globals(), locals(), ['main'])
        module.main()
    except ImportError, err:
        print(
            "[ERROR] Cannot import module 'ansiblite.modules.{}'. Error: {}".format(
                opts.module_path, err.message)
        )
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        sys.exit(1)
    # print stdout.get()


def parse():

    """parse command line

    :return : (options, args)"""
    parser = optparse.OptionParser()

    parser.usage = "%prog -[options] (-h for help)"

    parser.add_option('-m', '--module-path', dest='module_path',
        help="REQUIRED: full path of module source to execute")
    parser.add_option('-a', '--args', dest='module_args', default="",
        help="module argument string")
    opts, args = parser.parse_args()
    if not opts.module_path:
        parser.print_help()
        sys.exit(1)
    else:
        return opts, args
