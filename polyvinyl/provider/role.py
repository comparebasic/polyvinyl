import os, urllib, random, bcrypt
from . import form
from ..utils.exception import PolyVinylNotOk, PolyVinylKnockout, PolyVinylNoAuth
from ..utils import token as token_d, lin, identifier, user
from ..auth import cli
from .. import SALT_BYTES, SEEK_END, SEEK_CUR, SEEK_START

ROLES_NAME = "roles"


def set_id(role, token):
    if role.get("id"):
        raise PolyVinylNoAuth("Id already exists on role")
    role["id"] = token


def verify_roles(role, names):
    role_id = role.get("id")
    if not role_id:
        raise PolyVinylNoAuth("No role id defined in role")

    details = [
        "ident",     
            "verify={}@{}".format(",".join(names), role_id)]

    for k, v in names.items():
        details.append(k)
        details.append(v)

    ok, reason = cli.query_path(config["auth-socket"], req.server.key, details)

    if not ok:
        return False

    else:
        for r in reason.split(","):
            role[r.decode("utf-8")] = True 

    return True, reason
    

def add_role(req, ident, data={}):
    config = req.server.config
    role_id = req.role["id"] 
    role_name = ident.name

    date = token_d.now()
    path = get_userfile(config, role_id, ROLES_NAME)
    with open(path, "wb+") as f:
        six = cli.query_path(config["auth-socket"], req.server.key, (
            "ident",     
                "role_make={}@{}".format(role_name, role_id),
        ))

        lin.send_rec(f, ["date", date, "role", role_name])
        data["role-code-{}".format(role_name)] = six
