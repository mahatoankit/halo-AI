"""
Management command to reset user password for testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Reset a user password for testing"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username to reset password for")
        parser.add_argument(
            "--password",
            type=str,
            default="testpass123",
            help="New password (default: testpass123)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Password reset for user "{username}" to "{password}"'
                )
            )

            # Show user details
            self.stdout.write(f"User details:")
            self.stdout.write(f"  - ID: {user.pk}")
            self.stdout.write(f"  - Email: {user.email}")
            self.stdout.write(f'  - Role: {getattr(user, "role", "N/A")}')
            self.stdout.write(f"  - Active: {user.is_active}")
            self.stdout.write(f'  - Approved: {getattr(user, "is_approved", "N/A")}')

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User "{username}" does not exist'))

            # Show available users
            users = User.objects.all()
            if users:
                self.stdout.write("Available users:")
                for u in users:
                    self.stdout.write(f"  - {u.username}")
