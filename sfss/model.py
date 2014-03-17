import binascii

from filestorage import fs


class FileStorage(object):

    def __init__(self):
        pass

    def put(self, _file):
        return fs.put(_file.encoded_path, _file.content)


class File(object):

    def __init__(self, path=None, content=None):
        self.path = path
        self.content = content

        self._content_got = False

    @property
    def encoded_path(self):
        ''' encoded path for filestorage '''
        if not hasattr(self, '_encoded_path'):
            path = self.path
            if isinstance(path, unicode):
                path = path.encode('utf-8')
            self._encoded_path = binascii.b2a_base64(path)[:-1]
        return self._encoded_path

    def save(self):
        return fs.put(self.encoded_path, self.content)

    def get_content(self):
        if self.content is None:
            if not self._content_got:
                self.content = fs.get(self.encoded_path)
                self._content_got = True
        return self.content


class Stats(object):

    def get(self):
        # TODO: including storages, storage proxies and webserver self.
        return fs.stats()
