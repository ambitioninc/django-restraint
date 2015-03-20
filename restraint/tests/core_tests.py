from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django_dynamic_fixture import G
from mock import patch, Mock

from restraint import core
from restraint.update_restraint_db import update_restraint_db


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
    def test_load_all_perms(self):
        def perm_set_getter(u):
            perm_sets = ['individual']
            if u.is_superuser:
                perm_sets.append('super')
            return perm_sets

        config = {
            'perm_set_getter': perm_set_getter,
            'perm_sets': ['super', 'individual'],
            'perms': {
                'can_edit_stuff': {
                    'all_stuff': None,
                    'some_stuff': None,
                },
                'can_view_stuff': {}
            },
            'default_access': {
                'super': {
                    'can_edit_stuff': ['all_stuff', 'some_stuff'],
                    'can_view_stuff': [],
                },
                'individual': {
                    'can_edit_stuff': ['some_stuff'],
                }
            }
        }
        core.register_restraint_config(config)
        update_restraint_db()

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
        def perm_set_getter(u):
            perm_sets = ['individual']
            if u.is_superuser:
                perm_sets.append('super')
            return perm_sets

        config = {
            'perm_set_getter': perm_set_getter,
            'perm_sets': ['super', 'individual'],
            'perms': {
                'can_edit_stuff': {
                    'all_stuff': None,
                    'some_stuff': None,
                },
                'can_view_stuff': {}
            },
            'default_access': {
                'super': {
                    'can_edit_stuff': ['all_stuff', 'some_stuff'],
                    'can_view_stuff': [],
                },
                'individual': {
                    'can_edit_stuff': ['some_stuff'],
                }
            }
        }
        core.register_restraint_config(config)
        update_restraint_db()

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


class TestRestraintHasPerm(SimpleTestCase):
    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_with_level_true(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertTrue(r.has_perm('can_edit_stuff', 'all_stuff'))

    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_with_level_false(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertFalse(r.has_perm('can_edit_stuff', 'no_stuff'))

    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_without_level_true(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertTrue(r.has_perm('can_edit_stuff'))

    @patch.object(core.Restraint, '_load_perms', spec_set=True)
    def test_without_level_false(self, mock_load_perms):
        r = core.Restraint(Mock())
        r._perms = {
            'can_edit_stuff': {
                'all_stuff': None,
                'some_stuff': None,
            }
        }
        self.assertFalse(r.has_perm('can_view_stuff'))
