import socketserver, argparse, json, os, select, stat

from . import handlers, cli
from .. import lin
from ..utils.log import GetLogger
from ..utils.exception import PolyVinylNotOk
from ..utils import identifier

class PolyVinylAuthHandler(socketserver.StreamRequestHandler):

    def handle(self):
        items = []
        content = b""
        while True:
            try:
                content = lin.read_next(self.rfile)
            except (ValueError, TypeError) as err:
                self.respond("no", err.args[0], "")
                return
                
            if content is None:
                break

            items.append(content)

        if len(items) == 0:
            self.respond("no", "no items recieved", "")

        self.auth(items)


    def auth(self, items):
        if self.server.key:
            try:
                lin.verify(self.server.key, items)
            except Exception as err:
                self.server.logger.log("Invalid message details", err.args)
                self.respond("no", "Invalid message details", "")
                return

        data = lin.arr_to_dict(items)
        if not data.get("ident"):
            raise PolyVinylNotOk("Ident not found")

        ident = identifier.Ident(data["ident"].decode('utf-8'))
        try:
            if not hasattr(handlers, ident.tag):
                raise PolyVinylNotOk("Handler not found {}".format(ident.tag))

            try:
                resp = getattr(handlers, ident.tag)(self, ident, data)
            except PolyVinylNotOk:
                raise

            self.server.logger.log("Auth run {}".format(ident.tag))
            if resp:
                self.respond("ok", resp, "")
            else:
                self.respond("ok", "")

            return

        except PolyVinylNotOk as err:
            self.server.logger.log("Invalid login", err.args)
            self.respond("no", err.args[0], "")
            return

        self.server.logger.log("Noop")
        self.respond("no", "")


    def respond(self, *args):
        lin.send(self.wfile, args)


class PolyVinylAuthServer(socketserver.UnixStreamServer):
    def __init__(self, config, logger, _bind_and_activate=True):
        self.config = config
        self.logger = logger
        self.key = None
        if config.get("auth-key"):
            self.key = lin.load_key(config["auth-key"])
        super().__init__(config["auth-socket"], PolyVinylAuthHandler, True)
        perms = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP
        os.chmod(config["auth-socket"], perms)


