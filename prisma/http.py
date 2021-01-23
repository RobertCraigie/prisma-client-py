# WARNING: if you are editing this file you must stage it before running tests
#
# NOTE: we don't care which http method we use here as this file is replaced
# with the method that the user specifies

HTTP = None

try:
    import aiohttp
except ImportError:
    pass
else:
    from ._aiohttp_http import HTTP, Response


try:
    import requests
except ImportError:
    pass
else:
    from ._requests_http import HTTP, Response


if HTTP is None:
    raise ImportError('Either aiohttp or requests must be installed.')
