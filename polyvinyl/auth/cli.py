import socket
from .. import lin
from ..utils.exception import PolyVinylNotOk

ENC = "hmac-concat"

def query_path(path, key, details):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path) 
    except FileNotFoundError as err:
        raise PolyVinylError(err.args[0], err)

    sig = lin.get_sig(key, details)
    details = [b"aim", ENC] + list(details) + ["end-sig", sig, ""] 
    lin.send(sock, details)
    answer = lin.read_next(sock) 
    reason = lin.read_next(sock)
    if answer != b"ok":
        sock.close()
        raise PolyVinylNotOk("Invalid", reason)

    sock.close()
    return reason
