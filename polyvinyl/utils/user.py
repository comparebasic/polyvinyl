import os, urllib, random, bcrypt
from .. import lin, SALT_BYTES, SEEK_END, SEEK_CUR, SEEK_START
from ..utils.exception import PolyVinylNotOk, PolyVinylKnockout

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
        req.server.logger.error("User Exists {}".format(path))
        raise PolyVinylNotOk("User Exists")
    
    data["salt"] = bcrypt.gensalt()

    details = [
        "email-token", email_token,
        "email", data["email"],
        "fullname", data["fullname"],
        "salt", data["salt"]]

    req.server.logger.log("Create User {}".format(details))
    dir_path = get_userdir(config, email_token.decode("utf-8")) 
    os.mkdir(dir_path)
    with open(path, "wb+") as f:
        lin.send_r(f, details) 

    for v in ["forms", "idents"]:
        os.mkdir(os.path.join(dir_path, v))

        
def pw_hash(req, config, data):
    path = get_userfile(config, data["email-token"])

    if not os.path.exists(path):
        data["error"] = "User not found"
        raise PolyVinylKnockout("User not found")

    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        
        if f.tell() == 0:
            raise PolyVinylNotOk("Empty User File")

        value = lin.latest_r(f, b"salt")
        password = data["password"].encode("utf-8")
        del data["password"]

        return bcrypt.hashpw(password, value)
