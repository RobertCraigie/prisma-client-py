import sys
import json
import logging
from typing import Dict, List, Optional, Type, Any
from pydantic import BaseModel


log: logging.Logger = logging.getLogger(__name__)


class Request(BaseModel):
    # JSON RPC protocol version
    jsonrpc: str = '2.0'

    # identifies a request
    id: int

    # request intention
    method: str

    # request payload
    params: Optional[Dict[str, Any]]


class Response(BaseModel):
    id: int
    jsonrpc: str = '2.0'
    result: Optional[Dict[str, Any]]


class Manifest(BaseModel):
    prettyName: str
    defaultOutput: str
    denylist: Optional[List[str]]
    requiresEngines: Optional[List[str]]
    requiresGenerators: Optional[List[str]]


# TODO: proper types
method_mapping: Dict[str, Type[Request]] = {
    'getManifest': Request,
    'generate': Request,
}


def readline() -> Optional[str]:
    try:
        line = input()
    except EOFError:
        log.debug('Ignoring EOFError')
        return None

    return line


def parse(line: str) -> Request:
    data = json.loads(line)
    try:
        method = data['method']
    except (KeyError, TypeError):
        # TODO
        raise
    else:
        request_type = method_mapping.get(method)
        if request_type is None:
            raise RuntimeError(f'Unknown method: {method}')

    return request_type(**data)


def reply(response: Response) -> None:
    dumped = json.dumps(response.dict()) + '\n'
    print(dumped, file=sys.stderr, flush=True)
    log.debug('Replied with %s', dumped)
