try:
    import BaseHTTPServer as base_http_server
    import SocketServer as socketserver
    from urlparse import parse_qs
except ImportError:
    import http.server as base_http_server
    import socketserver
    from urllib.parse import parse_qs

import json
import requests
import argparse
from functools import wraps
from pprint import pprint


class ANSI:
    green = '\033[32m'
    orange = '\033[33m'
    yellow = '\033[93m'

    reset = '\033[0m'


def do_wrapper(func):
    @wraps(func)
    def wrapper(self):
        headers = dict(self.headers.items())

        try:
            try:
                target = headers.pop('X-Relay-Target')
            except KeyError:
                target = headers.pop('x-relay-target')

        except KeyError:
            target = args.default_target

        if not target:
            print('No default target provided and no X-Relay-Target header found!')
            return

        self.target_url = 'https://{}{}'.format(target, self.path)
        self.target_headers = dict(self.headers.items())

        print('relaying {}'.format(self.target_url))
        response = func(self)

        self.send_response(response.status_code)
        if args.debug:
            print('\n{}STATUS CODE: {}'.format(ANSI.green, response.status_code, ANSI.reset))

        if args.debug:
            print('\n{}RESPONSE HEADERS:{}'.format(ANSI.yellow, ANSI.reset))
            print(ANSI.yellow)

        for name, value in response.headers.items():
            self.send_header(name, value)
            if args.debug:
                print('    "{}": "{}"'.format(name, value))

        if args.debug:
            print(ANSI.reset)

        self.end_headers()

        if args.debug:
            print(ANSI.orange)
            if response.headers.get('Content-Type') == 'application/json':
                print('\n{}JSON CONTENT:{}'.format(ANSI.orange, ANSI.reset))
                print(ANSI.orange)
                pprint(json.loads(response.content.decode('utf8')))
                print(ANSI.reset)
            else:
                print('\n{}CONTENT:{}'.format(ANSI.bold, ANSI.orange, ANSI.reset))
                print(ANSI.orange)
                print(response.content)
                print(ANSI.reset)

        if args.debug:
            print()

        self.wfile.write(response.content)

    return wrapper


class Relay(base_http_server.BaseHTTPRequestHandler):

    @do_wrapper
    def do_GET(self):
        return requests.get(self.target_url, headers=self.target_headers)

    @do_wrapper
    def do_HEAD(self):
        return requests.head(self.target_url, headers=self.target_headers)

    @do_wrapper
    def do_POST(self):
        try:
            content_length = int(self.target_headers.pop('Content-Length'))
        except KeyError:
            content_length = int(self.target_headers.pop('content-length'))  # python 2

        post_data = parse_qs(self.rfile.read(content_length))
        return requests.post(self.target_url, headers=self.target_headers, data=post_data)

    def log_message(self, format, *args):
        return  # suppress log messages


parser = argparse.ArgumentParser(
    description='Simple HTTP to HTTPS redirector.',
    epilog='Make sure to either set a default target with --target or send an "X-Relay-Target: your.target" header with your request!'
)
parser.add_argument('-t', '--default_target', type=str, help='Global default target if you don\'t provide the X-Relay-Target header.')
parser.add_argument('-d', '--debug', help='Print return codes and data.', action='store_true')
parser.add_argument('-i', '--interface', type=str, default='localhost', help='Interface where the relay runs on.')
parser.add_argument('-p', '--port', type=int, default=8000, help='The port that the relay should use.')

args = parser.parse_args()

print('Starting https relay on {0.interface}:{0.port}'.format(args))
httpd = socketserver.TCPServer((args.interface, args.port), Relay)
httpd.serve_forever()
