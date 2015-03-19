from collections import defaultdict

from restraint.models import PermAccess


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
    perm_access = PermAccess.objects.filter(perm_set__name__in=perm_set_names).prefetch_related('perm_levels__perm')
    if which_perms:
        perm_access = perm_access.filter(perm_levels__perm__name__in=which_perms)

    perms = defaultdict(dict)
    for p in perm_access:
        for l in p.perm_levels.all():
            perms[l.perm.name].update({
                l.name: config['perms'][l.perm.name].get(l.name)
            })

    return perms
