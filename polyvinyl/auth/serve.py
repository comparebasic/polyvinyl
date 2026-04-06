import socketserver, argparse, json, os, select, stat, hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

from . import handlers, cli
from ..utils.log import GetLogger
from ..utils.exception import PolyVinylNotOk, PolyVinylError
from ..utils import identifier, lin

keys = {}

def get_role_key(config):

    if not keys.get("role"):
        key = {"pub": None, "priv": None}
        priv_path = os.path.join(config["dirs"]["auth-keys"], "role.priv")
        pub_path = os.path.join(config["dirs"]["auth-keys"], "role.pub")
        try:
            with open(pub_path, "rb") as f:
                key["pub"] = load_pem_public_key(f.read())

            with open(priv_path, "rb") as f:
                key["priv"] = load_pem_private_key(f.read(), password=None)

        except FileNotFoundError as err:
            raise err

        keys["role"] = key

    if not keys.get("role"):
        raise PolyVinylNotOk("Invalid", ident)

    return keys["role"]


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
                func = getattr(handlers, ident.tag)
                self.server.logger.debug("Func {} Ident {} Data {}".format(ident.tag, ident, data))
                resp = func(self, ident, data)
            except PolyVinylNotOk:
                raise

            self.server.logger.log("Auth run {}".format(ident.tag))
            print("Resp {}".format(resp))
            if resp:
                h = hashlib.sha256()
                for x in resp:
                    print("adding {}".format(x))
                    if isinstance(x, (str)):
                        x = x.encode("utf-8")

                    h.update(x)

                digest = h.digest()
                print("digest {}".format(digest.hex()))
                resp.append(self.server.keys["role"]["priv"].sign(h.hexdigest().encode("utf-8")))
                    
                details = ["ok"] + resp + [""]
                self.respond(details)
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
        self.keys = {}
        self.load_keys()
        if config.get("auth-key"):
            self.key = lin.load_key(config["auth-key"])
        super().__init__(config["auth-socket"], PolyVinylAuthHandler, True)
        perms = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP
        os.chmod(config["auth-socket"], perms)

    def load_keys(self):
        self.keys = { 
            "role": get_role_key(self.config)
        }
        print(self.keys)

