import os
import glob
import logging
import hashlib
import subprocess

PAR2BIN = 'par2'
PARITY_CUT_OFF_SIZE = 100 * 1024  # 100kb

logger = logging.getLogger(__name__)



class ParchiveException(Exception):
    pass


def _metadata(path):
    sha = hashlib.sha256()
    md5 = hashlib.md5()
    with open(path) as parity:
        while True:
            chunk = parity.read(1024)
            if chunk:
                sha.update(chunk)
                md5.update(chunk)
            else:
                break
    return {
        'sha256': sha.hexdigest(),
        'md5': md5.hexdigest(),
        'lastModified': os.path.getmtime(path),
        'size': os.path.getsize(path)
    }


def build_metadata(paths):
    meta = {}
    for path in paths:
        meta[os.path.basename(path)] = _metadata(path)
    return meta


def create(path, name, redundancy=5, force=False, files=1):
    if not force and os.path.getsize(path) < PARITY_CUT_OFF_SIZE:
        logger.info('Skipping parity creation for "%s", too small.' % name)
        return []
    folder_path = os.path.dirname(path)
    with open(os.devnull, 'wb') as DEVNULL:
        if subprocess.call([
                PAR2BIN,
                'c',
                '-n{}'.format(files),
                '-r{}'.format(redundancy),
                os.path.join(folder_path, '%s.par2' % name),
            path],
                stdout=DEVNULL,
                stderr=DEVNULL) == 0:
            return [
                os.path.abspath(fpath)
                for fpath in
                glob.glob(os.path.join(folder_path, '*.par2'))
                if name in fpath
            ]
        raise ParchiveException()


def verify_file(to_verify, parities):
    return subprocess.call([PAR2BIN, 'v', ' '.join(parities), to_verify]) is 0


def restory_file():
    pass
