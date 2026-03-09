import os, urllib, random, bcrypt
from ..utils import bstream
from .exception import DingerNotOk 
from .. import SALT_BYTES, SEEK_END, SEEK_CUR, SEEK_START

def create(req, config, data):
    email_token = bstream.quote(data["email"])
    req.server.logger.log("Email Token {}".format(email_token))
    fname = "{}.rseg".format(email_token.decode("utf-8"))
    path = os.path.join(config["dirs"]["user-data"],fname)

    req.server.logger.log("Email Token Value {}".format(
        bstream.unquote(email_token)))

    if os.path.exists(path):
        req.server.logger.log("User Exists {}".format(path))
        raise DingerNotOk("User Exists")
    
    data["salt"] = bcrypt.gensalt()
    data["password-hash"] = bcrypt.hashpw(
        data["password"].encode("utf-8"), data["salt"])
    del data["password"]

    details = [
        "email-token", email_token,
        "fullname", data["fullname"],
        "salt", data["salt"]]

    req.server.logger.log("Create User {}".format(details))
    with open(path, "wb+") as f:
        bstream.send_r(f, details) 

        
def pw_hash(req, config, data):
    fname = "{}.rseg".format(data["email-token"])
    path = os.path.join(config["dirs"]["user-data"],fname)

    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            raise DingerNotOk("Empty User File")

        value = bstream.latest_r(f, b"salt")
        password = data["password"].encode("utf-8")
        del data["password"]

        return bcrypt.hashpw(password, value)
