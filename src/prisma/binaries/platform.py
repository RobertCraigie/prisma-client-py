import platform
import re
import subprocess
import sys
from functools import lru_cache
from typing import Optional

import distro  # type: ignore # pyright: reportMissingTypeStubs=false


class OsSettings:
    system: str
    machine: str
    libssl: str
    distro: Optional[str]

    def __init__(
        self, system: str, machine: str, libssl: str, distro: Optional[str]
    ) -> None:
        self.system = system
        self.machine = machine
        self.libssl = libssl
        self.distro = distro

    def is_windows(self) -> bool:
        return self.system.lower() == 'windows'


@lru_cache()
def get_openssl() -> str:
    process = subprocess.run(
        ['openssl', 'version', '-v'], stdout=subprocess.PIPE, check=True
    )
    version = parse_openssl_version(str(process.stdout, sys.getdefaultencoding()))
    if version not in ("1.0.x", "1.1.x"):
        # If not 1.0 or 1.1 then it's most likely 3.0
        # Currently prisma doesn't provide binaries for 3.0
        # But we can use the latest stable 1.1.x
        # See: https://github.com/prisma/prisma/issues/11356
        return "1.1.x"
    return version


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
    if distro_id == "raspbian":
        return "arm"
    if distro_id == "nixos":
        return "nixos"
    if (
        distro_id == "fedora"
        or "fedora" in distro_like
        or "rhel" in distro_like
        or "centos" in distro_like
    ):
        return "rhel"
    if (
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


def resolve_darwin(os_settings: OsSettings) -> Optional[str]:
    if os_settings.system == "darwin" and os_settings.machine == "aarch64":
        return "darwin-arm64"
    if os_settings.system == "darwin":
        return "darwin"
    return None


def resolve_linux(os_settings: OsSettings) -> Optional[str]:
    if os_settings.system == "linux":
        if os_settings.machine == "aarch64":
            return f"linux-arm64-openssl-{os_settings.libssl}"
        if os_settings.machine == "arm":
            return f"linux-arm-openssl-{os_settings.libssl}"
        if os_settings.distro == "musl":
            return "linux-musl"
        if os_settings.distro == "nixos":
            return "linux-nixos"
        if os_settings.distro:
            return f"{os_settings.distro}-openssl-{os_settings.libssl}"
    return None


def resolve_other_platforms(os_settings: OsSettings) -> Optional[str]:
    if os_settings.system in ("windows", "freebsd", "openbsd", "netbsd"):
        return os_settings.system
    return None


def resolve_platform(os_settings: OsSettings) -> str:
    resolvers = (resolve_darwin, resolve_linux, resolve_other_platforms)
    for resolver in resolvers:
        platform = resolver(os_settings)
        if platform is not None:
            return platform
    return "debian-openssl-1.1.x"  # default fallback
