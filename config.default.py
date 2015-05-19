import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    # WSDOT_ACCESS_CODE must be set to the one assigned to you by WSDOT.
    # See: http://www.wsdot.wa.gov/traffic/api/
    #
    # WSDOT_ACCESS_CODE = 'ENTER_YOUR_ACCESS_CODE'

    # Directory to store the collected data
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    JSON_DIR = os.path.join(DgATA_DIR, 'json')
    CSV_DIR = os.path.join(DATA_DIR, 'csv')

    # Interval in seconds to call the API.
    # Wsdot states that the API refreshes every 90 seconds
    PERIODIC_TIMER_INTERVAL = 60


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
