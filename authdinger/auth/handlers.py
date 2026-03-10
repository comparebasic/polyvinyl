import os, bcrypt
from ..utils.exception import DingerNotOk
from ..utils import bstream
from .. import SEEK_END, SEEK_CUR, SEEK_START
import datetime


def get_authdir(config, email_token):
    return os.path.join(config["dirs"]["auth-data"], email_token)

def get_authfile(config, email_token):
    return os.path.join(get_authdir(config, email_token),
                "auth.linr")

def get_tokenfile(config, email_token, token):
    return os.path.join(get_authdir(config, email_token), token)

def Handle(req, config, ident, data):
    func = None
    if ident.ext == "email":
        if ident.tag == "pw_auth":
            func = pw_auth
            data["email-token"] = ident.base

        if ident.tag == "pw_set":
            func = pw_set
            data["email-token"] = ident.base

    if not func:
        raise DingerNotOk("Not func found for handler {}".format(ident))

    func(req, config, data)


def pw_auth(req, config, data):
    req.server.logger.log("Auth Password {}".format(
        bstream.unquote(data["email-token"])))

    path = get_authfile(config, data["email-token"])

    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            raise DingerNotOk("Empty User File")

        value = bstream.latest_r(f, b"password-hash")

    req.server.logger.log("Auth Password data {} vs pw {}".format(data, value))

    if value != data["password-hash"]:
        raise DingerNotOk("password mismatch")


def token_create(req, config, data):
    req.server.logger.log("Setting Token {}".format(
        bstream.unquote(data["email-token"])))

    dir_path = get_authdir(config, data["email-token"])
    if not os.path.exists(dir_path):
        raise DingerNotOk("User dir not found")

    token = utils.token(data["email-token"])
    path = get_tokenfile(config, data["email-token"], token)

    with open(path, "w+") as f:
        f.write(rfc822(datetime.now()))

    return token


def token_consume(req, config, data):
    req.server.logger.log("Consuming Token {}".format(
        bstream.unquote(data["email-token"])))

    dir_path = get_authdir(config, data["email-token"])
    if not os.path.exists(dir_path):
        raise DingerNotOk("User dir not found")

    token = utils.token(data["email-token"])
    path = get_tokenfile(config, data["email-token"], token)

    if not os.path.exists(path):
        raise DingerNotOk("Invalid")

    os.remove(path)


def pw_set(req, config, data):
    req.server.logger.log("Setting Password {}".format(
        bstream.unquote(data["email-token"])))

    path = get_authfile(config, data["email-token"])

    dir_path = get_authdir(config, data["email-token"])
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        os.mkdir(os.path.join(dir_path, "tokens"))

    with open(path, "wb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            details = [
                "email-token", data["email-token"],
                "password-hash", data["password-hash"]]
        else:
            details = ["password-hash", data["password-hash"]]

        bstream.send_r(f, details)
