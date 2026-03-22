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

            if isinstance(value, (bytes)):
                value = value.decode("utf-8")
            data[k] = value 
    return data


def get_path_ext(config, ident):
    if ident.location:
        templ_dir = config["dirs"].get(ident.location);
    else:
        templ_dir = config["dirs"].get("page");
            
    parts = ident.name.split(".")
    if len(parts) > 1:
        ext = parts[-1]
    else:
        ext = None

    path = os.path.join(templ_dir, ident.name)
    return path, ext
