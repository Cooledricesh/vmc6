"""
Custom management command to create superuser for managed=False User model.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Create a superuser for the custom User model'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--name', type=str, help='User name')
        parser.add_argument('--password', type=str, help='Password')

    def handle(self, *args, **options):
        email = options.get('email') or input('Email: ')
        name = options.get('name') or input('Name: ')
        password = options.get('password') or input('Password: ')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email "{email}" already exists.'))
            return

        # Create superuser
        now = timezone.now()
        user = User.objects.create(
            email=email,
            name=name,
            password=make_password(password),
            role='admin',
            status='active',
            department=None,
            position=None,
            created_at=now,
            updated_at=now
        )

        self.stdout.write(self.style.SUCCESS(f'Superuser created successfully: {user.email}'))
        self.stdout.write(self.style.SUCCESS(f'  - Name: {user.name}'))
        self.stdout.write(self.style.SUCCESS(f'  - Role: {user.role}'))
        self.stdout.write(self.style.SUCCESS(f'  - Status: {user.status}'))
