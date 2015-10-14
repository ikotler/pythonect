# Copyright (c) 2012-2013, Itzik Kotler
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

try:

    # If < Python 2.7, use the backported unittest2 package

    import unittest2 as unittest

except ImportError:

    # Probably > Python 2.7, use unittest

    import unittest


import sys
import re
import imp
import shlex
import os


# Consts

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
TEST_DIR = os.path.dirname(os.path.abspath(__file__))


# Local imports

pythonect_interpreter = imp.load_source('pythonect_interpreter', BASE_DIR + os.sep + 'pythonect')


def _not_buffered():

    return hasattr(sys.stdout, "getvalue") is False


class TestPythonectInterpreter(unittest.TestCase):

    @unittest.skipIf(_not_buffered(), 'sys.stdout is not buffered')
    def test_command_mode(self):

        pythonect_interpreter.main(argv=shlex.split("""pythonect -c '"Hello, world" -> print'"""))

        self.assertRegexpMatches(sys.stdout.getvalue().strip(), '.*Hello, world.*')

    @unittest.skipIf(_not_buffered(), 'sys.stdout is not buffered')
    def test_script_mode_p2y(self):

        pythonect_interpreter.main(argv=shlex.split('pythonect ' + TEST_DIR + os.sep + 'helloworld.p2y'))

        self.assertRegexpMatches(sys.stdout.getvalue().strip(), '.*Hello, world.*')

    @unittest.skipIf(_not_buffered(), 'sys.stdout is not buffered')
    def test_script_mode_dia(self):

        pythonect_interpreter.main(argv=shlex.split('pythonect ' + TEST_DIR + os.sep + 'helloworld.dia'))

        self.assertRegexpMatches(sys.stdout.getvalue().strip(), '.*Hello, world.*')

    @unittest.skipIf(_not_buffered(), 'sys.stdout is not buffered')
    def test_module_mode(self):

        pythonect_interpreter.main(argv=shlex.split('pythonect -m foobar'))

        self.assertRegexpMatches(sys.stdout.getvalue().strip(), '.*Hello, world.*')

    @unittest.skipIf(_not_buffered(), 'sys.stdout is not buffered')
    def test_maxthreads_cmd_option(self):

        pythonect_interpreter.main(argv=shlex.split('pythonect -mt 1 -c "[1,2,3,4,5,6,7,8,9] -> print"'))

        self.assertTrue(len(set(re.findall('Thread-[\d]', sys.stdout.getvalue().strip()))) == 1)
