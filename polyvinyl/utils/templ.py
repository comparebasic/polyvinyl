import os, pystache
from datetime import datetime
from dateutil.tz import tzlocal
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..utils.token import rfc822
from ..utils import identifier
from ..utils.exception import PolyVinylError, PolyVinylReChain

renderer = pystache.Renderer()
cache = {}


def render_stache(req, ident, data):
    config = req.server.config
    prep = cache.get(ident.ident)
    if not prep:
        templ_dir = None
        if ident.location:
            templ_dir = config["dirs"].get(ident.location);
        else:
            templ_dir = config["dirs"].get("page");
                
        parts = ident.name.split(".")
        ext = parts[-1]
        try:
            with open(os.path.join(templ_dir, ident.name), "r") as f:
                prep = pystache.parse(f.read())
                cache[ident] = prep
        except FileNotFoundError as err:
            raise PolyVinylError(err.args[0], err)

    return renderer.render(prep, {"data": data, "role": req.role, "session": req.session})


def templ_from(req, ident, data):
    config = req.server.config

    if ident.location:
        templ_dir = config["dirs"].get(ident.location);
    else:
        templ_dir = config["dirs"].get("page");
            
    parts = ident.name.split(".")
    ext = parts[-1]

    if ext == "stache":
        return render_stache(req, ident, data) 
    else:
        path =os.path.join(templ_dir, ident.name)
        try:
            with open(path, "r") as f:
                content = f.read()

            if ext == "format":
                try:
                    return content.format(**data)
                except KeyError as err:
                    raise PolyVinylError("Key Error in templ", err) 
            elif ext == "form":
                pass
            else:
                return content
        except FileNotFoundError as err:
            raise PolyVinylError(err.args[0], path, err)


def emailMsgFromIdent(req, ident, data, from_addr, to_addrs):
    subject_ident = identifier.Ident(
        "content={}_subject.format@{}".format(ident.name, ident.location))
    subject = templ_from(req, subject_ident, data)

    text_ident = identifier.Ident(
        "content={}_txt.format@{}".format(ident.name, ident.location))
    text = templ_from(req, text_ident, data)

    html_ident = identifier.Ident(
        "content={}_html.format@{}".format(ident.name, ident.location))
    html = templ_from(req, html_ident, data)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ",".join(to_addrs)
    msg["Date"] = rfc822(datetime.now(tzlocal()))
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    return msg
