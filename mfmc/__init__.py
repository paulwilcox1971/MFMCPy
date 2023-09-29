"""
How to use imports.

import mfmc - import everything. Functions will need to be accessed via the
appropriate sub-module, e.g. mfmc.write.fn_open_file_for_writing
"""
print('mfmc._init__.py')

from . import write
from . import read
from . import check
from . import strs
from . import spec
from . import utils




