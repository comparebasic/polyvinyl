import os, hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

from ..utils import identifier
from ..utils.exception import PolyVinylNotOk 


def arr_append_sig(ident, key, items):
    if ident.name == "hmac-sha256":
        key = bytes.fromhex(ident.location)
        h = hmac.new(key, b"", hashlib.sha256)
        for v in items:
            if isinstance(v, (str)):
                v = v.encode("utf-8")
            h.update(v)

        return h.digest()

    elif ident.name == "ed25519-sha256":
        h = hashlib.sha256()
        for v in items:
            if isinstance(v, (str)):
                v = v.encode("utf-8")

            h.update(v)

    return key["priv"].sign(h.digest())


def get_role_key(config, name, proto):
    key = {"pub": None, "priv": None, "name": name}
    priv_path = os.path.join(config["dirs"]["auth-keys"], "{}.priv".format(name))
    pub_path = os.path.join(config["dirs"]["auth-keys"], "{}.pub".format(name))
    try:
        with open(pub_path, "rb") as f:

            concat_type = "ed25519-sha256"
            ident_s = "pub_key={}@{}".format(concat_type, name)
            try:
                key["pub"] = load_pem_public_key(f.read())
            except ValueError as err:
                raise PolyVinylError("Unable to load key {}".format(pub_path), err)
            key["pub-ident"] = identifier.Ident(ident_s)

        with open(priv_path, "rb") as f:
            ident_s = "priv_key={}@{}".format(concat_type, name)
            try:
                key["priv"] = load_pem_private_key(f.read(), password=None)
            except ValueError as err:
                raise PolyVinylError("Unable to load key {}".format(priv_path), err)
            key["priv-ident"] = identifier.Ident(ident_s)


    except FileNotFoundError as err:
        raise err

    return key
