from django.test import SimpleTestCase, TestCase

from restraint import core


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


class TestGetPerms(TestCase):
    def test_get_all_perms(self):
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
            }
        }
