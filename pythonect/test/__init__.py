import os.path
import unittest


def get_tests():

    return unittest.TestLoader().discover(os.path.dirname(__file__))
