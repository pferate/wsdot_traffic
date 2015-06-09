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
    results, diff = collector.collect_data()
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

def run_publisher(plotly_options, sleep_time, json_dir, working_dir, archive_dir, url_map_csv):
    while True:
        print("{}\tChecking for ready files.".format(datetime.now()))
        # Most (all?) exceptions should be handled within the function,
        # so no need to duplicate it out here.
        publish_ready_files(plotly_options, json_dir, working_dir, archive_dir, url_map_csv)
        print("{}\tDone.".format(datetime.now()))
        sleep(sleep_time)

def publish_ready_files(plotly_options, json_dir, working_dir, archive_dir, url_map_csv):
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
        url_map = publish_routes(plotly_options, plotly_data)

        # Create URL File if not there
        if not os.path.isfile(url_map_csv):
            with open(url_map_csv, 'w') as f:
                f.write('route_id,url\n')
                for route_id, url in url_map.items():
                    f.write('{},{}\n'.format(route_id, url))


        # Move JSON files to the Archive Directory
        for filename in os.listdir(working_dir):
            in_file = '{dir}/{file}'.format(dir=working_dir, file=filename)
            out_file = '{dir}/{file}'.format(dir=archive_dir, file=filename)
            os.rename(in_file, out_file)
    except plotly_exceptions.PlotlyAccountError as error:
        print('An error occured while publishing: [{}]'.format(error))
    except requests_exceptions.HTTPError as error:
        print('There was a HTTP Error: [{}]'.format(error))
    except requests_exceptions.ConnectionError as error:
        print('There was a Connection Error: [{}]'.format(error))

def publish_routes(plotly_options, plotly_routes):
    if not plotly_routes:
        print('No routes to plot')
        return
    plotly.sign_in(plotly_options['USERNAME'], plotly_options['API_KEY'])

    widgets = ['Sending data to Plotly: ', pb.Percentage(), ' ', pb.Bar(marker=pb.RotatingMarker()),
               ' ', pb.ETA(), ' ', pb.FileTransferSpeed()]
    progress = pb.ProgressBar(widgets=widgets)
    url_map = {}
    retry_count = 5
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
        attempt_count = 0
        while True:
            try:
                plot_url = plotly.plot(fig, filename=plotly_filename, fileopt='extend',
                                       world_readable=True, auto_open=False)
                url_map[route_id] = plot_url
                break
            except plotly_exceptions.PlotlyAccountError as error:
                if attempt_count < retry_count:
                    attempt_count += 1
                    print('An error occured while publishing: [{}]'.format(error))
                    for i in range(10):
                        print('.', end='')
                        sleep(1)
                    print('\tRetrying')
                else:
                    # Ran out of attempts, raise the error up a level
                    raise error

    return url_map
