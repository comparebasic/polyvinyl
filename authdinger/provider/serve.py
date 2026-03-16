import argparse, json, urllib, traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

from ..utils.maps import http_messages

from ..utils.log import GetLogger
from ..utils.exception import \
     DingerNotOk, DingerError, DingerKnockout, DingerReChain, DingerNotFound
from ..utils import templ, identifier, form, session, handler
from . import handlers


class DingerHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.header_stage = {}
        self.done = False
        self.form_data = {}
        self.query_data = {}
        self.cookie = {}
        self.session = {}
        self.content = ""
        self.code = 0 
        return super().__init__(*args, **kwargs)


    def parse_form(self):
        length = self.headers.get("Content-Length")
        if length:
            content = self.rfile.read(int(length))
            params = form.parseFormData(content.decode("utf-8"))

            if params:
                for k,v in params.items():
                    params[k] = urllib.parse.unquote(v,
                        encoding=None, errors=None)
        
            return params
        return {}

    def parse_query(self):
        idx = self.path.find("?")

        if idx != -1 and idx+1 < len(self.path):
            return form.parseFormData(self.path[idx+1:])
        else:
            return {}


    def resolve(self, path, data):
        config = self.server.config

        chain = self.server.routes.get(path)

        if not chain:
            raise DingerNotFound(path)

        handler.do_chain(self, chain, data)


    def do_GET(self):
        return self._do_STUFF()


    def do_POST(self):
        return self._do_STUFF()


    def _do_STUFF(self):
        path, _ = form.parseUrl(self.path)

        config = self.server.config

        self.query_data = self.parse_query()
        self.form_data = self.parse_form()
        if self.headers.get("Cookie"):
            self.cookie = session.parse_cookie(self.headers["Cookie"])

        data = {"error": None}
        try:
            self.resolve(path, data)
        except DingerNotFound as err:
            data["error"] = str(err.args)
            self.resolve("/not-found", data)
            self.code = 404
        except DingerError as err:
            data["error"] = str(err.args)
            self.resolve("/error", data)
            self.code = 500
        except Exception as err:
            data["error"] = str(err.args)
            self.resolve("/error", data)
            self.code = 500
            self.server.logger.error(err, traceback.format_exception(err))

        if self.code == 0:
            self.code = 200

        if not self.header_stage.get("Content-Type"):
            self.header_stage["Content-Type"] = "text/html";

        self.send_response(self.code, http_messages[self.code]) 
        for k,v in self.header_stage.items():
            self.send_header(k, v)
        self.end_headers()

        if len(self.content) > 0:
            self.wfile.write(bytes(self.content, "utf-8"))
            

class DingerProviderServer(HTTPServer):
    def __init__(self, config, logger, address):
        self.routes = handler.setup_config(config, "routes", handlers)
        self.config = config
        self.logger = logger
        return super().__init__(address, DingerHandler)

