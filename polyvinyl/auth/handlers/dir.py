import os


def get_authdir(config, email_token):
    return os.path.join(config["dirs"]["auth-data"], email_token)


def get_authfile(config, email_token):
    return os.path.join(get_authdir(config, email_token),
                "auth.linr")


def get_tokenfile(config, email_token, token):
    return os.path.join(
            os.path.join(
                get_authdir(config, email_token),
                "tokens"),
            token)
