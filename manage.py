#!/usr/bin/env python3

import os
from flask.ext.script import Manager, Shell, Server
from wsdot_traffic import app, collector, parser

# Look for the config from ENV, but if it's not there, assume Production
app.config.from_object(os.environ.get('APP_SETTINGS', 'config.ProductionConfig'))

# Store the API Key in ENV
os.environ['WSDOT_ACCESS_CODE'] = app.config.get('WSDOT_ACCESS_CODE')

manager = Manager(app)
manager.add_command("runserver", Server())
manager.add_command("shell", Shell())

@manager.command
def runcollector():
    """Run the collector script.  (WS DOT)"""
    collector.run_collector(app.config.get('PERIODIC_TIMER_INTERVAL'),
                                  app.config.get('JSON_DIR'))

@manager.command
def current():
    """Collect the current traffic status.  (WS DOT)"""
    results, diff = collector.collect_data()
    route_list = parser.current_traffic(results)
    print('ID\tCurrent\tAverage\tDescription')
    for route in route_list:
        # print(route)
        print('{}\t{}\t{}\t{}'.format(route['id'], route['current'],
                                      route['average'], route['description']))

@manager.command
def batch_convert():
    parser.json2csv_batch(app.config.get('JSON_DIR'), app.config.get('CSV_DIR'))

manager.run()
