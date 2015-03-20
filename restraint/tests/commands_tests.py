from django.core.management import call_command
from django.test import SimpleTestCase
from mock import patch


class UpdateRestraintDbTest(SimpleTestCase):
    @patch('restraint.management.commands.update_restraint_db.update_restraint_db', spec_set=True)
    def test_wo_flush_default_access(self, mock_update_restraint_db):
        call_command('update_restraint_db')
        mock_update_restraint_db.assert_called_once_with(flush_default_access=False)

    @patch('restraint.management.commands.update_restraint_db.update_restraint_db', spec_set=True)
    def test_w_flush_default_access(self, mock_update_restraint_db):
        call_command('update_restraint_db', flush_default_access=True)
        mock_update_restraint_db.assert_called_once_with(flush_default_access=True)
