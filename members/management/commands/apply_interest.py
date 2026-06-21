from django.core.management.base import BaseCommand
from members.services import apply_daily_interest


class Command(BaseCommand):
    help = "Apply daily loan interest"

    def handle(self, *args, **kwargs):
        apply_daily_interest()
        self.stdout.write("Interest applied successfully")
