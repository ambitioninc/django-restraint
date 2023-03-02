from django.contrib.contenttypes.models import ContentType
from django.db import models

from six import python_2_unicode_compatible

from restraint.managers import PermSetManager, PermManager, PermLevelManager, PermAccessManager


@python_2_unicode_compatible
class PermSet(models.Model):
    """
    This is essentially a group that has a name.
    Each PermSet will have a PermAccess associated with it that will contain the groups full permissions
    The permissions are indicated through PermAccess.perm_levels.

    Fields:
     - Name
     - Display_name
     - Perm_access (One To One to PermAccess) For this set, this user type has these levels

    Example:
     - Name: manager
     - Display Name: Managers
    """
    name = models.CharField(max_length=256, unique=True, blank=True)
    display_name = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    objects = PermSetManager()

    def __str__(self):
        return f'{self.display_name}:{self.name}'


@python_2_unicode_compatible
class Perm(models.Model):
    """
    This is the actual permission name specific to what each app will add, for example competition_all.

    Fields:
     - Name
     - Display_name

    Example:
     - Name: can_edit_accounts
     - Display Name: Users: Edit
     - Levels (Reverse Many To Many to PermLevel)
    """
    name = models.CharField(max_length=256, unique=True, blank=True)
    display_name = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    objects = PermManager()

    def __str__(self):
        return f'{self.display_name}:{self.name}'


@python_2_unicode_compatible
class PermLevel(models.Model):
    """
    Each specific Perm can have different levels of access for the same permission.
    A blank level indicates that its either a yes/no decision
    Other options might look like all, created_by, etc...
    This should be unique and handled by each app independently

    Fields:
     - Perm (Foreign Key)
     - Name
     - Display_name

    Example:
    This is an example of a permission that can have multiple levels of permissions.
    Let's take the example permission of can_edit_accounts with three different permission levels:
     - Created_by: Can only edit accounts created by the user tied to the permission
     - Own: Can only edit their own account
     - Under: Can edit accounts that they manage

    Created By:
     - Permission: can_edit_accounts
     - Name: created_by
     - Display Name: Can Edit Users Created

    Own:
     - Permission: can_edit_accounts
     - Name: own
     - Display Name: Can Edit Own Account

    Under:
     - Permission: can_edit_accounts
     - Name: under
     - Display Name: Can Edit Subordinate Accounts
    """
    perm = models.ForeignKey(Perm, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, blank=True)
    display_name = models.TextField(blank=True)

    objects = PermLevelManager()

    class Meta:
        unique_together = ('perm', 'name')

    def __str__(self):
        return f'{self.name}:{self.display_name}[PERM]{self.perm}'


class PermAccess(models.Model):
    """
    Provides access a list of permission levels for a permission set or for an individual
    user.

    This is what is used to determine what groups or individuals have access to.
    The access is determined by what levels are assigned to each group or individual.
    This can be found in the many to many relationship to levels `PermAccess.perm_levels.all()`

    Fields:
     - PermSet (One To One)
     - Perm_user_type (ContentType, Generic Foreign Key)
     - Perm_user_id (id of the object associated with the content type)
     - Perm_levels (Many to Many PermLevel)

    Example:
    An example would be for the manager permission set and allowing any manager to have access to two levels,
    own and under so they can edit their own account and any subordinate accounts.
     - Perm Set: manager
     - User Type: None
     - User Id: 0
     - Perm Levels
        - Own
        - Under
    """
    perm_set = models.OneToOneField(PermSet, null=True, default=None, on_delete=models.CASCADE)
    perm_user_type = models.ForeignKey(ContentType, null=True, default=None, on_delete=models.CASCADE)
    perm_user_id = models.PositiveIntegerField(default=0)
    perm_levels = models.ManyToManyField(PermLevel)

    class Meta:
        unique_together = ('perm_user_type', 'perm_user_id')

    objects = PermAccessManager()

    def __str__(self):  # pragma: no cover
        return f'[PERM_SET]{self.perm_set}[USER_TYPE]{self.perm_user_type}[USER_ID]{self.perm_user_id}'
