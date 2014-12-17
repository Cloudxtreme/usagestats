"""Simple WSGI script to store the usage reports.
"""


import os
import re


DESTINATION = '.'  # Current directory
MAX_SIZE = 524288  # 512 KiB


date_format = re.compile(br'^[0-9]{2,12}\.[0-9]{3}$')


def store(report, address):
    """Stores the report on disk.
    """
    lines = [l for l in report.split(b'\n') if l]
    for line in lines:
        if line.startswith(b'date:'):
            date = line[5:]
            if date_format.match(date):
                filename = 'report_%s.txt' % date.decode('ascii')
                filename = os.path.join(DESTINATION, filename)
                if os.path.exists(filename):
                    return "file exists"
                with open(filename, 'wb') as fp:
                    if not isinstance(address, bytes):
                        address = address.encode('ascii')
                    fp.write(b'remote_addr:' + address + b'\n')
                    fp.write(report)
                return None
            else:
                return "invalid date"
    return "missing date field"


def application(environ, start_response):
    """WSGI interface.
    """

    def send_response(status, body):
        if not isinstance(body, bytes):
            body = body.encode('utf-8')

        start_response(status, [('Content-Type', 'text/plain'),
                                ('Content-Length', '%d' % len(body))])
        return [body]

    if environ['REQUEST_METHOD'] != 'POST':
        return send_response('403 Forbidden', "invalid request")

    # Gets the posted input
    request_body = b''
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        if request_body_size < MAX_SIZE:
            request_body = environ['wsgi.input'].read(request_body_size)
    except ValueError:
        request_body = environ['wsgi.input'].read(MAX_SIZE)
        request_body_size = len(request_body)

    if request_body_size >= MAX_SIZE:
        return send_response('403 Forbidden', "report too big")

    # Tries to store
    response_body = store(request_body, environ.get('REMOTE_ADDR'))
    if not response_body:
        status = '200 OK'
        response_body = "stored"
    else:
        status = '501 Server Error'

    # Sends the response
    return send_response(status, response_body)


if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.web import server
    from twisted.web.wsgi import WSGIResource

    resource = WSGIResource(reactor, reactor.getThreadPool(), application)

    site = server.Site(resource)
    reactor.listenTCP(8000, site)
    reactor.run()
