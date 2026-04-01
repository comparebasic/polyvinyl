"Session opening/closing and creation"
from .. import perms as perms_d, user, session, templ, form as form_d, maps,api as api_d
from ...auth import cli
from ...utils import token, mapper, config as config_d, chain, lin
from ...utils.exception import PolyVinylNotOk, PolyVinylError, PolyVinylKnockout


def session_start(req, ident, data):
    "Start a new session, assuming previous functions have validated the user\n"

    token = mapper.val_from_ident(req, ident, data)
    if not token:
        raise PolyVinylNotOk(ident)

    session.start(req, token)

    cookie = "Ssid={}; Expires={}; HttpOnly; Secure; SameSite=Lax;".format(
        req.session["session-token"],
        req.session["session-expires"]
    )
    req.header_stage["Set-Cookie"] = cookie
    req.server.logger.warn("Session Start {}".format(req.session))


def session_close(req, ident, data):
    "Close a session, and remove the cookie from the browser\n"
    session.close(req, ident)
    cookie = "Ssid=; Expires={}; HttpOnly; Secure; SameSite=Strict;".format(
        "Thu, 01 Jan 1970 00:00:00 GMT"
    )
    req.header_stage["Set-Cookie"] = cookie
    req.server.logger.warn("Session Close {}".format(req.session))
