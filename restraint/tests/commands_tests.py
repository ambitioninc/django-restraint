from django.core.management import call_command
from django.test import TestCase
from django_dynamic_fixture import G
from mock import patch

from restraint.models import PermSet


class UpdateRestraintDbTest(TestCase):
    @patch('restraint.management.commands.update_restraint_db.update_restraint_db', spec_set=True)
    def test_wo_flush_perm_sets(self, mock_update_restraint_db):
        G(PermSet)
        call_command('update_restraint_db')
        mock_update_restraint_db.assert_called_once_with()
        self.assertTrue(PermSet.objects.exists())

    @patch('restraint.management.commands.update_restraint_db.update_restraint_db', spec_set=True)
    def test_w_flush_perm_sets(self, mock_update_restraint_db):
        G(PermSet)
        call_command('update_restraint_db', flush_permission_sets=True)
        mock_update_restraint_db.assert_called_once_with()
        self.assertFalse(PermSet.objects.exists())
