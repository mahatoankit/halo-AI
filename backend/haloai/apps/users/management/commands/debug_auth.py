"""
Management command to debug and fix authentication issues
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from apps.users.models import CustomUser


class Command(BaseCommand):
    help = "Debug and fix authentication issues"

    def handle(self, *args, **options):
        self.stdout.write("🔍 Debugging authentication issues...")

        # Check all users
        users = CustomUser.objects.all()
        self.stdout.write(f"Found {users.count()} users in database")

        test_credentials = [
            ("admin", "demo123"),
            ("community_admin_bhairahawa", "demo123"),
            ("farmer_krishna", "demo123"),
            ("farmer_sita", "demo123"),
            ("farmer_ram", "demo123"),
        ]

        for username, password in test_credentials:
            self.stdout.write(f"\n=== Testing {username} ===")

            try:
                user = CustomUser.objects.get(username=username)

                # Check user status
                self.stdout.write(f"Role: {user.role}")
                self.stdout.write(f"Is Active: {user.is_active}")
                self.stdout.write(f"Is Approved: {user.is_approved}")
                self.stdout.write(f"Has Usable Password: {user.has_usable_password()}")

                # Test password check
                password_valid = check_password(password, user.password)
                self.stdout.write(
                    f'Password Check: {"✅ VALID" if password_valid else "❌ INVALID"}'
                )

                # Test Django authenticate
                auth_result = authenticate(username=username, password=password)
                self.stdout.write(
                    f'Django Authenticate: {"✅ SUCCESS" if auth_result else "❌ FAILED"}'
                )

                # Fix issues
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    self.stdout.write("  🔧 Fixed: Set user as active")

                if user.role == "community_admin" and not user.is_approved:
                    user.is_approved = True
                    user.save()
                    self.stdout.write("  🔧 Fixed: Approved community admin")

                # If password is invalid, reset it
                if not password_valid:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(f"  🔧 Fixed: Reset password to {password}")

                    # Test again
                    auth_result = authenticate(username=username, password=password)
                    self.stdout.write(
                        f'  ✅ Re-test: {"SUCCESS" if auth_result else "STILL FAILED"}'
                    )

            except CustomUser.DoesNotExist:
                self.stdout.write(f"❌ User {username} does not exist")

                # Create missing user
                if username == "admin":
                    admin_user = CustomUser.objects.create_user(
                        username="admin",
                        password="demo123",
                        email="admin@halo-ai.demo",
                        role="admin",
                        is_staff=True,
                        is_superuser=True,
                        is_active=True,
                        is_approved=True,
                    )
                    self.stdout.write("  🔧 Created admin user")

        self.stdout.write("\n🎉 Authentication debugging completed!")
        self.stdout.write("\nTry logging in with these credentials:")
        self.stdout.write("- admin / demo123 (Global Admin)")
        self.stdout.write("- community_admin_bhairahawa / demo123 (Community Admin)")
        self.stdout.write("- farmer_krishna / demo123 (Farmer)")
        self.stdout.write("- farmer_sita / demo123 (Farmer)")
        self.stdout.write("- farmer_ram / demo123 (Farmer)")
