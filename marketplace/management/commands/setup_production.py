import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command

class Command(BaseCommand):
    """
    Custom command to set up the production environment.
    This command will:
    1. Apply database migrations.
    2. Create or update a superuser using environment variables.
    """
    help = 'Sets up the production environment by applying migrations and creating/updating a superuser.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting production setup...'))

        # 1. Apply database migrations
        self.stdout.write(self.style.HTTP_INFO('Applying database migrations...'))
        try:
            call_command('migrate')
            self.stdout.write(self.style.SUCCESS('Database migrations applied successfully.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error applying migrations: {e}'))
            return

        # 2. Create or update a superuser
        self.stdout.write(self.style.HTTP_INFO('Checking for superuser...'))
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                'Superuser environment variables not set. Skipping superuser setup.'
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True}
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
        else:
            self.stdout.write(self.style.HTTP_INFO(f'Superuser "{username}" already exists. Checking password.'))
            if not user.check_password(password):
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" password has been updated.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" password is up to date.'))
        
        self.stdout.write(self.style.SUCCESS('Production setup finished.'))
