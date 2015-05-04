# flake8: noqa
from .version import __version__
from .core import register_restraint_config, get_restraint_config, Restraint, update_restraint_db


default_app_config = 'restraint.apps.RestraintConfig'
