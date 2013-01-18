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

import subprocess
import re


def get_version():

    version = "0.0.0.dev0"

    try:

        git = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        git.stderr.close()

        git_output = git.stdout.readlines()[0]

        git_ver = re.match('^\w+(?P<MAJOR>\d+)\.(?P<MINOR>\d+)(\.(?P<MICRO>\d+)(\-(?P<POST>\d+))?)?', git_output)

        if git_ver is not None:

            # MAJOR.MINOR

            version = git_ver.group('MAJOR') + '.' + git_ver.group('MINOR')

            if git_ver.groupdict('MICRO') is not None:

                # MAJOR.MINOR.MICRO

                version = version + '.' + git_ver.group('MICRO')

                if git_ver.groupdict('POST') is not None:

                    # MAJOR.MINOR.MICRO-POST

                    version = version + '.post' + git_ver.group('POST')

    except Exception as e:

        pass

    return version
