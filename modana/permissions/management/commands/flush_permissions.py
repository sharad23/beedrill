from django.core.management import BaseCommand
from permissions.helpers import flush_permissions


class Command(BaseCommand):
    """
    Update permissions
    """

    def handle(self, **options):
        flush_permissions()
