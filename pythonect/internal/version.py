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

    except Exception, e:

        pass

    return version
