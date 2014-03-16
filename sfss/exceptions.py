class SFSSException(Exception):
    ''' base exception for sfss. '''


class NoAvailableStorageServer(SFSSException):
    ''' No available storage server. '''
