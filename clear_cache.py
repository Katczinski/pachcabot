import pathlib
import shutil

for p in pathlib.Path('.').rglob('__pycache__'):
    print(f'removing {p}')
    shutil.rmtree(p)

for p in pathlib.Path('.').rglob('*.py[co]'):
    print(f'unlinking {p}')
    p.unlink()
    
print("Done")