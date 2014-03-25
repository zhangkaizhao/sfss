import time
import random
import threading
import asyncio

import aiomemcache

from .exceptions import NoAvailableStorageServer
from . import settings


class Storage(object):

    def __init__(self, servers, max_retry=3, retry_after_seconds=2,
                 max_encoded_path_length=250, max_content_size=None):
        self.servers = servers
        self.max_retry = max_retry
        self.retry_after_seconds = retry_after_seconds
        self.max_encoded_path_length = max_encoded_path_length
        self.max_content_size = max_content_size

        self.num_servers = len(self.servers)

        if self.num_servers != len(servers):
            raise Exception('Repeated server in servers.')

        self._server = self.servers[0] if self.num_servers == 1 else None

        # server -> bad_at
        self._bad_servers = {}

        # server -> conn
        self._cached_conns = {}

        self._lock = threading.Lock()

    def _get_random_server(self):
        retried = 0
        while True:
            with self._lock:
                for server, bad_at in self._bad_servers.items():
                    if bad_at + self.retry_after_seconds < time.time():
                        try:
                            del self._bad_servers[server]
                        except:
                            pass

            if self._server is not None:
                return self._server

            server = random.choice(self.servers)
            if server not in self._bad_servers:
                return server
            # XXX mv max retry in get_conn
            retried += 1
            if retried >= self.max_retry:
                break
            asyncio.sleep(0.001)
        return None

    def _get_conn(self, server):
        ''' get connection by server within socket timeout. '''
        # create connection if not yet
        with self._lock:
            conn = self._cached_conns.get(server)
            if not conn:
                host, port = server.split(':')
                port = int(port)
                conn = aiomemcache.Client(
                    host, port,
                    connect_timeout=self.retry_after_seconds)
                self._cached_conns[server] = conn

        # try to connect in socket_timeout
        start_time = time.time()
        while True:
            _protocol = yield from conn._get_connection()
            if _protocol.is_connected:
                return conn
            if start_time + conn._timeout < time.time():
                break
            # XXX need to change with async
            time.sleep(0.001)
        return None

    def get_conn(self):
        ''' get random connection within max retry. '''
        for _ in range(self.max_retry):
            server = self._get_random_server()
            if not server:
                raise NoAvailableStorageServer()
            conn = self._get_conn(server)
            if conn is not None:
                return conn
            else:
                self._bad_servers[server] = time.time()
        raise NoAvailableStorageServer()

    def put(self, path, content):
        # can we use generator to avoid high memory usage at one time?
        #content = b''.join(file_iter)
        for _ in range(2):
            conn = None
            try:
                conn = yield from self.get_conn()
                yield from conn.set(path, content)
                return True
            except NoAvailableStorageServer:
                raise
            except ConnectionRefusedError:
                if conn is not None:
                    with self._lock:
                        server = '{0}:{1}'.format(conn.host, conn.port)
                        self._bad_servers[server] = time.time()
        return False

    def get(self, path):
        for _ in range(2):
            conn = None
            try:
                conn = yield from self.get_conn()
                # '' -> empty body
                # or None -> non-existent or connection broken
                got = yield from conn.get(path)
                if got is not None:
                    return got
            except NoAvailableStorageServer:
                raise
            except ConnectionRefusedError:
                if conn is not None:
                    with self._lock:
                        server = '{0}:{1}'.format(conn.host, conn.port)
                        self._bad_servers[server] = time.time()
        return got

    def stats(self):
        # TODO get each Beansdb node stat
        outdict = {}
        for server in self.servers:
            conn = None
            try:
                conn = yield from self._get_conn(server)
                stats = yield from conn.stats()
                stats = {k.decode(): v.decode() for k, v in stats.items()}
                outdict[server] = stats if stats else {}
            except NoAvailableStorageServer:
                raise
            except ConnectionRefusedError:
                outdict[server] = {}
                if conn is not None:
                    with self._lock:
                        server = '{0}:{1}'.format(conn.host, conn.port)
                        self._bad_servers[server] = time.time()
        return outdict


fs = Storage(
    settings.STORAGE_PROXIES,
    settings.STORAGE_PROXY_MAX_RETRY,
    settings.STORAGE_PROXY_RETRY_AFTER_SECONDS,
    settings.MAX_ENCODED_PATH_LENGTH,
    settings.MAX_CONTENT_SIZE)
