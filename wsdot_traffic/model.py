import json
from operator import itemgetter

from . import collector

def bytes2json(bytes_in):
    return json.loads(bytes_in.decode('utf-8'))

def get_routes(sort_key=False, reverse=False):
    results, diff = collector.collect_data()
    output_list = []
    for route_info in bytes2json(results):
        output_list.append({'id':          route_info['TravelTimeID'],
                            'description': route_info['Description'],
                            'current':     route_info['CurrentTime'],
                            'average':     route_info['AverageTime'],
                            })
    if sort_key:
        try:
            output_list = sorted(output_list, key=itemgetter(sort_key), reverse=reverse)
        except KeyError:
            pass
    return output_list
