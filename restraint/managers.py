from django.contrib.contenttypes.models import ContentType
from django.db import models
from manager_utils import sync


class PermSetManager(models.Manager):
    def sync_perm_sets(self, perm_sets):
        """
        Syncs the provided dictionary of perm sets to PermSet models.
        """
        from restraint.models import PermSet
        sync(
            self.get_queryset(),
            [PermSet(name=name, display_name=config.get('display_name', '')) for name, config in perm_sets.items()],
            ['name'], ['display_name']
        )


class PermManager(models.Manager):
    def sync_perms(self, perms):
        """
        Syncs the perms to Perm models.
        """
        from restraint.models import Perm
        return sync(
            self.get_queryset(),
            [Perm(name=name, display_name=config.get('display_name', '')) for name, config in perms.items()],
            ['name'], ['display_name'], return_upserts_distinct=True
        )


class PermLevelManager(models.Manager):
    def sync_perm_levels(self, perms):
        """
        Given a dictionary of perms that map to perm levels, sync the perm levels
        to PermLevel objects in the database.
        """
        from restraint.models import Perm, PermLevel
        perm_objs = {p.name: p for p in Perm.objects.all()}
        perm_levels = []
        for perm, perm_config in perms.items():
            assert(perm_config['levels'])
            for l, level_config in perm_config['levels'].items():
                perm_levels.append(
                    PermLevel(perm=perm_objs[perm], name=l, display_name=level_config.get('display_name', '')))
        sync(self.get_queryset(), perm_levels, ['name', 'perm'], ['display_name'])


class PermAccessManager(models.Manager):
    def update_perm_set_access(self, config, new_perms=None, flush_previous_config=False):
        """
        Update the access for perm sets with a config. The user can optionally flush
        the previous config and set it to the new one.
        """
        from restraint.models import PermSet, PermAccess, PermLevel
        if new_perms is None:
            new_perms = []
        for perm_set in PermSet.objects.all():
            perm_access, created = PermAccess.objects.get_or_create(perm_set=perm_set)
            perm_access_levels = []
            for perm, perm_levels in config.get(perm_set.name, {}).items():
                # If we are not flushing the previous config, continue if the perm not among the newly created perms
                # this is necessary because perm access is mutable; We don't want to destroy modifications made to
                # existing permissions
                if not created and not flush_previous_config and perm not in [p.name for p in new_perms]:
                    continue
                assert(perm_levels)
                perm_access_levels.extend(PermLevel.objects.filter(perm__name=perm, name__in=perm_levels))

            if flush_previous_config:
                perm_access.perm_levels.clear()
            perm_access.perm_levels.add(*perm_access_levels)

    def add_individual_access(self, user, perm_name, level_name):
        """
        Given a user, a permission name, and the name of the level, add the level in the permission access for
        the individual user.
        """
        from restraint.models import PermAccess, PermLevel
        pa, created = PermAccess.objects.get_or_create(
            perm_user_id=user.id,
            perm_user_type=ContentType.objects.get_for_model(user)
        )
        pa.perm_levels.add(PermLevel.objects.get(
            perm__name=perm_name,
            name=level_name
        ))

    def remove_individual_access(self, user, perm_name, level_name):
        """
        Given a user, a permission name, and the name of the level, remove the level in the permission access for
        the individual user.
        """
        from restraint.models import PermAccess, PermLevel
        pa = PermAccess.objects.get(
            perm_user_id=user.id,
            perm_user_type=ContentType.objects.get_for_model(user)
        )
        pa.perm_levels.remove(PermLevel.objects.get(
            perm__name=perm_name,
            name=level_name
        ))
