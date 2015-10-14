#!/usr/bin/env python
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

    import setuptools

except ImportError:

    from distribute_setup import use_setuptools

    use_setuptools()

    import setuptools


import sys


# Functions

def _safe_get_version():

    tmp_globals = {}

    # Importing _version.py may raise ImportError due to missing dependencies

    exec(compile(open('pythonect/_version.py').read(), 'pythonect/_version.py', 'exec'), tmp_globals)

    version = tmp_globals['__version__']

    return version


# Entry Point

if __name__ == "__main__":

    dependencies = ['networkx>=1.7', 'six', 'nose']

    major, minor = sys.version_info[:2]

    python_27 = (major > 2 or (major == 2 and minor >= 7))

    # < Python 2.7 ?

    if not python_27:

        # Python 2.6

        dependencies = dependencies + ['ordereddict>=1.1', 'argparse', 'importlib', 'unittest2']

    setupconf = dict(
        name='Pythonect',
        version=_safe_get_version(),
        author='Itzik Kotler',
        author_email='xorninja@gmail.com',
        url='http://www.pythonect.org/',
        license='BSD',
        description='A general-purpose dataflow programming language based on Python, written in Python',

        long_description=open('README.rst').read(),
        scripts=['bin/pythonect'],
        data_files=[('', ['LICENSE'])],
        packages=setuptools.find_packages(),

        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 2.6',
        ],

        install_requires=dependencies,

        test_suite='nose.collector',

        zip_safe=False
    )

    setuptools.setup(**setupconf)
