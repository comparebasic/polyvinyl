import os
from . import ident

def templFrom(config, ident, data):
    templ_dir = None
    if ident.tag:
        templ_dir = config["dirs"].get(ident.tag);
    else:
        templ_dir = config["dirs"].get("page");
            
    with open(os.path.join(templ_dir, ident.source), "r") as f:
        content = f.read()
        if ident.ext == "format":
            return content.format(**data)
        else:
            return content
