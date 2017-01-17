# Ansiblite

Lite version of Ansible, an IT automation tool

## Limitation compare to original Ansible version

- python >= 2.7
- only one (local) host support, no inventory
- argparse used instead of optparse


## Modules

Ansiblite supports only python modules

- system/ping
- system/setup

## Testing modules

`ansiblite test` command is a simple functionality that allows module developers (or testers)
to run a module outside of the ansible program, locally, on the current machine.

Example:

```sh
$ ./ansiblite test -m system.ping

{"invocation": {"module_args": {"data": null}}, "changed": false, "ping": "pong"}
```
