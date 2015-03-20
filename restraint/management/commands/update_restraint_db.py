from optparse import make_option

from django.core.management.base import BaseCommand

from restraint.core import update_restraint_db


class Command(BaseCommand):
    """
    A management command for updating the restraint permissions based on the
    restraint config.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--flush_default_access',
            action='store_true',
            dest='flush_default_access',
            default=False,
            help='Flush all permission sets before updating'
        ),
    )

    def handle(self, *args, **options):
        """
        Runs the command to update the restraint db.
        """
        update_restraint_db(flush_default_access=options['flush_default_access'])
