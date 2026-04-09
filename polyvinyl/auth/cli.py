import socket
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from . import sign, enc
from ..utils import lin
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


def query_path(path, self_key, enc_key, details):
    aim = "concat={}@{}".format(enc_key["sym-ident"].name, enc_key["sym-ident"].location)

    sig = sign.arr_append_sig(self_key["priv-ident"], self_key, details)
    details += ["end-sig", sig]

    print("Details {}".format(details))

    msg = enc.pack(enc_key, details)

    print("Enc Details {}".format([b"aim", aim, msg, ""]))
    exit(1)

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path) 
    except FileNotFoundError as err:
        raise PolyVinylError("Unable to connnect to socket {}".format(path), err)

    lin.send(sock, [b"aim", aim, msg, ""])
    answer = lin.recv_rec(sock) 
    sock.close()

    if len(answer):
        ok = cli_to_bool(oks)
        anser = answer[1:]
    else:
        ok = False

    return ok, answer 


def respond(stream, ident, details):
    details = [b"aim", ident.ident] + details + [""]
    lin.send(stream, details)
