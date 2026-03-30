import argparse, os, glob
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        files = glob.glob("%s/*" % self.server.path)
        latest = max(files, key=os.path.getctime)
        print(latest)

        self.send_response(200, "Ok") 
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        with open(latest, "rb") as f:
            self.wfile.write(f.read())


class Server(HTTPServer):
    def __init__(self, path, address):

        self.path = path
        return super().__init__(address, Handler)


def parse_cli():
    parser = argparse.ArgumentParser(
        prog="EmailSpoofer",
        description="Displays the latest email in a web response")
    parser.add_argument("--path")
    parser.add_argument("--port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli()

    try:
        port = int(args.port)
    except (ValueError, TypeError) as err:
        raise ValueError("Expected interger for port number", err)

    print("Serving PolyVinyl Provider on port {}".format(port))
    httpd = Server(args.path, ('localhost', port))

    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()

