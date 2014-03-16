import argparse

import morepath

app = morepath.App()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host')
    parser.add_argument('--port', type=int, dest='port')
    args = parser.parse_args()

    kwargs = {}
    if args.host:
        kwargs['host'] = args.host
    if args.port:
        kwargs['port'] = args.port

    #morepath.autosetup()
    config = morepath.setup()
    config.scan()
    config.commit()
    morepath.run(app, **kwargs)


if __name__ == '__main__':
    main()
