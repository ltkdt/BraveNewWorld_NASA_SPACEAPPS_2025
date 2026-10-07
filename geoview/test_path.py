import os
from pathlib import Path

print(os.path.join(Path(os.getcwd()).parents[0], 'media', 'figures'))
print(os.path.join(Path(os.getcwd()), 'media', 'figures'))
print(os.path.join(os.getcwd(), 'media', 'figures'))