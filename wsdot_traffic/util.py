import json
import re
from datetime import datetime, timedelta

def bytes2json(bytes_in):
    return json.loads(bytes_in.decode('utf-8'))


def clean_js_timestamp(raw_js_datestring=None):
    # test_string = '/Date(1431113400000-0700)/'
    date_pattern = 'Date\((\d*)(\d{3})([-+]\d{2})00\)'
    matches = re.search(date_pattern, raw_js_datestring)
    timestamp, millisecs, tz_offset = matches.groups()
    offset = timedelta(hours=int(tz_offset))
    # print(offset)
    dt_obj = datetime.utcfromtimestamp(int(timestamp)) + offset
    return dt_obj
