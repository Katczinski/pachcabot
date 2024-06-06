import socket
import json as Json
import requests
import requestparser
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = '127.0.0.1'
PORT = 5000            # Arbitrary non-privileged port

# # socket.getaddrinfo(HOST, PORT)
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen(1)
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by', addr)
#         while True:
#             data = conn.recv(1024)
#             if data:
#                 r = requestparser.RequestParser(data.decode("utf-8"))
#                 print(data)
#                 json_req = Json.loads(r.data[0])
#                 print(json_req)
#                 if "type" in json_req:
#                     print(f'type: {json_req["type"]}')
#                 if "event" in json_req:
#                     print(f'type: {json_req["event"]}')
#                 conn.send("""HTTP/1.1 200 OK Content-Type: text/html <html><body>Hello World</body></html>""")

import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable
from functools import partial

class S(BaseHTTPRequestHandler):
    callback:Callable
    callback_self:object

    def __init__(self, callback:Callable=None, *args, **kwargs):
        self.callback = callback
        # self.callback_self = callback_self
        super().__init__(*args, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("hi!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        if self.callback: self.callback(post_data.decode('utf-8'))
        self._set_headers()
        self.wfile.write(self._html("POST!"))


def run(server_class=HTTPServer, handler_class=S, callback:Callable=print,  addr="127.0.0.1", port=5000):
    server_address = (addr, port)
    my_handler = partial(S, callback)
    httpd = server_class(server_address, my_handler)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()

class Bot:
    def callback(self, msg):
        print("From Bot callback:", msg)

    def run(self):
        run(callback=self.callback)

b = Bot()
b.run()

# if __name__ == "__main__":

#     parser = argparse.ArgumentParser(description="Run a simple HTTP server")
#     parser.add_argument(
#         "-l",
#         "--listen",
#         default="localhost",
#         help="Specify the IP address on which the server listens",
#     )
#     parser.add_argument(
#         "-p",
#         "--port",
#         type=int,
#         default=8000,
#         help="Specify the port on which the server listens",
#     )
#     args = parser.parse_args()
#     run(addr=args.listen, port=args.port)