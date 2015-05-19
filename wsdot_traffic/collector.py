import os
import urllib.request
from time import sleep, strftime


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
    with urllib.request.urlopen(WSDOT_API_URLS['GET_TRAVEL_TIMES']) as api_call:
        content = api_call.read()
    return content

def collect_data(last_results=None, collection_dir=None):
    # latest_travel_times() is subject to external network errors
    results = latest_travel_times()
    diff = False
    if collection_dir and last_results != results:
        datetime = strftime('%Y%m%d.%H%M%S')
        diff = True
        file_name = '{dir}/travel_times.{datetime}.json'.format(dir=collection_dir,
                                                                datetime=datetime)
        with open(file_name, 'wb') as output_file:
            output_file.write(results)
    return results, diff

def run_collector(sleep_time, collection_dir):
    # exist_ok was introduced in Python3.2.
    # If we need to work with older versions, this can change to a try...except
    os.makedirs(collection_dir, exist_ok=True)
    last_results = None

    while True:
        sleep(sleep_time)
        try:
            last_results, diff = collect_data(last_results, collection_dir)
            if diff:
                # print(current_datetime, current_results)
                print("New Data!")
            else:
                print("No change")
        except urllib.error.URLError as e:
            print(e)
            continue


if __name__ == '__main__':
    print(collect_data())
