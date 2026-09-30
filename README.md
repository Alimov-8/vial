# Vial

[![PyPI](https://img.shields.io/pypi/v/vialframe)](https://pypi.org/project/vialframe/)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Vial is a small [WSGI](https://peps.python.org/pep-3333/) web framework. It is meant to be quick to start with, and small enough that you can read the framework when you want to know exactly what it does.

It does not pick your database, your project layout, or your server yet. You write handlers, Vial routes the request, and any WSGI server runs the app.

**PyPI:** [https://pypi.org/project/vialframe/](https://pypi.org/project/vialframe/)

**Source:** [https://github.com/Alimov-8/vial](https://github.com/Alimov-8/vial)

![How a request reaches Vial](https://raw.githubusercontent.com/Alimov-8/vial/main/img.png)

A web server accepts the HTTP request. A WSGI server calls your Vial app. Vial matches a route, runs the handler, and returns the response.

## Requirements

Python 3.13.2 or newer.

Vial stands on a few libraries:

* [WebOb](https://webob.org/) for the request.
* [parse](https://pypi.org/project/parse/) for path parameters.
* [Jinja2](https://jinja.palletsprojects.com/) for templates.
* [WhiteNoise](https://whitenoise.readthedocs.io/) for static files.

## Installation

```console
$ pip install vialframe
```

The package name on PyPI is `vialframe`. You import it as `vial`.

## Example

### Create it

Create a file `app.py`:

```python
from vial.app import Vial

app = Vial()

@app.route("/")
def index(request, response):
    response.text = "Hello, Vial"

@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"

@app.route("/json")
def json_handler(request, response):
    response.json = {"framework": "vial"}
```

### Run it

Create a file `run.py` next to it:

```python
from wsgiref.simple_server import make_server

from app import app

with make_server("127.0.0.1", 8000, app) as server:
    print("Serving on http://127.0.0.1:8000")
    server.serve_forever()
```

```console
$ python run.py
Serving on http://127.0.0.1:8000
```

For anything beyond a local check, use a production WSGI server:

```console
$ pip install gunicorn
$ gunicorn app:app
```

### Check it

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The response body is:

```text
Hello, Vial
```

Open [http://127.0.0.1:8000/hello/Ada](http://127.0.0.1:8000/hello/Ada):

```text
Hello, Ada
```

Open [http://127.0.0.1:8000/json](http://127.0.0.1:8000/json):

```json
{"framework": "vial"}
```

You already have an app that:

* Serves `GET /` with a plain-text body.
* Reads a path parameter from `/hello/{name}`.
* Returns JSON, with `Content-Type: application/json`.

An unknown path returns **404** and the body `Not Found.`

## Routing

Every handler takes `request` and `response`. Path parameters are extra arguments.

The decorator and `add_route` do the same thing:

```python
@app.route("/about")
def about(request, response):
    response.text = "About"

def new_page(request, response):
    response.text = "New page"

app.add_route("/new-page", new_page)
```

Registering the same path twice raises `AssertionError`.

### Class-based handlers

One class owns one URL. The method name is the HTTP verb. A verb you did not define returns **405** `Method Not Allowed`.

```python
@app.route("/books")
class Books:
    def get(self, request, response):
        response.text = "Read books"

    def post(self, request, response):
        response.text = "Create a book"
```

### Allowed methods

A function handler accepts every method unless you list the ones you want:

```python
@app.route("/home", allowed_methods=["get"])
def home(request, response):
    response.text = "Hello"
```

`POST /home` then returns **405**.

## Request and response

`request` is a WebOb request. `request.method`, `request.path`, `request.url`, `request.GET`, `request.POST`, and `request.body` are the ones you will use most. The rest is in the [WebOb request reference](https://docs.pylonsproject.org/projects/webob/en/stable/reference.html#request).

Set one attribute on `response`. Vial fills in the body and `Content-Type`.

| You set | Content-Type | Example |
| --- | --- | --- |
| `response.text` | `text/plain` | `response.text = "Hello"` |
| `response.html` | `text/html` | `response.html = "<h1>Hello</h1>"` |
| `response.json` | `application/json` | `response.json = {"ok": True}` |

`response.status_code` defaults to `200`.

## Templates

Put Jinja2 templates in a `templates/` directory and run the server from the project root. `app.template` renders one and you assign it to `response.html`.

`templates/home.html`:

```html
<h1>{{ title }}</h1>
<p>{{ body }}</p>
```

```python
@app.route("/page")
def page(request, response):
    response.html = app.template(
        "home.html",
        context={"title": "Vial", "body": "Hello"},
    )
```

Pass another folder when you construct the app: `Vial(templates_dir="theme")`.

## Static files

Files in `static/` are served from the site root. `static/styles.css` is available at `/styles.css`.

```python
app = Vial(static_dir="assets")
```

## Exceptions

With no handler, an exception propagates to the WSGI server. Add one and Vial calls it instead:

```python
def on_exception(request, response, exception):
    response.status_code = 500
    response.text = "Something went wrong"

app.add_exception_handler(on_exception)
```

## Middleware

Subclass `Middleware` and override `process_request` and `process_response`. Call `super().__init__(app)`.

The last middleware you add runs first on the way in and last on the way out.

```python
from vial.middleware import Middleware

class LoggingMiddleware(Middleware):
    def process_request(self, request):
        print("request", request.url)

    def process_response(self, request, response):
        print("response", request.url)

app.add_middleware(LoggingMiddleware)
```

## Testing

`app.test_session()` returns a Requests session bound to the app. No server, no port.

```python
from vial.app import Vial

def test_home():
    app = Vial()

    @app.route("/home")
    def home(request, response):
        response.text = "Home"

    client = app.test_session()
    response = client.get("http://testserver/home")

    assert response.status_code == 200
    assert response.text == "Home"
```

Use any host under `http://testserver`. That prefix is what the session is mounted on.

## Development

Clone the repo if you want to change Vial itself:

```console
$ git clone https://github.com/Alimov-8/vial.git
$ cd vial
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -e .
$ pip install -r requirements.txt
$ pytest
$ pytest --cov=vial
```

`main.py` is a sample app that uses the features above. `pip install -e .` installs that checkout, so imports use your local code.

## License

MIT. See [LICENSE](LICENSE).
