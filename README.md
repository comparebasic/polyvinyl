# PolyVinyl

This is a task-management and web application framework based on the following things:

- Server and Handler files for the two services included: `Auth` and `Provider`.
- Configuration pipeline known as a `Chain` based on Spatial Oriented Programming.
- Set of utilities for simple stuff such as token and session handling.
- Identifier syntax for defining common actions in the form `<tag>=<name>@<location>`.
- Simple data format for storing and streaming data known as `Lin`.

This system is presently written in Python 3 and available under a 3-clause BSD [Licence](LICENSE).

Architectural Diagram:

![Architectural Diagram](/doc/polyvinyl-arch.svg)

# Convention

The main convention of the system is that it uses a series three-part
identifiers to define behavior. These identifiers are stored in a
[configuration](example/config.json) file that loads against a
[module](polyvinyl/provider/handlers.py) with functions defined to be triggered by the
identifiers.

An example identifiery is as follows, see more about identifiers [here](/doc/identifier.md):

```
<tag>=<name>@<location>
```


This is the function signature for handling the behavior of an identitifier.

```python
def func(request, ident, data):
    # do stuff
```

The actions of the handler functions are three fold:
    
1. Modify values in the `data` dict argument which is carried to subsequent
handler functions
2. Modify attributes of the `Request` 
    - Add/modify response headers
    - Add/modify response content
    - Set response mime type or status code
2. Raises an exception
    - indicate an error
    - knockout to the next branch in the chain
    - respond with an erroronous response code such as 404 or 500

Such that `content=dashboard.html@page` loads the `content` function to render
the `dashboard.html` file in the `page` folder.

Some functions raise exceptions which tell the server to move on to the next
series of identifiers, serving essentially as an if/else statement. Some
functions also generate a new list of identifiers, by raising the
`PolyVinylReChain` exception, which allows pages to include content from other
places defined for a specific user.

```python
    "data_eq=on@register"
    # will raise a PolyVinylKnockout() exception if data["register"] != "on"
```

This is why the configuration is so dense in exchange for a complete view of
the system in one configuration file. This is also how the system can be used
to compose web services, manually or through a user-interface that generates a
configuration file.

# Services

Two services are included, one for authentication and one for web services management.

## Auth 

This service is a unix socket server using the a protocal that communicates
content length in two bytes, followed by that content. It transmits identifiers
and small pieces of information back and forth. The largest reason for this
architecure is to sequester off the authentication and user data into seperate
processes that can be run under seperate system users or on seperate machines.
While centralizing sensative data. Using the `Lin` format that you can read
more about [here](/doc/lin.md).

Code can be found in the [auth](polyvinyl/auth) folder of the source folder.

More on the Auth service [here](/doc/auth.md).

## Provider 

This is a configuration based web services framework powerd by the JSON
configuration found at [example/config.json](example/config.json).

Found in the [provider](polyvinyl/provider) folder of the source folder.

# Spatial Oriented Programming

This is a discipline of creating small parts that get routed around the
application almost like spaces. It is focus thinking about software behaviour
in lists, queues, and combinable components that create pipelines. The
pipeline's control is expected to be visible through configuration that can be
authored or user-generated.

# `Chain` Configuration Syntax

Here is an example configuration for the routes of the login page:

```jsonc
"routes": {
    "/auth/login": [
        ["get", "idents=login.idents@page", "end"],
        ["post", "injest=login.json@page", 
            ["data_eq=password@auth-method", [
                    ["data_eq=on@register", "register", "pw_set", 
                        "session_start", "redir=/auth/dashboard", "end"],
                    ["data_neq=on@register", "pw_auth", 
                        "session_start", "redir=/auth/dashboard", "end"]
                ]
            ]
        ],
        ["idents=login.idents@page", "end"]
    ]
}
```

At a high level this is loading and processing a login page. Because this
example uses the Provider service
([provider/serve.py](polyvinyl/provider/serve.py)), all of the `tag` values of
the identifiers will reference functions defined in
[provider/handlers.py](polyvinyl/provider/handlers.py).

See more about how this breaks down [here](/doc/chain.md).


# Identifier Syntax

The identifier is a simple string that represents three distinct parts and can
be repurposed for several uses.

The identifier syntax is a 3 part data identifier with the following syntax:

    <tag>=<name>@<location>

This is used for defining what function to run, what action to perform, or what
credentials to use for actions like user login or registration.

example identifiers:

- redir=/auth/login
- map=action/path@req
- pw_set
- session_start
- register=test%40cb%2elocal@email
    

To describe what each identifier does, It's worth understanding what this
system does: it routes a series of actions to move data and process or produce
a webpage.

See more about what these identifiers mean in the
[Identifier](/doc/identifier.md) documentation.

# Python3 packages used

- bcrypt
- pystache

# Status

PolyVinyl is presently in development with the hope that it can launch demos
and become thoroughly tested in the near future.


(c) Copyright 2026 - Compare Basic Incorporated
See [licence](LICENSE) for details.

PolyVinyl is a product from Compare Basic Incorporated see
[comparebasic.com](https://comparebasic.com) for details.
