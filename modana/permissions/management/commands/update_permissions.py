from django.core.management import BaseCommand
from permissions.helpers import update_permissions


class Command(BaseCommand):
    """
    Update permissions
    """

    def handle(self, **options):
        update_permissions()
