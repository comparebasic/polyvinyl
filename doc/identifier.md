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

## Example Identifier Descriptions

- redir=/auth/login

This identifier indicates that the page should issue a redirect to the page "/auth/login".


- map=action/path@req

This moves data from the request object to the pages `data` object, and moves the key from `path` to `action`. This is used to create forms that submit to the page they were loaded in.

In essence the above identifier performs this action:
    
    data["action"] = req.path


- pw_set

This calls the handler function `pw_set` in the case of the Provider server requests.

In essence the above identifier performs this action:

    handlers.pw_set(req, ident, data)


- session_start

This calls the handler function `session_start` in the case of the Provider server requests. This handler function requires a `map` identifier to have run to populate what it needs to open the session (usually an email and validation must have already happened).

In essence the above identifier performs this action:

    handlers.pw_set(req, ident, data)


- register=test%40cb%2elocal@email

This is an example of an identifier send across the connection to the Auth service. This is an email (test@cb.local) that has been quoted to contain only ascii letters and numbers, with everything else quoted similar to a url quote convention.


In essence the above identifier performs this action:

    Call the auth service and send this over the connection to initiate the registration method in that service with the <name> portion of the identifier as the email value.



