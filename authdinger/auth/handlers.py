import os, bcrypt
from ..utils.exception import DingerNotOk
from ..utils import bstream
from .. import SEEK_END, SEEK_CUR, SEEK_START

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

    fname = "{}.rseg".format(data["email-token"])
    path = os.path.join(config["dirs"]["auth-data"],fname)

    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            raise DingerNotOk("Empty User File")

        value = bstream.latest_r(f, b"password-hash")

    req.server.logger.log("Auth Password data {} vs pw {}".format(data, value))

    if value != data["password-hash"]:
        raise DingerNotOk("password mismatch")


def pw_set(req, config, data):
    req.server.logger.log("Setting Password {}".format(
        bstream.unquote(data["email-token"])))

    fname = "{}.rseg".format(data["email-token"])
    print("fname is {}".format(fname))
    path = os.path.join(config["dirs"]["auth-data"],fname)

    with open(path, "wb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            details = [
                "email-token", data["email-token"],
                "password-hash", data["password-hash"]]
        else:
            details = ["password-hash", data["password-hash"]]

        bstream.send_r(f, details)
