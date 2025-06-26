from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a system administrator user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", type=str, required=True, help="Username for the admin"
        )
        parser.add_argument(
            "--email", type=str, required=True, help="Email for the admin"
        )
        parser.add_argument(
            "--password", type=str, required=True, help="Password for the admin"
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists.'))
            return

        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role="admin",
            is_approved=True,
            first_name="System",
            last_name="Administrator",
        )

        self.stdout.write(
            self.style.SUCCESS(f'System admin "{username}" created successfully.')
        )
