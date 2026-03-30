"These are the handlers for the Provider" 
import bcrypt, sys, json
from . import perms as perms_d
from ..utils.exception import \
     PolyVinylNotOk, PolyVinylError, PolyVinylKnockout, PolyVinylReChain, PolyVinylNotOk, PolyVinylNoAuth
from .. import chain, lin
from ..auth import cli
from ..utils import user, session, templ, form as form_d, token, \
    maps, api as api_d, config as config_d
from ..utils.maps import mime_map
from smtplib import SMTP


from ..utils.form import injest, query_set_form, save_form, load

def save_amend(req, ident, data):
    return save_form(req, ident, data, amend=True)


def newsletter(req, indent, data):
    req.server.logger.debug("Newsletter signup {}".format(data))


def auth(req, ident, data):
    if not hasattr(perms_d, ident.name):
        raise PolyVinylNoAuth(ident)
    
    func = getattr(perms_d, ident.name)
    func(req, req.role, data)


def try_auth(req, ident, data):
    try:
        auth(req, ident, data)
    except PolyVinylNoAuth as no_auth:
        raise PolyVinylKnockout(*no_auth.args)


def title(req, ident, data):
    data["title"] = ident.name

def api(req, ident, data):
    "Returns data about the handlers and the configuration"
    config = req.server.config
    if ident.name == "handlers":
        req.content += api_d.handlers(req, sys.modules.get(__name__))

    if ident.name == "config":
        req.content  += api_d.config(req, sys.modules(__name__))


def end(req, ident, data):
    "Set the request complete and ready to respond\n"
    req.done = True
    raise PolyVinylKnockout()


def map(req, ident, data):
    "Map key/value pairs to the `data` object\n"
    "<name> can be a comma seperated list of slash seperated key/value pairs \n"
    "<location> is the object to pull from\n"

    config = req.server.config
    kv = maps.kv_from_ident(ident) 

    match ident.location:
        case "req":
            for k,v in kv.items():
                if not hasattr(req, v):
                    raise PolyVinylKnockout("Field not found for req {}".format(ident))

            data[key] = getattr(req, v)
        case "query" | "form" | "data" | "cookie" | "session" | "config":
            match ident.location:
                case "query":
                    source = req.query_data
                case "form":
                    source = req.form_data
                case "data":
                    source = data 
                case "cookie":
                    source = req.cookie
                case "session":
                    source = req.session
                case "config":
                    source = config 
                case _:
                    raise PolyVinylError("Map source not defined", ident)

    maps.map(kv, source, data)
    req.server.logger.log("After Map {} {}".format(ident, data))


def set_query(req, ident, data):
    "Reset the Request.query object to the `<map>` body arguments provided" 
    req.query_data = {}
    if ident.name:
        _map(req, ident, data, req.query_data)


def get(req, ident, data):
    "Ensure Request method is GET"
    if req.command != "GET":
        raise PolyVinylKnockout("Method mismatch")


def post(req, ident, data):
    "Ensure Request method is POST"
    if req.command != "POST":
        raise PolyVinylKnockout("Method mismatch")


def idents(req, ident, data):
    "Inject identifiers that are listed in a file into the chain during runtime\n"
    "Any directory can have a file listing Identifiers.\n"
    "If <location> is `user` the user folder will be used and a user must be set in the session\n"
    chain.idents(req, ident, data)


def content(req, ident, data):
    "Load and process content from templates into the Requests output response buffer\n"
    "Expected <location> types are `stache`, `format` or web file extension `html/css/js/txt`\n"
    config = req.server.config

    parts = ident.name.split(".")
    ext = parts[-1]

    mime = mime_map.get(ext)
    if mime:
        req.header_stage["Content-Type"] = mime;
    req.content += templ.templ_from(req, ident, data)


def form(req, ident, data):
    config = req.server.config
    path, ext = config_d.get_path_ext(config, ident)
    if ext == "json":
        with open(path, "r") as f:
            config_data = json.loads(f.read())
            form_d.gen_html(req, ident, data, config_data)



def query_eq(req, ident, data):
    if not req.query_data.get(ident.location):
        raise PolyVinylKnockout()

    if ident.name and req.query_data[ident.location] != ident.name:
        raise PolyVinylKnockout()

def query_neq(req, ident, data):
    try:
        query_eq(req, ident, data)
    except PolyVinylKnockout:
        return

    raise PolyVinylKnockout()

def data_eq(req, ident, data):
    "Ensure a `data` key and value is present\n"
    "<name> is the value\n"
    "<location> is the key\n"
    req.server.logger.log("data_eq {} vs {}".format(data.get(ident.location), ident.name))
    if not data.get(ident.location):
        raise PolyVinylKnockout()

    if ident.name and data[ident.location] != ident.name:
        raise PolyVinylKnockout()


def data_neq(req, ident, data):
    "Ensure a `data` key and value is NOT present\n"
    "<name> is the value\n"
    "<location> is the key\n"
    try:
        data_eq(req, ident, data)
    except PolyVinylKnockout:
        return

    raise PolyVinylKnockout()


def form_eq(req, ident, data):
    req.server.logger.log("data_eq {} vs {}".format(data.get(ident.location), ident.name))
    if not req.form_data.get(ident.location):
        raise PolyVinylKnockout()

    if ident.name and req.form_data[ident.location] != ident.name:
        raise PolyVinylKnockout()


def form_neq(req, ident, data):
    try:
        form_eq(req, ident, data)
    except PolyVinylKnockout:
        return

    raise PolyVinylKnockout()


inc = static = page = content

def redir(req, ident, data):
    "Populate the Request headers for a redirect to another url\n"

    if ident.location == "data":
        location = data.get(ident.name)
    else:
        location = ident.name

    session.redir(req, location)
    

def pw_auth(req, ident, data):
    "Call the Auth service to validate a password\n"
    config = req.server.config
    if config.get("auth-socket"): 
        email_token = lin.quote(data["email"]).decode("utf-8")
        password_hash = user.pw_hash(req, email_token, req.form_data["password"])
        del req.form_data["password"]

        cli.query_path(config["auth-socket"], req.server.key, (
            "ident",     
                "pw_auth={}@email".format(email_token),
            "password-hash",
                password_hash
        ))
    else:
        raise PolyVinylNotOk("No Auth Service Defined")


def token_consume_code(req, ident, data):
    "Call the Auth service to validate and consume a login six-code\n"
    config = req.server.config
    if config.get("auth-socket"): 
        email_token = lin.quote(data["email"]).decode("utf-8")

        cli.query_path(config["auth-socket"], req.server.key, (
            "ident",     
                "token_consume_code={}@email".format(email_token),
            "six-code",
                data["six-code"]
            ))

        del data["six-code"]
    else:
        raise PolyVinylNotOk("No Auth Service Defined")


def token_consume(req, ident, data):
    "Call the Auth service to validate and consume a login token\n"
    config = req.server.config
    if config.get("auth-socket"): 
        email_token = lin.quote(data["email"]).decode("utf-8")

        cli.query_path(config["auth-socket"], req.server.key, (
            "ident",     
                "token_consume={}@email".format(email_token),
            "token",
                data["token"],
            ))

        del data["token"]
    else:
        raise PolyVinylNotOk("No Auth Service Defined")


def session_start(req, ident, data):
    "Start a new session, assuming previous functions have validated the user\n"
    session.start(req, data)

    cookie = "Ssid={}; Expires={}; HttpOnly; Secure; SameSite=Lax;".format(
        data["session-token"], data["session-expires"])
    del data["session-token"]
    del data["session-expires"]
    req.header_stage["Set-Cookie"] = cookie

    req.server.logger.warn("Login Cookie {}".format(cookie))


def session_open(req, ident, data):
    "Open an existing session, assuming previous functions have validated the user\n"
    session.load(req, data)
    req.server.logger.log("Session {}".format(req.session))


def session_close(req, ident, data):
    "Close a session, and remove the cookie from the browser\n"
    session.close(req, ident)
    cookie = "Ssid=; Expires={}; HttpOnly; Secure; SameSite=Strict;".format(
        "Thu, 01 Jan 1970 00:00:00 GMT")
    req.header_stage["Set-Cookie"] = cookie
    

def pw_set(req, ident, data):
    "Call the Auth service to set a users password\n"
    config = req.server.config
    if config.get("auth-socket"): 
        if req.form_data.get("password"):
            email_token = lin.quote(data["email"]).decode("utf-8")
            password_hash = user.pw_hash(req, email_token, req.form_data["password"])
            cli.query_path(config["auth-socket"], req.server.key, (
                "ident", 
                    "pw_set={}@email".format(email_token),
                "password-hash",
                    password_hash 
            ))
    else:
        raise PolyVinylNotOk("No Auth Service Defined")


def register(req, ident, data):
    "Call the Auth service to register a new user\n"
    config = req.server.config
    try:
        user.create(req, config, data)
    except PolyVinylNotOk as err:
        raise PolyVinylNotOk("Unable to register", err.args[0])

    if config.get("auth-socket"): 
        email_token = lin.quote(data["email"]).decode("utf-8")
        cli.query_path(config["auth-socket"], req.server.key, (
            "ident", 
                "register={}@email".format(email_token),
            ))

        data["email-token"] = email_token
    else:
        raise PolyVinylNotOk("No Auth Service Defined")


def email(req, ident, data):
    "Send an email\n"
    config = req.server.config

    if not data.get('email-token'):
        data["email-token"] = lin.quote(data["email"]).encode("utf-8")

    data["subscription-url"] = user.get_subscription_url(req, data["email-token"])
    data["url"] = config["url"] 

    req.server.logger.debug("Data for email {} {}".format(ident, data))

    msg = templ.email_msg_from_ident(req, 
        ident,
        data,
        from_addr=config["system-email"],
        to_addrs=[data["email"]])

    try:
        with SMTP(config["smtp"]) as smtp:
            smtp.send_message(msg, from_addr=msg["From"], to_addrs=msg["To"])
    except Exception as err:
        req.server.logger.log(err, data)
        raise PolyVinylNotOk(err)


def set_token_url(req, ident, data):
    "Create the token url, usually for inclusion in an email\n"
    if not data.get('email-token'):
        data["email-token"] = lin.quote(data["email"]).decode("utf-8")
    
    data["login-url"] = "{}{}?email={}&six-code={}".format(
        data["url"], ident.name, data["email-token"], data["six-code"])
    

def get_token(req, ident, data):
    "Call the Auth service to create a new token\n"
    config = req.server.config

    if config.get("auth-socket"): 
        email_token = lin.quote(data["email"]).decode("utf-8")
        six_code = cli.query_path(config["auth-socket"], req.server.key, (
            "ident", 
                "get_signin_code={}@email".format(email_token),
        ))
        data["six-code"] = six_code.decode("utf-8")
    else:
        raise PolyVinylNotOk("No Auth Service Defined")
