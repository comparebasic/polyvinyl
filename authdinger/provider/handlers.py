import socket
from .. import DingerNotOk
from ..utils import bstream
from ..utils import user 

def Handle(req, config, ident, data):
    func = None
    if ident.tag == "action":
        func = config["_handler-action"].get(ident.base)
    elif ident.tag == "func":
        func = config["_handler-func"].get(ident.base)

    if not func:
        raise DingerNotOk("Not func found for handler {}".format(ident))

    func(req, config, data)


def pw_auth(req, config, data):
    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        bstream.send(sock, (
                "pw_auth@{}".format(data["user"]),
                data["password"], 
                ""))

        answer = bstream.read_next(sock) 
        if answer != "ok":
            reason = bstream.read_next(sock)
            sock.close()
            raise DingerNotOk("Invalid", reason)

        sock.close()

    else:
        raise DingerNotOk("No Auth Service Defined")


def redir(req, config, data):
    req.send_response(307)
    req.send_header("Location", data["redir"])
    req.end_headers()


def setup_handlers(config):
    config["_handler-func"] = {
        "pw_auth": pw_auth,
        "register": user.create,
    }
    config["_handler-action"] = {
        "redir": redir,
    }
    
