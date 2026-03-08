import os
from authdinger import \
    ParseConfig, ParseCli, DingerAuthServer, DingerProviderServer, \
    GetLogger

def run_auth(config, logger):
    logger.log("Serving AuthDinger Auth on socket {}".format(config["auth-socket"]))
    streamd = DingerAuthServer(config, logger) 

    try:
        streamd.serve_forever()
    finally:
        streamd.server_close()
        os.remove(config["auth-socket"])


def run_provider(config, logger):
    try:
        port = int(config["port"])
    except (ValueError, TypeError) as err:
        raise ValueError("Expected interger for port number", err)

    logger.log("Serving AuthDinger Provider on port {}".format(port))
    httpd = DingerProviderServer(config,
        GetLogger(config), ('localhost', port))

    try:
        logger.warn("Serving...")
        httpd.serve_forever()
    finally:
        httpd.server_close()


if __name__ == "__main__":
    cli = ParseCli()
    config = ParseConfig(cli.config)
    config["log-color"] = cli.log_color
    logger = GetLogger(config)

    if not cli.type or cli.type == "auth":
        run_auth(config, logger)

    if not cli.type or cli.type == "provider":
        run_provider(config, logger)
