# Ansiblite changes

## ansible/module_utils/basic.py

Keep only in `def _load_params()`:

```python
global _ANSIBLE_ARGS
if _ANSIBLE_ARGS is not None:
    buffer = _ANSIBLE_ARGS
else:
    if sys.version_info < (3,):
        buffer = sys.stdin.read()
    else:
        buffer = sys.stdin.buffer.read()
    _ANSIBLE_ARGS = buffer
```
