from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from manager_utils import sync


class PermSetManager(models.Manager):
    def sync_perm_sets(self, perm_sets):
        """
        Syncs all private perm sets the provided dictionary of perm sets to PermSet models.
        """
        from restraint.models import PermSet
        sync(
            queryset=self.get_queryset().filter(
                is_private=True
            ),
            model_objs=[
                PermSet(
                    name=name,
                    display_name=config.get('display_name', ''),
                    is_private=True,
                    is_locked=config.get('locked', False),
                    is_hidden=config.get('hidden', False)
                )
                for name, config in perm_sets.items()
            ],
            unique_fields=[
                'name'
            ],
            update_fields=[
                'display_name',
                'is_locked',
                'is_hidden'
            ]
        )


class PermManager(models.Manager):
    def sync_perms(self, perms):
        """
        Syncs the perms to Perm models.
        """
        from restraint.models import Perm
        return sync(
            queryset=self.get_queryset(),
            model_objs=[
                Perm(
                    name=name,
                    display_name=config.get('display_name', ''),
                    is_locked=config.get('locked', False),
                    is_hidden=config.get('hidden', False)
                )
                for name, config in perms.items()
            ],
            unique_fields=[
                'name'
            ],
            update_fields=[
                'display_name',
                'is_locked',
                'is_hidden'
            ],
            return_upserts_distinct=True
        )


class PermLevelManager(models.Manager):
    def sync_perm_levels(self, perms):
        """
        Given a dictionary of perms that map to perm levels, sync the perm levels
        to PermLevel objects in the database.
        """
        from restraint.models import Perm, PermLevel
        perm_objs = {
            p.name: p
            for p in Perm.objects.all()
        }
        perm_levels = []
        for perm, perm_config in perms.items():
            assert perm_config['levels']
            for level, level_config in perm_config['levels'].items():
                perm_levels.append(PermLevel(
                    perm=perm_objs[perm],
                    name=level,
                    display_name=level_config.get('display_name', '')
                ))
        sync(
            queryset=self.get_queryset(),
            model_objs=perm_levels,
            unique_fields=[
                'name',
                'perm'
            ],
            update_fields=[
                'display_name'
            ]
        )


class PermAccessManager(models.Manager):
    def set_default(self, permission_set_name, permission_name, levels=None):
        """
        Sets default levels for a permission for a permission set
        :param permission_set_name: The name of the permission set
        :param permission_name: The name of the permission
        :param levels: A list of levels
        """
        from restraint.models import PermSet, PermAccess, PermLevel
        permission_access = PermAccess.objects.get_or_create(
            perm_set=PermSet.objects.get(name=permission_set_name)
        )[0]
        if levels:
            permission_levels = PermLevel.objects.filter(
                perm__name=permission_name,
                name__in=levels
            )
            permission_access.perm_levels.set(permission_levels)
        else:
            permission_access.perm_levels.clear()

    def update_perm_set_access(self, config, new_perms=None, flush_previous_config=False):
        """
        Update the access for private perm sets with a config. The user can optionally flush
        the previous config and set it to the new one.
        """

        # Do model imports to avoid circular
        from restraint.models import PermSet, PermAccess, PermLevel

        # Ensure that new perms is not none
        if new_perms is None:  # pragma: no cover
            new_perms = []

        # Loop over each private permission set
        for perm_set in PermSet.objects.filter(is_private=True):
            perm_access, created = PermAccess.objects.get_or_create(perm_set=perm_set)
            perm_access_levels = []
            for perm, perm_levels in config.get(perm_set.name, {}).items():
                # If we are not flushing the previous config, continue if the perm not among the newly created perms
                # this is necessary because perm access is mutable; We don't want to destroy modifications made to
                # existing permissions
                if not created and not flush_previous_config and perm not in [p.name for p in new_perms]:
                    continue
                assert perm_levels
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

    @transaction.atomic
    def assign_default_permissions_from_permission_set(self, to_permission_set, from_permission_set):
        """
        Create default permission access for a permission set from another permission set
        """

        # Local imports to avoid circular dependency
        from restraint.models import PermAccess

        # Get the permission access
        to_permission_set_access, to_permission_set_access_created = PermAccess.objects.get_or_create(
            perm_set=to_permission_set
        )
        from_permission_set_access = PermAccess.objects.filter(perm_set=from_permission_set).first()

        # If we did not create the permission access, do nothing
        if not to_permission_set_access_created or from_permission_set_access is None:
            return False

        # Use the same levels as the from access
        to_permission_set_access.perm_levels.set(from_permission_set_access.perm_levels.all())
