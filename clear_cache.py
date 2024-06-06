import pathlib

[p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]
[p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]