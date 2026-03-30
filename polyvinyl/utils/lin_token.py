import os, time
from ..utils import token as token_d, config as config_d
from ..utils.exception import PolyVinylError, PolyVinylNotOk
from .. import lin, SEEK_END, SEEK_START

def make(path, content):
    if os.path.exists(path):
        raise FileExistsError(path)

    token = token_d.get_token(content)
    with open(path, "wb+") as f:
        lin.send_rec(f, [token])

    return token


def next_nth(path):
    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        latest = lin.next_rec(f, None)
        if latest and latest.get("nth"):
            n = int.from_bytes(latest["nth"], "big") + 1
        else:
            n = 1

        if n < token_d.TOKEN_MAX:
            f.seek(0, SEEK_START)
            token = f.read(token_d.TOKEN_SIZE)

            return n, token_d.get_nth(token, n)

    return -1, None


def next_or_make(path, content):
    n = -1
    if not os.path.exists(path):
        make(path, content)
        return next_nth(path)

    if os.path.exists(path):
        n, six = next_nth(path)
        if n >= 1:
            return n, six
        else:
            orig, name, ext = config_d.get_name_ext(path)
            prev = name + '_' + token_d.now_hex() + "." + ext
            os.rename(path, prev)

            make(path, content)
            return next_nth(path)


def check(path, six: str, consume=False):
    if not os.path.exists(path):
        raise PolyVinylError("Token does not exist")

    with open(path, "rb") as f:
        token = f.read(token_d.TOKEN_SIZE)

    try:
        if not token_d.check_six(token, six):
            return False 
    except ValueError as err:
        return False 

    if not consume:
        return True

    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        latest = lin.next_rec(f, None)
        if latest and latest.get("nth"):
            n = int.from_bytes(latest["nth"], "big")
            if n >= token_d.nth(six):
                raise PolyVinylNotOk("Token already consumed")

    with open(path, "ab") as f:
        f.seek(0, SEEK_END)
        lin.send_rec(f, [
            "nth", token_d.nth(six).to_bytes(4, "big"),
            "consume-date", token_d.time_bytes(time.time())
        ])

    return True 
