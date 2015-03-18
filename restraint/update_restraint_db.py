"""
Functions for updating the restraing configuration in the database.
"""
from restraint.models import PermSet
from restraint.core import get_restraint_config

from manager_utils import sync


def update_restraint_db():
    update_perm_sets()


def update_perm_sets():
    """
    Updates PermSet models in the DB based on the restraint config.
    """
    perm_sets = get_restraint_config()['perm_sets']
    sync(PermSet.objects.all(), [PermSet(name=name) for name in perm_sets], ['name'])
