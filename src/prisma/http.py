# NOTE: we don't care which http method we use here as this file is replaced
# with the method that the user specifies
# pyright: reportUnusedImport=false

HTTP = None

try:
    import aiohttp
except ImportError:
    pass
else:
    from ._aiohttp_http import HTTP, Response, client


if HTTP is None:
    try:
        import requests
    except ImportError:
        pass
    else:
        from ._requests_http import HTTP, Response, client


if HTTP is None:
    raise ImportError('Either aiohttp or requests must be installed.')
