import urllib, json, os, time

from .. import lin, SEEK_END
from ..utils import identifier, config as config_d, token as token_d, user, templ
from ..utils.exception import PolyVinylNotOk, PolyVinylError

html_tag_templ_ident = identifier.Ident("content=form_html_tag.format@inc")
button_templ_ident = identifier.Ident("content=form_button.format@inc")
fieldset_templ_ident = identifier.Ident("content=form_fieldset.format@inc")
labeled_templ_ident = identifier.Ident("content=form_fieldset_labeled.format@inc")
input_templ_ident = identifier.Ident("content=form_input.format@inc")
multi_templ_ident = identifier.Ident("content=form_multi.format@inc")
optional_templ_ident = identifier.Ident("content=form_optional.format@inc")

def _item_templ(req, ident, vals):
    try:
        return  templ.templ_from(req, ident, vals)
    except PolyVinylError as err:
        raise PolyVinylError("Unable to find field type", ident, err)

FORM_OPTIONAL = "<div class=\"optional\">{}</div>"

def _trans_data(req, data, origin, fields, unpack=False):

    kv = {}
    deps = {}

    try:
        for k,v in fields.items():
            if isinstance(v, (str)):
                ident = identifier.Ident(v)
                match ident.tag:
                    case "depends":
                        deps[(ident.location,ident.name)] = (k, origin[k])
                    case "value":
                        if ident.location == "missing":
                            value = origin.get(k)
                            if not value:
                                value = ident.name
                        else:
                            value = ident.name

                        if unpack and isinstance(value, (bytes)):
                            value = value.decode("utf-8")

                        data[k] = value
                    case "process":
                        match ident.location:
                            case "quote":
                                value =lin.quote(origin[k]).decode("utf-8")
                            case "unquote":
                                value = lin.unquote(origin[k]).decode("utf-8")
                            case "lower":
                                value = origin[k].lower()
                            case "upper":
                                value = origin[k].upper()

                        if ident.name:
                            key = ident.name
                        else:
                            key = k

                        if unpack and isinstance(value, (bytes)):
                            value = value.decode("utf-8")

                        data[key] = value
                        data[k] = origin[k]
                    case "date":
                        if unpack:
                            data[k] = token_d.time_from_bytes(origin[k])
                        elif ident.location == "now":
                            data[k] = token_d.time_bytes(time.time()) 

            elif isinstance(v, (bool)):
                if v or origin.get(k):
                    data[k] = origin[k]

        for dep,val in deps.items():
            k,v = dep
            if origin.get(k) and origin[k] == v:
                key, value = val

                if unpack and isinstance(value, (bytes)):
                    value = value.decode("utf-8")

                data[key] = value

        req.server.logger.debug("Data after injest {}".format(data))

    except (KeyError, ValueError) as err:
        req.server.logger.warn(err)
        raise PolyVinylNotOk(err)
        

def save_form(req, ident, data, amend=False):
    config = req.server.config

    kv = {}
    deps = {}

    fields = {}
    path, ext = config_d.get_path_ext(config, ident)
    if ext == "json":
        with open(path, "r") as f:
            js = json.loads(f.read())
            fields.update(js["persist"])
            name = js.get("persist-name")
            if not name:
                name = ident.name

    if amend:
        orig = fields
        fields = {}
        for k,v in orig.items():
            ident = identifier.Ident(v)
            if ident.tag == "date":
                fields[k] = v
            elif req.form_data.get(k):
                fields[k] = v

    form_data = {}
    _trans_data(req, form_data, req.form_data, fields)

    name = "{}.linr".format(name)

    email_token = data["email-token"]
    user_dir = user.get_userdir(config, email_token) 
    path = os.path.join(os.path.join(user_dir, "forms"), name)

    details = []
    for k,v in form_data.items():
        details.append(k)
        details.append(v)

    try:
        if amend:
           with open(path, "ab") as f:
                f.seek(0, SEEK_END)
                lin.send_rec(f, details) 
           req.data["update"] = "Updating {}".format(details) 

        else:
            with open(path, "wb+") as f:
                lin.send_rec(f, details) 
    except FileNotFoundError as err:
        raise PolyVinylNotOk("User or file not found", err)



def injest(req, ident, data):
    config = req.server.config
    fields = {}
    path, ext = config_d.get_path_ext(config, ident)
    if ext == "json":
        with open(path, "r") as f:
            js = json.loads(f.read())
            fields.update(js["injest"])
    
    _trans_data(req, data, req.form_data, fields)


def query_set_form(req, ident, data):
    config = req.server.config
    fields = {}
    path, ext = config_d.get_path_ext(config, ident)
    if ext == "json":
        with open(path, "r") as f:
            js = json.loads(f.read())
            fields.update(js["injest"])

    orig = fields
    fields = {}
    for k,v in orig.items():
        if req.query_data.get(k):
            fields[k] = v
    
    _trans_data(req, req.form_data, req.query_data, fields)
    req.server.logger.debug("Data after injest_query_set {} {}".format(req.form_data, req.query_data))


def load(req, ident, data):
    config = req.server.config

    fields = {}
    path, ext = config_d.get_path_ext(config, ident)
    if ext == "json":
        with open(path, "r") as f:
            form_config = json.loads(f.read())
            fields.update(form_config["persist"])
            name = form_config.get("persist-name")
            if not name:
                name = ident.name

    if not form_config:
        raise PolyVinylError("File for config not found", err)

    email_token = None
    if req.role and req.session:
        email_token = data["email-token"]
    elif req.role and form_config.get("scope"):
        scope = identifier.Ident(form_config["scope"])
        if scope.location == "role":
            req.server.logger.debug("Form load scope {} role {}".format(
                scope,
                req.role
            ))
            if req.role.get(scope.tag) and not scope.name or req.role.get(scope.name):
                email_token = req.role["email-token"]

    if not email_token:
        raise PolyVinylError("User for file to load not found")

    name = "{}.linr".format(name)
    user_dir = user.get_userdir(config, email_token) 
    path = os.path.join(os.path.join(user_dir, "forms"), name)

    try:
        with open(path, "rb") as f:
            f.seek(0, SEEK_END)
            rec = lin.next_rec(f, None)
            req.server.logger.debug("Rec {}".format(rec))

            _trans_data(req, data, rec, fields, unpack=True) 
    except FileNotFoundError as err:
        print(path)
        raise PolyVinylError("File for loading not found", err)
    

def parseFormData(s):
    data = {}
    for x in s.split("&"):
        pairs = x.split("=", 2)
        if len(pairs) == 2:
            k = pairs[0]
            v = pairs[1]
            data[k] = urllib.parse.unquote_plus(v, encoding=None, errors=None)
    return data


def to_query(config, data):
    query = ""
    for k, v in data.items():

        if query:
            query += "&"

        if isinstance(k, (bytes)):
            k = k.decode("utf-8")
        else:
            k = urllib.parse.quote(k, encoding=None, errors=None)

        if isinstance(v, (bytes)):
            v = v.decode("utf-8")
        else:
            v = urllib.parse.quote(k, encoding=None, errors=None)

        query += "{}={}".format(k, v) 
    return query

def parseUrl(s):
    t = s.split("?")
    if len(t) == 1:
        return (t[0], None)
    return (t[0], t[1])

def compare_digest(config, ident, form, html, fields):
    h = hashlib.sha256()
    h.update(form)
    h.update(fields)
    h.update(html)
    digest = h.hexdigest()
    # compare to digets on disk


def render_item(req, ident, data, optional=False, content=""):
    name = ident.location
    value = None 
    if ident.tag == "radio" or ident.tag == "button":
        parts = name.split("/")
        if len(parts) == 2:
            name = parts[1]
            value = parts[0]
    
    if not value:
        value = data.get(name)

    vals = {
        "class":"",
        "label": ident.name,
        "type": "text" if ident.tag == "input" else ident.tag,
        "name": name,
        "value": " value=\"{}\"".format(value) if value else "",
        "control": "",
        "content": content,
        "input-extra":""
    }

    if ident.tag == "password":
        vals["control"] = "<span class=\"marker eye\">&#128065;</span>"


    field = ""

    match ident.tag:
        case  "button":
            templ_ident = button_templ_ident
        case  "always_button":
            vals["type"] = "button"
            vals["class"] = "class=\"always-valid\""
            templ_ident = button_templ_ident
        case "fieldset":
            if ident.name:
                if ident.name == "_":
                    vals["label"] = ""

                templ_ident = labeled_templ_ident
            else:
                templ_ident = fieldset_templ_ident
        case "password" | "password":
            templ_ident = input_templ_ident
        case "radio":
            templ_ident = multi_templ_ident
        case "checkbox":
            vals["value"] = " value=\"on\""
            if data.get(name) == "on":
                vals["input-extra"] = " checked=\"checked\""
            templ_ident = multi_templ_ident
        case "checkbox:checked":
            vals["value"] = "value=\"on\""
            if data.get(name) != "off":
                vals["input-extra"] = " checked=\"checked\""
            vals["type"] = "checkbox"
            templ_ident = multi_templ_ident
        case "para":
            vals = {"tag":"p", "content": ident.name}
            templ_ident = html_tag_templ_ident
        case "input":
            templ_ident = input_templ_ident
        case _:
            raise PolyVinylError("Field type not found", ident)


    field = _item_templ(req, templ_ident, vals)

    if optional:
        return FORM_OPTIONAL.format(field)
    else:
        return field

def rev_gen_loop(req, ident, chain, data, content=""):
    top = len(chain)-1
    for i, v in enumerate(reversed(chain)):
        if isinstance(v, (list)):
            content += gen_loop(req, ident, data, v)
        else:
            ident = identifier.Ident(v)
            content = render_item(req, ident, data, i < top, content)

    return content


def gen_loop(req, ident, data, chain):
    content = ""
    for v in chain:
        content += "\n"
        if isinstance(v, (str)):
            ident = identifier.Ident(v)
            match ident.tag:
                case "input" | "checkbox" | "checkbox:checked" | "button" | "always_button" | \
                    "option" | "radio" | "fieldset" | "password" | "para":
                    content += render_item(req, ident, data)
        elif isinstance(v, (list)):
            content += rev_gen_loop(req, ident, v, data)

    return content


def gen_script(ident, form_jsid, validation):
    content = "<script type=\"text/javascript\">"
    content += "window._polyvinyl.Form.register(\"{}\", {})".format(
        form_jsid,
        json.dumps(validation)
    )
    content += "</script>"
    return content


def gen_html(req, ident, data, config_data):
    config = req.server.config
    form_jsid = "form_jsid{}".format(req.get_unique())
    req.content += "<form id=\"{}\" method=\"POST\" action=\"{}\">".format(
        form_jsid,
        config_data["action"])
    req.content += gen_loop(req, ident, data, config_data["idents"])
    req.content += gen_script(ident, form_jsid, config_data["validation"])
    req.content += "</form>"


def process_form(req, ident, data):
    # process form fields.json 
    pass
