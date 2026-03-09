import socket
from .. import DingerNotOk
from ..utils import bstream
from ..utils import user 
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
    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        data["email-token"] = bstream.quote(data["email"]).decode("utf-8")
        password_hash = user.pw_hash(req, config, data)

        bstream.send(sock, (
            "ident",     
                "pw_auth@{}.email".format(data["email-token"]),
            "password-hash",
                password_hash, 
            ""))

        answer = bstream.read_next(sock) 
        if answer != b"ok":
            reason = bstream.read_next(sock)
            sock.close()
            raise DingerNotOk("Invalid", reason)

        sock.close()

    else:
        raise DingerNotOk("No Auth Service Defined")


def pw_set(req, config, data):
    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        email_token = bstream.quote(data["email"]).decode("utf-8")
        bstream.send(sock, (
            "ident", 
                "pw_set@{}.email".format(email_token),
            "password-hash",
                data["password-hash"], 
            ""))

        answer = bstream.read_next(sock) 
        if answer != b"ok":
            reason = bstream.read_next(sock)
            sock.close()
            raise DingerNotOk("Invalid", reason)

        sock.close()

    else:
        raise DingerNotOk("No Auth Service Defined")


def register(req, config, data):
    try:
        user.create(req, config, data)
    except DingerNotOk as err:
        raise DingerNotOk("Unable to register", err.args[0])


def redir(req, config, data):
    req.send_response(302)
    req.send_header("Location", data["redir"])
    req.end_headers()


def setup_handlers(config):
    config["_handler-func"] = {
        "pw_auth": pw_auth,
        "pw_set": pw_set,
        "register": user.create,
    }
    config["_handler-action"] = {
        "redir": redir,
    }
