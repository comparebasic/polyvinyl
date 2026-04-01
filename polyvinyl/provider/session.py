import time, os
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from . import user
from .. import SESSION_DAYS, SEEK_END, SEEK_CUR, SEEK_START
from ..utils import lin, mapper
from ..utils.token import get_text_token, rfc822, time_bytes
from ..utils.exception import PolyVinylNotOk, PolyVinylError, PolyVinylKnockout


def redir(req, location):
    config = req.server.config

    if not location:
        location = "/error"
    elif req.query_data:
        location = "{}?{}".format(
            location,
            form_d.to_query(req.server.config, req.query_data))
        
    if not location.startswith("http"):
        location = "{}{}".format(config["url"], location)

    req.code = 302
    req.header_stage["Location"] = location
    req.server.logger.log("Redir {}".format(location))
    

def parse_cookie(cookie):
    data = {}
    for x in cookie.split(";"):
        pairs = x.split("=", 2)
        if len(pairs) == 2:
            k = pairs[0]
            v = pairs[1]
            data[k] = v 

    return data


def load(req, email_token):
    config = req.server.config

    req.role = user.load_user(config, email_token)
    req.role.update(user.load_roles(config, email_token))

    req.server.logger.warn("Loaded User/Role {}".format(req.role))

    if not req.role:
        req.session = {} 
        raise PolyVinylNotOk("User not found")


def load_from(req, ssid):
    config = req.server.config
    if not req.cookie.get("Ssid"):
        return

    path = os.path.join(config["dirs"]["sessions"], req.cookie["Ssid"])
    keys = config["fields"]["session"]

    try:
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            req.session.update(lin.map_str_r(f, keys))
    except FileNotFoundError:
        return

    if not req.session.get("email-token"):
        req.server.logger.debug("Session {}".format(req.session))
        raise PolyVinylNotOk("User email-token not found")

    load(req, req.session["email-token"])


def start(req, email_token):
    config = req.server.config

    token = get_text_token(email_token)
    path = os.path.join(config["dirs"]["sessions"],token)

    details = ["email-token", email_token,
        "start-time", time_bytes(time.time()),
        "session-token", token,
        "session-expires", rfc822(
                datetime.now(tzlocal())+timedelta(days=SESSION_DAYS))]

    with open(path, "wb+") as f:
        lin.send_rec(f, details) 

    session = mapper.arr_to_dict(details)

    if not session.get("email-token") or session["email-token"] != email_token:
        req.server.logger.debug("Session {}".format(req.session))
        raise PolyVinylNotOk("User email-token does not match or not found")

    req.session = session
    load(req, req.session["email-token"])


def close(req, ident):
    config = req.server.config
    if not req.cookie.get("Ssid"):
        raise PolyVinylNotOk("No Ssid from cookie")

    path = os.path.join(config["dirs"]["sessions"], req.cookie["Ssid"])
    if not os.path.exists(path):
        raise PolyVinylNotOk("No Ssid file found")

    os.remove(path)
    req.session = {}
