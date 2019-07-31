import unittest
loader = unittest.TestLoader()
folder = './test'
suite = loader.discover(folder)

runner = unittest.TextTestRunner()
runner.run(suite)
