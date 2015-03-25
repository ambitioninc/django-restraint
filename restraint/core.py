from collections import defaultdict
from itertools import chain

from django.db.models import Q

from restraint import models


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


def update_restraint_db(flush_default_access=False):
    """
    Updates the restraint db based on the restraint config.
    Can optionally flush the previous default access configuration.
    """
    config = get_restraint_config()
    models.PermSet.objects.sync_perm_sets(config['perm_sets'])
    models.Perm.objects.sync_perms(config['perms'])
    models.PermLevel.objects.sync_perm_levels(config['perms'])
    models.PermAccess.objects.update_perm_set_access(config.get('default_access', {}), flush_default_access)


class Restraint(object):
    """
    The primary way of accessing permissions. The programmer loads a restraint object with the
    permission object and which permissions they want to load. One permissions are loaded for
    that account, the user may check if a user has certain permissions and also restrict
    querysets based on access levels that a user has.
    """
    def __init__(self, user, which_perms=None):
        """
        Initializes the Restraint object.

        :type user: Any object
        :param user: A user in a project

        :type which_perms: list
        :param which_perms: The permissions to be loaded for the user, or all permissions if None.
        """
        self._config = get_restraint_config()
        self._user = user
        self._load_perms(user, which_perms)

    @property
    def perms(self):
        return self._perms

    def _load_perms(self, account, which_perms):
        perm_set_names = self._config['perm_set_getter'](account)
        perm_levels = models.PermLevel.objects.filter(
            Q(permaccess__perm_set__name__in=perm_set_names) | Q(
                permaccess__perm_user_id=account.id,
                permaccess__perm_user_type__app_label=account._meta.app_label,
                permaccess__perm_user_type__model=account._meta.model_name)).select_related('perm')
        if which_perms:
            perm_levels = perm_levels.filter(perm__name__in=which_perms)

        self._perms = defaultdict(dict)
        for l in perm_levels:
            self._perms[l.perm.name].update({
                l.name: self._config['perms'][l.perm.name]['levels'][l.name]['id_filter']
            })

    def has_perm(self, perm, level=None):
        """
        Returns true if the restraint object has the perm. If a level is not specified, it returns
        true if that perm exists for any level.

        :type perm: string
        :param perm: The permission to check

        :type level: string
        :param level: The level to check, or any level if None
        """
        return perm in self._perms and level in self._perms[perm] if level else perm in self._perms

    def filter_qset(self, qset, perm):
        """
        Given a permission, filter the queryset by its levels.

        :type qset: A Django QuerySet
        :param qset: The queryset to be filtered

        :type perm: string
        :param perm: The permission over which to do the filtering
        """
        if not self.has_perm(perm):
            # If the user doesnt have the perm, return no data
            return qset.none()
        elif None in self._perms[perm].values():
            # If any levels are none, return the full queryset
            return qset
        else:
            # Filter the queryset by the union of all filters
            return qset.filter(id__in=set(chain(*[l(self._user) for l in self._perms[perm].values()])))
