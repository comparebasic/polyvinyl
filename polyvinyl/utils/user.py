import os, urllib, random, bcrypt
from .. import lin, SALT_BYTES, SEEK_END, SEEK_CUR, SEEK_START
from ..utils.exception import PolyVinylNotOk 

def get_userdir(config, email_token):
    return os.path.join(config["dirs"]["user-data"], email_token)

def get_userfile(config, email_token):
    return os.path.join(get_userdir(config, email_token),
                "details.linr")

def create(req, config, data):
    email_token = lin.quote(data["email"])
    path = get_userfile(config, email_token.decode("utf-8"))

    req.server.logger.log("Email Token Value {}".format(
        lin.unquote(email_token)))

    if os.path.exists(path):
        req.server.logger.log("User Exists {}".format(path))
        raise PolyVinylNotOk("User Exists")
    
    data["salt"] = bcrypt.gensalt()

    details = [
        "email-token", email_token,
        "email", data["email"],
        "fullname", data["fullname"],
        "salt", data["salt"]]

    req.server.logger.log("Create User {}".format(details))
    os.mkdir(get_userdir(config, email_token.decode("utf-8")))
    with open(path, "wb+") as f:
        lin.send_r(f, details) 

        
def pw_hash(req, config, data):
    path = get_userfile(config, data["email-token"])

    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            raise PolyVinylNotOk("Empty User File")

        value = lin.latest_r(f, b"salt")
        password = data["password"].encode("utf-8")
        del data["password"]

        return bcrypt.hashpw(password, value)
