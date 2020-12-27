import re
import subprocess
import platform as _platform
from functools import lru_cache


def name():
    return _platform.system().lower()


def check_for_extension(file):
    if name() == 'windows':
        if '.gz' in file:
            return file.replace('.gz', '.exe.gz')
        return file + '.exe'
    return file


def linux_distro():
    distro = _platform.linux_distribution()[0].lower()
    if distro in ['centos', 'fedora', 'rhel']:
        return 'rhel'

    if distro == 'alpine':
        return 'alpine'

    # default to debian
    return 'debian'


@lru_cache(maxsize=None)
def binary_platform():
    platform = name()
    if platform != 'linux':
        return platform

    distro = linux_distro()
    if distro == 'alpine':
        return 'linux-musl'

    ssl = get_openssl()
    return f'{distro}-openssl-{ssl}'


def get_openssl():
    process = subprocess.run(
        ['openssl', 'version', '-v'], stdout=subprocess.PIPE, check=True
    )
    return parse_openssl_version(str(process.stdout, 'utf-8'))


def parse_openssl_version(string: str) -> str:
    match = re.match(r'^OpenSSL\s(\d+\.\d+)\.\d+', string)
    if match is None:
        # default
        return '1.1.x'

    return match.group(1) + '.x'
