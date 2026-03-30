import time, os
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from .. import lin
from ..utils.exception import \
     PolyVinylNotOk, PolyVinylError, PolyVinylKnockout, PolyVinylReChain
from .. import SESSION_DAYS, SEEK_END, SEEK_CUR, SEEK_START
from ..utils import user 
from ..utils.token import get_text_token, rfc822, time_bytes


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

def close(req, ident):
    config = req.server.config
    if not req.cookie.get("Ssid"):
        raise PolyVinylNotOk("No Ssid from cookie")

    path = os.path.join(config["dirs"]["sessions"], req.cookie["Ssid"])
    if not os.path.exists(path):
        raise PolyVinylNotOk("No Ssid file found")

    os.remove(path)
    req.session = {}


def load(req):
    data = {}
    config = req.server.config
    if not req.cookie.get("Ssid"):
        return

    path = os.path.join(config["dirs"]["sessions"], req.cookie["Ssid"])
    keys = config["fields"]["session"]

    try:
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            data.update(lin.map_str_r(f, keys))
    except FileNotFoundError:
        return
        
    req.server.logger.log("Session Data {}".format(data))

    if data.get("email-token"):
        email_token = data["email-token"]
    else:
        if data.get("email"):
            email_token = lin.quote(data["email"]).decode("utf-8")
        else:
            raise PolyVinylNotOk("User email-token not found")

    req.role = user.load_role(config, email_token)
    if req.role:
        req.session = data
    else:
        raise PolyVinylNotOk("User not found")

    req.server.logger.warn("Role {} Session {}".format(req.role, req.session))


def start(req, data):
    config = req.server.config

    if data.get("email-token"):
        email_token = data["email-token"]
    else:
        if data.get("email"):
            email_token = lin.quote(data["email"])
        else:
            raise PolyVinylNotOk("User email-token not found")

    token = get_text_token(email_token)
    path = os.path.join(config["dirs"]["sessions"],token)

    data["start-time"] = time_bytes(time.time())
    data["session-token"] = token
    data["session-expires"] = rfc822(
            datetime.now(tzlocal())+timedelta(days=SESSION_DAYS))

    with open(path, "wb+") as f:
        details = ["email-token", email_token, 
            "session-token", data["session-token"],
            "start-time", data["start-time"]]
        lin.send_rec(f, details) 
