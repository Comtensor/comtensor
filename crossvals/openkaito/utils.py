from protocol import Version



__version__ = "0.2.2"
version_split = __version__.split(".")
__spec_version__ = (
    (10000 * int(version_split[0]))
    + (100 * int(version_split[1]))
    + (1 * int(version_split[2]))
)


def get_version():
    version_split = __version__.split(".")
    return Version(
        major=int(version_split[0]),
        minor=int(version_split[1]),
        patch=int(version_split[2]),
    )