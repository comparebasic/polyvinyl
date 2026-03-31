import os, bcrypt, time
from ... import lin
from ...utils.exception import PolyVinylNotOk
from ...utils import token, lin_token
from ... import SEEK_END, SEEK_CUR, SEEK_START
from . import dir as dir_d


def pw_auth(req, ident, data):
    config = req.server.config
    req.server.logger.log("Auth Password {}".format(
        lin.unquote(ident.name)))

    path = dir_d.get_authfile(config, ident.name)

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

    path = dir_d.get_authfile(config, ident.name)
    with open(path, "wb") as f:
        f.seek(0, SEEK_END)
        details = ["password-hash", data["password-hash"]]
        lin.send_rec(f, details)


def register(req, ident, data):
    config = req.server.config
    req.server.logger.log("Register {}".format(
        lin.unquote(ident.name)))

    dir_path = dir_d.get_authdir(config, ident.name)
    if os.path.exists(dir_path):
        raise PolyVinylNotOk("User already exists")

    os.mkdir(dir_path)
    os.mkdir(os.path.join(dir_path, "tokens"))

    path = dir_d.get_authfile(config, ident.name)
    with open(path, "wb") as f:
        details = ["email-token", ident.name, 
            "register-time", token.time_bytes(time.time())]

        lin.send_rec(f, details)
