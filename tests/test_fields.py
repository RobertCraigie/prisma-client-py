from prisma import Base64


def test_base64_eq() -> None:
    """Base64 field instances can be compared"""
    data = Base64.encode(b'foo')
    assert (data == Base64.encode(b'foo')) is True
    assert (data == Base64.encode(b'foo1')) is False
    assert (data == b'foo') is False
