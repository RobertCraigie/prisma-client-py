import re
import sys
import subprocess
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
    if hasattr(platform, 'freedesktop_os_release'):
        # For python >= 3.10
        distro = platform.freedesktop_os_release()
    else:
        distro = platform.linux_distribution()
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
    process = subprocess.run(['openssl', 'version', '-v'], stdout=subprocess.PIPE, check=True)
    return parse_openssl_version(str(process.stdout, sys.getdefaultencoding()))


def parse_openssl_version(string: str) -> str:
    match = re.match(r'^OpenSSL\s(\d+\.\d+)\.\d+', string)
    if match is None:
        # default
        return '1.1.x'

    return match.group(1) + '.x'
