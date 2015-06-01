import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    # WSDOT_ACCESS_CODE must be set to the one assigned to you by WSDOT.
    # See: http://www.wsdot.wa.gov/traffic/api/
    #
    WSDOT_ACCESS_CODE = 'ENTER_VALUE'

    # Directory to store the collected data
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    DIRECTORIES = {
        'JSON': os.path.join(DATA_DIR, 'json'),
        'WORKING': os.path.join(DATA_DIR, 'working'),
        'ARCHIVE': os.path.join(DATA_DIR, 'archive'),
        'CSV': os.path.join(DATA_DIR, 'csv'),
    }

    # Interval in seconds to call the API.
    # Wsdot states that the API refreshes every 90 seconds
    PERIODIC_TIMER_INTERVAL = 120

    PLOTLY_OPTIONS = {
        'USERNAME': 'ENTER_VALUE',
        'API_KEY': 'ENTER_VALUE',
        'DIRECTORY': 'WS DOT',
    }


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
