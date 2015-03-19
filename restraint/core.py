from collections import defaultdict

from restraint.models import PermLevel


# A global variable for holding the configuration of django restraint
RESTRAINT_CONFIG = {}


def register_restraint_config(restraint_config):
    RESTRAINT_CONFIG.clear()
    RESTRAINT_CONFIG.update(restraint_config)


def get_restraint_config():
    if RESTRAINT_CONFIG:
        return RESTRAINT_CONFIG
    else:
        raise RuntimeError('No restraint config has been registered')


def get_perms(account, which_perms=None):
    """
    Given an account and which_perms to get, return a dictionary of all permissions, their
    levels, and associated functions to retrieve restricted object IDs.
    """
    config = get_restraint_config()
    perm_set_names = config['perm_set_getter'](account)
    perm_levels = PermLevel.objects.filter(permaccess__perm_set__name__in=perm_set_names).select_related('perm')
    if which_perms:
        # Note that this doesn't completely filter out the permission levels that might have perms different
        # than those in which_perms. Django 1.7 has the abilty to do better filtering on prefetched object
        perm_levels = perm_levels.filter(perm__name__in=which_perms)

    perms = defaultdict(dict)
    for l in perm_levels:
        perms[l.perm.name].update({
            l.name: config['perms'][l.perm.name].get(l.name)
        })

    return perms
