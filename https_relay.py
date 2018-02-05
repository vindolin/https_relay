import http.server
import socketserver
from urllib.parse import parse_qs
import requests
import argparse
from functools import wraps


def do_wrapper(func):
    @wraps(func)
    def wrapper(self):
        headers = dict(self.headers.items())

        try:
            target = headers.pop('X-Relay-Target')
        except KeyError:
            target = args.default_target

        if not target:
            print('No default target provided and no X-Relay-Target header found!')
            return

        self.target_url = 'https://{}{}'.format(target, self.path)
        self.target_headers = dict(self.headers.items())

        print('relaying {}'.format(self.target_url))

        self.wfile.write(func(self).content)

    return wrapper


class Relay(http.server.BaseHTTPRequestHandler):
    @do_wrapper
    def do_GET(self):
        return requests.get(self.target_url, headers=self.target_headers)

    @do_wrapper
    def do_HEAD(self):
        print('not implemented!')

    @do_wrapper
    def do_POST(self):
        content_length = int(self.target_headers.pop('Content-Length'))
        post_data = parse_qs(self.rfile.read(content_length))
        return requests.post(self.target_url, headers=self.target_headers, data=post_data)

    def log_message(self, format, *args):
        return  # suppress log messages


parser = argparse.ArgumentParser(
    description='Simple HTTP to HTTPS redirector.',
    epilog='Make sure to either set a default target with --target or send an "X-relay-target: your.target" header with your request!'
)
parser.add_argument('-t', '--default_target', type=str, help='Global default target if you don\'t provide the X-Relay-Target header.')
parser.add_argument('-i', '--interface', type=str, default='localhost', help='Interface where the relay runs on.')
parser.add_argument('-p', '--port', type=int, default=8000, help='The port that the relay should use.')

args = parser.parse_args()

print('Starting https relay on {0.interface}:{0.port}'.format(args))
httpd = socketserver.TCPServer((args.interface, args.port), Relay)
httpd.serve_forever()
