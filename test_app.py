import pytest

from conftest import app, test_client


def test_basic_route_adding(app):
    @app.route("/home")
    def home(request, response):
        response.text = "Home Page"


def test_duplicate_route_throws_exception(app):
    @app.route("/home")
    def home(request, response):
        response.text = "Home Page"

    with pytest.raises(AssertionError):
        @app.route("/home")
        def home_page(request, response):
            response.text = "Home Page"

def test_requests_can_be_sent_test_client(app, test_client):
    @app.route("/home")
    def home(request, response):
        response.text = "Home Page"

    response = test_client.get("http://testserver/home")
    assert response.text == "Home Page"


def test_parametrized_routing(app, test_client):
    @app.route("/hello/{name}")
    def greeting(request, response, name):
        response.text = f"Hello {name}"

    assert test_client.get("http://testserver/hello/Vial").text == "Hello Vial"
    assert test_client.get("http://testserver/hello/framework").text == "Hello framework"


def test_default_response(test_client):
    response = test_client.get("http://testserver/test")
    assert response.text == "Not Found."
    assert response.status_code == 404


def test_class_based_get(app, test_client):
    @app.route("/books")
    class Books:
        def get(self, request, response):
            response.text = "Read Books"

    response = test_client.get("http://testserver/books")
    assert response.text == "Read Books"


def test_class_based_post(app, test_client):
    @app.route("/books")
    class Books:
        def post(self, request, response):
            response.text = "Create Books"

    response = test_client.post("http://testserver/books")
    assert response.text == "Create Books"


def test_class_based_method_not_allowed(app, test_client):
    @app.route("/books")
    class Books:
        def post(self, request, response):
            response.text = "Create Books"

    response = test_client.get("http://testserver/books")
    assert response.text == "Method Not Allowed"
    assert response.status_code == 405


def test_alternative_route_adding(app, test_client):
    def home(request, response):
        response.text = "Home Page"

    app.add_route("/home", home)

    response = test_client.get("http://testserver/home")
    assert response.text == "Home Page"
