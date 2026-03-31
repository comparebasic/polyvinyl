from ..utils.exception import PolyVinylNoAuth

def make_nav(req, ident, data, path):
    nav_kv = {}
    for _, nav in req.server.nav.lookup.items():

        if nav.perms:
            try:
                for inst in nav.perms:
                    # knockout if permission fails
                    inst.func(req, ident, data) 
            except PolyVinylNoAuth:
                continue

        if nav.path == path:
            nav_kv[nav.name] = True
        else:
            nav_kv[nav.name] = nav.path

    return nav_kv

def ident_perm(req, ident):
    pass 
