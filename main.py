from app import Vial


app = Vial()


@app.route("/home")
def home(request, response):
    response.text = "Hello from Home page"

@app.route("/about")
def about(request, response):
    response.text = "Hello from About page"

@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello {name}"

@app.route("/books")
class Books:
    def get(self, request, response):
        response.text = "Read Books"

    def post(self, request, response):
        response.text = "Create Books"


def new_page(request, response):
    response.text = f"New Page"

app.add_route("/new-page", new_page)


@app.route("/new-template")
def new_template(request, response):
    response.body = app.template(
        template_name="home.html",
        context={"title": "Title", "body": "Body"},
    )


def on_exception(request, response, exception):
    # TODO: Make better exception handling
    response.text = str(exception)

app.add_exception_handler(on_exception)


@app.route("/exception")
def exception_throwing_handler(request, response):
    raise AttributeError("Raised AttributeError Exception")
