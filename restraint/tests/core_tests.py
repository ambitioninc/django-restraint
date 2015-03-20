from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django_dynamic_fixture import G

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
            'perm_sets': ['super', 'individual', 'staff'],
            'perms': {
                'can_edit_stuff': {
                    'all_stuff': None,
                    'some_stuff': lambda a: User.objects.filter(id=a.id).values_list('id', flat=True),
                    'only_superusers': lambda a: User.objects.filter(is_superuser=True).values_list('id', flat=True),
                },
                'can_view_stuff': {
                    '': None,
                }
            },
            'default_access': {
                'super': {
                    'can_edit_stuff': ['all_stuff', 'some_stuff'],
                    'can_view_stuff': [],
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
        update_restraint_db()

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
