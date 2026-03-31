import argparse, json, urllib, traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

from . import handlers, setup as setup_d
from .. import chain, lin
from ..utils.maps import http_messages
from ..utils.log import GetLogger
from ..utils.exception import \
     PolyVinylNotOk, PolyVinylError, PolyVinylKnockout, PolyVinylReChain, \
     PolyVinylNotFound, PolyVinylNoAuth
from ..utils import templ, identifier, form, session, perms, config as config_d


class PolyVinylHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.data = {}
        self.header_stage = {}
        self.done = False
        self.form_data = {}
        self.query_data = {}
        self.cookie = {}
        self.session = {}
        self.role = {} 
        self.content = ""
        self.code = 0 
        self.unique_idx = 0
        self.nav = None
        return super().__init__(*args, **kwargs)


    def get_unique(self):
        self.unique_idx += 1
        return self.unique_idx


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

        ch = self.server.routes.get(path)

        if not ch:
            raise PolyVinylNotFound(path)

        chain.do_chain(self, ch, data)


    def do_GET(self):
        return self._do_STUFF()


    def do_POST(self):
        return self._do_STUFF()


    def _do_STUFF(self):
        path, _ = form.parseUrl(self.path)
        self.server.logger.warn("Processing {}".format(path))

        config = self.server.config

        self.query_data = self.parse_query()
        self.form_data = self.parse_form()
        if self.headers.get("Cookie"):
            self.cookie = session.parse_cookie(self.headers["Cookie"])
            session.load(self)

        self.data = {"error": None}

        try:
            if self.role:
                self.role["ident"] = identifier.Ident(
                    "id={}@user".format(self.role["email-token"]))
            else:
                self.role["ident"] = identifier.Ident("id=@anon")

            self.nav = perms.make_nav(self, self.role, self.data, path)

            self.resolve(path, self.data)
        except PolyVinylNoAuth as no_auth:
            self.server.logger.warn("Auth Error {}".format(str(no_auth.args)))
            self.data["error"] = str(no_auth.args)
            self.resolve("/no-auth", self.data)
            self.code = 403
        except PolyVinylKnockout as ko:
            pass
        except PolyVinylNotFound as err:
            self.data["error"] = str(err.args)
            self.content = ""
            self.resolve("/not-found", self.data)
            self.code = 404
        except PolyVinylError as err:
            self.server.logger.error(err, traceback.format_exception(err))
            self.data["error"] = str(err.args)
            self.content = ""
            self.resolve("/error", self.data)
            self.code = 500
        except Exception as err:
            self.data["error"] = str(err.args)
            self.content = ""
            self.resolve("/error", self.data)
            self.code = 500
            self.server.logger.error(err, traceback.format_exception(err))

        if self.code == 0:
            self.code = 200

        if self.code != 302 and not self.header_stage.get("Content-Type"):
            path, name, ext = config_d.get_path_ext(self.path)  
            if ext:
                self.header_stage["Content-Type"] = maps.mime_maps.get(ext);

            if not self.header_stage.get("Content-Type"):
                self.header_stage["Content-Type"] = "text/html"

        self.send_response(self.code, http_messages[self.code]) 
        for k,v in self.header_stage.items():
            self.send_header(k, v)
        self.end_headers()

        if len(self.content) > 0:
            self.wfile.write(bytes(self.content, "utf-8"))

        self.server.logger.warn("Served {}".format(path))
            

class PolyVinylProviderServer(HTTPServer):
    def __init__(self, config, logger, address):
        self.routes = chain.setup_config(config, "routes", handlers)

        self.config = config
        self.logger = logger
        self.handlers = handlers
        self.key = None
        if config.get("provider-key"):
            self.key = lin.load_key(config["provider-key"])

        setup_chain = chain.setup_config(config, "setup", setup_d)
        chain.linear(self, setup_chain)

        return super().__init__(address, PolyVinylHandler)

