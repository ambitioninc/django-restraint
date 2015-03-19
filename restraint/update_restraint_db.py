"""
Functions for updating the restraing configuration in the database.
"""
from restraint.models import PermSet, Perm, PermLevel, PermAccess
from restraint.core import get_restraint_config

from manager_utils import sync


def update_restraint_db():
    update_perm_sets()
    update_perms()
    update_perm_levels()
    update_default_access()


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
        if levels:
            for l in levels:
                perm_levels.append(PermLevel(perm=perm_objs[perm], name=l))
        else:
            perm_levels.append(PermLevel(perm=perm_objs[perm], name=''))

    sync(PermLevel.objects.all(), perm_levels, ['name', 'perm'])


def update_default_access():
    """
    Updates the default configuration for permission set access.
    """
    default_access = get_restraint_config().get('default_access', {})
    for perm_set in PermSet.objects.all():
        perm_access, created = PermAccess.objects.get_or_create(perm_set=perm_set)
        if created and perm_set.name in default_access:
            for perm, perm_levels in default_access[perm_set.name].items():
                # Add the default blank name for no perm levels
                perm_levels = perm_levels or ['']
                perm_access.perm_levels.add(*PermLevel.objects.filter(perm__name=perm, name__in=perm_levels))
