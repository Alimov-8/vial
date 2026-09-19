from wsgiref import simple_server


def app(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "text/plain")]
    start_response(status, headers)
    return [b"Hello World"]

server = simple_server.make_server("localhost", 8000, app)
server.serve_forever()
