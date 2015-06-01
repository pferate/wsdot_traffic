import os
import urllib.request
from time import strftime


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
    if last_results != results:
        diff = True
    if diff and collection_dir:
        datetime = strftime('%Y%m%d.%H%M%S')
        file_name = '{dir}/travel_times.{datetime}.json'.format(dir=collection_dir,
                                                                datetime=datetime)
        with open(file_name, 'wb') as output_file:
            output_file.write(results)
    return results, diff


if __name__ == '__main__':
    print(collect_data())
