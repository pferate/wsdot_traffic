#WS DOT Traffic Times

Real-time traffic times for various routes are provided by Washington State Department of Transportation (WS DOT).  That information is collected, parsed and then sent to [plotly](https://plot.ly).

This project is written in Python 3 and uses [Flask](http://flask.pocoo.org/) for a web framework and command-line manager.
  
The command-line tool has the following usage:

<pre>
usage: manage.py {publish,runpublisher,current,shell,runcollector,runserver}

positional arguments:
  {publish,runpublisher,current,shell,runcollector,runserver}
    publish             Publish ready (collected) files to Plotly
    runpublisher        Publish ready (collected) files to Plotly periodically
    current             Collect the current traffic status. (WS DOT)
    shell               Runs a Python shell inside Flask application context.
    runcollector        Run the collector script. (WS DOT)
    runserver           Runs the Flask development server i.e. app.run()
</pre>

For more information about the WS DOT API and to request an Access Code (API KEY) go the the [Traveler Information API page](http://www.wsdot.wa.gov/traffic/api/).

