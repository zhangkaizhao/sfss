## NOTE: connect to storages if none storage proxies available?
# for now, storages are just used for stats fetch query.
# just connect to storage proxies by now
STORAGES = ['127.0.0.1:7900', '127.0.0.1:7901', '127.0.0.1:7902']
STORAGE_PROXIES = ['127.0.0.1:8900', '127.0.0.1:8901']
STORAGE_PROXY_MAX_RETRY = 3
STORAGE_PROXY_RETRY_AFTER_SECONDS = 2
MAX_ENCODED_PATH_LENGTH = 250
MAX_CONTENT_SIZE = 2 * 1024 * 1024  # 2MB
