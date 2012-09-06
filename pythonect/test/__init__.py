import os.path


try:

    # If < Python 2.7, use the backported unittest2 package

    import unittest2 as unittest

except ImportError:

    # Probably > Python 2.7, use unittest

    import unittest


def get_tests():

    return unittest.TestLoader().discover(os.path.dirname(__file__))
