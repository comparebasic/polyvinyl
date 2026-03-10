import argparse, json, urllib
from http.server import BaseHTTPRequestHandler, HTTPServer

from .. import GetLogger, DingerNotOk
from ..utils import templ, ident, form, session
from .handlers import Handle, setup_handlers

ext_mime = {
    "css": "text/css",
    "format": "text/html",
    "html": "text/html",
    "txt": "text/plain"
}

class DingerHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.header_stage = {}
        self.session = {}
        return super().__init__(*args, **kwargs)

    def do_cookie(self, config):
        cookie = self.headers.get("Cookie")
        if cookie:
            self.server.logger.warn("Session From {}".format(cookie))
            ssion = session.from_cookie(config, cookie)
            if ssion:
                self.session = ssion
                self.server.logger.warn("Session Data {}".format(self.session))

    def do_GET(self):
        config = self.server.config
        self.do_cookie(config)

        path, query = form.parseUrl(self.path)

        route = config["routes"].get(path)
        if not route:
            self.send_response(404)
            route = config["routes"]["/not-found"]
        else:
            self.send_response(200)

        data = {}

        data["action"] = path
        if query:
            params = form.parseFormData(query)
            data.update(params)
        else:
            data["redir"] = None
    
        if not data.get("error"):
            data["error"] = None
            

        content = ""
        for p in route:
            p_ident = ident.Ident(p)
            if p_ident.tag == "page" or p_ident.tag == "static":
                data.update(self.session)
                mime = ext_mime.get(p_ident.ext)
                if mime:
                    self.header_stage["Content-Type"] = mime;
            content += templ.templFrom(config, p_ident, data)

        if not self.header_stage.get("Content-Type"):
            self.header_stage["Content-Type"] = "text/html";

        for k,v in self.header_stage.items():
            self.send_header(k, v)
        self.end_headers()

        self.wfile.write(bytes(content, "utf-8"))

    def do_POST(self):
        path, _ = form.parseUrl(self.path)

        config = self.server.config
        handler = config["handlers"].get(path)

        if not handler:
            self.path = "/not-found"
            return self.do_GET()

        data = {}

        length = self.headers.get("Content-Length")
        if length:
            content = self.rfile.read(int(length))

            params = form.parseFormData(content.decode("utf-8"))
            if params:
                for k,v in params.items():
                    params[k] = urllib.parse.unquote(v,
                        encoding=None, errors=None)
                data.update(params)
        
        for h in handler:
            h_ident = ident.Ident(h)
            try:
                Handle(self, config, h_ident, data)
            except DingerNotOk as err:
                knockout = config["knockouts"].get(path)
                if knockout:
                    k_ident = ident.Ident(knockout)
                    if k_ident.tag == "get":
                        data["error"] = err.args[0]
                        self.path = "{}?{}".format(
                            k_ident.source, 
                            form.toQuery(config, data))
                        self.do_GET()
                        return

                self.server.logger.error("handler error", err)
                self.server.logger.error("handler error", h_ident)
                self.path = "/error"
                return self.do_GET()


class DingerProviderServer(HTTPServer):
    def __init__(self, config, logger, address):
        self.config = config
        self.logger = logger
        setup_handlers(config)
        return super().__init__(address, DingerHandler)

