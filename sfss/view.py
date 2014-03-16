import mimetypes
import urllib

import webob.exc

from exceptions import NoAvailableStorageServer
from filestorage import fs
from main import app
from model import FileStorage, File, Stats


def _create_file_from_request(request):
    # dirty path got
    path = request.GET.get('path')
    if not path:
        raise webob.exc.HTTPBadRequest('missing path argument.')

    path = urllib.unquote(path)
    if path.startswith('/') or '\\' in path or '//' in path:
        raise webob.exc.HTTPBadRequest('invalid path argument.')
    _file = File(path)
    # validate path
    if len(_file.encoded_path) > fs.max_encoded_path_length:
        raise webob.exc.HTTPBadRequest('path length too long.')

    return _file


def _read_file_content_from_request(request):
    f = request.POST.get('upload_file', None)
    if f is None:
        raise webob.exc.HTTPBadRequest('missing upload_file field.')
    _f = f.file

    content = b''
    read_size = 0
    while True:
        # chunk size 64KB
        chunk = _f.read(65536)
        len_chunk = len(chunk)
        if len_chunk == 0:
            break
        read_size = read_size + len_chunk
        # check if content too large
        if read_size > fs.max_content_size:
            raise webob.exc.HTTPRequestEntityTooLarge(
                'file size limited to 2MB.')
        content = content + chunk

    return content


@app.view(model=FileStorage, name='', request_method='POST')
def post_file(self, request):
    ''' create file '''
    # dirty path got
    _file = _create_file_from_request(request)
    _file.content = _read_file_content_from_request(request)
    try:
        ret = self.put(_file)
    except NoAvailableStorageServer:
        raise webob.exc.HTTPBadGateway('no available storage server.')
    if not ret:
        raise webob.exc.HTTPBadGateway('failed to post file.')

    def set_headers(response):
        # set Content-Type, etc headers
        response.status = '201 Created'

    request.after(set_headers)


@app.view(model=File, name='', request_method='PUT')
def put_file(self, request):
    ''' update file '''
    _file = _create_file_from_request(request)
    self.path = _file.path
    self.content = _read_file_content_from_request(request)
    try:
        ret = self.save()
    except NoAvailableStorageServer:
        raise webob.exc.HTTPBadGateway('no available storage server.')
    if not ret:
        raise webob.exc.HTTPBadGateway('failed to put file.')


@app.view(model=File)
def file_content(self, request):
    ''' get file '''
    _file = _create_file_from_request(request)
    self.path = _file.path
    try:
        content = self.get_content()
    except NoAvailableStorageServer:
        raise webob.exc.HTTPBadGateway('no available storage server.')
    if content is None:
        raise webob.exc.HTTPNotFound()

    content_type = mimetypes.guess_type(self.path)[0] or \
        'application/octet-stream'

    def set_headers(response):
        # set Content-Type, etc headers
        response.content_type = content_type

    request.after(set_headers)

    return content


@app.json(model=Stats)
def stats(self, request):
    return self.get()
