import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..utils import identifier


def pack(key, items:list) -> bytes:
    cipher = Cipher(algorithms.AES(key["sym"]), modes.CBC(key["iv"]))
    encryptor = cipher.encryptor()
    
    total = 0
    obfused = bytearray()
    for v in items:
        if isinstance(v, (str)):
            v = v.encode("utf-8")

        l = len(v).to_bytes(2, "big")
        obfused += encryptor.update(l)
        obfused += encryptor.update(v)
        total += len(l) + len(v)

    pad = 16 - (total % 16)
    encryptor.update(b"\x00" * pad)

    return bytes(obfused + encryptor.finalize())


def unpack(key, obfused:bytes) -> list:
    cipher = Cipher(algorithms.AES(key["sym"]), modes.CBC(key["iv"]))
    decryptor = cipher.decryptor()
    content = decryptor.update(obfused) + decryptor.finalize()
    
    return arr_to_dict(from_bytes(content))


def get_key(config, name) -> bytes:
    path = os.path.join(config["dirs"]["auth-keys"], "{}.sym".format(name))
    iv_path = os.path.join(config["dirs"]["auth-keys"], "{}.iv".format(name))

    key = {"sym":None, "iv": None, "name": name}

    with open(path, "r") as f:
        key["sym"] = bytes.fromhex(f.read())
        key["sym-ident"] = identifier.Ident("=sym-aes@{}".format(name))

    with open(iv_path, "r") as f:
        key["iv"] = bytes.fromhex(f.read())

    return key
