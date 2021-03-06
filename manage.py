#!/usr/bin/env python3

import logging
import os
import sys
from flask import Flask
from flask.ext.logconfig import LogConfig
from flask.ext.script import Manager, Shell, Server

from wsdot_traffic import collector, parser
from wsdot_traffic.collector import run_collector
from wsdot_traffic.publisher import run_publisher, publish_ready_files


app = Flask(__name__)

# Look for the config from ENV, but if it's not there, assume Production
app.config.from_object(os.environ.get('APP_SETTINGS', 'config.ProductionConfig'))

logcfg = LogConfig(app)

logger = logging.getLogger('wsdot_traffic')

def check_configuration():
    missing_entries = False
    required_entries = [
        "['PLOTLY_OPTIONS']['USERNAME']",
        "['PLOTLY_OPTIONS']['API_KEY']",
        "['WSDOT_ACCESS_CODE']",
    ]
    for entry in required_entries:
        try:
            if eval('app.config'+entry) == 'ENTER_VALUE':
                raise KeyError()
        except KeyError:
            logger.critical('Config Value: [{}] needs to be defined'.format(entry))
            missing_entries = True
    return not missing_entries

if not check_configuration():
    sys.exit(1)

# Store the API Key in ENV
os.environ['WSDOT_ACCESS_CODE'] = app.config.get('WSDOT_ACCESS_CODE')

manager = Manager(app)
manager.add_command("runserver", Server())
manager.add_command("shell", Shell())

@manager.command
def runcollector():
    """Run the collector script.  (WS DOT)"""
    logger.info('Starting Periodic Collector')
    run_collector(app.config.get('PERIODIC_TIMER_INTERVAL'),
                  app.config.get('DIRECTORIES').get('JSON'))

@manager.command
def runpublisher():
    """Publish ready (collected) files to Plotly periodically"""
    logger.info('Starting Periodic Publisher')
    run_publisher(app.config.get('PLOTLY_OPTIONS'),
                  10 * app.config.get('PERIODIC_TIMER_INTERVAL'),
                  app.config.get('DIRECTORIES').get('JSON'),
                  app.config.get('DIRECTORIES').get('WORKING'),
                  app.config.get('DIRECTORIES').get('ARCHIVE'),
                  app.config.get('URL_MAP_CSV'))

@manager.command
def publish():
    """Publish ready (collected) files to Plotly"""
    logger.info('Starting One-time Publisher')
    publish_ready_files(app.config.get('PLOTLY_OPTIONS'),
                        app.config.get('DIRECTORIES').get('JSON'),
                        app.config.get('DIRECTORIES').get('WORKING'),
                        app.config.get('DIRECTORIES').get('ARCHIVE'),
                        app.config.get('URL_MAP_CSV'))

@manager.command
def current():
    """Collect the current traffic status.  (WS DOT)"""
    logger.info('Getting Current traffic status')
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
