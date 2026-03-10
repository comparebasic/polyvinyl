import random, time, hashlib, os
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from .. import DingerNotOk, SESSION_DAYS, SEEK_END, SEEK_CUR, SEEK_START
from ..utils import bstream


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
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            data = bstream.map_r(f, keys)
            print("DATA {}".format(data))

            if data.get("email-token") is not None:
                fname = "{}.rseg".format(data["email-token"].decode("utf-8"))
                u_path = os.path.join(
                    config["dirs"]["user-data"], fname)
                u_keys = config["fields"]["user"]

                del data["email-token"]
                with open(u_path, "rb") as u:
                    u.seek(0, SEEK_END)
                    data.update(bstream.map_r(u, u_keys))

                    for k,v in data.items():
                        data[k] = v.decode("utf-8")

                    return data
    except FileNotFoundError:
        raise DingerNotOk("User not found")


def time_bytes(t):
    return int(t*1000000).to_bytes(8)


def rfc822(dt):
    ctime = dt.ctime()
    return "{}, {} {}".format(
        ctime[:3], ctime[4:8], dt.strftime(" %d %Y %H:%M:%S %Z"))


def get_token(content):
    h = hashlib.sha256()
    h.update(content)
    h.update(time_bytes(time.time()))
    h.update(random.randbytes(4))
    return h.hexdigest() 


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
