import json
import os
import re

from .model import bytes2json


# {'AverageTime': 6,
#   'CurrentTime': 6,
#   'Description': 'M St. in Tacoma To NB I-5 @ Pierce King County Line',
#   'Distance': 5.32,
#   'EndPoint': {'Description': 'I-5 @ Pierce King County Line',
#                'Direction': 'N',
#                'Latitude': 47.255624,
#                'Longitude': -122.33113,
#                'MilePost': 139.41,
#                'RoadName': 'I-5'},
#   'Name': 'NB I-5,Tacoma To Pierce King County Line',
#   'StartPoint': {'Description': 'I-5 @ Tacoma Dome in Tacoma',
#                  'Direction': 'N',
#                  'Latitude': 47.234492,
#                  'Longitude': -122.427958,
#                  'MilePost': 134.09,
#                  'RoadName': 'I-5'},
#   'TimeUpdated': '/Date(1431113400000-0700)/',
#   'TravelTimeID': 125},

def current_traffic(json_obj):
    if isinstance(json_obj, bytes):
        json_obj = bytes2json(json_obj)
    output_list = []
    for route_info in json_obj:
        output_list.append({'id':          route_info['TravelTimeID'],
                            'description': route_info['Description'],
                            'current':     route_info['CurrentTime'],
                            'average':     route_info['AverageTime'],
                            })
    return output_list

def get_routes(json_obj):
    if isinstance(json_obj, bytes):
        json_obj = bytes2json(json_obj)
    return get_values(json_obj, 'Description')

def get_values(json_obj, key):
    if isinstance(json_obj, bytes):
        json_obj = bytes2json(json_obj)
    output_dict = {}
    for route_info in json_obj:
        output_dict[route_info['TravelTimeID']] = route_info.get(key, '')
    return output_dict

def json2csv_batch(json_dir, csv_dir):
    # exist_ok was introduced in Python3.2.
    # If we need to work with older versions, this can change to a try...except
    os.makedirs(csv_dir, exist_ok=True)
    filename_pattern = 'travel_times\.(\d{4})(\d{2})(\d{2})\.(\d{2})(\d{2})(\d{2})\.json'
    output_dict = {}
    # The timestamp is coming from the filename, so we can sort by filename to get
    # the times in the correct order
    for filename in sorted(os.listdir(json_dir)):
        matches = re.search(filename_pattern, filename)
        Y, m, d, H, M, S = matches.groups()
        datetime = '{year}-{month}-{day} {hour}:{min}:{sec}'.format(year=Y,
                                                                    month=m,
                                                                    day=d,
                                                                    hour=H,
                                                                    min=M,
                                                                    sec=S)
        filepath = '{dir}/{file}'.format(dir=json_dir, file=filename)
        with open(filepath) as f:
            # If the data being deserialized is not a valid JSON document,
            # a ValueError will be raised.
            try:
                json_out = json.load(f)
            except ValueError:
                continue
        for route_info in json_out:
            if not output_dict.get(route_info['TravelTimeID']):
                output_dict[route_info['TravelTimeID']] = []
            # We _could_ just put the output file syntax here to speed things up, but I'm
            # not sure if there will be any more processing done yet.
            output_dict[route_info['TravelTimeID']].append((datetime,
                                                            route_info['CurrentTime'],
                                                            route_info['AverageTime']))
    for route_id, route_data in output_dict.items():
        csv_file = '{dir}/route_{id}.csv'.format(dir=csv_dir, id=route_id)
        with open(csv_file, 'w') as f:
            f.write('date,value,average\n')
            for datetime, value, average in route_data:
                f.write('{datetime},{value},{avg}\n'.format(datetime=datetime,
                                                            value=value,
                                                            avg=average))


if __name__ == '__main__':
    print('#'*30)
