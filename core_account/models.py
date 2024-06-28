from django.db import models
from core_account.manager import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils.text import slugify
import uuid



class User(AbstractBaseUser, PermissionsMixin):
    GENDER = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Not confirmed", "Not confirmed"),
    )
    
    # General Information about the user
    profile = models.ImageField(upload_to="profile/images", db_index=True)
    profile_slug = models.SlugField(unique=True, max_length=255, db_index=True, default='')
    name = models.CharField(max_length=100,  db_index=True)
    username = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(db_index=True, unique=True)
    date_of_birth = models.DateField(default=None, null=True, db_index=True)
    gender = models.CharField(max_length=100, choices=GENDER, null=True, db_index=True)
    mobile_number = models.BigIntegerField(null=True)
    otp = models.PositiveIntegerField(null=True)
    otp_limit = models.IntegerField(null=True)
    otp_delay = models.TimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=None, null=True)
    is_blocked = models.BooleanField(default=False, null=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    auth_provider = models.CharField(max_length=50, db_index=True, default=None, null=True)
    password = models.CharField(max_length=200, db_index=True, default=None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    groups = models.ManyToManyField(Group, related_name='user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions', blank=True)

    def save(self, *args, **kwargs):
        if not self.profile_slug:
            max_slug_length = 255
            username_slug = slugify(self.username)
            uuid_suffix = uuid.uuid4().hex[:8]
            allowed_username_length = max_slug_length - len(uuid_suffix) - 1
            if len(username_slug) > allowed_username_length:
                username_slug = username_slug[:allowed_username_length]
            self.profile_slug = f"{username_slug}-{uuid_suffix}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)