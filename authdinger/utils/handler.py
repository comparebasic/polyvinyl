from ..utils import identifier
from ..utils.exception import \
    DingerNotOk, DingerKnockout, DingerError, DingerReChain

class Inst(object):
    def __init__(self, ident, mod):

        self.ident = ident
        if not hasattr(mod, ident.tag):
            raise ValueError("Missing function for {}".format(ident))

        self.func = getattr(mod, ident.tag)

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
            except DingerKnockout as ko:
                continue
            except DingerNotOk as nok:
                data["error"] = str(nok.args)
                continue
            except DingerError as err:
                data["error"] = str(err.args)
                raise 

        elif isinstance(h, (Inst)):
            req.server.logger.log("Handle {}".format(h))
            try:
                h.func(req, h.ident, data)

            except (DingerNotOk, DingerError) as err:
                data["error"] = err.args[0]
                raise
        else:
            raise TypeError(h)
        

def Handle(req, chain, data, fmap):
    try:
        do_chain(req, chain, data, fmap)
    except DingerNotOk as err:
       raise 

    if not req.done:
        for k,v in self.header_stage.items():
            self.send_header(k, v)
        self.end_headers()

        self.wfile.write(bytes(content, "utf-8"))

    req.done = True


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
                        sub_sub_chain.append(Inst(identifier.Ident(sv), mod))
                    elif sv == True:
                        sub_sub_chain.append(Inst(ident, mod))

                sub_chain.extend(sub_sub_chain)
            else:
                sub_chain.append(Inst(ident, mod))

    return sub_chain
            

def setup_config(config, key, mod):
    route_insts = {}
    for path, chain in config[key].items():
        route_insts[path] = _setup_chain(config, chain, mod)

    return route_insts
