# apps/authentication/models.py
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password, check_password


class UserManager(BaseUserManager):
    """
    Custom manager for User model to provide Django auth compatibility.
    """
    def get_by_natural_key(self, email):
        """
        Get user by email (natural key for authentication).
        """
        return self.get(email=email)


class User(models.Model):
    """
    Custom User model that maps to Supabase 'users' table.
    Schema matches docs/database.md and supabase/migrations/*.sql

    IMPORTANT: managed=False means Django does NOT manage the database schema.
    All schema changes must be done via Supabase migrations.
    """

    class Meta:
        db_table = 'users'
        managed = False  # ★★★ Django does not manage DB schema
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    # Django auth system requirements (does NOT affect DB schema due to managed=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    # Custom manager for authentication
    objects = UserManager()

    # Primary key
    id = models.BigAutoField(primary_key=True)

    # Required fields
    email = models.CharField(max_length=255, unique=True, verbose_name='이메일')
    password = models.CharField(max_length=255, verbose_name='비밀번호')
    name = models.CharField(max_length=100, verbose_name='이름')

    # Optional fields
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='소속 학과')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='직책')

    # Role and status
    role = models.CharField(max_length=20, verbose_name='역할')
    status = models.CharField(max_length=20, default='pending', verbose_name='상태')

    # Timestamps
    created_at = models.DateTimeField(verbose_name='생성일시')
    updated_at = models.DateTimeField(verbose_name='수정일시')

    def __str__(self):
        return self.email

    # Django auth system compatibility methods
    @property
    def is_anonymous(self):
        """Always return False for real users"""
        return False

    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True

    def get_username(self):
        """Return the identifying username for this User"""
        return self.email

    @property
    def is_staff(self):
        """Is the user a member of staff? (admin or manager)"""
        return self.role in ['admin', 'manager']

    @property
    def is_superuser(self):
        """Is the user a superuser? (admin only)"""
        return self.role == 'admin'

    @property
    def is_active(self):
        """Django compatibility - returns True if user is active"""
        return self.status == 'active'

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return self.role == 'admin'

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app?"""
        return self.role == 'admin'

    def is_approved(self):
        """Check if user is approved (active status)"""
        return self.status == 'active'

    def is_pending(self):
        """Check if user is pending approval"""
        return self.status == 'pending'

    def is_rejected(self):
        """Check if user is rejected (inactive status)"""
        return self.status == 'inactive'

    def can_access_department(self, department):
        """Check if user can access a specific department"""
        if self.role in ['admin', 'manager']:
            return True
        return self.department == department

    def set_password(self, raw_password):
        """Set user password (hashed)"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password is correct"""
        return check_password(raw_password, self.password)
