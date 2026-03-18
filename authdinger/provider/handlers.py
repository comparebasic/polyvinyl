import socket, bcrypt
from ..utils.exception import \
     DingerNotOk, DingerError, DingerKnockout, DingerReChain
from ..utils import bstream, user, session, templ, form, token
from ..utils.maps import mime_map
from smtplib import SMTP
import smtplib


def _map(req, ident, data, dest):
    config = req.server.config

    kv = {}
    for field in ident.name.split(","):
        parts = field.split("/")
        key = parts[0]
        if len(parts) == 1:
            val_key = parts[0]
        elif len(parts) == 2:
            val_key = parts[1]
        else:
            raise DingerError("Unparsable fields definition", ident.name)

        kv[key] = val_key


    match ident.location:
        case "req":
            for k,v in kv.items():
                if not hasattr(req, v):
                    raise DingerKnockout("Field not found for req {}".format(ident))

            data[key] = getattr(req, v)
        case "query" | "form" | "data" | "cookie" | "session" | "config":
            match ident.location:
                case "query":
                    source = req.query_data
                case "form":
                    source = req.form_data
                case "data":
                    source = data 
                case "cookie":
                    source = req.cookie
                case "session":
                    source = req.session
                case "config":
                    source = config 

            for k,v in kv.items():
                if v.endswith("?"):
                    v = v[:-1]
                    if k.endswith("?"):
                        k = k[:-1]
                    dest[k] = source.get(v)
                else:
                    if not source.get(v):
                        raise DingerKnockout("Field not found for query {}".format(ident))
                    dest[k] = source[v]

    req.server.logger.log("After Map {} {}".format(ident, dest))


def end(req, ident, data):
    req.done = True
    raise DingerKnockout()


def map(req, ident, data):
    _map(req, ident, data, data)


def set_query(req, ident, data):
    req.query_data = {}
    if ident.name:
        _map(req, ident, data, req.query_data)


def get(req, ident, data):
    if req.command != "GET":
        raise DingerKnockout("Method mismatch")


def post(req, ident, data):
    if req.command != "POST":
        raise DingerKnockout("Method mismatch")

def content(req, ident, data):
    config = req.server.config

    parts = ident.name.split(".")
    ext = parts[-1]

    mime = mime_map.get(ext)
    if mime:
        req.header_stage["Content-Type"] = mime;
    req.content += templ.templFrom(config, ident, data)


def data_eq(req, ident, data):
    req.server.logger.log("data_eq {} vs {}".format(data.get(ident.location), ident.name))
    if not data.get(ident.location):
        raise DingerKnockout()

    if ident.name and data[ident.location] != ident.name:
        raise DingerKnockout()

def data_neq(req, ident, data):
    try:
        data_eq(req, ident, data)
    except DingerKnockout:
        return

    raise DingerKnockout()


inc = static = page = content

def redir(req, ident, data):
    req.send_response(302)
    if ident.location == "data":
        location = data.get(ident.name)
    else:
        location = ident.name

    if not location:
        location = "/error"
    elif req.query_data:
        location = "{}?{}".format(
            location,
            form.toQuery(req.server.config, req.query_data))
        
    req.send_header("Location", location)
    for k,v in req.header_stage.items():
        req.send_header(k, v)
    req.end_headers()
    req.done = True
    

def pw_auth(req, ident, data):
    config = req.server.config
    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        data["email-token"] = bstream.quote(data["email"]).decode("utf-8")
        password_hash = user.pw_hash(req, config, data)

        bstream.send(sock, (
            "ident",     
                "pw_auth={}@email".format(data["email-token"]),
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


def token_consume_code(req, ident, data):
    config = req.server.config
    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        email_token = bstream.quote(data["email"]).decode("utf-8")

        bstream.send(sock, (
            "ident",     
                "token_consume_code={}@email".format(email_token),
            "six-code",
                data["six-code"], 
            ""))

        answer = bstream.read_next(sock) 
        if answer != b"ok":
            reason = bstream.read_next(sock)
            sock.close()
            raise DingerNotOk("Invalid", reason)

        del data["six-code"]
        sock.close()

    else:
        raise DingerNotOk("No Auth Service Defined")



def token_consume(req, ident, data):
    config = req.server.config
    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        email_token = bstream.quote(data["email"]).decode("utf-8")

        bstream.send(sock, (
            "ident",     
                "token_consume={}@email".format(email_token),
            "token",
                data["token"], 
            ""))

        answer = bstream.read_next(sock) 
        if answer != b"ok":
            reason = bstream.read_next(sock)
            sock.close()
            raise DingerNotOk("Invalid", reason)

        del data["token"]
        sock.close()

    else:
        raise DingerNotOk("No Auth Service Defined")


def session_start(req, ident, data):
    session.start(req, data)

    cookie = "Ssid={}; Expires={}; HttpOnly; Secure; SameSite=Strict;".format(
        data["session-token"], data["session-expires"])
    del data["session-token"]
    del data["session-expires"]
    req.header_stage["Set-Cookie"] = cookie


def session_open(req, ident, data):
    session.load(req, data)
    req.server.logger.log("Session {}".format(req.session))


def session_close(req, ident, data):
    session.close(req, ident)
    cookie = "Ssid=; Expires={}; HttpOnly; Secure; SameSite=Strict;".format(
        "Thu, 01 Jan 1970 00:00:00 GMT")
    req.header_stage["Set-Cookie"] = cookie
    

def pw_set(req, ident, data):
    config = req.server.config
    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        if data.get("password"):
            data["password-hash"] = bcrypt.hashpw(
                data["password"].encode("utf-8"), data["salt"])
            del data["password"]

        email_token = bstream.quote(data["email"]).decode("utf-8")
        bstream.send(sock, (
            "ident", 
                "pw_set={}@email".format(email_token),
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


def register(req, ident, data):
    config = req.server.config
    try:
        user.create(req, config, data)
    except DingerNotOk as err:
        raise DingerNotOk("Unable to register", err.args[0])

    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        email_token = bstream.quote(data["email"]).decode("utf-8")
        bstream.send(sock, (
            "ident", 
                "register={}@email".format(email_token),
            ""))

        answer = bstream.read_next(sock) 
        if answer != b"ok":
            reason = bstream.read_next(sock)
            sock.close()
            raise DingerNotOk("Invalid", reason)

        data["email-token"] = email_token
        sock.close()

    else:
        raise DingerNotOk("No Auth Service Defined")


def email(req, ident, data):
    config = req.server.config

    if not data.get('email-token'):
        data["email-token"] = bstream.quote(data["email"]).encode("utf-8")

    msg = templ.emailMsgFromIdent(config, 
        ident,
        data,
        from_addr=config["system-email"],
        to_addrs=[data["email"]])

    with SMTP(config["smtp"]) as smtp:
        smtp.send_message(msg, from_addr=msg["From"], to_addrs=msg["To"])


def set_token_url(req, ident, data):
    if not data.get('email-token'):
        data["email-token"] = bstream.quote(data["email"]).decode("utf-8")
    
    data["login-url"] = "{}{}?email={}&six-code={}".format(
        data["url"], ident.name, data["email-token"], data["six-code"])
    

def get_token(req, ident, data):
    config = req.server.config

    if config.get("auth-socket"): 
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(config["auth-socket"]) 

        email_token = bstream.quote(data["email"]).decode("utf-8")
        bstream.send(sock, (
            "ident", 
                "token_create={}@email".format(email_token),
            ""))

        answer = bstream.read_next(sock) 
        if answer != b"ok":
            reason = bstream.read_next(sock)
            sock.close()
            raise DingerNotOk("Invalid", reason)

        tk = bstream.read_next(sock)
        data["token"] = tk.decode("utf-8")
        data["six-code"] = token.get_six(data["token"])
        sock.close()

    else:
        raise DingerNotOk("No Auth Service Defined")

