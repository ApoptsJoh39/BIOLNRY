
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    """
    Custom command to set up the production environment.
    This command will:
    1. Apply database migrations.
    2. Create a superuser if one does not exist, using environment variables.
    """
    help = 'Sets up the production environment by applying migrations and creating a superuser.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting production setup...'))

        # 1. Apply database migrations
        self.stdout.write(self.style.HTTP_INFO('Applying database migrations...'))
        from django.core.management import call_command
        try:
            call_command('migrate')
            self.stdout.write(self.style.SUCCESS('Database migrations applied successfully.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error applying migrations: {e}'))
            # Exit if migrations fail, as the rest depends on the schema being correct.
            return

        # 2. Create a superuser if one does not exist
        self.stdout.write(self.style.HTTP_INFO('Checking for superuser...'))
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                'Superuser environment variables not set (DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD). Skipping superuser creation.'
            ))
        elif User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" already exists. Skipping creation.'))
        else:
            self.stdout.write(self.style.HTTP_INFO(f'Creating superuser "{username}"...'))
            try:
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating superuser: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Production setup finished.'))
