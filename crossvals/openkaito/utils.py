from crossvals.openkaito.protocol import Version

__version__ = "0.2.5"

def get_version():
    version_split = __version__.split(".")
    return Version(
        major=int(version_split[0]),
        minor=int(version_split[1]),
        patch=int(version_split[2]),
    )