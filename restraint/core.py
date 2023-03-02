from collections import defaultdict
from itertools import chain

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from restraint import models
from restraint.signals import restraint_db_updated


def get_restraint_config():
    return import_string(settings.RESTRAINT_CONFIGURATION)()


@transaction.atomic
def update_restraint_db(flush_default_access=False):
    """
    Updates the restraint db based on the restraint config.
    Can optionally flush the previous default access configuration.
    """
    config = get_restraint_config()
    models.PermSet.objects.sync_perm_sets(config['perm_sets'])
    updated_perms, new_perms = models.Perm.objects.sync_perms(config['perms'])
    models.PermLevel.objects.sync_perm_levels(config['perms'])
    models.PermAccess.objects.update_perm_set_access(config.get('default_access', {}), new_perms, flush_default_access)
    restraint_db_updated.send(sender=None, config=config)


def has_permission(user, user_permissions, permission, level):
    """
    The default permission checker.

    Returns true if the restraint object has the perm. If a level is not specified, it returns
    true if that perm exists for any level.
    """
    return (
        permission in user_permissions and level in user_permissions[permission]
        if level
        else permission in user_permissions and len(user_permissions[permission])
    )


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

        # Save a reference to the config
        self._config = get_restraint_config()

        # Save a reference to the user
        self._user = user

        # Save a reference wo which perms we loaded
        self._which_perms = which_perms

        # Set the permission checkers
        self._permission_checkers = [has_permission]
        if self._config.get('perm_checker'):
            self._permission_checkers.append(self._config.get('perm_checker'))

    @cached_property
    def perms(self):
        """
        Load and cache the permissions associated with the user
        """
        perm_set_names = self._config['perm_set_getter'](self._user)
        perm_levels = models.PermLevel.objects.filter(
            Q(permaccess__perm_set__name__in=perm_set_names) | Q(
                permaccess__perm_user_id=self._user.id,
                permaccess__perm_user_type__app_label=self._user._meta.app_label,
                permaccess__perm_user_type__model=self._user._meta.model_name)).select_related('perm')
        if self._which_perms:
            perm_levels = perm_levels.filter(perm__name__in=self._which_perms)

        perms = defaultdict(dict)
        for level in perm_levels:
            perms[level.perm.name].update({
                level.name: self._config['perms'][level.perm.name]['levels'][level.name]['id_filter']
            })
        return perms

    def has_perm(self, perm, level=None):
        """
        Call the configured permission checker
        """
        # Try and find the first one that passes
        # Do this in a loop to avoid additional checks when not necessary
        for permission_checker in self._permission_checkers:
            if permission_checker(
                user=self._user,
                user_permissions=self.perms,
                permission=perm,
                level=level
            ):
                return True
        return False

    def filter_qset(self, qset, perm, restrict_kwargs=None):
        """
        Given a permission, filter the queryset by its levels.

        :type qset: A Django QuerySet
        :param qset: The queryset to be filtered

        :type perm: string
        :param perm: The permission over which to do the filtering
        """

        # Check if any permission filters exist
        # If none exist we know we can allow all
        permission_filters = self.perms[perm].values()
        allow_all = True if not len(permission_filters) or None in permission_filters else False
        has_perm = self.has_perm(perm)

        # The user does not have this permission for any level
        if not has_perm:
            # if this restraint only protects a certain subset of the queryset, return the rest
            if restrict_kwargs is not None:
                return qset.exclude(**restrict_kwargs)
            # else return nothing
            else:
                return qset.none()
        elif has_perm and allow_all:
            # If any levels are none, return the full queryset
            return qset
        else:
            # Filter the queryset by the union of all filters
            return qset.filter(id__in=set(chain(*[level(self._user) for level in self.perms[perm].values()])))
