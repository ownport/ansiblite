# Ansiblite


## scripts/test-module

`test-module` is a simple program that allows module developers (or testers) to run
a module outside of the ansible program, locally, on the current machine.

Example:

```sh
$ ./hacking/test-module -m lib/ansible/modules/commands/shell -a "echo hi"
```

This is a good way to insert a breakpoint into a module, for instance.

For more complex arguments such as the following yaml:

```yaml
parent:
  child:
    - item: first
      val: foo
    - item: second
      val: boo
```
Use:
```sh
$ ./hacking/test-module -m module \
    -a "{"parent": {"child": [{"item": "first", "val": "foo"}, {"item": "second", "val": "bar"}]}}"
```
