"""
HubGrep environment configurations.
"""
import os


class Config:
    """ Base configuration. """
    DEBUG = False
    TESTING = False
    LOGLEVEL = "debug"
    VERSION = "0.0.1"

    CRAWLER_SLEEP_NO_BLOCK = 5


class _EnvironmentConfig(Config):
    CRAWLER_USER_AGENT = f'HobGrebbit v{Config.VERSION} {os.environ.get("HUBGREP_CRAWLERS_USER_AGENT_SUFFIX")}'
    INDEXER_URL = os.environ.get("HUBGREP_INDEXER_URL")


class ProductionConfig(_EnvironmentConfig):
    """ Production Configuration. """
    DEBUG = False


class DevelopmentConfig(_EnvironmentConfig):
    """ Development configuration. """
    DEBUG = True


class BuildConfig(Config):
    """ Build configuration, in bundling and preparation for deployment. """
    TESTING = True
    DEBUG = True


class TestingConfig(Config):
    """ Test configuration, as used by tests. """
    TESTING = True
    DEBUG = True
