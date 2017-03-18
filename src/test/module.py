from __future__ import (absolute_import, division, print_function)

import sys
import json


class Stdin():

    def __init__(self, args):
        self._args = args

    def read(self):
        return json.dumps(dict(ANSIBLE_MODULE_ARGS={}))


def run_test(module_name, args):

    # TODO wrap stdin & stdout
    # from pprint import pprint

    sys.stdin = Stdin(args)
    try:
        module = __import__(
            'ansible.modules.{}'.format(module_name),
            globals(), locals(), ['main'])
        module.main()
    except ImportError, err:
        print(
            "Cannot import module 'ansiblite.modules.{}'. Error: {}".format(
                module_name, err.message)
        )

        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        sys.exit(1)
    # print stdout.get()
