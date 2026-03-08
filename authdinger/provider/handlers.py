from .. import DingerNotOk
from ..utils import bstream

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
    if req.user_server:
        ident_s = "pw_auth@{}".format(data["user"])
        b = bstream.add(b"", ident_s)
        b = bstream.add(b"", data["password"])
        print("Sending {}".format(b))
        req.user_server.sendall(b)
        resp = req.user_server.recv(1024)
        print("Recieved {}".format(resp))
    else:
        raise DingerNotOk("No Auth Service Defined")


def redir(req, config, data):
    req.send_response(307)
    req.send_header("Location", data["redir"])
    req.end_headers()
    print("sending redir headers")


def setup(config):
    config["_handler-func"] = {
        "pw_auth": pw_auth,
    }
    config["_handler-action"] = {
        "redir": redir,
    }
    
