Setup
=====

The Restraint Configuration
---------------------------
Restraint is configured all in one place using the :code:`RESTRAINT_CONFIGURATION` django setting.

An example Restraint configuration is provided below. Details of the configuration are outlined in later sections.


.. code-block:: python


    config = {
        'perm_set_getter': perm_set_getter_function,
        'perm_sets': {
            'super': {
                'display_name': 'Super',
            },
            'individual': {
                'display_name': 'Individual',
            },
            'staff': {
                'display_name': 'Staff'
            }
        },
        'perms': {
            'can_edit_stuff': {
                'display_name': 'Can Edit Stuff',
                'levels': {
                    'all_stuff': {
                        'display_name': 'All Stuff',
                        'id_filter': None,
                    },
                    'some_stuff': {
                        'display_name': 'Some Stuff',
                        'id_filter': lambda a: User.objects.filter(id=a.id).values_list('id', flat=True),
                    },
                    'only_superusers': {
                        'display_name': 'Only Superusers',
                        'id_filter': lambda a: User.objects.filter(is_superuser=True).values_list('id', flat=True),
                    },
                },
            },
            'can_view_stuff': {
                'display_name': 'Can View Stuff',
                'levels': constants.BOOLEAN_LEVELS_CONFIG,
            }
        },
        'default_access': {
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
        }
    }

Defining The Permission Set Getter
----------------------------------
The :code:`perm_set_getter` key in the configuration points to a function that takes a user object. This function is responsible for returning a list of all perm sets that are associated with that user object. For example,

.. code-block:: python

    def perm_set_getter(user):
        perm_sets = ['individual']
        if u.is_superuser:
            perm_sets.append('super')
        if u.is_staff:
            perm_sets.append('staff')
        return perm_sets


In this example, the user object is a Django :code:`User` model, and the perm_set_getter function returns *individual*, *super*, or *staff* permission sets based on the contents of the user object.


Defining Permission Sets
------------------------
The :code:`perm_sets` key is responsible for defining all of the permission sets of your application. These must correlate directly with what `perm_set_getter` may return.

In the configuration from above, the user has defined that the permission sets are *super*, *individual*, and *staff*. Along with this, human-readable display names are also configured in the dictionary.


Defining Permissions And Their Levels
------------------------------------- 
The :code:`perms` key is responsible for defining all of the permissions and their associated levels. Each top-level key in the :code:`perms` config defines the permission name, and the dictionary for each permission defines the display name of the permission and the levels that are associated with that permission.

In the above example, the :code:`can_edit_stuff` permission is defined over three levels. Each of these levels defines a callable :code:`id_filter` function that can take the user and return lists of IDs associated with the querysets that should be restricted. For example, the :code:`some_stuff` level only allows the user to edit stuff that belongs to their account ID while the :code:`only_superusers` level allows one to edit the stuff belonging to super users. The :code:`all_stuff` level has no :code:`id_filter`, so it provides access over the entire queryset.

Note that if a user has been granted multiple permission levels over the same permission, the results of those levels will be unioned together.

If a permission is Boolean and has no levels, it must be configured with the :code:`BOOLEAN_LEVELS_CONFIG` object provided in the :code:`constants` module of Restraint.


Defining Default Permission Set Access
--------------------------------------
The Restraint configuration also allows the user to provide the default access levels for all permission sets. This prevents the user from having to write data migrations or initial fixtures to populate their permissions.

For example, the above configuration allows *super* users to edit all stuff or any stuff and also provides them access to view stuff. The above configuration only allows *individual* users to edit some stuff without being able to view stuff.


Syncing Your Configuration To The Database
------------------------------------------
The Restraint configuration will need to be synced to the database before it can be used by an application. Similar to Django's :code:`update_permissions`, Restraint provides an :code:`update_restraint_db` management command. When this command is called, all permission sets and permission levels are synced. Any permission sets and levels that were in the configuration before and not in the current one will be deleted.

The :code:`default_access` configuration in the Restraint configuration will only be synced the first time this management command is executed. This behavior can be overridden by passing the :code:`--flush_default_access` parameter to the management command.


How Do I Add Permissions To Individuals?
----------------------------------------
Adding permissions to individuals is not supported in the setup methods of Restraint. However, this may be done dynamically with model manager methods that are covered in the :doc:`Usage<usage>` documentation.