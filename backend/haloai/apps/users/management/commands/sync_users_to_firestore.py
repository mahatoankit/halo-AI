"""
Django management command to sync existing users to Firestore
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from services.firestore_user_service import firestore_user_service

User = get_user_model()


class Command(BaseCommand):
    help = "Sync existing Django users to Firestore for enhanced profile storage"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="Force update existing Firestore profiles",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            help="Sync specific user by ID",
        )

    def handle(self, *args, **options):
        if not firestore_user_service.is_available():
            self.stdout.write(
                self.style.ERROR(
                    "Firestore is not available. Check Firebase configuration."
                )
            )
            return

        if options["user_id"]:
            # Sync specific user
            try:
                user = User.objects.get(pk=options["user_id"])
                self.sync_user(user, options["force_update"])
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'User with ID {options["user_id"]} does not exist.'
                    )
                )
        else:
            # Sync all users
            users = User.objects.all()
            total_users = users.count()

            self.stdout.write(f"Found {total_users} users to sync...")

            synced = 0
            skipped = 0
            errors = 0

            for user in users:
                try:
                    if self.sync_user(user, options["force_update"]):
                        synced += 1
                    else:
                        skipped += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error syncing user {user.username}: {e}")
                    )
                    errors += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Sync complete: {synced} synced, {skipped} skipped, {errors} errors"
                )
            )

    def sync_user(self, user, force_update=False):
        """Sync a single user to Firestore"""
        # Check if profile already exists
        existing_profile = firestore_user_service.get_user_profile(user.pk)

        if existing_profile and not force_update:
            self.stdout.write(f"Skipping {user.username} (already exists)")
            return False

        # Prepare profile data
        profile_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "phone": getattr(user, "phone", "") or "",
            "role": getattr(user, "role", "farmer"),
            "assigned_region": getattr(user, "assigned_region", "") or "",
            "is_approved": getattr(user, "is_approved", True),
            "profile_type": getattr(user, "role", "farmer"),
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
            "sync_source": "management_command",
        }

        if existing_profile:
            # Update existing profile
            success = firestore_user_service.update_user_profile(user.pk, profile_data)
            action = "updated"
        else:
            # Create new profile
            success = firestore_user_service.create_user_profile(user.pk, profile_data)
            action = "created"

        if success:
            self.stdout.write(
                self.style.SUCCESS(f"{action.capitalize()} profile for {user.username}")
            )
            return True
        else:
            self.stdout.write(
                self.style.WARNING(f"Failed to {action} profile for {user.username}")
            )
            return False
