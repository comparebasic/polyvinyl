from ..utils.exception import PolyVinylError, PolyVinylKnockout

def val_from_ident(req, ident, data):
    match ident.location:
        case "data":
            return data.get(ident.name)
        case "session":
            return req.session.get(ident.name)
        case "form":
            return req.form_data.get(ident.name)
        case "query":
            return req.query_data.get(ident.name)

    return None


def arr_to_dict(arr):
    data = {}
    for i in range(0, len(arr), 2):
        data[arr[i]] = arr[i+1]

    if len(arr) % 2:
        data[arr[-1]] = True

    return data


def kv_from_ident(ident):
    kv = {}
    for field in ident.name.split(","):
        parts = field.split("/")
        key = parts[0]
        if len(parts) == 1:
            val_key = parts[0]
        elif len(parts) == 2:
            val_key = parts[1]
        else:
            raise PolyVinylError("Unparsable fields definition", ident.name)

        kv[key] = val_key
    return kv


def map(kv, source, dest):
    for k,v in kv.items():
        if v.endswith("?"):
            v = v[:-1]
            if k.endswith("?"):
                k = k[:-1]
            dest[k] = source.get(v)
        else:
            if not source.get(v):
                raise PolyVinylKnockout("Field not found for query {}".format(v))
            dest[k] = source[v]
