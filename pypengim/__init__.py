"""pyPengIm: Teochew (Chaoshan) text processing tool.

    from pypengim import pyPengIm
    tool = pyPengIm()
    tool.pinyin('潮汕人食糜')

Data files live inside the package at ``pypengim/data/`` and are independent of CWD.
The main class depends on jieba and cn2an, loaded on demand: using only
``pypengim.accent`` / ``pypengim.romanization`` does not require them.
"""
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

__all__ = ['pyPengIm', 'PyPengIm', 'AccentConverter', 'romanization', 'utils', 'DATA_DIR']
__version__ = '0.2.0'


def __getattr__(name):
    if name in ('pyPengIm', 'PyPengIm'):
        from .core import pyPengIm
        return pyPengIm          # PyPengIm is the PEP 8 alias
    if name == 'AccentConverter':
        from .accent import AccentConverter
        return AccentConverter
    if name in ('romanization', 'utils', 'accent', 'core', 'syllable'):
        import importlib
        return importlib.import_module('.' + name, __name__)
    raise AttributeError("module 'pypengim' has no attribute '{}'".format(name))
