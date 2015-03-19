from django.test import SimpleTestCase

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
