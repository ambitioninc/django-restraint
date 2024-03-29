"""
Provides the ability to run test on a standalone Django app.
"""
import sys
from optparse import OptionParser

import django

from settings import configure_settings


# Configure the default settings
configure_settings()
if django.VERSION[1] >= 7:
    django.setup()


# Django nose must be imported here since it depends on the settings being configured
from django_nose import NoseTestSuiteRunner


def run(*test_args, **kwargs):
    if not test_args:
        test_args = ['restraint']

    kwargs.setdefault('interactive', False)

    test_runner = NoseTestSuiteRunner(**kwargs)

    failures = test_runner.run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    (options, args) = parser.parse_args()

    run(*args, **options.__dict__)
