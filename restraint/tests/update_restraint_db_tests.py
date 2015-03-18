from django.test import TestCase

from restraint.core import register_restraint_config
from restraint.models import PermSet
from restraint.update_restraint_db import update_restraint_db


class UpdateRestraintDbTest(TestCase):
    def test_full_update_scenario(self):
        register_restraint_config({
            'perm_sets': ['global', 'restricted']
        })
        update_restraint_db()

        self.assertEquals(
            set(PermSet.objects.values_list('name', flat=True)), set(['global', 'restricted']))
