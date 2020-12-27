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
    # NOTE: this has only been tested on ubuntu
    distro_id, distro_id_like = _get_linux_distro_details()
    if distro_id == 'alpine':
        return 'alpine'

    if any(distro in distro_id_like for distro in ['centos', 'fedora', 'rhel']):
        return 'rhel'

    # default to debian
    return 'debian'


def _get_linux_distro_details():
    process = subprocess.run(
        ['cat', '/etc/os-release'], stdout=subprocess.PIPE, check=True
    )
    output = str(process.stdout, 'utf-8')

    match = re.search(r'ID="?([^"\n]*)"?', output)
    distro_id = match.group(1) if match else ''

    match = re.search(r'ID_LIKE="?([^"\n]*)"?', output)
    distro_id_like = match.group(1) if match else ''
    return distro_id, distro_id_like


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
