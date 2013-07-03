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

import glob
import os
import importlib
import sys


class PythonectInputFileFormatParser(object):

    def parse(self, source):

        raise NotImplementedError("Subclasses should implement this!")


def get_parsers(parsers_path):

    parsers = {}

    # For each directory in parsers path

    for component_directory in parsers_path.split(os.path.pathsep):

        # Add component directory to path

        sys.path.insert(0, component_directory)

        components_list = glob.glob(component_directory + '/*.py')

        # For each *.py file in directory

        for component_file in components_list:

            component = os.path.splitext(os.path.basename(component_file))[0]

            try:

                current_module = importlib.import_module(component)

                for name in dir(current_module):

                    if not name.startswith('_'):

                        obj = getattr(current_module, name)

                        try:

                            if obj != PythonectInputFileFormatParser and issubclass(obj, PythonectInputFileFormatParser):

                                for ext in obj.FILE_EXTS:

                                    parsers[ext] = obj()

                        except TypeError:

                            pass

            except Exception:

                pass

    return parsers
