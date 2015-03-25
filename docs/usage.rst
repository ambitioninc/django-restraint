Usage
=====

After Restrain is set up, the only object you need to use is the :code:`Restraint` object.

Restraint Initialization
------------------------
The :code:`Restraint` object is initialized as follows:

.. code-block:: python

    from restraint import Restaint

    # Load all permissions for the user
    r = Restraint(user)

    # Load some permissions for the user
    r = Restraint(user, ['can_edit_accounts'])

The above code example shows how to initialize the object by loading all of the permissions for the user in the restraint object and how to also only load some of the permissions.


Checking For Permissions
------------------------
When the :code:`Restraint` object is initialized, the :code:`has_perm` method may be used to determine the user has a particular permission.

.. code-block:: python

    from restraint import Restaint

    # Load all permissions for the user
    r = Restraint(user)

    # Check if the user has any level for a permission
    r.has_perm('can_edit_accounts')

    # Check if the user has a particular level for a permission
    r.has_perm('can_edit_accounts', 'all_accounts')

The above example shows how to check if a user has any level for a permission or if they have a level for a permission.


Checking Object Access
----------------------
The user has the ability to define what IDs may be edited based on an :code:`id_filter` function for each level in the Restraint configuration. The :code:`Restraint` object can filter a queryset by the filters owned by the user by calling :code:`filter_qset`.

.. code-block:: python

    from restraint import Restaint

    # Load all permissions for the user
    r = Restraint(user)

    # Filter a queryset based on the user's permission levels
    users_i_can_edit = r.filter_qset(User.objects.all(), 'can_edit_accounts')


In the above example, all :code:`User` objects were filtered down to the ones that can be edited by the user.


Dynamically Syncing Permission Set Access
-----------------------------------------
Restraint provides a model manager method if a user wants to sync a permission set access configuration to the database.

.. code-block:: python

    from restraint.models import PermAccess

    PermAccess.objects.update_perm_set_access({
        'super': {
            'can_edit_stuff': ['all_stuff', 'some_stuff'],
            'can_view_stuff': [constants.BOOLEAN_LEVELS_NAME],
        },
        'individual': {
            'can_edit_stuff': ['some_stuff'],
        },
        'staff': {
            'can_edit_stuff': ['some_stuff', 'only_superusers']
        }
    }, True)


In the above example, the same format as the :code:`default_access` part of the Restraint configuration is used to sync the configuration of permission sets.


Adding And Removing Permissions For Individuals
-----------------------------------------------
Along with allowing permissions to be specified over permission sets, Restraint also provides the ability to assign permission levels to specific users.

To add a permission level to a user, do the following:

.. code-block:: python

    from restraint import constants
    from restraint.models import PermAccess

    user = individual_user_model_object

    # Add a defined level
    PermAccess.add_individual_access(user, 'my_perm', 'my_perm_level')

    # Add the boolean level
    PermAccess.add_individual_access(user, 'my_perm', constants.BOOLEAN_LEVELS_NAME)

To remove a permission level to a user, do the following:

.. code-block:: python

    from restraint import constants
    from restraint.models import PermAccess

    user = individual_user_model_object

    # Remove a defined level
    PermAccess.remove_individual_access(user, 'my_perm', 'my_perm_level')

    # Removef the boolean level
    PermAccess.remove_individual_access(user, 'my_perm', constants.BOOLEAN_LEVELS_NAME)

When individual permissions are added, they will be accessed the same way as permission set levels with the :code:`Restraint` object.