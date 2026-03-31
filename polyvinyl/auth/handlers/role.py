import os
from ... import lin
from ...utils.exception import PolyVinylNotOk
from ...utils import lin_token
from . import dir as dir_d


def _code(req, ident, data, consume=False):
    config = req.server.config
    req.server.logger.log("Consuming Token {}".format(
        lin.unquote(ident.location)))

    email_token = ident.location
    dir_path = dir_d.get_authdir(config, email_token)
    if not os.path.exists(dir_path):
        raise PolyVinylNotOk("User dir not found", dir_path)

    path = dir_d.get_tokenfile(config, email_token, "{}.linr".format(ident.name))
    if not lin_token.check(path, data["six-code"], consume):
        raise PolyVinylNotOk("Invalid", path)

    req.server.logger.log("Token Consumed {}".format(path))


def role_consume(req, ident, data):
    _code(req, ident, data, consume=True)


def role_check(req, ident, data):
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
    return code
