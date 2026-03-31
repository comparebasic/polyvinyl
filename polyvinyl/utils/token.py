import random, time, hashlib, os

TOKEN_SIZE = 64
TOKEN_MAX = 19

def now_hex():
    return now().hex()

def now():
    return time_bytes(time.time())


def time_bytes(t):
    return int(t*1000000).to_bytes(8)


def time_from_bytes(v):
    return time.strftime(
        '%Y-%m-%d %H:%M:%S',
        time.localtime(float(int.from_bytes(v, "big"))/1000000.0))


def make_token(content:bytes, nonce_one: bytes, nonce_two: bytes):
    h = hashlib.sha512()
    h.update(content)
    h.update(nonce_one)
    h.update(nonce_two)
    return h.digest()


def get_token(content):
    if not isinstance(content, (bytes)):
        content = content.encode("utf-8")

    return make_token(content, time_bytes(time.time()), random.randbytes(16))

def get_text_token(content):
    if not isinstance(content, (bytes)):
        content = content.encode("utf-8")

    return make_token(content, time_bytes(time.time()), random.randbytes(16))[32:].hex()

def nth(six: str):
    return int(six[4:6])


def get_nth(raw_token, n: int):
    tlength = 3 
    if n*tlength > len(raw_token)-tlength:
        raise ValueError("position is greater than max", n)

    pos = n*tlength
    b3 = raw_token[pos:pos+tlength]
    four = int.from_bytes(b3, "big") % 9999

    print("Pos {} B3 {} Four {} N {}".format(pos, int.from_bytes(b3, "big"), four, n))
    return "{:04d}{:02d}".format(four, n)


def check_six(raw_token, six: str):
    if isinstance(six, (bytes)):
        six = six.decode("ascii")
    print("{} vs {}".format(get_nth(raw_token, nth(six)), six))
    return get_nth(raw_token, nth(six)) == six


def get_short_token(content):
    return get_token(content)[32:]


def rfc822(dt):
    ctime = dt.ctime()
    return "{}, {} {} {} {}".format(
        ctime[:3], ctime[8:10], ctime[4:7], ctime[20:24], dt.strftime("%H:%M:%S %z (%Z)"))
