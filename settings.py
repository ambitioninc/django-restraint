import os
import json

from django.conf import settings


def configure_settings():
    """
    Configures settings for manage.py and for run_tests.py.
    """
    if not settings.configured:
        # Determine the database settings depending on if a test_db var is set in CI mode or not
        test_db = os.environ.get('DB', None)
        if test_db is None:
            db_config = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'django_restraint',
                'USER': os.environ.get('DBUSER', 'ambition_dev'),
                'PASSWORD': os.environ.get('DBPASS', 'ambition_dev'),
                'HOST': os.environ.get('DBHOST', 'localhost')
            }
        elif test_db == 'postgres':
            db_config = {
                'ENGINE': 'django.db.backends.postgresql',
                'USER': 'postgres',
                'NAME': 'restraint',
            }
        elif test_db == 'sqlite':
            db_config = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'restraint',
            }
        else:
            raise RuntimeError('Unsupported test DB {0}'.format(test_db))

        # Check env for db override (used for github actions)
        if os.environ.get('DB_SETTINGS'):
            db_config = json.loads(os.environ.get('DB_SETTINGS'))

        settings.configure(
            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
            NOSE_ARGS=['--nocapture', '--nologcapture', '--verbosity=1'],
            MIDDLEWARE_CLASSES=(),
            DATABASES={
                'default': db_config,
            },
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'restraint',
                'restraint.tests',
            ),
            ROOT_URLCONF='restraint.urls',
            DEBUG=False,
            SECRET_KEY='12345',
            DEFAULT_AUTO_FIELD='django.db.models.AutoField',
            RESTRAINT_CONFIGURATION=(
                'restraint.tests.configuration.get_configuration'
            )
        )
