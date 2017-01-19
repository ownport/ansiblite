
from __future__ import (absolute_import, division, print_function)

import os
import stat

from ansiblite.parsing.dataloader import DataLoader


def run_playbooks(playbooks):


    if not playbooks:
        return


    for playbook in playbooks:
        if not os.path.exists(playbook):
            raise IOError("the playbook: %s could not be found" % playbook)
        if not (os.path.isfile(playbook) or stat.S_ISFIFO(os.stat(playbook).st_mode)):
            raise IOError("the playbook: %s does not appear to be a file" % playbook)

    loader = DataLoader()
