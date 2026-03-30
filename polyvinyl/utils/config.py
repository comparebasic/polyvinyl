import argparse, json, os
from ..utils import identifier
from ..lin import unquote

def ParseConfig(path):
    with open(path, "r") as f:
        config = json.loads(f.read())
        return config


def ParseCli():
    parser = argparse.ArgumentParser(
        prog="PolyVinyl",
        description="PolyVinyl Server")
    parser.add_argument("--config")
    parser.add_argument("--log-color", action="store_true")
    parser.add_argument("--type", choices=["provider", "auth", "sasl"], required=False)
    return parser.parse_args()


def map_keys(keys, items, data):
    for k, v in items.items():
        if not keys:
            if isinstance(v, (bytes)):
                v = v.decode("utf-8")
            data[k] = v 

        elif keys[k]:
            value = v
            if isinstance(keys[k], (str)):
                ident = identifier.Ident(keys[k])
                if ident.tag == "unquote":
                    value = unquote(value)
                if ident.name:
                    k = ident.name

                if isinstance(value, (bytes)) and ident.tag != "bin":
                    value = value.decode("utf-8")
            elif isinstance(value, (bytes)):
                value = value.decode("utf-8")
            data[k] = value 
    return data


def get_name_ext(s):
    if not s:
        return s, None, None

    idx = -1
    length = len(s)
    for i in range(length-1, 0, -1):
        c = s[i]
        if c == '.' or c == b'.':
            idx = i

    if idx == -1:
        return s, None, None

    return s, s[:idx], s[idx+1:]


def get_path_ext(config, ident):
    if ident.location:
        templ_dir = config["dirs"].get(ident.location);
    else:
        templ_dir = config["dirs"].get("page");
            
    fname, name, ext = get_name_ext(ident.name)

    path = os.path.join(templ_dir, fname)
    return path, ext
