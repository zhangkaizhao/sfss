import json
import mimetypes
#import io
import urllib.parse
from urllib.parse import parse_qs

from .filestorage import fs
from .model import File

chunk_size = 8 * 1024  # 8KB
max_file_size = 2 * 1024 * 1024  # 2MB


def simple_app(environ, start_response):
    # TODO: rearrange
    request_method = environ['REQUEST_METHOD']
    path_info = environ['PATH_INFO']
    query_string = environ['QUERY_STRING']

    if path_info == '/files':
        if request_method == 'POST':
            arguments = parse_qs(query_string)
            file_paths = arguments.get('path', None)
            if not file_paths:
                status = '400 Bad Request'
                start_response(status, [])
                return []

            file_path = file_paths[0]

            # validate path
            file_path = urllib.parse.unquote(file_path)
            if file_path.startswith('/') or '\\' in file_path or \
                    '//' in file_path:
                status = '400 Bad Request'
                start_response(status, [])
                return []
            _file = File(file_path)
            if len(_file.encoded_path) > fs.max_encoded_path_length:
                status = '400 Bad Request'
                start_response(status, [])
                return []

            ## which wsgi server support reading by chunk?
            ## aiohttp does not support now...
            #rfile = environ['wsgi.input']
            #buffered = io.BytesIO()
            #read_size = 0
            #while True:
            #    # XXX, how to stream?
            #    chunk = rfile.read(chunk_size)
            #    len_chunk = len(chunk)
            #    if not len_chunk:
            #        break
            #    buffered = buffered + chunk
            #    read_size = read_size + len_chunk
            #    if read_size > max_file_size:
            #        status = '416 Request Entity too Large'
            #        start_response(status, [])
            #        return []
            #_file.content = buffered.getvalue()
            # XXX
            rfile = environ['wsgi.input']
            content = yield from rfile.read()
            if len(content) > max_file_size:
                status = '416 Request Entity too Large'
                start_response(status, [])
                return []
            _file.content = content

            ret = yield from _file.save()
            if ret:
                status = '201 Created'
                start_response(status, [])
                return []
            else:
                status = '500 Server Internal Error'
                start_response(status, [])
                return ['can not put file into storage.']
        else:
            status = '405 Method Not Allowed'
            start_response(status, [])
            return []

    elif path_info == '/file':
        arguments = parse_qs(query_string)
        file_paths = arguments.get('path', None)
        if not file_paths:
            status = '400 Bad Request'
            start_response(status, [])
            return []

        file_path = file_paths[0]

        # validate path
        file_path = urllib.parse.unquote(file_path)
        if file_path.startswith('/') or '\\' in file_path or \
                '//' in file_path:
            status = '400 Bad Request'
            start_response(status, [])
            return []
        _file = File(file_path)
        if len(_file.encoded_path) > fs.max_encoded_path_length:
            status = '400 Bad Request'
            start_response(status, [])
            return []

        if request_method == 'GET':
            file_content = yield from _file.get_content()
            if file_content is None:
                status = '404 Not Found'
                start_response(status, [])
                return []
            else:
                _type = mimetypes.guess_type(file_path)[0]
                content_type = _type or 'application/octet-stream'
                status = '200 OK'
                response_headers = [('Content-type', content_type)]
                start_response(status, response_headers)
                return [file_content]

        elif request_method == 'PUT':
            # XXX
            rfile = environ['wsgi.input']
            content = yield from rfile.read()
            if len(content) > max_file_size:
                status = '416 Request Entity too Large'
                start_response(status, [])
                return []
            _file.content = content

            ret = yield from _file.save()
            if ret:
                status = '200 OK'
                start_response(status, [])
                return []
            else:
                status = '500 Server Internal Error'
                start_response(status, [])
                return []
        else:
            status = '405 Method Not Allowed'
            start_response(status, [])
            return []
    elif path_info == '/status':
        stats = yield from fs.stats()
        body = json.dumps(stats).encode()
        status = '200 OK'
        response_headers = [('Content-type', 'application/javascript')]
        start_response(status, [])
        return [body]
    else:
        status = '404 Not Found'
        start_response(status, [])
        return []

    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return []


def main():
    import os
    import sys
    import argparse
    import logging
    import ssl
    import asyncio
    from aiohttp.wsgi import WSGIServerHttpProtocol
    server = WSGIServerHttpProtocol(simple_app)

    parser = argparse.ArgumentParser(description="Run simple http server.")
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
        '--ssl', action="store_true", dest='ssl', help='Run ssl mode.')
    parser.add_argument(
        '--sslcert', action="store", dest='certfile', help='SSL cert file.')
    parser.add_argument(
        '--sslkey', action="store", dest='keyfile', help='SSL key file.')

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

    if args.ssl:
        here = os.path.join(os.path.dirname(__file__), 'tests')

        if args.certfile:
            certfile = args.certfile or os.path.join(here, 'sample.crt')
            keyfile = args.keyfile or os.path.join(here, 'sample.key')
        else:
            certfile = os.path.join(here, 'sample.crt')
            keyfile = os.path.join(here, 'sample.key')

        sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslcontext.load_cert_chain(certfile, keyfile)
    else:
        sslcontext = None

    loop = asyncio.get_event_loop()
    f = loop.create_server(
        lambda: server,
        args.host,
        args.port,
        ssl=sslcontext)
    svr = loop.run_until_complete(f)
    socks = svr.sockets
    print('serving on', socks[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
