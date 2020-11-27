# tests/runner.py
import fnmatch
import glob
import os
import sys
import unittest

from importlib import import_module

import tests

# import your test modules
if len(sys.argv) > 1:
    test_modules = sys.argv[1:]
else:
    test_modules = fnmatch.filter(os.listdir('tests'), '[!_]*.py')
    test_modules = [s[:-3] for s in test_modules]

for module in test_modules:
    import_module('tests.' + module)

# initialize the test suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# add tests to the test suite

for module in test_modules:
    suite.addTests(loader.loadTestsFromModule(getattr(tests,module)))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
