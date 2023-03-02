from django.contrib.auth.models import User

from restraint import constants


def perm_set_getter(u):
    perm_sets = ['individual']
    if u.is_superuser:
        perm_sets.append('super')
    if u.is_staff:
        perm_sets.append('staff')
    return perm_sets


def user_some_stuff_id_filter(user):
    return User.objects.filter(id=user.id).values_list('id', flat=True)


def user_only_super_users_id_filter(user):
    return User.objects.filter(is_superuser=True).values_list('id', flat=True)


def get_configuration():
    return {
        'perm_set_getter': perm_set_getter,
        'perm_sets': {
            'super': {
                'display_name': 'Super',
            },
            'individual': {
                'display_name': 'Individual',
            },
            'staff': {
                'display_name': 'Staff'
            },
            'locked_and_hidden': {
                'display_name': 'This is locked and hidden'
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
                        'id_filter': user_some_stuff_id_filter,
                    },
                    'only_superusers': {
                        'display_name': 'Only Superusers',
                        'id_filter': user_only_super_users_id_filter,
                    },
                },
            },
            'can_view_stuff': {
                'display_name': 'Can View Stuff',
                'levels': constants.BOOLEAN_LEVELS_CONFIG,
            },
            'can_access_users_named_foo': {
                'display_name': 'Can Foo',
                'levels': constants.BOOLEAN_LEVELS_CONFIG,
                'locked': True,
                'hidden': True
            }
        },
        'default_access': {
            'super': {
                'can_edit_stuff': ['all_stuff', 'some_stuff'],
                'can_view_stuff': [constants.BOOLEAN_LEVELS_NAME],
                'can_access_users_named_foo': [constants.BOOLEAN_LEVELS_NAME],
            },
            'individual': {
                'can_edit_stuff': ['some_stuff'],
            },
            'staff': {
                'can_edit_stuff': ['some_stuff', 'only_superusers']
            }
        }
    }
