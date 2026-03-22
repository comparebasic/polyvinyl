import os, types
from .utils import identifier, user
from .utils.exception import \
    PolyVinylNotOk, PolyVinylKnockout, PolyVinylError, PolyVinylReChain, PolyVinylNoAuth

class Inst(object):
    def __init__(self, ident, mod):

        if not hasattr(mod, ident.tag):
            raise ValueError("Missing function for {}".format(ident))

        self.ident = ident
        func = getattr(mod, ident.tag)
        if not isinstance(func, (types.FunctionType)):
            raise ValueError("Handler function is not a function for {}".format(ident))

        self.func = func

    def __str__(self):
        return "Inst<{}>".format(self.ident)

    def __repr__(self):
        return self.__str__()


def do_chain(req, chain, data):
    "This function goes through the chain, and tries each branch until one"
    "completes or there are no more to try."
    if req.done:
        return

    for h in chain:
        if isinstance(h, (list)):
            try:
                # go through this branch of the chain
                do_chain(req, h, data)
                continue
            except PolyVinylKnockout as ko:
                req.server.logger.log("Knockout {}".format(ko))
                continue
            except PolyVinylNotOk as nok:
                data["error"] = str(nok.args)
                req.server.logger.log("NotOk {}".format(nok))
                continue
            except PolyVinylError as err:
                data["error"] = str(err.args)
                req.server.logger.log("Error {}".format(err))
                raise 

        elif isinstance(h, (Inst)):
            req.server.logger.log("Handle {}".format(h))
            try:
                h.func(req, h.ident, data)
            except PolyVinylReChain as re:
                req.server.logger.warn("ReChain {}", re.args[0])
                do_chain(req, re.args[0], data)
            except (PolyVinylNotOk, PolyVinylError) as err:
                data["error"] = err.args[0]
                raise
        else:
            raise TypeError(h)
        

def Handle(req, chain, data, fmap):
    try:
        do_chain(req, chain, data, fmap)
    except PolyVinylNotOk as err:
       raise 

    if not req.done:
        for k,v in self.header_stage.items():
            self.send_header(k, v)
        self.end_headers()

        self.wfile.write(bytes(content, "utf-8"))

    req.done = True


def idents(req, ident, data):
    config = req.server.config

    if ident.location == "user":
        req.server.logger.log(" -> Users Ident {}".format(ident))
        if not req.role.get("email-token"):
            raise PolyVinylNoAuth(ident)

        templ_dir = os.path.join(user.get_userdir(config, req.role["email-token"]), "idents")
    elif ident.location:
        templ_dir = config["dirs"].get(ident.location);
    else:
        templ_dir = config["dirs"].get("page");

    try:
        with open(os.path.join(templ_dir, ident.name), "r") as f:
            content = f.read()
            ch = [
                Inst(identifier.Ident(v.strip()), req.server.handlers) \
                    for v in content.split("\n") \
                    if v.strip()
            ]
            raise PolyVinylReChain(ch)
    except FileNotFoundError as err:
        pass
    

def _setup_chain(config, chain, mod):
    sub_chain = []
    for i, v in enumerate(chain):
        if isinstance(v, (list)):
            sub_chain.append(_setup_chain(config, v, mod))

        if isinstance(v, (str)):
            if not isinstance(v, (identifier.Ident)):
                ident = identifier.Ident(v)

            if config.get("templates") and config["templates"].get(ident.location): 
                sub_sub_chain = []
                # handle page stuff here
                for sv in config["templates"][ident.location]:
                    if isinstance(sv, (str)):
                        inst = Inst(identifier.Ident(sv), mod)
                    elif sv == True:
                        # place original intent in place of the variable True
                        inst = Inst(ident, mod)
                    sub_sub_chain.append(inst)

                sub_chain.extend(sub_sub_chain)
            else:
                sub_chain.append(Inst(ident, mod))

    return sub_chain
            

def setup_config(config, key, mod):
    route_insts = {}
    for path, chain in config[key].items():
        route_insts[path] = _setup_chain(config, chain, mod)

    return route_insts
