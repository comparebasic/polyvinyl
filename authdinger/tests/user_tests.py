from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7523 import ClientSecretJWT

client_id = "01234567"
secret = "secretsecretsecret"

token_endpoint = 'http://localhost:3000/oauth/token'
session = OAuth2Session(
    client_id, secret,
    token_endpoint_auth_method=ClientSecretJWT(token_endpoint),
)
session.fetch_token(token_endpoint)
