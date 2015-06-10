import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    # WSDOT_ACCESS_CODE must be set to the one assigned to you by WSDOT.
    # See: http://www.wsdot.wa.gov/traffic/api/
    #
    WSDOT_ACCESS_CODE = 'ENTER_VALUE'

    BASE_DIR = os.path.dirname(__file__)
    # Directory to store the collected data
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    DIRECTORIES = {
        'LOG': os.path.join(BASE_DIR, 'log'),
        'JSON': os.path.join(DATA_DIR, 'json'),
        'WORKING': os.path.join(DATA_DIR, 'working'),
        'ARCHIVE': os.path.join(DATA_DIR, 'archive'),
        'CSV': os.path.join(DATA_DIR, 'csv'),
    }
    URL_MAP_CSV = os.path.join(DATA_DIR, 'url_map.csv')

    # Make Log directory
    os.makedirs(DIRECTORIES['LOG'], exist_ok=True)

    LOGCONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s   %(name)-15s %(module)-10s %(funcName)-20s %(levelname)-10s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'formatter':'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'log', 'wsdot_traffic.log'),
                'encoding': 'utf-8',
                'maxBytes': 5*1024*1024,
                'backupCount': 5
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
                'formatter':'default',
                'stream': 'ext://sys.stderr',
            },
        },
        'loggers': {
            'wsdot_traffic': {
                'handlers': ['file', 'console'],
                # 'level': 'CRITICAL',
                # 'level': 'ERROR',
                # 'level': 'WARNING',
                'level': 'INFO',
                # 'level': 'DEBUG',
            }
        }
    }

    LOGCONFIG_QUEUE = ['wsdot_traffic']

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
