"""
Authentication forms for user registration and login.
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User


class SignupForm(UserCreationForm):
    """
    User registration form with custom fields and validation.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '이메일 주소'
        }),
        label='이메일',
        help_text='유효한 이메일 주소를 입력하세요.'
    )

    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '이름'
        }),
        label='이름',
        help_text='실명을 입력하세요.'
    )

    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '소속 학과 (선택사항)'
        }),
        label='학과',
        help_text='소속 학과를 입력하세요.'
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호'
        }),
        label='비밀번호',
        help_text='4자 이상 입력하세요.'
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호 확인'
        }),
        label='비밀번호 확인',
        help_text='동일한 비밀번호를 다시 입력하세요.'
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'department', 'password1', 'password2')

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get('email')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('이미 등록된 이메일입니다.')

        return email

    def clean_password1(self):
        """Validate password strength."""
        password1 = self.cleaned_data.get('password1')

        # Check minimum length
        if len(password1) < 4:
            raise ValidationError('비밀번호는 최소 4자 이상이어야 합니다.')

        return password1

    def save(self, commit=True):
        """Create new user with pending status."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.department = self.cleaned_data.get('department')
        user.role = 'viewer'  # Default role for new users
        user.status = 'pending'  # Requires admin approval

        # Set hashed password
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    User login form with email and password authentication.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '이메일 주소',
            'autofocus': True
        }),
        label='이메일'
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호'
        }),
        label='비밀번호'
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='로그인 유지'
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """Authenticate user with email and password."""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Try to get user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')

            # Check if user is approved
            if user.status == 'pending':
                raise ValidationError('승인 대기 중인 계정입니다. 관리자 승인을 기다려주세요.')
            elif user.status == 'inactive':
                raise ValidationError('비활성화된 계정입니다. 관리자에게 문의하세요.')

            # Authenticate user
            user = authenticate(
                request=self.request,
                username=email,  # Using email as username
                password=password
            )

            if user is None:
                raise ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        """Return authenticated user."""
        return getattr(self, 'user_cache', None)