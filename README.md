# AuthDinger

Two services, one for a SAML based user management framework, and another as an
OAUTH frontend service.

## AuthDingerUser

This service is starts with a UDP socket server using the SAML protocol for
authentication, and the superset of that protocol for user management

found in the [auth](authdinger/auth) folder of the source folder.

## AuthDingerServer

This service is a frontend for the OAuth protocol and it's interaction with the
underlying User service.

found in the [provider](authdinger/provider) folder of the source folder.
