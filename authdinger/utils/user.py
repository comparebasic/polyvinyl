import os, urllib
from .bstream import quote, unquote
from .exception import DingerNotOk 

def create(req, config, data):
    email_token = quote(data["email"])
    req.server.logger.log("Email Token {}".format(email_token))
    fname = "{}.rseg".format(email_token)
    path = os.path.join(config["dirs"]["user-data"],fname)

    req.server.logger.log("Email Token Value {}".format(unquote(email_token)))

    if os.path.exists(path):
        raise DingerNotOk("User Exists")

    user_file = open(path, "w+");

    

    
    
