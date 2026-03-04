#!/usr/bin/env python3
import sys, os, json

def nav(pages, coord):
    pass

def loadTemplate(data, name):
    if not data.get("templates"):
        data["templates"] = {}

    if not data["templates"].get(name):
        path = os.path.join(data["dir"], name)
        file = open(path, "r")
        data["templates"][name] = file.read()

def config(fname):
    with open(fname, "r") as f:
        data = json.loads(f.read())
        print(data)
        for t in data["inc-dir"]:
            loadTemplate(data, t)
            
    return data

def page(data, name):
    pass

def build(data):
    print(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Expected argument 1 to be a config file")

    configData = config(sys.argv[1])
    build(configData)
