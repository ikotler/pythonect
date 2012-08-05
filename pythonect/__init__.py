# Version

try:

    from _version import __version__

    # Clean up namespace

    del _version

except ImportError, e:

    from internal.version import get_version

    __version__ = get_version()

    # Clean up namespace

    del e, get_version, internal


# API

try:

    from internal.eval import eval, split

except ImportError, e:

    # When imported by setup.py, it's expected that not all the dependencies will be there

    pass
