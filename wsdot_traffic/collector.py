import logging
import os
from six.moves.urllib.request import urlopen
from six.moves.urllib import error as urllib_error
from time import sleep, strftime

from . import util


logger = logging.getLogger('wsdot_traffic.collector')

WSDOT_API_URLS = {}

def config_wsdot_api_urls(api_key=None):
    # Dynamically generate a dict for the WS DOT API URLs
    if not api_key:
        api_key = os.environ.get('WSDOT_ACCESS_CODE')
    wsdot_api_base_url = 'http://www.wsdot.wa.gov/Traffic/api'
    wsdot_api_actions = {
        'GET_TRAVEL_TIMES': 'TravelTimes/TravelTimesREST.svc/GetTravelTimesAsJson',
    }

    wsdot_url_format = '{base}/{action}?AccessCode={access_code}'
    for name, action in wsdot_api_actions.items():
        WSDOT_API_URLS[name] = wsdot_url_format.format(base=wsdot_api_base_url,
                                                       action=action,
                                                       access_code=api_key,
                                                       )

def latest_travel_times():
    if not WSDOT_API_URLS:
        config_wsdot_api_urls()
    try:
        api_call = urlopen(WSDOT_API_URLS['GET_TRAVEL_TIMES'])
        content = api_call.read()
    except urllib_error.HTTPError:
        content = None
    return content

def collect_data(last_results=None, collection_dir=None):
    # latest_travel_times() is subject to external network errors
    results = latest_travel_times()
    diff = False
    if last_results != results:
        diff = True
    if diff and collection_dir:
        datetime = strftime('%Y%m%d.%H%M%S')
        file_name = '{dir}/travel_times.{datetime}.json'.format(dir=collection_dir,
                                                                datetime=datetime)
        with open(file_name, 'wb') as output_file:
            output_file.write(results)
    return results, diff

def get_routes(url_map_filepath=None):
    # Open URL File if it's there
    url_map = {}
    if url_map_filepath and os.path.isfile(url_map_filepath):
        with open(url_map_filepath, 'r') as f:
            for line in f:
                route_id, url = line.strip().split(',')
                try:
                    url_map[int(route_id)] = url
                except ValueError:
                    pass
    results, diff = collect_data()
    output_dict = {}
    for route_info in util.bytes2json(results):
        output_dict[route_info['TravelTimeID']] = {'id':          route_info['TravelTimeID'],
                                                   'name':        route_info['Name'],
                                                   'description': route_info['Description'],
                                                   'current':     route_info['CurrentTime'],
                                                   'average':     route_info['AverageTime'],
                                                   'update_time': route_info['TimeUpdated'],
                                                   'url':         url_map.get(route_info['TravelTimeID'], ''),
                                                   }
    return output_dict

def run_collector(sleep_time, json_dir):
    # exist_ok was introduced in Python3.2.
    # If we need to work with older versions, this can change to a try...except
    os.makedirs(json_dir, exist_ok=True)
    try:
        logger.info("Locating latest file")
        newest_filepath = sorted(os.listdir(json_dir))[-1]
        with open('{dir}/{file}'.format(dir=json_dir, file=newest_filepath), mode='rb') as f:
            logger.info("Loading latest file")
            last_results = f.read()
    except IndexError:
        logger.info("No file found in JSON directory")
        last_results = None

    while True:
        try:
            logger.info("Getting current traffic data")
            last_results, diff = collect_data(last_results, json_dir)
            if diff:
                logger.debug("New Data!")
            else:
                logger.debug("No Change")
        except urllib_error.URLError as e:
            logger.error(e)
        sleep(sleep_time)

if __name__ == '__main__':
    print(collect_data())
