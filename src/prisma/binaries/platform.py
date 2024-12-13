import ssl
import platform as _platform
from functools import lru_cache
from typing import Tuple


def name() -> str:
    return _platform.system().lower()


def check_for_extension(file: str) -> str:
    if name() == 'windows' and '.exe' not in file:
        if '.gz' in file:
            return file.replace('.gz', '.exe.gz')
        return file + '.exe'
    return file


def linux_distro() -> str:
    # NOTE: this has only been tested on ubuntu
    distro_id, distro_id_like = _get_linux_distro_details()
    if distro_id == 'alpine':
        return 'alpine'

    if any(distro in distro_id_like for distro in ['centos', 'fedora', 'rhel']):
        return 'rhel'

    # default to debian
    return 'debian'


def _get_linux_distro_details() -> Tuple[str, str]:
    if hasattr(_platform, 'freedesktop_os_release'):
        # For python >= 3.10
        distro = _platform.freedesktop_os_release()
    else:
        distro = _platform.linux_distribution()
    return distro.get('ID', ''), distro.get('ID_LIKE', '')


@lru_cache(maxsize=None)
def binary_platform() -> str:
    platform = name()
    if platform != 'linux':
        return platform

    distro = linux_distro()
    if distro == 'alpine':
        return 'linux-musl'

    ssl = get_openssl()
    return f'{distro}-openssl-{ssl}'


def get_openssl() -> str:
    return '.'.join(str(x) for x in ssl.OPENSSL_VERSION_INFO)
