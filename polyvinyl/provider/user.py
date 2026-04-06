import os, urllib, random, bcrypt
from . import form, role as role_d
from ..utils.exception import PolyVinylNotOk, PolyVinylKnockout
from ..utils import token as token_d, lin, identifier
from ..auth import cli
from .. import SALT_BYTES, SEEK_END, SEEK_CUR, SEEK_START

DETAILS_NAME = "details"


def get_userdir(config, email_token):
    return os.path.join(config["dirs"]["user-data"], email_token)


def get_userfile(config, email_token, name):
    return os.path.join(get_userdir(config, email_token),
                "{}.linr".format(name))


def load_user(config, role, password=None, code=None, consume="no"):
    role_id = role.get("id")
    if not role_id:
        raise PolyVinylNoAuth("No role id defined in role")

    path = get_userfile(config, role_id, DETAILS_NAME)
    user = None

    keys = config["fields"]["user"]
    try:
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            keys = config["fields"]["user"]
            if not code:
                keys["salt"] = "bin"
            user = lin.map_str_r(f, keys)
    except FileNotFoundError:
        pass
    
    if not code:
        value = bcrypt.hashpw(password, user["salt"]).hex()
        code = pw_auth(config, role_id, value)
        del user["salt"]

    if not code:
        raise PolyVinylNoAuth("No code defined for user, password {}".format(
            bool(password)))

    names = []
    with open(path, "rb") as f:
        f.seek(0, SEEK_END)
        while True:
            rec = lin.next_rec(f, None)
            if not rec:
                break

            names.append(rec["role"])
    ok, reason =  verify_roles(role, names, code, consume)
    if not ok:
        raise PolyVinylNoAuth(reason)

    if user:
        role["user"] = user


def create(req, config, data):
    role_id = lin.quote(data["email"]).decode("utf-8")
    path = get_userfile(config, role_id, DETAILS_NAME)

    req.server.logger.log("Email Token Value {}".format(
        lin.unquote(role_id)))

    if os.path.exists(path):
        req.server.logger.error("User Exists {}".format(path))
        raise PolyVinylNotOk("User Exists")
    
    data["salt"] = bcrypt.gensalt()

    details = [
        "role-id", role_id,
        "email", data["email"],
        "fullname", data["fullname"],
        "salt", data["salt"]]

    req.server.logger.log("Create User {}".format(details))
    dir_path = get_userdir(config, role_id) 
    os.mkdir(dir_path)

    with open(path, "wb+") as f:
        lin.send_rec(f, details) 

    role_d.set_id(req.role, role_id)

    for v in ["forms", "idents"]:
        os.mkdir(os.path.join(dir_path, v))

    if config.get("auth-socket"): 
        cli.query_path(config["auth-socket"], req.server.key, (
            "ident", 
                "register={}".format(role_id),
            ))

    else:
        raise PolyVinylNotOk("No Auth Service Defined")

    role_ident = identifier.Ident("role={}@{}".format("subscriptions", role_id))
    add_role(req, role_ident)


def pw_auth(config, role_id, value):
    "Call the Auth service to validate a password\n"
    if config.get("auth-socket"): 
        del req.form_data["password"]

        code = cli.query_path(config["auth-socket"], req.server.key, (
            "ident",     
                "password_auth={}@{}".format(value, role_id),
        ))

        return code
    else:
        raise PolyVinylNotOk("No Auth Service Defined")


def get_subscription_urls(req, role_id):
    config = req.server.config

    six = cli.query_path(config["auth-socket"], req.server.key, (
        "ident",     
            "get_code=subscriptions@{}".format(role_id),
    ))

    manage = "{}/{}?{}".format(
        config["url"], "auth/subscriptions", form.to_query(config, {
        "email": role_id,
        "code":six
    }));

    unsubscribe = "{}/{}?{}".format(
        config["url"], "auth/subscriptions", form.to_query(config, {
        "email": role_id,
        "code": six,
        "unsub": "all"
    }));

    return {
        "subscription-url": manage,
        "unsubscribe-url": unsubscribe,
        "url": config["url"]
    }
