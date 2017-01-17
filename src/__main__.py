
import sys

# Cleaner removes from sys.path any external libs to avoid potential
# conflicts with existing system libraries
from ansiblite.utils.pyenv import Cleaner
sys.path = Cleaner.syspath()

from ansiblite import Ansiblite

Ansiblite()
