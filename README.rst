TODO

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

start web servers
-----------------

cd to sfss directory::

    $ cd /path/to/sfss

bootstrap our environment::

    $ python2 bootstrap.py

if zc.buildout version conflicts with setuptools version, then use::

    $ python2 bootstrap.py -v 2.1.1

buildout to get all dependencies::

    $ ./bin/buildout -vv

edit web server configure::

    $ vi sfss/settings.py

start server using default wsgiref.simple_server::

    $ ./bin/sfss --host 0.0.0.0 --port 8888

now server will run on http://0.0.0.0:8888

test with curl
--------------

note: replace 0.0.0.0:8888 to real host and port if not in the same machine.

create file with POST method::

    $ curl -v -F "upload_file=@/path/to/local/file" -X POST "http://0.0.0.0:8888/files?path=file/path/to/save"

or update file with PUT method::

    $  curl -F "upload_file=@/path/to/local/file" -X PUT "http://0.0.0.0:8888/file?path=file/path/to/save"

get file content with GET method::

    $ curl -v "http://127.0.0.1:5000/file?path=file/path/saved"
