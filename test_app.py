from logging import raiseExceptions

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


def test_template_handler(app, test_client):
    @app.route("/test-template")
    def test_template(request, response):
        response.body = app.template(
            template_name="test.html",
            context={"title": "Test Title", "body": "Test Body"},
        )

    response = test_client.get("http://testserver/test-template")
    assert "Test Title" in response.text
    assert "Test Body" in response.text
    assert "text/html" in response.headers["Content-Type"]


def test_with_custom_exception_handler(app, test_client):
    def on_exception(request, response, exception):
        response.text = "Something bad happened"

    app.add_exception_handler(on_exception)

    @app.route("/exception")
    def exception_throwing_handler(request, response):
        raise AttributeError()

    response = test_client.get("http://testserver/exception")
    assert response.text == "Something bad happened"

def test_with_no_exception_handler(app, test_client):
    with pytest.raises(AttributeError):
        @app.route("/exception")
        def exception_throwing_handler(request, response):
            raise AttributeError()

        test_client.get("http://testserver/exception")

def test_non_existent_static_file(test_client):
    assert test_client.get("http://testserver/nonexistent.css").status_code == 404

def test_serving_static_file(test_client):
    response = test_client.get("http://testserver/test.css")
    print(response)
    assert response.text == "body { background-color: chocolate; }"
