import socketserver, argparse, json, os, select

from ..utils.log import GetLogger
from ..utils.exception import DingerNotOk
from ..utils import ident, bstream
from .handlers import Handle

STATE_LENGTH = "length"
STATE_KEY = "key"
STATE_VALUE = "value"
states = [STATE_LENGTH, STATE_KEY, STATE_VALUE]

class DingerAuthHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.server.logger.log("Auth handle")
        config = self.server.config

        more = True
        state = STATE_LENGTH
        content_state = STATE_KEY
        first = None

        items = []

        content = b""
        while more != False:
            try:
                content = bstream.read_next(self.rfile)
            except (ValueError, TypeError) as err:
                self.server.logger.error("Erronous login")
                self.respond("no", err.args[0], "")
                return
                
            if content is None:
                break

            items.append(content)

        if len(items) == 0:
            self.respond("no", "no items recieved", "")

        data = bstream.arr_to_dict(items)
        if not data.get("ident"):
            raise DingerNotOk("Ident not found")

        p_ident = ident.Ident(data["ident"].decode('utf-8'))
        self.server.logger.log("Auth handle ident{}".format(p_ident))
        try:
            Handle(self, config, p_ident, data)

            self.server.logger.log("Successful login")
            self.respond("ok", "")
            return

        except DingerNotOk as err:
            self.server.logger.log("Invalid login")
            self.respond("no", err.args[0], "")
            return

        self.server.logger.log("Noop login")
        self.respond("no", "")


    def respond(self, *args):
        bstream.send(self.wfile, args)


class DingerAuthServer(socketserver.UnixStreamServer):
    def __init__(self, config, logger, bind_and_activate=True):
        self.config = config
        self.logger = logger
        return super().__init__(config["auth-socket"],
            DingerAuthHandler, bind_and_activate)
