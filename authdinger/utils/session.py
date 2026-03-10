import time, os
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from .. import DingerNotOk, SESSION_DAYS, SEEK_END, SEEK_CUR, SEEK_START
from ..utils import bstream
from ..utils.user import get_userfile
from ..utils.token import get_token, rfc822


def from_cookie(config, cookie):
    c_data = {}
    for x in cookie.split(";"):
        pairs = x.split("=", 2)
        if len(pairs) == 2:
            k = pairs[0]
            v = pairs[1]
            c_data[k] = v 

    path = os.path.join(config["dirs"]["sessions"], c_data["Ssid"])
    keys = config["fields"]["session"]
    try:
        f = open(path, "rb")
    except FileNotFoundError:
        raise DingerNotOk("Session not found")
        
    f.seek(0, SEEK_END)
    s_data = bstream.map_r(f, keys)
    f.close()

    if not s_data.get("email-token"):
        raise DingerNotOk("User email-token not found")

    u_path = get_userfile(config, s_data["email-token"].decode("utf-8"))
    u_keys = config["fields"]["user"]

    try:
        u = open(u_path, "rb")
    except FileNotFoundError:
        raise DingerNotOk("User not found")

    u.seek(0, SEEK_END)
    data = bstream.map_r(u, u_keys)
    u.close()

    for k,v in data.items():
        data[k] = v.decode("utf-8")

    for k,v in keys.items():
        if v and s_data.get(k):
            print(k)
            data[k] = s_data[k].decode("utf-8")

    return data


def time_bytes(t):
    return int(t*1000000).to_bytes(8)


def start(req, config, data):
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
