from collections import defaultdict
from itertools import chain

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


class Restraint(object):
    """
    The primary way of accessing permissions. The programmer loads a restraint object with the
    permission object and which permissions they want to load. One permissions are loaded for
    that account, the user may check if a user has certain permissions and also restrict
    querysets based on access levels that a user has.
    """
    def __init__(self, account, which_perms=None):
        self._config = get_restraint_config()
        self._account = account
        self._load_perms(account, which_perms)

    @property
    def perms(self):
        return self._perms

    def _load_perms(self, account, which_perms):
        perm_set_names = self._config['perm_set_getter'](account)
        perm_levels = PermLevel.objects.filter(permaccess__perm_set__name__in=perm_set_names).select_related('perm')
        if which_perms:
            perm_levels = perm_levels.filter(perm__name__in=which_perms)

        self._perms = defaultdict(dict)
        for l in perm_levels:
            self._perms[l.perm.name].update({
                l.name: self._config['perms'][l.perm.name].get(l.name)
            })

    def has_perm(self, perm, level=None):
        """
        Returns true if the restraint object has the perm. If a level is not specified, it returns
        true if that perm exists for any level.
        """
        return perm in self._perms and level in self._perms[perm] if level else perm in self._perms

    def filter_qset(self, qset, perm):
        """
        Given a permission, filter the queryset by its levels.
        """
        if not self.has_perm(perm):
            # If the user doesnt have the perm, return no data
            return qset.none()
        elif None in self._perms[perm].values():
            # If any levels are none, return the full queryset
            return qset
        else:
            # Filter the queryset by the union of all filters
            return qset.filter(id__in=set(chain(*[l(self._account) for l in self._perms[perm].values()])))
