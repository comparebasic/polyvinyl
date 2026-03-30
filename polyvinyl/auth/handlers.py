import os, bcrypt, time
from datetime import datetime
from .. import lin
from ..utils.exception import PolyVinylNotOk
from ..utils import token, lin_token
from .. import SEEK_END, SEEK_CUR, SEEK_START


def get_authdir(config, email_token):
    return os.path.join(config["dirs"]["auth-data"], email_token)


def get_authfile(config, email_token):
    return os.path.join(get_authdir(config, email_token),
                "auth.linr")


def get_tokenfile(config, email_token, token):
    return os.path.join(
            os.path.join(
                get_authdir(config, email_token),
                "tokens"),
            token)


def pw_auth(req, ident, data):
    config = req.server.config
    req.server.logger.log("Auth Password {}".format(
        lin.unquote(ident.name)))

    path = get_authfile(config, ident.name)

    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            raise PolyVinylNotOk("Empty User File")

        value = lin.latest_r(f, b"password-hash")

    req.server.logger.log("Auth Password data {} vs pw {}".format(data, value))

    if value != data["password-hash"]:
        raise PolyVinylNotOk("password mismatch")


def pw_set(req, ident, data):
    config = req.server.config
    req.server.logger.log("Setting Password {}".format(
        lin.unquote(ident.name)))


    dir_path = get_authdir(config, ident.name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        os.mkdir(os.path.join(dir_path, "tokens"))

    path = get_authfile(config, ident.name)
    with open(path, "wb") as f:
        f.seek(0, SEEK_END)
        details = ["password-hash", data["password-hash"]]
        lin.send_rec(f, details)


def register(req, ident, data):
    config = req.server.config
    req.server.logger.log("Register {}".format(
        lin.unquote(ident.name)))

    dir_path = get_authdir(config, ident.name)
    if os.path.exists(dir_path):
        raise PolyVinylNotOk("User already exists")

    os.mkdir(dir_path)
    os.mkdir(os.path.join(dir_path, "tokens"))

    path = get_authfile(config, ident.name)
    with open(path, "wb") as f:
        details = ["email-token", ident.name, 
            "register-time", token.time_bytes(time.time())]

        lin.send_rec(f, details)


def get_signin_code(req, ident, data):
    config = req.server.config
    email_token = ident.name
    req.server.logger.log("Setting Token {}".format(
        lin.unquote(ident.name)))

    email_token = ident.name
    dir_path = get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        raise PolyVinylNotOk("User dir not found", dir_path)

    path = get_tokenfile(config, ident.name, "signin.linr")
    n, code = lin_token.next_or_make(path, email_token)
    return code


def token_consume_code(req, ident, data):
    config = req.server.config
    req.server.logger.log("Consuming Token {}".format(
        lin.unquote(ident.name)))

    email_token = ident.name
    dir_path = get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        raise PolyVinylNotOk("User dir not found", dir_path)

    path = get_tokenfile(config, ident.name, "signin.linr")
    if not lin_token.check(path, data["six-code"], consume=True):
        raise PolyVinylNotOk("Invalid", path)

    req.server.logger.log("Token Consumed {}".format(path))


def subscription_code(req, ident, data):
    config = req.server.config
    req.server.logger.log("Getting Email Subscription {}".format(
        lin.unquote(ident.name)))

    email_token = ident.name
    dir_path = get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        raise PolyVinylNotOk("User dir not found", dir_path)

    path = get_tokenfile(config, ident.name, "subscriptions.linr")
    n, code = lin_token.next_or_make(path, email_token)
    return code


def token_consume(req, ident, data):
    config = req.server.config
    req.server.logger.log("Consuming Token {}".format(
        lin.unquote(ident.name)))

    email_token = ident.name
    dir_path = get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        raise PolyVinylNotOk("User dir not found", dir_path)

    tk = data["token"].decode("utf-8") 
    path = get_tokenfile(config, ident.name, tk)

    if not os.path.exists(path):
        raise PolyVinylNotOk("Invalid", path)

    os.remove(path)

    req.server.logger.log("Token Consumed {}".format(path))
