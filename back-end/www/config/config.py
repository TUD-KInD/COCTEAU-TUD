import os
from pathlib import Path
from os.path import abspath, join, dirname


secret_dir = abspath(join(dirname( __file__ ), "..", "..", "secret"))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = Path(join(secret_dir, "db_url_staging")).read_text().strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UNSPLASH_ACCESS_KEY = Path(join(secret_dir, "unsplash_access_key_staging")).read_text().strip()
    GOOGLE_SIGNIN_CLIENT_ID = Path(join(secret_dir, "google_signin_client_id_staging")).read_text().strip()
    JWT_PRIVATE_KEY = Path(join(secret_dir, "private_key")).read_text().strip()


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = Path(join(secret_dir, "db_url_production")).read_text().strip()
    UNSPLASH_ACCESS_KEY = Path(join(secret_dir, "unsplash_access_key_production")).read_text().strip()
    GOOGLE_SIGNIN_CLIENT_ID = Path(join(secret_dir, "google_signin_client_id_production")).read_text().strip()


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = Path(join(secret_dir, "db_url_testing")).read_text().strip()


# Select the active configuration via the APP_CONFIG environment variable.
# Defaults to "staging" to preserve the previous local development behavior.
# The Docker deployment sets APP_CONFIG=production.
_config_by_name = {
    "production": ProductionConfig,
    "staging": StagingConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
_active_config = os.environ.get("APP_CONFIG", "staging").strip().lower()
config = _config_by_name.get(_active_config, StagingConfig)()
