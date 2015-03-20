"""
Functions for updating the restraing configuration in the database.
"""
from restraint.models import PermSet, Perm, PermLevel, PermAccess
from restraint.core import get_restraint_config

from manager_utils import sync


def update_restraint_db(flush_default_access=False):
    update_perm_sets()
    update_perms()
    update_perm_levels()
    update_default_access(flush_default_access)


def update_perm_sets():
    """
    Updates PermSet models in the DB based on the restraint config.
    """
    perm_sets = get_restraint_config()['perm_sets']
    sync(PermSet.objects.all(), [PermSet(name=name) for name in perm_sets], ['name'])


def update_perms():
    """
    Updates Perm models in the DB based on the restraint config.
    """
    perms = get_restraint_config()['perms']
    sync(Perm.objects.all(), [Perm(name=perm) for perm in perms], ['name'])


def update_perm_levels():
    """
    Updates the PermLevel models in the DB based on the restraint config.
    """
    perms = get_restraint_config()['perms']
    perm_objs = {p.name: p for p in Perm.objects.all()}
    perm_levels = []
    for perm, levels in perms.items():
        assert(levels)
        for l in levels:
            perm_levels.append(PermLevel(perm=perm_objs[perm], name=l))

    sync(PermLevel.objects.all(), perm_levels, ['name', 'perm'])


def update_default_access(flush_default_access):
    """
    Updates the default configuration for permission set access.
    """
    default_access = get_restraint_config().get('default_access', {})
    PermAccess.objects.update_perm_set_access(default_access, flush_default_access)
