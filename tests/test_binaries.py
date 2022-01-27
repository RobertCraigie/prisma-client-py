import platform
from typing import Any, List, Optional, Tuple
import pytest

import distro  # type: ignore # pyright: reportMissingTypeStubs=false
import prisma.binaries.platform as binaries_platform


def mock(obj: Any):
    return lambda: obj


def test_mock_windows_os(monkeypatch: pytest.MonkeyPatch):
    """
    Mock the platform.system() to return "Windows" and platform.machine()
    to return default "x86_64".

    Tests resolve_other_platforms() and asserts that it returns the expected value.

    Additionaly tests resolve_linux() and resolve_darwin()
    and makes sure they return None
    """
    monkeypatch.setattr(platform, "system", mock("Windows"))
    monkeypatch.setattr(platform, "machine", mock("x86_64"))
    monkeypatch.setattr(binaries_platform, "get_openssl", mock("1.1.x"))
    monkeypatch.setattr(distro, "id", mock(""))
    monkeypatch.setattr(distro, "like", mock(""))

    assert platform.system() == "Windows"
    os_settings = binaries_platform.get_os_settings()
    assert os_settings.is_windows()

    assert binaries_platform.resolve_darwin(os_settings) is None
    assert binaries_platform.resolve_linux(os_settings) is None
    assert binaries_platform.resolve_other_platforms(os_settings) == "windows"


MACHINES = ["aarch64", "x86_64"]


@pytest.mark.parametrize(("machine,"), MACHINES)
def test_mock_darwin_os(monkeypatch: pytest.MonkeyPatch, machine: str):
    """
    Mock the platform.system() to return "Darwin" and platform.machine() to return
    either "aarch64" or "x86_64".

    Tests resolve_darwin() and makes sure it returns "darwin-arm64" for aarch64
    and "darwin" for x86_64.

    Additionaly tests resolve_linux() and resolve_other_platforms()
    and makes sure they return None
    """
    monkeypatch.setattr(platform, "system", mock("Darwin"))
    monkeypatch.setattr(platform, "machine", mock(machine))
    monkeypatch.setattr(binaries_platform, "get_openssl", mock("1.1.x"))
    monkeypatch.setattr(distro, "id", mock(""))
    monkeypatch.setattr(distro, "like", mock(""))

    assert platform.system() == "Darwin"

    os_settings = binaries_platform.get_os_settings()

    assert not os_settings.is_windows()
    if machine == "aarch64":
        assert binaries_platform.resolve_darwin(os_settings) == "darwin-arm64"
    else:
        assert binaries_platform.resolve_darwin(os_settings) == "darwin"
    assert binaries_platform.resolve_linux(os_settings) is None
    assert binaries_platform.resolve_other_platforms(os_settings) is None


# DISTRO_ID, DISTRO_LIKE, EXPECTED
DISTRO_ID_LIKE: List[Tuple[str, str, str]] = [
    ("alpine", "", "musl"),
    ("raspbian", "", "arm"),
    ("nixos", "", "nixos"),
    ("ubuntu", "debian", "debian"),
    ("debian", "debian", "debian"),
    ("fedora", "fedora", "rhel"),
    ("rhel", "rhel", "rhel"),
    ("centos", "centos", "rhel"),
    ("oracle", "fedora", "rhel"),
]


@pytest.mark.parametrize(("distro_id,distro_like,expected"), DISTRO_ID_LIKE)
def test_resolve_known_distro(
    monkeypatch: pytest.MonkeyPatch, distro_id: str, distro_like: str, expected: str
):
    """
    Mock the platform.system() to return "linux" and platform.machine()
    to return default "x86_64".

    Tests resolve_known_distro() and asserts that it
    returns expected distro names.
    """
    monkeypatch.setattr(platform, "system", mock("linux"))
    monkeypatch.setattr(platform, "machine", mock("x86_64"))
    monkeypatch.setattr(binaries_platform, "get_openssl", mock("1.1.x"))
    monkeypatch.setattr(distro, "id", mock(distro_id))
    monkeypatch.setattr(distro, "like", mock(distro_like))

    os_settings = binaries_platform.get_os_settings()
    assert os_settings.distro == expected


# TODO: add openssl to parameters
# TODO: add more arm datapoints
# MACHINE, DISTRO_ID, DISTRO_LIKE, RESOLVED_DISTRO, EPXECTED
LINUX_PLATFORMS: List[Tuple[str, str, str, Optional[str], str]] = [
    ("x86_64", "alpine", "", "musl", "linux-musl"),
    ("aarch64", "ubuntu", "debian", "debian", "linux-arm64-openssl-1.1.x"),
    ("arm", "raspbian", "", "arm", "linux-arm-openssl-1.1.x"),
    ("x86_64", "nixos", "", "nixos", "linux-nixos"),
    ("x86_64", "fedora", "fedora", "rhel", "rhel-openssl-1.1.x"),
    ("x86_64", "debian", "debian", "debian", "debian-openssl-1.1.x"),
    ("x86_64", "niche-distro", "niche-like", None, "debian-openssl-1.1.x"),
    ("arm", "niche-distro", "niche-like", None, "linux-arm-openssl-1.1.x"),
    ("aarch64", "niche-distro", "niche-like", None, "linux-arm64-openssl-1.1.x"),
]


@pytest.mark.parametrize(
    "machine,distro_id,distro_like,resolved_distro,expected_platform",
    LINUX_PLATFORMS,
)
def test_resolve_linux(
    monkeypatch: pytest.MonkeyPatch,
    distro_id: str,
    distro_like: str,
    machine: str,
    resolved_distro: str,
    expected_platform: str,
):  # pylint: disable=too-many-arguments

    """
    Mocks the platform.system() to return "linux" and platform.machine()
    to return either "aarch64" or "x86_64".

    Tests resolve_platform() and asserts that it returns expected binary platform.

    Additionaly tests resolve_known_distro()
    """
    # TODO: arguments can be simplified to a namedtuple or something
    monkeypatch.setattr(platform, "system", mock("Linux"))
    monkeypatch.setattr(platform, "machine", mock(machine))
    monkeypatch.setattr(binaries_platform, "get_openssl", mock("1.1.x"))
    monkeypatch.setattr(distro, "id", mock(distro_id))
    monkeypatch.setattr(distro, "like", mock(distro_like))
    os_settings = binaries_platform.get_os_settings()
    assert os_settings.distro == resolved_distro
    assert binaries_platform.resolve_platform(os_settings) == expected_platform
