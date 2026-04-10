import socket
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from . import sign, enc
from ..utils import lin, identifier
from ..utils.exception import PolyVinylNotOk, PolyVinylError

ENC = "hmac-concat"

Incomplete = b"in"
Ok = b"ok"
No = b"no"


def cli_to_bool(ok: bytes):
    match ok:
        case b"ok":
            return True
        case b"no":
            return False 
        case b"in":
            return Incomplete 


def send(stream, sign_key, enc_key, details):
    aim = "concat={}@{}".format(enc_key["sym-ident"].name, enc_key["sym-ident"].location)

    sig = sign.arr_append_sig(sign_key["priv-ident"], sign_key, details)
    details += ["end-sig", sig]
    print("Details {}".format(details))

    msg = enc.pack(enc_key, details)

    print("Enc Details {}".format([b"aim", aim, msg, ""]))
    lin.send(stream, [b"aim", aim, msg, ""])


def recv(stream, keys):
    obf = lin.recv_rec(stream)
    print("Obf {}".format(obf))

    if obf.get("aim"):
        aim = obf["aim"] 
    else:
        raise PolyVinylError("Expected aim to be first item", obf)

    aim_ident = identifier.Ident(aim)

    print(aim_ident)
    sign_key = keys[aim_ident.location]
    enc_key = keys[aim_ident.name]

    if aim.tag == b"concat" and aim.name == b"sym-aes":
        obfused = obf[2]

    items = unpack(enc_key, obfused)

    try:
        sign.arr_verify_sig(sign_key["pub-ident"], sign_key, items)
    except Exception as err:
        raise err

    return arr_to_dict(items)


def send_recv(path, ident, keys, details):

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path) 
    except FileNotFoundError as err:
        raise PolyVinylError("Unable to connnect to socket {}".format(path), err)

    print(keys.keys())
    sign_key = keys[ident.location]
    enc_key = keys[ident.name]

    send(sock, sign_key, enc_key, details)
    answer = recv(sock, keys) 
    sock.close()

    if len(answer):
        ok = cli_to_bool(answer["ok"])
    else:
        ok = False

    return ok, answer 
