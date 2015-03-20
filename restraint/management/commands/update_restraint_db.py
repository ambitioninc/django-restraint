from optparse import make_option

from django.core.management.base import BaseCommand

from restraint.models import PermSet
from restraint.update_restraint_db import update_restraint_db


class Command(BaseCommand):
    """
    A management command for updating the restraint permissions based on the
    restraint config.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--flush_permission_sets',
            action='store_true',
            dest='async',
            default=False,
            help='Flush all permission sets before updating'
        ),
    )

    def handle(self, *args, **options):
        """
        Runs the command to update the restraint db.
        """
        if options['flush_permission_sets']:
            PermSet.objects.all().delete()

        update_restraint_db()
