import os, shutil
from polyvinyl import lin

CONFIG_DIR = "example/"

users = {
    "testone": {
        "name": "testone",
        "email":"testone@cb.local",
        "fullname": "Test One",
        "password": "TestyPantsyOne9_"
    }
}

def get_user(name):
    return users[name]

def get_token(user):
    return lin.quote(user["email"]).decode("utf-8")

def wipe_user(user):
    email_token = get_token(user)

    path = os.path.join(
        os.path.join(CONFIG_DIR, "user-data"),
            email_token)

    if os.path.exists(path):
        shutil.rmtree(path)
    
    path = os.path.join(
        os.path.join(CONFIG_DIR, "auth-data"),
            email_token)

    if os.path.exists(path):
        shutil.rmtree(path)

def wipe_session(ssid):
    path = os.path.join(
        os.path.join(CONFIG_DIR, "sessions"),
            ssid)

    if os.path.exists(path):
        os.remove(path)
