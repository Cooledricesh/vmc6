from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for User model"""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError('이메일은 필수입니다')
        if not username:
            raise ValueError('사용자명은 필수입니다')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault('is_active', 'active')
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_active') != 'active':
            raise ValueError('Superuser must have is_active=active.')
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role=admin.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser):
    """
    Custom User model that maps to Supabase 'users' table.
    Uses email as the unique identifier.
    """
    # Role choices
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    # Primary key
    id = models.BigAutoField(primary_key=True, db_column='id')

    # Required fields
    email = models.EmailField(
        unique=True,
        db_column='email',
        verbose_name='이메일'
    )
    username = models.CharField(
        max_length=100,
        unique=True,
        db_column='username',
        verbose_name='사용자명'
    )

    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        db_column='role',
        verbose_name='역할'
    )

    # Department (optional)
    department = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='department',
        verbose_name='부서'
    )

    # Status
    is_active = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_column='is_active',
        verbose_name='상태'
    )

    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        db_column='created_at',
        verbose_name='생성일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        verbose_name='수정일시'
    )

    # Manager
    objects = UserManager()

    # Required for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        managed = False  # Supabase manages the schema
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the email address."""
        return self.email

    def get_short_name(self):
        """Return the username."""
        return self.username

    @property
    def is_staff(self):
        """Is the user a member of staff? (admin or manager)"""
        return self.role in ['admin', 'manager']

    @property
    def is_superuser(self):
        """Is the user a superuser? (admin only)"""
        return self.role == 'admin'

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: admin has all permissions
        return self.role == 'admin'

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: admin has all permissions
        return self.role == 'admin'

    def is_approved(self):
        """Check if user is approved (active status)"""
        return self.is_active == 'active'

    def is_pending(self):
        """Check if user is pending approval"""
        return self.is_active == 'pending'

    def is_rejected(self):
        """Check if user is rejected (inactive status)"""
        return self.is_active == 'inactive'

    def can_access_department(self, department):
        """Check if user can access a specific department"""
        # Admin and manager can access all departments
        if self.role in ['admin', 'manager']:
            return True
        # Viewer can only access their own department
        return self.department == department
