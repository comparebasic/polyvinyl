import os, urllib, random, bcrypt
from .. import lin, SALT_BYTES, SEEK_END, SEEK_CUR, SEEK_START
from ..utils.exception import PolyVinylNotOk, PolyVinylKnockout
from ..utils import form
from ..auth import cli


def get_userdir(config, email_token):
    return os.path.join(config["dirs"]["user-data"], email_token)


def get_userfile(config, email_token):
    return os.path.join(get_userdir(config, email_token),
                "details.linr")

def load_role(config, email_token, auth=True):
    path = get_userfile(config, email_token)
    keys = config["fields"]["user"]

    try:
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            keys = config["fields"]["user"]
            if auth:
                keys["salt"] = "bin"
            role = lin.map_str_r(f, keys)
            role["email-token"] = email_token
            return role
    except FileNotFoundError:
        pass
    

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
        lin.send_rec(f, details) 

    for v in ["forms", "idents"]:
        os.mkdir(os.path.join(dir_path, v))


def pw_hash(req, email_token, password):
    "Call the Auth service to validate a password\n"
    config = req.server.config
    role = load_role(config, email_token, auth=True)
    print(role)
    if isinstance(password, (str)):
        password = password.encode("utf-8")
    if role:
        return bcrypt.hashpw(password, role["salt"])


def get_subscription_urls(req, email_token):
    config = req.server.config

    six = cli.query_path(config["auth-socket"], req.server.key, (
        "ident",     
            "subscription_code={}@email".format(email_token),
    ))

    manage = "{}/{}?{}".format(
        config["url"], "auth/subscriptions", form.to_query(config, {
        "email": email_token.encode("utf-8"),
        "code":six
    }));

    unsubscribe = "{}/{}?{}".format(
        config["url"], "auth/subscriptions", form.to_query(config, {
        "email": email_token.encode("utf-8"),
        "code": six,
        "unsub": "all"
    }));

    return {
        "subscription-url": manage,
        "unsubscribe-url": unsubscribe,
        "url": config["url"]
    }
