import os

from ansiblite.inventory import Inventory
from ansiblite.vars import VariableManager
from ansiblite.parsing.dataloader import DataLoader
from ansiblite.executor.playbook_executor import PlaybookExecutor

from ansiblite.utils.display import Display
display = Display()


def run_playbooks(playbooks, options=None):
    ''' run Ansible playbooks
    '''
    if not playbooks:
        return

    for playbook in playbooks:
        if not os.path.exists(playbook):
            raise IOError("the playbook: %s could not be found" % playbook)
        if not (os.path.isfile(playbook) or stat.S_ISFIFO(os.stat(playbook).st_mode)):
            raise IOError("the playbook: %s does not appear to be a file" % playbook)

    loader = DataLoader()
    variable_manager = VariableManager()

    # create the inventory, and filter it based on the subset specified (if any)
    inventory = Inventory(loader=loader, variable_manager=variable_manager,
        host_list=options.inventory if options.inventory else None)
    variable_manager.set_inventory(inventory)

    # (which is not returned in list_hosts()) is taken into account for
    # warning if inventory is empty.  But it can't be taken into account for
    # checking if limit doesn't match any hosts.  Instead we don't worry about
    # limit if only implicit localhost was in inventory to start with.
    #
    # Fix this when we rewrite inventory by making localhost a real host (and thus show up in list_hosts())
    no_hosts = False
    if len(inventory.list_hosts()) == 0:
        # Empty inventory
        display.warning("provided hosts list is empty, only localhost is available")
        no_hosts = True

    # inventory.subset(options.subset)
    if len(inventory.list_hosts()) == 0 and no_hosts is False:
        # Invalid limit
        raise AnsibleError("Specified --limit does not match any hosts")

    # flush fact cache if requested
    # if options.flush_cache:
    #     _flush_cache(inventory, variable_manager)

    # create the playbook executor, which manages running the plays via a
    # task queue manager
    pbex = PlaybookExecutor(playbooks=playbooks,
                            inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader,
                            options=options,
                            passwords={})
    results = pbex.run()

    print(results)
