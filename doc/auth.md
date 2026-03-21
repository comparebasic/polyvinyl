# Auth Service

This service uses a series of strings, communicated using the `Lin` format, to
accept and respond to queries for authentication, or to create authentication
tokens.

## Communication Protocol

A unix socket is provided to read and write the `Lin` format, which is inspired
by SAML but only provides a subset of it's functionality for now.

More on the `Lin` format is written [here](/doc/lin.md).


## Trust Establishment

Currently (unix socket):

- Clients establish trust by the file path of the unix socket.
- Clients are trusted by signing messages with a shared HMAC key

Going forward (inet or unix socket):

TLS or Public and private key signatures and encryption may be used to
establish trust between this service and it's clients.

- Clients require responses to be signed with an ECDSA certificate.
- Clients are trusted by signing messages with an ECDSA certificate.
- Communication is encrypted after the "aim" keyword and value


## Client Verification

Client verification is done via an HMAC signature for portions of the message.

For example, the following message includes an HMAC signature of all the values
after "hmac-concat" and before "end-sig":

```
    03: aim
    11: hmac-concat
    05: ident
    31: fpw_auth=test%40cb%2elocal@email
    13: password-hash
    62: <password hash bytes> 
    07: end-sig
    32: <signature bytes>
```
    
Here is the action message (with ... for password and signature values):

```
    \{0}\{3}aim\{0}\x0bhmac-concat\{0}\{5}ident\{0}\x1fpw_auth=test%40cb%2elocal@email\{0}\rpassword-hash\{0}\{62}...\{0}\{7}end-sig\{0}\{32}...\{0}\{0}
```

Note: "aim" is a term to indicate that the protocol is being defined, in this
service the next string defines how the rest of communication should proceed.

## Artifact Storage

The Auth server is designed to only store sensative information while expecting
another application server to store user data, and user-generated content. This
seperation is important because it limits the potential for the two to mix,
decreasing the likelyhood that user interactions can poison authentication
data.

Stored in auth:

- Password hashes
- Authentication tokens

Stored in app server (Provider):

- Password salt
- User details
- User data
- Application data

Because the salt is stored in the application server, the hashed password is
passed to the Auth service. This limits the time that the raw password exists
while ensuring that the raw password never leaves the memory space of the
application server.

For now, that transmission of the password hash is unecrypted but encapsulated
between the TCP/IP stream of the unix socket between the application and
authentication server.
