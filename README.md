# PolyVinyl

This is a task-management and web application framework based on the following things:

- Server and Handler files for the two services included: `Auth` and `Provider`.
- Configuration pipeline known as a `Chain` based on Spatial Oriented Programming.
- Set of utilities for simple stuff such as token and session handling.
- Identifier syntax for defining common actions in the form `<tag>=<name>@<location>`.
- Simple data format for storing and streaming data known as `Lin`.

This system is presently written in Python 3 and available under a 3-clause BSD [Licence](LICENSE).

Architectural Diagram:

![Architectural Diagram](doc/polyvinyl-arch.svg)

# Convention

The main convention of the system is that it uses a series three-part
identifiers to define behavior. These identifiers are stored in a
[configuration](example/config.json) file that loads against a
[module](polyvinyl/provider/handlers.py) with functions defined to be triggered by the
identifiers.

An example identifiery is as follows, see more about identifiers [here](doc/identifier.md):

```
<tag>=<name>@<location>
```


This is the function signature for handling the behavior of an identitifier.

```python
def func(request, ident, data):
    # do stuff that either:
    #
    #    1. modifies values in the *data* dict argument
    #    or
    #    2. raises an exception
```

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
and small pieces of information. The largest value is a that it can easily
centralize and house sensative data in a seperate process using a seperate
system user. Using the `Lin` format that you can read more about [here](doc/lin.md).

Found in the [auth](polyvinyl/auth) folder of the source folder.

## Provider 

This is a configuration based web services framework powerd by the JSON
configuration found at [example/config.json](example/config.json).

Found in the [provider](polyvinyl/provider) folder of the source folder.

# Spatial Oriented Programming

This is a discipline of creating small parts that get routed around the
application almost like spaces. It has a strong focus on keeping behaviour in
lists and configuration that can be read and discussed at a high level.

# `Chain` Configuration Syntax

Here is an example configuration for the routes of the login page:

```jsonc
"routes": {
    "/auth/login": [
        ["get", "map=action/path@req", "content=login-form.format@page", "end"],
        ["post", "map=email,auth-method,password?,fullname?@form", 
            ["data_eq=on@register", "register", "pw_set"],
            ["data_neq=on@register", "pw_auth"],
                "session_start", "redir=/auth/dashboard", "end"]
        ["map=action/path@req", "content=login-form.format@page", "end"]
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

See more about what these identifiers mean in the [Identifier](doc/identifier.md) documentation.

(c) Copyright 2026 - Compare Basic Incorporated
See [licence](LICENSE) for details.
