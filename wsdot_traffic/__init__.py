from flask import Flask, render_template

from .model import get_routes

app = Flask(__name__)


@app.route('/')
def hello_world():
    route_list = get_routes(sort_key='id')
    return render_template('route_table.html', routes=route_list)


if __name__ == '__main__':
    app.run()
