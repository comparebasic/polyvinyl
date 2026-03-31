import os, pystache
from datetime import datetime
from dateutil.tz import tzlocal
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..utils import identifier, config as config_d
from ..utils.token import rfc822
from ..utils.exception import PolyVinylError, PolyVinylReChain, PolyVinylNotOk

renderer = pystache.Renderer()
cache = {}

def render_stache(req, ident, data):
    config = req.server.config
    prep = cache.get(ident.ident)
    if not prep:
        path, ext = config_d.get_path_ext(config, ident)

        try:
            with open(path, "r") as f:
                prep = pystache.parse(f.read())
                if config.get("cache"):
                    cache[ident.ident] = prep
        except FileNotFoundError as err:
            raise PolyVinylError(err.args[0], err)
    
    if len(req.nav):
        nav = "<nav><ul>"
        for k,v in req.nav.items():
            if v is True:
                nav += "<li><span class=\"active\">{}</span></li>\n".format(k)
            else:
                nav += "<li><a href=\"{}\">{}</a></li>\n".format(v, k)
        nav += "</ul></nav>"
            
    else:
        nav = ""

    return renderer.render(prep, {
        "data": data,
        "role": req.role,
        "session": req.session,
        "nav": nav
    })


def templ_from(req, ident, data):
    config = req.server.config

    path, ext = config_d.get_path_ext(config, ident)

    if ext == "stache":
        return render_stache(req, ident, data) 
    else:
        try:

            prep = cache.get(ident.ident)
            if not prep:
                with open(path, "r") as f:
                    prep = f.read()
                    if config.get("cache"):
                        cache[ident.ident] = prep

            content = prep
            if ext == "format":
                try:
                    return content.format(**data)
                except KeyError as err:
                    raise PolyVinylNotOk("Key Error in templ", err, ident) 
            else:
                return content
        except FileNotFoundError as err:
            raise PolyVinylError(err.args[0], path, err)


def email_msg_from_ident(req, ident, data, from_addr, to_addrs):
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
