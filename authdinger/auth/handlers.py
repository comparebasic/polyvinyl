from ..utils.exception import DingerNotOk

def Handle(req, config, ident, data):
    func = None
    if ident.tag == "pw_auth":
        func = pw_auth
        data["user"] = ident.base

    if not func:
        raise DingerNotOk("Not func found for handler {}".format(ident))

    func(req, config, data)


def pw_auth(req, config, data):
    if data.get("password") == "password" and data.get("user") == "test":
        return
    else:
        raise DingerNotOk("auth fail")
