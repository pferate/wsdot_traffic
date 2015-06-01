import json
import os
import urllib.request
from datetime import datetime
from time import sleep
from requests import exceptions as requests_exceptions

import progressbar as pb

from plotly import plotly, exceptions as plotly_exceptions
from plotly.graph_objs import Data, Layout, Scatter, XAxis, YAxis, Font, Figure

from . import collector, parser, util


def get_routes():
    results, diff = collector.collect_data()
    output_dict = {}
    for route_info in util.bytes2json(results):
        output_dict[route_info['TravelTimeID']] = {'id':          route_info['TravelTimeID'],
                                                   'name':        route_info['Name'],
                                                   'description': route_info['Description'],
                                                   'current':     route_info['CurrentTime'],
                                                   'average':     route_info['AverageTime'],
                                                   'update_time': route_info['TimeUpdated'],
                                                   }
    return output_dict

def run_collector(sleep_time, json_dir):
    # exist_ok was introduced in Python3.2.
    # If we need to work with older versions, this can change to a try...except
    os.makedirs(json_dir, exist_ok=True)
    try:
        newest_filepath = sorted(os.listdir(json_dir))[-1]
        with open('{dir}/{file}'.format(dir=json_dir, file=newest_filepath), mode='rb') as f:
            last_results = f.read()
    except IndexError:
        last_results = None

    while True:
        try:
            last_results, diff = collector.collect_data(last_results, json_dir)
            if diff:
                print("{}\tNew Data!".format(datetime.now()))
            else:
                print("{}\tNo change".format(datetime.now()))
        except urllib.error.URLError as e:
            print(e)
        sleep(sleep_time)

def run_publisher(plotly_options, sleep_time, json_dir, working_dir, archive_dir):
    while True:
        print("{}\tChecking for ready files.".format(datetime.now()))
        # Most (all?) exceptions should be handled within the function,
        # so no need to duplicate it out here.
        publish_ready_files(plotly_options, json_dir, working_dir, archive_dir)
        print("{}\tDone.".format(datetime.now()))
        sleep(sleep_time)

def publish_ready_files(plotly_options, json_dir, working_dir, archive_dir):
    # exist_ok was introduced in Python3.2.
    # If we need to work with older versions, this can change to a try...except
    os.makedirs(working_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Move JSON files to the Working Directory
    for filename in os.listdir(json_dir):
        in_file = '{dir}/{file}'.format(dir=json_dir, file=filename)
        out_file = '{dir}/{file}'.format(dir=working_dir, file=filename)
        os.rename(in_file, out_file)

    # Process the files
    plotly_data = None

    widgets = ['Parsing JSON files: ', pb.Counter(), ' ', pb.Bar()]
    progress = pb.ProgressBar(widgets=widgets)
    for filename in progress(sorted(os.listdir(working_dir))):
        filepath = '{dir}/{file}'.format(dir=working_dir, file=filename)
        with open(filepath) as f:
            # If the data being deserialized is not a valid JSON document,
            # a ValueError will be raised.
            try:
                json_out = json.load(f)
            except ValueError:
                print('Unable to load JSON (Skipping)')
                continue
        plotly_data = parser.json2plotly(json_out, plotly_data)
    try:
        publish_route(plotly_options, plotly_data)

        # Move JSON files to the Archive Directory
        for filename in os.listdir(working_dir):
            in_file = '{dir}/{file}'.format(dir=working_dir, file=filename)
            out_file = '{dir}/{file}'.format(dir=archive_dir, file=filename)
            os.rename(in_file, out_file)
    except plotly_exceptions.PlotlyAccountError as error:
        print('An error occured while publishing: [{}]'.format(error))
    except requests_exceptions.HTTPError as error:
        print('There was a HTTP Error: [{}]'.format(error))

def publish_route(plotly_options, plotly_routes):
    if not plotly_routes:
        print('No routes to plot')
        return
    plotly.sign_in(plotly_options['USERNAME'], plotly_options['API_KEY'])

    widgets = ['Sending data to Plotly: ', pb.Percentage(), ' ', pb.Bar(marker=pb.RotatingMarker()),
               ' ', pb.ETA(), ' ', pb.FileTransferSpeed()]
    progress = pb.ProgressBar(widgets=widgets)
    for route_id, route_data in progress(plotly_routes.items()):
        plotly_filename = '{dir}/route_{plot_id}'.format(dir=plotly_options['DIRECTORY'],
                                                         plot_id=route_data['id'])
        trace0 = Scatter(
            x=route_data['timestamp'],
            y=route_data['average'],
            name='Average Time',
        )

        trace1 = Scatter(
            x=route_data['timestamp'],
            y=route_data['time'],
            name='Current Time'
        )

        data = Data([trace0, trace1])

        layout = Layout(
            title=route_data['name'],
            xaxis=XAxis(
                # title='Date and Time',
                title='',
                titlefont=Font(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=YAxis(
                title='Travel Time (minutes)',
                titlefont=Font(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
        fig = Figure(data=data, layout=layout)
        # print(route_data['name'])
        # Take 1: if there is no data in the plot, 'extend' will create new traces.
        plot_url = plotly.plot(fig, filename=plotly_filename, fileopt='extend', world_readable=True, auto_open=False)
        # plot_url = plotly.plot(fig, filename=plotly_filename, world_readable=True, auto_open=False)
