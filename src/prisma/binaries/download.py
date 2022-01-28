import gzip
import os
import shutil
from pathlib import Path
from stat import S_IXUSR, S_IWUSR, S_IRUSR

from ..http import client
from ..utils import maybe_async_run


def download(url: str, to: Path) -> None:
    to.parent.mkdir(parents=True, exist_ok=True)

    tar = to.with_suffix('.gz.tmp')
    maybe_async_run(client.download, url, tar)

    # decompress to a tmp file before replacing the original
    with gzip.open(tar, 'rb') as f_in:
        with open(to, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # chmod +x
    os.chmod(to, S_IXUSR | S_IWUSR | S_IRUSR)

    # remove temporary files
    os.remove(tar)
