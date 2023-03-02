from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase
from django_dynamic_fixture import G
from mock import patch, Mock
from mock.mock import PropertyMock

from restraint import core, constants
from restraint.models import PermSet, Perm, PermLevel, PermAccess
import restraint.tests.configuration as test_configuration


class TestGetRestraintConfig(SimpleTestCase):
    def test_get_configuration(self):
        self.assertEqual(
            core.get_restraint_config()['perm_sets'],
            test_configuration.get_configuration()['perm_sets']
        )


class TestRestraintLoadPerms(TestCase):
    def setUp(self):
        core.update_restraint_db()

    def test_individual_user(self):
        # Create an individual user
        user = G(User, is_superuser=False, is_staff=False)

        # Get the users restraints
        restraints = core.Restraint(user)
        perms = restraints.perms
        self.assertEqual(
            perms,
            {
                'can_edit_stuff': {
                    'some_stuff': test_configuration.user_some_stuff_id_filter
                }
            }
        )

    def test_super_user(self):
        # Make a user that is a superuser and verify they get all proper permissions
        user = G(User, is_superuser=True)
        restraints = core.Restraint(user)
        perms = restraints.perms
        self.assertEquals(
            perms,
            {
                'can_edit_stuff': {
                    'all_stuff': None,
                    'some_stuff': test_configuration.user_some_stuff_id_filter,
                },
                'can_view_stuff': {
                    '': None
                },
                'can_access_users_named_foo': {
                    '': None
                }
            }
        )

    def test_user_with_additional_perms(self):
        # Make an individual user and verify they get all of the perms.
        # Also, add an individual permission to the user and verify they get that too
        user = G(User, is_superuser=False, is_staff=False)
        pa = G(PermAccess, perm_user_id=user.id, perm_user_type=ContentType.objects.get_for_model(user))
        pa.perm_levels.add(PermLevel.objects.get(name='all_stuff'))

        r = core.Restraint(user)
        perms = r.perms
        self.assertEquals(
            perms,
            {
                'can_edit_stuff': {
                    'some_stuff': test_configuration.user_some_stuff_id_filter,
                    'all_stuff': None
                }
            }
        )

    def test_load_some_perms(self):
        user = G(User, is_superuser=True)
        restraints = core.Restraint(user, ['can_edit_stuff'])
        perms = restraints.perms
        self.assertEquals(
            perms,
            {
                'can_edit_stuff': {
                    'all_stuff': None,
                    'some_stuff': test_configuration.user_some_stuff_id_filter
                }
            }
        )


class TestRestraintHasPerms(SimpleTestCase):
    @patch.object(core.Restraint, 'perms', new_callable=PropertyMock)
    def test_has_perm_w_level_true(self, mock_perms):
        mock_perms.return_value = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        r = core.Restraint(Mock())
        self.assertTrue(r.has_perm('can_edit_stuff', 'all_stuff'))

    @patch.object(core.Restraint, 'perms', new_callable=PropertyMock)
    def test_has_perm_w_level_false(self, mock_perms):
        mock_perms.return_value = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        r = core.Restraint(Mock())
        self.assertFalse(r.has_perm('can_edit_stuff', 'no_stuff'))

    @patch.object(core.Restraint, 'perms', new_callable=PropertyMock)
    def test_has_perm_wo_level_true(self, mock_perms):
        mock_perms.return_value = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        r = core.Restraint(Mock())
        self.assertTrue(r.has_perm('can_edit_stuff'))

    @patch.object(core.Restraint, 'perms', new_callable=PropertyMock)
    def test_has_perm_wo_level_false(self, mock_perms):
        mock_perms.return_value = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        r = core.Restraint(Mock())
        self.assertFalse(r.has_perm('can_mess_with_stuff'))


class TestRestraintFilterQSet(TestCase):
    def setUp(self):
        core.update_restraint_db()

    def test_filter_qset_global_access(self):
        # Make a user that is a superuser and verify they get all of the
        # super user perms
        u = G(User, is_superuser=True)
        # Make another user that they will be able to edit
        u2 = G(User)
        r = core.Restraint(u)

        filtered_qset = r.filter_qset(User.objects.all(), 'can_edit_stuff')
        self.assertEquals(set(filtered_qset), set([u, u2]))

    def test_filter_qset_local_access(self):
        # Make a user that is not a superuser
        u = G(User, is_superuser=False)
        # Make another user that they will not be able to edit
        G(User)
        r = core.Restraint(u)

        filtered_qset = r.filter_qset(User.objects.all(), 'can_edit_stuff')
        self.assertEquals(set(filtered_qset), set([u]))

    def test_filter_qset_multiple_local_access(self):
        # Make a user that is staff
        u = G(User, is_superuser=False, is_staff=True)
        # Make another user that they will not be able to edit
        G(User)
        # Make another super user that they will be able to edit
        u2 = G(User, is_superuser=True)
        r = core.Restraint(u)

        filtered_qset = r.filter_qset(User.objects.all(), 'can_edit_stuff')
        self.assertEquals(set(filtered_qset), set([u, u2]))

    def test_filter_qset_no_perms(self):
        # Make a user that is staff
        u = G(User, is_superuser=False, is_staff=True)
        # Load permissions that will not give them access to edit any accounts
        r = core.Restraint(u, ['bad_perm'])

        filtered_qset = r.filter_qset(User.objects.all(), 'can_edit_stuff')
        self.assertEquals(set(filtered_qset), set([]))

    def test_filter_qset_restrict_subset(self):
        models = [
            G(User, first_name='foo', last_name='foofington'),
            G(User, first_name='bar', last_name='barski'),
            G(User, first_name='foo', last_name='foogeelala'),
        ]
        # Make a user that is a superuser and verify they get all of the
        # super user perms
        u = G(User, is_superuser=True)
        r = core.Restraint(u)

        filtered_qset = r.filter_qset(
            User.objects.all(), 'can_access_users_named_foo', restrict_kwargs={'first_name': 'foo'})
        self.assertEquals(set(filtered_qset), set(models + [u]))

    def test_filter_qset_restrict_subset_no_perms(self):
        models = [
            G(User, first_name='foo', last_name='foofington'),
            G(User, first_name='bar', last_name='barski'),
            G(User, first_name='foo', last_name='foogeelala'),
        ]
        # Make a user that is a superuser and verify they get all of the
        # super user perms
        u = G(User, is_superuser=False)
        r = core.Restraint(u)

        filtered_qset = r.filter_qset(
            User.objects.all(), 'can_access_users_named_foo', restrict_kwargs={'first_name': 'foo'})
        self.assertEquals(set(filtered_qset), set([models[1]] + [u]))


class UpdateRestraintDbTest(TestCase):
    def add_custom_permission_set(self):
        # Setup a custom permission set
        custom_permission_set = PermSet.objects.create(
            name='custom',
            display_name='Custom',
            is_private=False
        )

        # Add some custom default access levels
        PermAccess.objects.set_default(
            permission_set_name=custom_permission_set.name,
            permission_name='can_edit_stuff',
            levels=['all_stuff']
        )

    @patch.object(core, 'get_restraint_config')
    def test_full_update_scenario_not_flush_default_access(self, mock_get_restraint_config):
        mock_get_restraint_config.return_value = {
            'perm_sets': {
                'global': {
                    'display_name': 'Global',
                },
                'restricted': {
                    'display_name': 'Restricted',
                },
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
                            'id_filter': None,
                        },
                    },
                },
                'can_view_stuff': {
                    'display_name': 'Can View Stuff',
                    'levels': constants.BOOLEAN_LEVELS_CONFIG,
                },
            },
            'default_access': {
                'global': {
                    'can_edit_stuff': ['all_stuff', 'some_stuff'],
                    'can_view_stuff': [constants.BOOLEAN_LEVELS_NAME],
                },
                'restricted': {
                    'can_edit_stuff': ['some_stuff'],
                }
            }
        }
        core.update_restraint_db()
        core.update_restraint_db()

    @patch.object(core, 'get_restraint_config')
    def test_full_update_scenario_not_flush_default_access_update_new_perm(self, mock_get_restraint_config):
        """
        Verifies that existing permission set is given access to new permission
        """
        config = {
            'perm_sets': {
                'global': {
                    'display_name': 'Global',
                },
                'restricted': {
                    'display_name': 'Restricted',
                    'locked': True,
                    'hidden': True
                },
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
                            'id_filter': None,
                        },
                    },
                },
                'can_view_stuff': {
                    'display_name': 'Can View Stuff',
                    'levels': constants.BOOLEAN_LEVELS_CONFIG,
                    'locked': True,
                    'hidden': True
                },
            },
            'default_access': {
                'global': {
                    'can_edit_stuff': ['all_stuff', 'some_stuff'],
                    'can_view_stuff': [constants.BOOLEAN_LEVELS_NAME],
                },
                'restricted': {
                    'can_edit_stuff': ['some_stuff'],
                }
            }
        }
        mock_get_restraint_config.return_value = config
        core.update_restraint_db()
        self.add_custom_permission_set()

        # add permission
        config['perms']['can_do_stuff'] = {
            'display_name': 'Can Do Stuff',
            'levels': {
                'all_stuff': {
                    'display_name': 'All Stuff',
                    'id_filter': None,
                },
                'this_thing': {
                    'display_name': 'This Thing',
                    'id_filter': None,
                },
            },
        }
        config['perms']['can_alter_stuff'] = {
            'display_name': 'Can Alter Stuff',
            'levels': constants.BOOLEAN_LEVELS_CONFIG
        }
        config['default_access']['global']['can_alter_stuff'] = [constants.BOOLEAN_LEVELS_NAME]
        config['default_access']['restricted']['can_do_stuff'] = ['all_stuff', 'this_thing']
        mock_get_restraint_config.return_value = config

        # update again
        core.update_restraint_db()

        self.assertEquals(
            set(PermSet.objects.filter(is_private=True).values_list('name', flat=True)),
            {'global', 'restricted'}
        )
        self.assertEquals(
            set(PermSet.objects.filter(is_locked=True).values_list('name', flat=True)),
            {'restricted'}
        )
        self.assertEquals(
            set(PermSet.objects.filter(is_hidden=True).values_list('name', flat=True)),
            {'restricted'}
        )
        self.assertEquals(
            set(PermSet.objects.all().values_list('name', flat=True)),
            {'global', 'restricted', 'custom'}
        )

        self.assertEquals(
            set(Perm.objects.values_list('name', flat=True)),
            {'can_view_stuff', 'can_edit_stuff', 'can_do_stuff', 'can_alter_stuff'}
        )
        self.assertEquals(
            set(Perm.objects.filter(is_locked=True).values_list('name', flat=True)),
            {'can_view_stuff'}
        )
        self.assertEquals(
            set(Perm.objects.filter(is_hidden=True).values_list('name', flat=True)),
            {'can_view_stuff'}
        )

        self.assertEquals(
            list(PermLevel.objects.order_by(
                'perm__name',
                'name'
            ).values_list(
                'perm__name',
                'name'
            )),
            [
                ('can_alter_stuff', ''),
                ('can_do_stuff', 'all_stuff'),
                ('can_do_stuff', 'this_thing'),
                ('can_edit_stuff', 'all_stuff'),
                ('can_edit_stuff', 'some_stuff'),
                ('can_view_stuff', '')
            ]
        )

        self.assertEquals(
            list(
                PermAccess.objects.order_by(
                    'perm_set__name',
                    'perm_levels__perm__name',
                    'perm_levels__name'
                ).values_list(
                    'perm_set__name',
                    'perm_levels__perm__name',
                    'perm_levels__name'
                )
            ),
            [
                ('custom', 'can_edit_stuff', 'all_stuff'),
                ('global', 'can_alter_stuff', ''),
                ('global', 'can_edit_stuff', 'all_stuff'),
                ('global', 'can_edit_stuff', 'some_stuff'),
                ('global', 'can_view_stuff', ''),
                ('restricted', 'can_do_stuff', 'all_stuff'),
                ('restricted', 'can_do_stuff', 'this_thing'),
                ('restricted', 'can_edit_stuff', 'some_stuff')
            ]
        )

    @patch.object(core, 'get_restraint_config')
    def test_full_update_scenario_flush_default_access(self, mock_get_restraint_config):
        config = {
            'perm_sets': {
                'global': {
                    'display_name': 'Global',
                },
                'restricted': {
                    'display_name': 'Restricted',
                },
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
                            'id_filter': None,
                        },
                    },
                },
                'can_view_stuff': {
                    'display_name': 'Can View Stuff',
                    'levels': constants.BOOLEAN_LEVELS_CONFIG,
                },
            },
            'default_access': {
                'global': {
                    'can_edit_stuff': ['all_stuff', 'some_stuff'],
                    'can_view_stuff': [constants.BOOLEAN_LEVELS_NAME],
                },
                'restricted': {
                    'can_edit_stuff': ['some_stuff'],
                }
            }
        }
        mock_get_restraint_config.return_value = config
        core.update_restraint_db()
        self.add_custom_permission_set()

        config = {
            'perm_sets': {
                'global': {
                    'display_name': 'Global',
                },
                'restricted': {
                    'display_name': 'Restricted',
                },
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
                            'id_filter': None,
                        },
                    },
                },
                'can_view_stuff': {
                    'display_name': 'Can View Stuff',
                    'levels': constants.BOOLEAN_LEVELS_CONFIG,
                },
            },
            'default_access': {
                'global': {
                    'can_edit_stuff': ['all_stuff'],
                },
            }
        }
        mock_get_restraint_config.return_value = config
        core.update_restraint_db(flush_default_access=True)

        self.assertEquals(
            set(PermSet.objects.filter(is_private=True).values_list('name', flat=True)),
            {'global', 'restricted'}
        )
        self.assertEquals(
            set(PermSet.objects.all().values_list('name', flat=True)),
            {'custom', 'global', 'restricted'}
        )

        self.assertEquals(
            set(Perm.objects.values_list('name', flat=True)),
            {'can_view_stuff', 'can_edit_stuff'}
        )

        self.assertEquals(
            list(PermLevel.objects.order_by(
                'perm__name',
                'name'
            ).values_list(
                'perm__name',
                'name'
            )),
            [
                ('can_edit_stuff', 'all_stuff'),
                ('can_edit_stuff', 'some_stuff'),
                ('can_view_stuff', '')
            ]
        )

        self.assertEquals(
            list(
                PermAccess.objects.order_by(
                    'perm_set__name',
                    'perm_levels__perm__name',
                    'perm_levels__name'
                ).values_list(
                    'perm_set__name',
                    'perm_levels__perm__name',
                    'perm_levels__name'
                )
            ),
            [
                ('custom', 'can_edit_stuff', 'all_stuff'),
                ('global', 'can_edit_stuff', 'all_stuff'),
                ('restricted', None, None)
            ]
        )
