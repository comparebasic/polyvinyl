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

![Auth digest diagram](auth-hmac-concat.svg)
    
Here is the actual bytes of the message (with ... for password and signature
values):

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

## Token Structure

The token system creates a long random string and then indexes into positions
of that string to generate unique values. 

Presently a sha512 is used to create 64 semi-rendom bytes, that can create 18
potential six digit codes.

The last two digits of the code indicate the position within the random token
value, meaning that only the first four digits are indicative of a randomized
value.

![Six Code Token Diagram](/doc/six-code-token.svg)

Because each token is presently a 64 byte semi-random string. The token is
stored in a `lin` file as the first value, then each six-code that is consumed
is stored as a lin record within that file. When all 18 values are consumed,
the file is moved and saved with it's date and a new token file is created.

This way new tokens can be allocated, and the consumption of tokens can also be
tracked, with the next available token also easily accessible.
