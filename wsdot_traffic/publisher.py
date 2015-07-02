import json
import logging
import os
from time import sleep
from requests import exceptions as requests_exceptions

import progressbar as pb

from plotly import plotly, exceptions as plotly_exceptions
from plotly.graph_objs import Data, Layout, Scatter, XAxis, YAxis, Font, Figure

from .parser import json2plotly

logger = logging.getLogger('wsdot_traffic.publisher')


def run_publisher(plotly_options, sleep_time, json_dir, working_dir, archive_dir, url_map_csv):
    while True:
        logger.info("Checking for ready files.")
        # Most (all?) exceptions should be handled within the function,
        # so no need to duplicate it out here.
        publish_ready_files(plotly_options, json_dir, working_dir, archive_dir, url_map_csv)
        logger.info("Finished publishing files.")
        sleep(sleep_time)

def publish_ready_files(plotly_options, json_dir, working_dir, archive_dir, url_map_csv):
    # exist_ok was introduced in Python3.2.
    # If we need to work with older versions, this can change to a try...except
    os.makedirs(working_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Move JSON files to the Working Directory
    logger.debug("Moving ready files to the Working directory.")
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
                logger.warning('Unable to load JSON (Skipping) [{}]'.format(filename))
                continue
        plotly_data = json2plotly(json_out, plotly_data)
    try:
        logger.debug("Publishing routes")
        url_map = publish_routes(plotly_options, plotly_data)

        # Create URL File if not there
        if not os.path.isfile(url_map_csv):
            logger.info("Creating new CSV map")
            with open(url_map_csv, 'w') as f:
                f.write('route_id,url\n')
                for route_id, url in url_map.items():
                    f.write('{},{}\n'.format(route_id, url))


        # Move JSON files to the Archive Directory
        logger.debug("Moving finished files to the Archive directory.")
        for filename in os.listdir(working_dir):
            in_file = '{dir}/{file}'.format(dir=working_dir, file=filename)
            out_file = '{dir}/{file}'.format(dir=archive_dir, file=filename)
            os.rename(in_file, out_file)
    except plotly_exceptions.PlotlyAccountError as error:
        logger.error('An error occured while publishing: [{}]'.format(error))
    except requests_exceptions.HTTPError as error:
        logger.error('There was a HTTP Error: [{}]'.format(error))
    except requests_exceptions.ConnectionError as error:
        logger.error('There was a Connection Error: [{}]'.format(error))
    logger.debug("Finished publishing ready files.")

def publish_routes(plotly_options, plotly_routes):
    if not plotly_routes:
        logger.warning('No routes to plot')
        return
    plotly.sign_in(plotly_options['USERNAME'], plotly_options['API_KEY'])

    widgets = ['Sending data to Plotly: ', pb.Percentage(), ' ', pb.Bar(marker=pb.RotatingMarker()),
               ' ', pb.ETA(), ' ', pb.FileTransferSpeed()]
    progress = pb.ProgressBar(widgets=widgets)
    url_map = {}
    retry_count = 5
    route_count = len(plotly_routes.items())
    route_index = 0
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
        route_index += 1
        while True:
            try:
                logger.debug("Updating route [{}] ({}/{})".format(route_id, route_index, route_count))
                plot_url = plotly.plot(fig, filename=plotly_filename, fileopt='extend',
                                       world_readable=True, auto_open=False)
                url_map[route_id] = plot_url
                break
            except plotly_exceptions.PlotlyAccountError as error:
                if attempt_count < retry_count:
                    attempt_count += 1
                    logger.error('An error occured while publishing: [{}]'.format(error))
                    sleep(10)
                    # for i in range(10):
                    #     print('.', end='')
                    #     sleep(1)
                    # logger.error('\tRetrying')
                else:
                    # Ran out of attempts, raise the error up a level
                    logger.error('Publishing route [{}] failed {} times, skipping it.'.format(route_id, retry_count))
                    raise error

    return url_map
