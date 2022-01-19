import re
import subprocess
import platform
import sys
import distro
from functools import lru_cache
from typing import Optional, TypedDict


class OsSettings(TypedDict):
    system: str
    machine: str
    libssl: str
    distro: Optional[str]


@lru_cache()
def get_openssl() -> str:
    process = subprocess.run(
        ['openssl', 'version', '-v'], stdout=subprocess.PIPE, check=True
    )
    return parse_openssl_version(str(process.stdout, sys.getdefaultencoding()))


@lru_cache()
def parse_openssl_version(string: str) -> str:
    match = re.match(r'^OpenSSL\s(\d+\.\d+)\.\d+', string)
    if match is None:
        # default
        return '1.1.x'

    return match.group(1) + '.x'


def resolve_known_distro(distro_id: str, distro_like: str) -> Optional[str]:
    if distro_id == "alpine":
        return "musl"
    elif distro_id == "raspbian":
        return "arm"
    elif distro_id == "nixos":
        return "nixos"
    elif (
        distro_id == "fedora"
        or "fedora" in distro_like
        or "rhel" in distro_like
        or "centros" in distro_like
    ):
        return "rhel"
    elif (
        distro_id == "ubuntu"
        or distro_id == "debian"
        or "ubuntu" in distro_like
        or "debian" in distro_like
    ):
        return "debian"
    return None


def get_os_settings() -> OsSettings:
    system = platform.system().lower()
    machine = platform.machine().lower()
    openssl_version = get_openssl()
    distro_id = distro.id()
    distro_like = distro.like()
    distr = resolve_known_distro(distro_id, distro_like)
    return OsSettings(
        system=system, machine=machine, libssl=openssl_version, distro=distr
    )


def resolve_platform(os: OsSettings) -> str:
    system, machine, libssl, distro = (
        os['system'],
        os['machine'],
        os['libssl'],
        os['distro'],
    )

    if system == "darwin" and machine == "aarch64":
        return "darwin-arm64"
    elif system == "darwin":
        return "darwin"
    elif system == "windows":
        return "windows"
    elif system == "freebsd":
        return "freebsd"
    elif system == "openbsd":
        return "openbsd"
    elif system == "netbsd":
        return "netbsd"
    elif system == "linux" and machine == "aarch64":
        return f"linux-arm64-openssl-{libssl}"
    elif system == "linux" and machine == "arm":
        return f"linux-arm-openssl-{libssl}"
    elif system == "linux" and distro == "musl":
        return "linux-musl"
    elif system == "linux" and distro == "nixos":
        return "linux-nixos"
    elif distro:
        return f"{distro}-openssl-{libssl}"
    return "debian-openssl-1.1.x"  # default fallback


def get_platform() -> str:
    return resolve_platform(get_os_settings())
