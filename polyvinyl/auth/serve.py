import socketserver, argparse, json, os, select, stat, hashlib

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from . import handlers, cli, sign
from ..utils.log import GetLogger
from ..utils.exception import PolyVinylNotOk, PolyVinylError
from ..utils import identifier, lin


class PolyVinylAuthHandler(socketserver.StreamRequestHandler):

    def handle(self):
        data = {} 
        content = b""
        try:
            data = cli.recv(self.rfile, self.server.keys)
        except (ValueError, TypeError) as err:
            lin.send(self.wfile, [b"no", b""])
            self.server.logger.error("Error recv", err)
            return

        if not data:
            lin.send(self.wfile, [b"no", b"no items recieved", b""])

        if data.get(b"ident"):
            self.auth(data)
        else:
            raise PolyVinylNotOk("Unknown Protocol", items[0])


    def auth(self, data):
        self.server.logger.debug("Auth data {}".format(data))
        ident = identifier.Ident(data.get(b"ident"))
        
        try:
            func = getattr(handlers, ident.tag)
            self.server.logger.debug("Func {} Ident {} Data {}".format(ident.tag, ident, data))
            resp = func(self, ident, data)
        except PolyVinylNotOk:
            raise

        self.server.logger.log("Auth run {}".format(ident.tag))
        print("Resp {}".format(resp))
        if resp is not None:
            arr_append_sig(resp, self.keys["auth"]["priv-ident"])
            cli.send(
                self.server.config["auth-sock"],
                self.keys["auth-priv"],
                self.keys["ayth-sym"],
                details
            )
        else:
            lin.send(self.wfile, [b"no", b""])


class PolyVinylAuthServer(socketserver.UnixStreamServer):
    def __init__(self, config, logger, _bind_and_activate=True):
        self.config = config
        self.logger = logger
        self.keys = {}
        self.load_keys()
        super().__init__(config["auth-socket"], PolyVinylAuthHandler, True)
        perms = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP
        os.chmod(config["auth-socket"], perms)

    def load_keys(self):
        self.keys = { 
            "auth": sign.get_role_key(self.config, "auth", "ed25519-sha256")
        }
        print(self.keys)

