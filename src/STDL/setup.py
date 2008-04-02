from distutils.core import setup
import py2exe

setup(console=['Main.py'],
      options = {"py2exe": {"packages": ["Coders"],
                            "dist_dir": '..\\..\\bin\\stdl'}})
