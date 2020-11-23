# tests/runner.py
import unittest

# import your test modules
import tests.assessment
import tests.asset
import tests.asset_group
import tests.invoice
import tests.score

# initialize the test suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(tests.assessment))
suite.addTests(loader.loadTestsFromModule(tests.asset))
suite.addTests(loader.loadTestsFromModule(tests.asset_group))
suite.addTests(loader.loadTestsFromModule(tests.invoice))
suite.addTests(loader.loadTestsFromModule(tests.score))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
