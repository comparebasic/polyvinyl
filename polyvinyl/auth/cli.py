import socket
from ..utils import lin
from ..utils.exception import PolyVinylNotOk

ENC = "hmac-concat"


class Incomplete:
    pass


def cli_to_bool(ok: bytes):
    match ok:
        case b"ok":
            return True
        case b"no":
            return False 
        case b"in":
            return Incomplete 


def query_path(path, key, details):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path) 
    except FileNotFoundError as err:
        raise PolyVinylError(err.args[0], err)

    sig = lin.get_sig(key, details)
    details = [b"aim", ENC] + list(details) + ["end-sig", sig, ""] 
    lin.send(sock, details)
    answer = lin.recv_rec(sock) 

    if len(answer):
        ok = cli_to_bool(oks)
        anser = answer[1:]
    else:
        ok = False

    sock.close()
    return ok, answer 


def respond(stream, ident, details):
    details = [b"aim", ident.ident] + details + [""]
    lin.send(stream, details)
