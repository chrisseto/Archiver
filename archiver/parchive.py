import os
import glob
import subprocess

PAR2BIN = 'par2'
PARITY_CUT_OFF_SIZE = 100 * 1024  # 100kb


def create_parity_files(path, force=False):
    if not force and os.path.getsize(path) < PARITY_CUT_OFF_SIZE:
        return False
    if subprocess.call([PAR2BIN, 'c', '-n1', path]) == 0:
        return [
            os.path.abspath(fpath)
            for fpath in
            glob.glob('*.par2')
            if path in fpath
        ]
    return False


def verify_parity_files():
    pass


def restory_file_from_parities():
    pass
