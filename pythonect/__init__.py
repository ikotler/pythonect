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
