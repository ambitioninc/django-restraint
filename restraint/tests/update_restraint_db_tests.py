from django.test import TestCase

from restraint.core import register_restraint_config
from restraint.models import PermSet, Perm, PermLevel
from restraint.update_restraint_db import update_restraint_db


class UpdateRestraintDbTest(TestCase):
    def test_full_update_scenario(self):
        register_restraint_config({
            'perm_sets': ['global', 'restricted'],
            'perms': {
                'can_edit_stuff': {
                    'all_stuff': None,
                    'some_stuff': None,
                },
                'can_view_stuff': {}
            }
        })
        update_restraint_db()

        self.assertEquals(
            set(PermSet.objects.values_list('name', flat=True)), set(['global', 'restricted']))

        self.assertEquals(
            set(Perm.objects.values_list('name', flat=True)), set(['can_view_stuff', 'can_edit_stuff']))

        self.assertEquals(
            set(PermLevel.objects.values_list('name', 'perm__name')),
            set([('all_stuff', 'can_edit_stuff'), ('some_stuff', 'can_edit_stuff'), ('', 'can_view_stuff')]))
