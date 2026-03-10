import random, time, hashlib, os
from ..utils import session

def get_token(content):
    h = hashlib.sha256()
    h.update(content)
    h.update(time_bytes(time.time()))
    h.update(random.randbytes(4))
    return h.hexdigest() 

def get_short_token(content):
    return get_token(content)[32:]

def rfc822(dt):
    ctime = dt.ctime()
    return "{}, {} {}".format(
        ctime[:3], ctime[4:8], dt.strftime(" %d %Y %H:%M:%S %Z"))
