# PolyVinyl UI

The user-interface is controlled by a json file that generates form HTML output
to send to the browser, provides the names and expected values to injest and
process the form on the backend, and wires up JavaScript behaviour in the
browser to give a modern feel to the web applications created in PolyVinyl.

An example version of a form configuration is [login.json](/example/page/login.json).

## Backend HTML Generation

The module which generates, the processes forms using the json configuration is
[utils.form](/polyvinyl/utils/form.py).

An example of the configuration used to generate the HTML form is:

```jsonc
{
    "idents":[
        "input=Email@email",
        ["fieldset", [
                ["radio=Use password@password/auth-method", "password=Password@password"],
                "radio=Email a code/link@send-email/auth-method"
            ] 
        ],
        ["checkbox=Register new user@register", "input=Fullname@fullname"],
        "button=Submit@submit"
    ],
    "action":"/auth/login",
    "injest": {
        "email": "process=email-token@quote",
        "auth-method": true,
        "password": "depends=password@auth-method",
        "register": false,
        "fullname": "depends=on@register"
    },
    "validation":{
        //... front end validation rules here
    }
}
```

Which generates the following form:

![Login Screenshot](/doc/login-screenshot.png)

## Browser Connection

As the Python backend generates the html for a form, it places a small
JavasCript element in the page to wire up the events and behaviour. The file
that runs most of the behaviour in the browser is [form.js](/ui/form.js).

Here is an example of what the backend places in the HTML output sent to the
browser.

```html
    <script type=text/javascript>
        window._polyvinyl.Form.register(jsid, <!-- json.dumps(validation) -->)
    </script>
```

The `jsid` comes from a unique value on the `PolyVinylHandler` object and has
been set as the HTML Form's `id` attribute.

`validation` is a section of the form's json file.

```jsonc
{
    "idents":[
        // ...
    ],
    "action":"/auth/login",
    "injest":[
        // ...
    ],
    "validation":{
        "password":{
            "rules": [
                ".{8,32}",
                false,
                "[A-Z]{1}",
                false,
                "[a-z]{1}",
                false,
                "[0-9]{1}",
                false,
                "[-,._$@!~+=/:;?#%^&*]{1}"
            ],
            "description":[
                "8-32 characters long,",
                " one of each: ",
                "a capital",
                ", ",
                "a lower case letter",
                ", ",
                "a number",
                ", and ",
                "a special character - _ , . : ; # ? ^ & * $ @ ! ~ + = /."
            ]
        },
        "email": {
            "rules":[".+@.+\\.[a-zA-Z]{2,}"], 
            "description": ["Enter a valid email"]
        },
        "fullname": {
            "rules":[".{2,}"],
            "description": ["Enter your full name"]
        },
        "auth-method":{"description": ["Select and authentication method"]}
    }
}
```

## The Front End

Details about the FrontEnd can be found [here](/doc/from-end.md)
