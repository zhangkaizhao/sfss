from model import FileStorage, File, Stats
from main import app


@app.path(model=FileStorage, path='files')
def get_filestorage():
    return FileStorage()


@app.path(model=File, path='file')
def get_file():
    # path will been cut if met first '/' if put path in uri!
    # now put path in query string, see views...
    return File()


@app.path(model=Stats, path='stats')
def get_stats():
    return Stats()
