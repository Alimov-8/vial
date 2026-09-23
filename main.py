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
