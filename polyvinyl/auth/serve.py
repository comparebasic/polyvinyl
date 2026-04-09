import socketserver, argparse, json, os, select, stat, hashlib

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from . import handlers, cli, sign
from ..utils.log import GetLogger
from ..utils.exception import PolyVinylNotOk, PolyVinylError
from ..utils import identifier, lin


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

        if items[0] == b"aim":
            self.auth(items)
        else:
            raise PolyVinylNotOk("Unknown Protocol", items[0])


    def auth(self, items):
        ident = identifier.Ident(items[1])
        if ident.tag == "concat" and ident.name == "rsa-sha256":
            key = self.server.keys.get(ident.location)
            if not key:
                raise PolyVinylNotOk("Unable find key", ident.location)

            msg = bytearray()
            for chunk in items[2:]:
                msg += key["priv"].decrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

            print("Msg {}".format(msg))

        if self.server.keys:
            try:
                lin.verify(self.server.keys, items)
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
                func = getattr(handlers, ident.tag)
                self.server.logger.debug("Func {} Ident {} Data {}".format(ident.tag, ident, data))
                resp = func(self, ident, data)
            except PolyVinylNotOk:
                raise

            self.server.logger.log("Auth run {}".format(ident.tag))
            print("Resp {}".format(resp))
            if resp is not None:
                arr_append_sig(resp, self.keys["role"]["priv-ident"])
                cli.respond(details)
            else:
                cli.respond("no", "")

            return

        except PolyVinylNotOk as err:
            self.server.logger.log("Invalid login", err.args)
            cli.respond("no", err.args[0], "")
            return

        self.server.logger.log("Noop")
        cli.respond("no", "")


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
            "role": sign.get_role_key(self.config, "role", "ed25519-sha256")
        }
        print(self.keys)

