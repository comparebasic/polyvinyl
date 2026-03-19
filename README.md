# PolyVinyl

This is a task-management and web application framework based on the following things:

- Server and Handler files for the two services included: `Auth` and `Provider`.
- Configuration pipeline known as a `Chain` based on Spatial Oriented Programming.
- Set of utilities for simple stuff such as token and session handling.
- Identifier syntax for defining common actions in the form `<tag>=<name>@<location>`.
- Simple data format for storing and streaming data known as `Lin`.

# Services

Two services are included, one for a authentication and one for a web services management framework.

## Auth 

This service is starts with a UNIX socket server using the a protocal that
communicates content length in two bytes, followed by content, to transmit a
series of identifiers. The response is communicated in similar identifiers.

found in the [auth](polyvinyl/auth) folder of the source folder.

## Provider 

This is a configuration based web services framework powerd by the JSON
configuration found at [example/config.json](example/config.json).

found in the [provider](polyvinyl/provider) folder of the source folder.

# Spatial Oriented Programming

This is a discipline of creating small parts that get routed around the application almost like spaces. It has a strong focus on keeping behaviour in lists and configuration that can be read and discussed at a high level.

# `Chain` configuration syntax

Here is an example configuration for the routes of the login page:

```json
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

At a high level this is loading and processing a login page. Becuase this example uses the [polyvinyl/provider/serve.py] Provider service, all of the `tag` values of the identifiers will reference functions defined in [provider/handlers.py](polyvinyl/provider/handlers.py).

See more about how this breaks down [here](/doc/chain.md).

# Identifier Syntax

The identifier is a simple string that represents three distinct parts and can be repurposed for several uses.

The identifier syntax is a 3 part data identifier with the following syntax:

    <tag>=<name>@<location>

This is used for defining what function to run, what action to perform, or what credentials to use for actions like user login or registration.


example identifiers:

    redir=/auth/login

    map=action/path@req

    pw_set

    session_start

    register=test%40cb%2elocal@email
    

To describe what each identifier does, It's worth understanding what this system does: it routes a series of actions to move data and process or product a webpage.

See more about how this breaks [here](doc/identifier.md).
