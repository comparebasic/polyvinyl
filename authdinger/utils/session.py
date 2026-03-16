import time, os
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from ..utils.exception import \
     DingerNotOk, DingerError, DingerKnockout, DingerReChain
from .. import SESSION_DAYS, SEEK_END, SEEK_CUR, SEEK_START
from ..utils import bstream
from ..utils.user import get_userfile
from ..utils.token import get_token, rfc822, time_bytes


def parse_cookie(cookie):
    data = {}
    for x in cookie.split(";"):
        pairs = x.split("=", 2)
        if len(pairs) == 2:
            k = pairs[0]
            v = pairs[1]
            data[k] = v 

    return data


def load(req, ident):
    data = {}
    config = req.server.config
    if not req.cookie.get("Ssid"):
        raise DingerNotOk("No Ssid from cookie")

    path = os.path.join(config["dirs"]["sessions"], req.cookie["Ssid"])
    keys = config["fields"]["session"]

    try:
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            data.update(bstream.map_str_r(f, keys))
    except FileNotFoundError:
        raise DingerNotOk("Session not found")
        
    req.server.logger.log("Session Data {}".format(data))

    if not data.get("email-token"):
        raise DingerNotOk("User email-token not found")

    path = get_userfile(config, data["email-token"])
    keys = config["fields"]["user"]

    try:
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            keys = config["fields"]["user"]
            data.update(bstream.map_str_r(f, keys))
    except FileNotFoundError:
        raise DingerNotOk("User not found")

    req.session = data


def start(req, data):
    config = req.server.config
    token = get_token(data["email-token"].encode('utf-8'))
    path = os.path.join(config["dirs"]["sessions"],token)

    data["start-time"] = time_bytes(time.time())
    data["session-token"] = token
    data["session-expires"] = rfc822(
            datetime.now(tzlocal())+timedelta(days=SESSION_DAYS))

    with open(path, "wb+") as f:
        details = ["email-token", data["email-token"], 
            "session-token", data["session-token"],
            "start-time", data["start-time"]]
        bstream.send_r(f, details) 
