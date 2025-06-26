"""
Management command to test authentication
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Test authentication for users"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Username to test")
        parser.add_argument("--password", type=str, help="Password to test")

    def handle(self, *args, **options):
        if options["username"] and options["password"]:
            # Test specific user
            self.test_auth(options["username"], options["password"])
        else:
            # Test all users with default passwords
            test_users = [
                ("admin", "admin123"),
                ("farmer_ram", "farmer123"),
                ("farmer_krishna", "farmer123"),
                ("community_admin_bhairahawa", "community123"),
                ("ankitmahato", "ankit123"),
            ]

            self.stdout.write("Testing authentication for all users:")
            self.stdout.write("=" * 50)

            for username, password in test_users:
                self.test_auth(username, password)
                self.stdout.write("")  # Empty line

    def test_auth(self, username, password):
        try:
            # First check if user exists
            user = User.objects.get(username=username)
            self.stdout.write(f"Testing: {username} / {password}")
            self.stdout.write(f"User exists: ✅")
            self.stdout.write(f'User active: {"✅" if user.is_active else "❌"}')
            self.stdout.write(
                f'User approved: {"✅" if getattr(user, "is_approved", True) else "❌"}'
            )

            # Test authentication
            auth_user = authenticate(username=username, password=password)

            if auth_user:
                self.stdout.write(f"Authentication: ✅ SUCCESS")
                self.stdout.write(f"Authenticated user ID: {auth_user.pk}")
                self.stdout.write(f'Role: {getattr(auth_user, "role", "N/A")}')
            else:
                self.stdout.write(f"Authentication: ❌ FAILED")

                # Try to reset password and test again
                user.set_password(password)
                user.save()
                self.stdout.write(f"Password reset, testing again...")

                auth_user = authenticate(username=username, password=password)
                if auth_user:
                    self.stdout.write(f"Authentication after reset: ✅ SUCCESS")
                else:
                    self.stdout.write(f"Authentication after reset: ❌ STILL FAILED")

        except User.DoesNotExist:
            self.stdout.write(f"Testing: {username} / {password}")
            self.stdout.write(f"User exists: ❌ USER NOT FOUND")

        except Exception as e:
            self.stdout.write(f"Testing: {username} / {password}")
            self.stdout.write(f"Error: ❌ {e}")
