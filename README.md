#WS DOT Traffic Times

Real-time traffic times for various routes are provided by Washington State Department of Transportation (WS DOT).  That information is collected, parsed and then sent to [plotly](https://plot.ly).

> **Warning: I don't know what I want to be when I grow up**

This project is still in development and will probably change drastically in the future.

I'm still figuring out the best way run the application and present the data to the end user.  Right now, the code runs on a local machine; collecting and storing data from WS DOT and then uploading the data to Plotly for presentation, using the `runcollector` and `runpublisher` commands in separate shells.  I'm thinking of migrating to a hosted/cloud solution, but haven't made any concrete decisions yet.  Google App Engine looks like it may be worth looking into, but then I'll have to port the code to Python2.7 (shouldn't be too difficult) or run it in a virtual machine.

I would like to find a good, free (or reasonably priced) environment to run the applications and store the data.  It is not a resource hungry application and can probably deal with some small delay spinning up instances.

This project is written in Python 3 and uses [Flask](http://flask.pocoo.org/) for a web framework and command-line manager.

##Usage
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


##Requirements
###WS DOT Access Code (API Key)
For collecting data, you will need to get an Access Code (API Key) from WS DOT.

For more information about the WS DOT API and to request an Access Code (API KEY) go the the [Traveler Information API page](http://www.wsdot.wa.gov/traffic/api/).

###Plotly Account and API Key
For publishing data to Plotly, you will need to create an account and get your associated API Key.

###Python Requirements
During development, Python 3.4 was used.  In the future, I plan on testing it with multiple versions (at least 2.7, for use in App Engine).

The following packages (and their dependancies) are needed to run this code in full.

* Flask
* Flask-LogConfig
* Flask-Script
* plotly
* progressbar33

##To-Do List
* Decide on a license
* Tests (!!!)
    * nose tests
    * tox
    * continuous integration (Travis)
    * coverage (Coveralls)
* Local graph views (D3 maybe?) 
    * Need to get data storage solution first
* App Engine Package
    * 2.7 Compatability
