# Version

try:

    from _version import __version__

except ImportError, e:

    from internal.version import get_version

    __version__ = get_version()
