"""Compatibility layer: legacy code ``from script.pyPengIm import pyPengIm`` still works.

Code has moved to the ``pypengim`` package; please use ``from pypengim import pyPengIm``.
This shim will be removed in a future release.
"""
import sys
import warnings

import pypengim
from pypengim import accent, core, romanization, syllable, utils

warnings.warn('script 包已迁移到 pypengim，请改用 from pypengim import pyPengIm',
              DeprecationWarning, stacklevel=2)

# Make script.xxx and pypengim.xxx point at the same module objects
for _name, _module in {'pyPengIm': core, 'accent': accent, 'romanization': romanization,
                       'syllable': syllable, 'utils': utils}.items():
    sys.modules[__name__ + '.' + _name] = _module
    setattr(sys.modules[__name__], _name, _module)
