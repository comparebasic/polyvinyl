import argparse, json, urllib, socket
from http.server import BaseHTTPRequestHandler, HTTPServer

from .. import GetLogger, DingerNotOk
from ..utils import templ, ident, form
from .handlers import Handle

class DingerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        config = self.server.config

        path, query = form.parseUrl(self.path)

        route = config["routes"].get(path)
        if not route:
            self.send_response(404)
            route = config["routes"]["/not-found"]
        else:
            self.send_response(200)

        self.send_header("Content-type", "text/html")
        self.end_headers()

        data = {}

        data["action"] = path
        if query:
            params = form.parseFormData(query)
            data.update(params)
        else:
            data["redir"] = None
    
        if not data.get("error"):
            data["error"] = None
            
        print(data)
        content = ""
        for p in route:
            p_ident = ident.Ident(p)
            content += templ.templFrom(config, p_ident, data)

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
                handlers.Handle(self, config, h_ident, data)
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
        logger.warn("Serving {}".format(address))
        return super().__init__(address, DingerHandler)

