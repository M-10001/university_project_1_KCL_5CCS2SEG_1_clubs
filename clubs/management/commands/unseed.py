from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club

class Command(BaseCommand):
    """The database unseeder."""

    def handle(self, *args, **options):
        User.objects.all().filter(is_admin = False).delete()
        Club.objects.all().delete()
