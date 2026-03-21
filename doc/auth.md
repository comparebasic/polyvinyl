# Auth Service

This service uses a series of strings, communicated using the `Lin` format, to
accept and respond to queries for authentication, or to create authentication
tokens.

## Communication Protocol

A unix socket is provided to read and write the `Lin` format, which is inspired
by SAML but only provides a subset of it's functionality for now.

More on the `Lin` format is written [here](doc/lin.md).

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
