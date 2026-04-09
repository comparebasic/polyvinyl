import os
from ...utils import lin, lin_token
from ...utils.exception import PolyVinylNotOk
from . import dir as dir_d
    

def _code(req, ident, data, consume=False):
    config = req.server.config
    email_token = ident.location
    role_name = ident.name

    req.server.logger.log("Consuming Token {}".format(
        lin.unquote(email_token)))

    dir_path = dir_d.get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        return b"no"

    path = dir_d.get_tokenfile(config, email_token, "{}.linr".format(role_name))
    if not lin_token.check(path, data["six-code"], consume):
        return b"no"

    return b"ok"


def get_code(req, ident, data):
    config = req.server.config
    email_token = ident.location
    role_name = ident.name

    req.server.logger.log("Consuming Token {}".format(
        lin.unquote(email_token)))

    dir_path = dir_d.get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        raise PolyVinylNotOk("User dir not found", dir_path)

    path = dir_d.get_tokenfile(config, email_token, "{}.linr".format(role_name))
    n, code = lin_token.next(path)

    if not code:
        raise PolyVinylNotOk("Invalid", path)

    return [Ok, token.now(), "code", code]


def consume_code(req, ident, data):
    _code(req, ident, data, consume=True)


def check_code(req, ident, data):
    _code(req, ident, data, consume=False)


def role_make(req, ident, data):
    config = req.server.config
    req.server.logger.log("Getting Email Subscription {}".format(
        lin.unquote(ident.location)))

    email_token = ident.location
    dir_path = dir_d.get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        raise PolyVinylNotOk("User dir not found", dir_path)

    path = dir_d.get_tokenfile(config, email_token, "{}.linr".format(ident.name))
    n, code = lin_token.next_or_make(path, email_token)

    return [Ok, token.now(), "code", code]


def verify(req, ident, data):
    config = req.server.config
    req.server.logger.log("Getting Email Subscription {}".format(
        lin.unquote(ident.location)))

    valid = False
    invalid = False 
    names = [] 
    ident = identifier.Ident("check_code=@{}".format(ident.location))
    for k,v in data.items():
        if k == b"ident":
            continue
                
        ident.name = k
        ok = _code(req, ident, {"six-code": v}, consume=False)
        if ok != b"ok":
            invalid = True
        else:
            valid = True

        names.append(k)
        names.append(ok)
            
    ok = b"ok"
    if not valid:
        ok = b"no"
    elif valid and invalid:
        ok = b"in"

    return [ok, token.now()] + names

    

