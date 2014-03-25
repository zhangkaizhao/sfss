==========================
Small file storage service
==========================

:Date: 2014,03,26
:Status: to be continued


overview
========

using:

* storage: Beansdb (git)
* storage proxy: Beanseye (git) (XXX will be removed soon)
* storage client: aiomemcache (git)
* web server programming language: Python (>= 3.3.0)
* asynchronous IO: asyncio
* WSGI server: aiohttp
* ...


howto
=====

start storage servers
---------------------

compile and install Beansdb::

    $ sudo apt-get install gcc autoconf automake libtool
    $ git clone https://github.com/douban/beansdb.get
    $ cd beansdb/
    $ ./autogen.sh
    $ ./configure
    $ make
    $ sudo make install
    $ # this will install beansdb to /usr/local

compile beansdb::

    $ sudo apt-get install golang
    $ git clone https://github.com/douban/beanseye.get
    $ cd beanseye/
    $ make

start nodes of Beansdb::

    $ beansdb -p 7900 -d -H /path/to/node-0/storage/directory
    $ beansdb -p 7901 -d -H /path/to/node-1/storage/directory
    $ beansdb -p 7902 -d -H /path/to/node-2/storage/directory
    $ beansdb -p 7903 -d -H /path/to/node-3/storage/directory
    $ beansdb -p 7904 -d -H /path/to/node-4/storage/directory
    $ beansdb -p 7905 -d -H /path/to/node-5/storage/directory
    $ #...

start proxies of Beanseye::

    $ cd /path/to/beanseye
    $ vi /path/to/beanseye/conf/proxy-0.ini
    $ ./bin/proxy -conf=/path/to/beanseye/proxy-0.ini
    $ vi /path/to/beanseye/conf/proxy-1.ini
    $ ./bin/proxy -conf=/path/to/beanseye/proxy-1.ini
    $ vi /path/to/beanseye/conf/proxy-2.ini
    $ ./bin/proxy -conf=/path/to/beanseye/proxy-2.ini
    $ # ...

now we can view status of storage proxies by its monitor HTTP server. e.g.
(note: replace 0.0.0.0:9900 to real host and port if not in the same machine.)

http://0.0.0.0:9900

http://0.0.0.0:9901

and more.

start web servers
-----------------

cd to sfss directory::

    $ cd /path/to/sfss

bootstrap our environment::

    $ python3 bootstrap.py

if zc.buildout version conflicts with setuptools version, then use::

    $ python3 bootstrap.py -v 2.1.1

or upgrade used setuptools to latest version.

edit buildout.cfg::

    $ vi buildout.cfg

buildout to get all dependencies::

    $ ./bin/buildout -vv

edit web server configure::

    $ vi sfss/settings.py

start server using aiohttp::

    $ ./bin/sfss --host 0.0.0.0 --port 8255

now server will run on http://0.0.0.0:8255

test with curl
--------------

(note: replace 0.0.0.0:8255 to real host and port if not in the same machine.)

create file with POST method::

    $ curl -v -F "upload_file=@/path/to/local/file" -X POST "http://0.0.0.0:8255/files?path=file/path/to/save"

or update file with PUT method::

    $  curl -F "upload_file=@/path/to/local/file" -X PUT "http://0.0.0.0:8255/file?path=file/path/to/save"

get file content with GET method::

    $ curl -v "http://0.0.0.0:8255/file?path=file/path/saved"

get stats of storage proxies::

    $ curl -v http://0.0.0.0:8255/status

service API
===========

note:

* all URL or arguments needed to use UTF-8 encoding if not all ASCII
* all URL or arguments needed to use url quote if not all ASCII

GET /file
---------

description: get file content

request arguments:

* path: required

response:

* status: 200 OK
* Content-Type header: guess by path extension with mimetypes.guess_type
* Content-Length: file size
* body: file content

error response:

* 400 Bad Request: missing or invalid arguments
* 404 Not Found: no such file by path
* 504 Gateway Timeout: none storage proxies available

POST /files
-----------

description: post a file to storage

request arguments:

* path: required (in query string)

request body: file content

response:

* status: 201 Created

error response:

* 400 Bad Request: missing or invalid arguments
* 413 Request Entity Too Large: file size more than 2MB
* 504 Gateway Timeout: none storage proxies available

PUT /file
---------

description: update file in storage or post a file to storage

request arguments:

* path: required (in query string)

request body: file content

response:

* status: 200 OK

error response:

* 400 Bad Request: missing or invalid arguments
* 413 Request Entity Too Large: file size more than 2MB
* 504 Gateway Timeout: none storage proxies available

GET /status
-----------

description: get server status

request arguments: None

response:

* status: 200 OK
* Content-Type header: application/json
* body: json format. each key is storage proxy address. e.g. ::

    {
        "127.0.0.1:8900": {
            "total_items": "0",
            "rusage_user": "0",
            "curr_connections": "2",
            "cmd_delete": "0",
            "rusage_maxrss": "6718",
            "cmd_get": "3",
            "time": "58",
            "pid": "5983",
            "uptime": "301",
            "bytes_written": "21",
            "threads": "12",
            "get_hits": "1",
            "cmd_set": "1",
            "curr_items": "0",
            "get_misses": "2",
            "bytes_read": "21",
            "rusage_system": "0",
            "total_connections": "2"
        },
        "127.0.0.1:8901": {
            "total_items": "0",
            "get_misses": "0",
            "curr_connections": "2",
            "cmd_delete": "0",
            "rusage_maxrss": "6718",
            "threads": "12",
            "cmd_get": "0",
            "time": "58",
            "pid": "5991",
            "uptime": "300",
            "rusage_user": "0",
            "total_connections": "2",
            "cmd_set": "0",
            "curr_items": "0",
            "bytes_written": "0",
            "bytes_read": "0",
            "rusage_system": "0",
            "get_hits": "0"
        }
    }

  This is generated by response of STATS command of memcached.
  Too many no needed information.
  Need to be cut in the future.

error response:

* 504 Gateway Timeout: none storage proxies available

TODO: including all stats of storages and status of webserver.
      then response body will like::

      {
          'storages': {
              'storage1': {
                  'name1': 'value1',
                  'name2': 'value2'
              },
              'storage2': {
                  'name11': 'value11',
                  'name12': 'value12'
              }
          },
          'webserver': {
              'name41': 'value41',
              'name42': 'value42'
          }
      }


simple client
=============

simple client in simple_client.py is just script for testing of posting file::

    $ python3 simple_client.py -h
    $ python3 simple_client.py --host 127.0.0.1 --port 8255 \
      --path folder/subfolder/filename.ext --filepath /path/to/local/file

TODO: benchmark on simple client
