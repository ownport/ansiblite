from __future__ import (absolute_import, division, print_function)

import sys

# Cleaner removes from sys.path any external libs to avoid potential
# conflicts with existing system libraries
from utils import Cleaner
sys.path = Cleaner.syspath()

from main import Ansiblite

Ansiblite()
