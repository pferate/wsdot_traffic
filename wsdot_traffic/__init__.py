from flask import Flask, render_template

from .model import get_routes
from .util import clean_js_timestamp

app = Flask(__name__)


@app.route('/')
def hello_world():
    route_dict = get_routes()
    for values in route_dict.values():
        values['update_time'] = clean_js_timestamp(values['update_time'])
    return render_template('route_table.html', routes=route_dict)


if __name__ == '__main__':
    app.run()
