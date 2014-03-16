import time
import random
import threading

import memcache

from exceptions import NoAvailableStorageServer
import settings


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
            # XXX need to change with async
            time.sleep(0.001)
        return None

    def _get_conn(self, server):
        ''' get connection by server within socket timeout. '''
        # create connection if not yet
        with self._lock:
            conn = self._cached_conns.get(server)
            if not conn:
                conn = memcache.Client(
                    [server],
                    socket_timeout=self.retry_after_seconds,
                    server_max_value_length=self.max_content_size)
                self._cached_conns[server] = conn

        # try to connect in socket_timeout
        start_time = time.time()
        while True:
            if conn.servers[0].connect():
                return conn
            if start_time + conn.socket_timeout < time.time():
                break
            # XXX need to change with async
            time.sleep(0.001)
        return None

    def get_conn(self):
        ''' get random connection within max retry. '''
        for _ in xrange(self.max_retry):
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
        for _ in xrange(2):
            conn = self.get_conn()
            ret = conn.set(path, content)
            if ret is not None:
                return ret
        return ret

    def get(self, path):
        for _ in xrange(2):
            conn = self.get_conn()
            # '' -> empty body
            # or None -> non-existent or connection broken
            got = conn.get(path)
            if got is not None:
                return got
        return got

    def stats(self):
        # TODO get each Beansdb node stat
        outdict = {}
        for server in self.servers:
            conn = self._get_conn(server)
            stats = conn.get_stats()
            outdict[server] = stats[0][1] if stats else {}
        return outdict


fs = Storage(
    settings.STORAGE_SERVERS,
    settings.STORAGE_MAX_RETRY,
    settings.RETRY_AFTER_SECONDS,
    settings.MAX_ENCODED_PATH_LENGTH,
    settings.MAX_CONTENT_SIZE)
