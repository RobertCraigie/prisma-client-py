import os
import gzip
import shutil
from pathlib import Path

from ..http import client
from ..utils import maybe_async_run


def download(url: str, to: str) -> None:
    Path(to).parent.mkdir(parents=True, exist_ok=True)

    tmp = to + '.tmp'
    tar = to + '.gz.tmp'
    maybe_async_run(client.download, url, tar)

    # decompress to a tmp file before replacing the original
    with gzip.open(tar, 'rb') as f_in:
        with open(tmp, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # chmod +x
    status = os.stat(tmp)
    os.chmod(tmp, status.st_mode | 0o111)

    # override the original
    shutil.copy(tmp, to)

    # remove temporary files
    os.remove(tar)
    os.remove(tmp)
