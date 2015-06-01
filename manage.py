#!/usr/bin/env python3

import os
from flask.ext.script import Manager, Shell, Server
from wsdot_traffic import app, collector, parser
from wsdot_traffic.model import run_collector, run_publisher, publish_ready_files

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
    run_collector(app.config.get('PERIODIC_TIMER_INTERVAL'),
                  app.config.get('DIRECTORIES').get('JSON'))

@manager.command
def runpublisher():
    """Publish ready (collected) files to Plotly periodically"""
    run_publisher(app.config.get('PLOTLY_OPTIONS'),
                  10 * app.config.get('PERIODIC_TIMER_INTERVAL'),
                  app.config.get('DIRECTORIES').get('JSON'),
                  app.config.get('DIRECTORIES').get('WORKING'),
                  app.config.get('DIRECTORIES').get('ARCHIVE'))

@manager.command
def publish():
    """Publish ready (collected) files to Plotly"""
    publish_ready_files(app.config.get('PLOTLY_OPTIONS'),
                        app.config.get('DIRECTORIES').get('JSON'),
                        app.config.get('DIRECTORIES').get('WORKING'),
                        app.config.get('DIRECTORIES').get('ARCHIVE'))

@manager.command
def current():
    """Collect the current traffic status.  (WS DOT)"""
    results, diff = collector.collect_data()
    route_list = parser.current_traffic(results)
    print('ID\tCurrent\tAverage\tName')
    for route in route_list:
        # print(route)
        print('{}\t{}\t{}\t{}'.format(route['id'], route['current'],
                                      route['average'], route['name']))

@manager.command
def json2csv_batch():
    parser.json2csv_batch(app.config.get('DIRECTORIES').get('JSON'),
                          app.config.get('DIRECTORIES').get('CSV'))

manager.run()
