#!/usr/bin/env python3
import sys, os, json

class Ident(object):
    def __init__(self, ident):
        parts = ident.split("@")
        self.ident = ident
        self.tag = None
        self.ext = None
        self.idx = None
        self.source = None
        if len(parts) == 1:
            self.tag = ident
            self.source = None
            self.idx = None
        else:
            self.tag = parts[0]
            try:
                self.idx = int(parts[1]) 
            except ValueError:
                self.source = parts[1]
                eparts =  self.source.split('.')
                if len(eparts) > 1 :
                    self.ext = eparts[-1]

    def __str__(self):
        return "Ident<{}@{}/{} {}>".format(self.tag, self.source, self.idx, self.ext) 


def getFrame(url):
    return "<iframe src=\"{}\"></iframe>".format(url)

def nav(config, coord):
    content = ["<nav>\n    <ul>\n"]
    for k,v in config["nav"].items():
        content.append("<li><a href=\"{}\">{}</a></li>\n".format(k, v))
    content.append("    </ul>\n</nav>\n")


def cache(config, ident):
    if not config.get("templates-cache"):
        config["templates-cache"] = {}

    content = config["templates-cache"].get(ident.ident)
    if not content:

        if ident.tag == "inc":
            if not config["templates-cache"].get(ident.ident):
                path = os.path.join(config["inc-dir"], ident.source)
                file = open(path, "r")
                content = config["templates-cache"][ident.ident] = file.read()

        elif ident.tag == "page":
            name = config["_current-page"]
            if ident.idx is not None:
                name = name[ident.idx]

            if name.startswith("http"):
                content = getFrame(name)

            elif not config["templates-cache"].get(name):
                path = os.path.join(config["content-dir"], name)
                file = open(path, "r")
                content = config["templates-cache"][name] = file.read()


    return content

def genConfig(fname):
    with open(fname, "r") as f:
        return json.loads(f.read())

def page(config, key, name):
    print("Generating {}".format(key))
    page = config["pages"][key]
    config["_current-page"] = config["pages"][key]

    template = config["template-pages"].get(key)
    if not template:
        template = config["templates"]["default"]
    else:
        template = config["templates"][template]

    fname = os.path.join(config["dest"], name)
    f = open(fname, "w+")

    data = {}
    print(template)
    for i, h in enumerate(template):
        data["title"] = config["titles"][key]
        ident = Ident(h)
        print(ident)
        if ident.tag == "nav":
            data["nav"] = nav(config, [i])

        if ident.tag == "inc" or ident.tag == "page":
            content = cache(config, ident)
            if ident.ext == "format":
                f.write(content.format(**data))
            else:
                f.write(content)
    f.close()


def build(config):
    print(config)
    for k,v in config["pages"].items():
        page(config, k, v)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Expected argument 1 to be a config file")

    configData = genConfig(sys.argv[1])
    build(configData)
