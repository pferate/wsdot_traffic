from flask import Flask, render_template

from .model import get_routes
from .util import clean_js_timestamp

app = Flask(__name__)


@app.route('/')
def route_table():
    route_dict = get_routes(url_map_filepath=app.config.get('URL_MAP_CSV'))
    for values in route_dict.values():
        values['update_time'] = clean_js_timestamp(values['update_time'])
    return render_template('route_table.html', routes=route_dict)

@app.route('/static')
def route_table_static():
    route_dict = get_routes(url_map_filepath=app.config.get('URL_MAP_CSV'))
    for values in route_dict.values():
        values['update_time'] = clean_js_timestamp(values['update_time'])
    return render_template('route_table_static.html', routes=route_dict)


if __name__ == '__main__':
    app.run()
