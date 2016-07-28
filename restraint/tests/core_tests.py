from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase
from django_dynamic_fixture import G
from mock import patch, Mock

from restraint import core, constants
from restraint.models import PermSet, Perm, PermLevel, PermAccess


class TestRegisterRestraintConfig(SimpleTestCase):
    def test_register_restraint_config(self):
        core.register_restraint_config({'config': 'config'})
        self.assertEquals(core.RESTRAINT_CONFIG, {'config': 'config'})


class TestGetRestraintConfig(SimpleTestCase):
    def test_get_restraint_config_not_set(self):
        core.RESTRAINT_CONFIG.clear()
        with self.assertRaises(RuntimeError):
            core.get_restraint_config()

    def test_get_restraint_config_set(self):
        core.register_restraint_config({'config': 'config'})
        self.assertEquals(core.get_restraint_config(), {'config': 'config'})


class TestRestraintLoadPerms(TestCase):
    def setUp(self):
        def perm_set_getter(u):
            perm_sets = ['individual']
            # if u.is_superuser:
            perm_sets.append('super')
            return perm_sets

        config = {
            'perm_set_getter': perm_set_getter,
            'perm_sets': {
                'super': {
                    'display_name': 'Super',
                },
                'individual': {
                    'display_name': 'Individual'
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
                            'id_filter': None,
                        },
                        'most_stuff': {
                            'display_name': 'Most Stuff',
                            'id_filter': None,
                        }
                    }
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
                }
            }
        }
        core.register_restraint_config(config)
        core.update_restraint_db()

    def test_load_all_perms_with_individual_perms(self):
        # Make a user that is a superuser and verify they get all of the
        # super user perms. Also, add an individual permission to the user
        # and verify they get that too
        u = G(User, is_superuser=True)
        pa = G(PermAccess, perm_user_id=u.id, perm_user_type=ContentType.objects.get_for_model(u))
        pa.perm_levels.add(PermLevel.objects.get(name='most_stuff'))

        r = core.Restraint(u)
        perms = r.perms
        self.assertEquals(perms, {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
                'most_stuff': None,
            }
        })

    def test_load_all_perms(self):
        # Make a user that is a superuser and verify they get all of the
        # super user perms
        u = G(User, is_superuser=True)
        r = core.Restraint(u)
        perms = r.perms
        self.assertEquals(perms, {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        })

    def test_load_some_perms(self):
        # Make a user that is a superuser and verify they get all of the
        # super user perms
        u = G(User, is_superuser=True)
        r = core.Restraint(u, ['can_edit_stuff'])
        perms = r.perms
        self.assertEquals(perms, {
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        })


class TestRestraintHasPerms(SimpleTestCase):
    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_has_perm_w_level_true(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertTrue(r.has_perm('can_edit_stuff', 'all_stuff'))

    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_has_perm_w_level_false(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertFalse(r.has_perm('can_edit_stuff', 'no_stuff'))

    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_has_perm_wo_level_true(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertTrue(r.has_perm('can_edit_stuff'))

    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_has_perm_wo_level_false(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_view_stuff': {
                '': None,
            },
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertFalse(r.has_perm('can_mess_with_stuff'))


class TestRestraintFilterQSet(TestCase):
    def setUp(self):
        def perm_set_getter(u):
            perm_sets = ['individual']
            if u.is_superuser:
                perm_sets.append('super')
            if u.is_staff:
                perm_sets.append('staff')
            return perm_sets

        config = {
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
        core.register_restraint_config(config)
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


class UpdateRestraintDbTest(TestCase):
    def test_full_update_scenario_not_flush_default_access(self):
        core.register_restraint_config({
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
        })
        core.update_restraint_db()
        core.update_restraint_db()

    def test_full_update_scenario_not_flush_default_access_update_new_perm(self):
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
        core.register_restraint_config(config)
        core.update_restraint_db()
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
        core.register_restraint_config(config)
        # update again
        core.update_restraint_db()

        self.assertEquals(
            set(PermSet.objects.values_list('name', flat=True)), set(['global', 'restricted']))

        self.assertEquals(
            set(Perm.objects.values_list('name', flat=True)),
            set(['can_view_stuff', 'can_edit_stuff', 'can_do_stuff', 'can_alter_stuff']))

        self.assertEquals(
            set(PermLevel.objects.values_list('name', 'perm__name')),
            set([
                ('all_stuff', 'can_edit_stuff'), ('some_stuff', 'can_edit_stuff'), ('', 'can_view_stuff'),
                ('all_stuff', 'can_do_stuff'), ('this_thing', 'can_do_stuff'), ('', 'can_alter_stuff'),
            ])
        )

        self.assertEquals(
            set(PermAccess.objects.values_list('perm_levels__name', 'perm_levels__perm__name', 'perm_set__name')),
            set([
                ('all_stuff', 'can_edit_stuff', 'global'), ('', 'can_view_stuff', 'global'),
                ('some_stuff', 'can_edit_stuff', 'global'), ('some_stuff', 'can_edit_stuff', 'restricted'),
                ('', 'can_alter_stuff', 'global'), ('all_stuff', 'can_do_stuff', 'restricted'),
                ('this_thing', 'can_do_stuff', 'restricted'),
            ])
        )

    def test_full_update_scenario_flush_default_access(self):
        core.register_restraint_config({
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
        })
        core.update_restraint_db()

        core.register_restraint_config({
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
        })
        core.update_restraint_db(flush_default_access=True)

        self.assertEquals(
            set(PermSet.objects.values_list('name', flat=True)), set(['global', 'restricted']))

        self.assertEquals(
            set(Perm.objects.values_list('name', flat=True)), set(['can_view_stuff', 'can_edit_stuff']))

        self.assertEquals(
            set(PermLevel.objects.values_list('name', 'perm__name')),
            set([('all_stuff', 'can_edit_stuff'), ('some_stuff', 'can_edit_stuff'), ('', 'can_view_stuff')]))

        self.assertEquals(
            set(PermAccess.objects.values_list('perm_levels__name', 'perm_levels__perm__name', 'perm_set__name')),
            set([('all_stuff', 'can_edit_stuff', 'global'), (None, None, 'restricted')])
        )
