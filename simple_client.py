#!/usr/bin/env python3

import os.path
import sys

import asyncio
import aiohttp


class SimpleClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def post(self, path, content):
        if isinstance(path, str):
            path = path.encode('utf-8')
        response = yield from aiohttp.request(
            'POST',
            'http://{0}:{1}/files'.format(self.host, self.port),
            params={'path': path},
            data=content)
        if response.status == 201:
            return True
        else:
            return False

    def put(self, path, content):
        if isinstance(path, str):
            path = path.encode('utf-8')
        response = yield from aiohttp.request(
            'PUT',
            'http://{0}:{1}/files'.format(self.host, self.port),
            {'path': path},
            content)
        if response.status == 200:
            return True
        else:
            return False


if __name__ == '__main__':
    import argparse
    import logging
    parser = argparse.ArgumentParser(description="Run simple client.")
    parser.add_argument(
        '--host', action="store", dest='host',
        default='127.0.0.1', help='Host name')
    parser.add_argument(
        '--port', action="store", dest='port',
        default=8080, type=int, help='Port number')
    parser.add_argument(
        '--iocp', action="store_true", dest='iocp',
        help='Windows IOCP event loop')
    parser.add_argument(
        '--path', action="store", dest='path',
        help='File path to store in server')
    parser.add_argument(
        '--filepath', action="store", dest='filepath',
        help='Local file path to read content')

    args = parser.parse_args()

    if ':' in args.host:
        args.host, port = args.host.split(':', 1)
        args.port = int(port)

    if args.iocp:
        from asyncio import windows_events
        sys.argv.remove('--iocp')
        logging.info('using iocp')
        el = windows_events.ProactorEventLoop()
        asyncio.set_event_loop(el)

    if args.path and args.filepath:
        filepath = os.path.abspath(args.filepath)
        if not os.path.isfile(filepath):
            parser.error('invalid local file path')
        with open(filepath, 'rb') as f:
            content = f.read()

        client = SimpleClient(args.host, args.port)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client.post(args.path, content))
    else:
        parser.print_help()
