from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from utils.models import ModelUtilsMixin
from utils.custom_enums import Level, UserRole, AvailabilityStatus, RegistrationMethod
from django.db import models, IntegrityError, transaction
from django.conf import settings
import random
import string
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import re
from django.core.exceptions import ValidationError

user = settings.AUTH_USER_MODEL

def individual_profile_image_upload_path(instance, filename):
    return f"imgs/individual/{instance.user.talk_id}/{slugify(instance.user.talk_id)}-{filename}"

def sp_profile_image_upload_path(instance, filename):
    return f"imgs/service_provider/{instance.user.talk_id}/{slugify(instance.user.talk_id)}-{filename}"

class UserManager(BaseUserManager):
    """User Manager that knows how to create users via email instead of username"""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, ModelUtilsMixin):
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    talk_id = models.CharField(max_length=255, unique=True, blank=True)
    email = models.EmailField(unique=True, blank=True)
    gender = models.CharField(max_length=11, default="male", choices=[("male", "Male"), ("female", "Female")])
    university = models.CharField(max_length=100, blank=True)
    level = models.CharField(default=Level.LEVEL_100[0], max_length=100, blank=False, choices=Level.choices())
    state = models.CharField(max_length=100, blank=True)
    user_role = models.CharField(max_length=255, default=UserRole.INDIVIDUALS[0], choices=UserRole.choices())
    registration_type = models.CharField(max_length=7, choices=RegistrationMethod.choices(), default=RegistrationMethod.INAPP[0])
    policy = models.BooleanField(default=False, blank=True)
    availability = models.CharField(max_length=255, choices=AvailabilityStatus.choices(), default=AvailabilityStatus.AVAILABLE[0], blank=True)
    email_verified = models.BooleanField(default=False, blank=True)
    hide_my_info = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False, blank=True)
    

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def profile(self):
        user_role = self.user_role
        data = {
            "user_id": self.id,
            "talk_id": self.talk_id,
            "user_role": user_role,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "university": self.university,
            "level": self.level,
            "state": self.state,
            "hide_my_info": self.hide_my_info,
            "email_verified": self.email_verified,
            "policy": self.policy,
            "marketing_emails": self.marketing_emails,
        }
        if user_role[0] == "individuals":
            data["phone_number"] = self.individuals_profile.phone_number
            data["date_of_birth"] = self.individuals_profile.date_of_birth
            data["interests"] = self.individuals_profile.interests
            data["bio"] = self.individuals_profile.bio
            data["profile_photo"] = self.individuals_profile.get_profile_photo().photo.url if hasattr(self.individuals_profile, 'get_profile_photo') else None
        elif user_role[1] == "service providers":
            data["business_name"] = self.serviceproviders_profile.business_name 
            data["business_email"] = self.serviceproviders_profile.business_email 
            data["business_tel"] = self.serviceproviders_profile.business_tel 
            data["business_type"] = self.serviceproviders_profile.business_type 
            data["description"] = self.serviceproviders_profile.description 
            data["city"] = self.serviceproviders_profile.city 
            data["address"] = self.serviceproviders_profile.address 
            data["address_verified"] = self.serviceproviders_profile.address_verified 
            data["logo"] = self.get_logo().logo.url if hasattr(self.serviceproviders_profile, 'get_logo') else None
        return data


    def save(self, *args, **kwargs):
        # (#) Only generate a talk_id when it's empty and we have initials to form it from.
        if not self.talk_id and self.first_name and self.last_name:
            # (#) Normalize initials to A-Z and provide safe fallbacks
            first = (self.first_name.strip() or "X")[0].upper()
            last = (self.last_name.strip() or "X")[0].upper()
            max_attempts = 100  # (#) increased from 10 to reduce chance of failure
            attempt = 0
            from django.utils.crypto import get_random_string
            while attempt < max_attempts:
                # (#) increase entropy: using 6 digits or alphanumeric suffix
                suffix = get_random_string(length=6, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                self.talk_id = f"{first}{last}{suffix}"
                try:
                    # (#) Atomic save ensures unique constraint violations roll back cleanly.
                    with transaction.atomic():
                        # (#) Optionally call self.clean() here to enforce format rules:
                        # self.clean()
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    attempt += 1
                    # (#) Loop will retry with a fresh talk_id
                    continue
            # (#) Be explicit in the error type and message
            raise RuntimeError(f"Failed to generate a unique talk_id after {max_attempts} attempts")
        # (#) If talk_id already set (or names missing), fall back to normal save behavior.
        super().save(*args, **kwargs)

@receiver(post_save, sender=CustomUser)
def create_otp_for_new_user(sender, instance, created, **kwargs):
    if created:
        OneTimePassword.objects.create(user=instance)

class OneTimePassword(ModelUtilsMixin):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp}"
    
    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = ''.join(random.choices(string.digits, k=6))
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)

class Individual(ModelUtilsMixin):
    user = models.OneToOneField(
        user, on_delete=models.CASCADE, related_name='individuals_profile')
    phone_number = models.CharField(max_length=25, blank=False)
    date_of_birth = models.DateField()
    interests = models.JSONField(blank=True, null=True)
    photo = models.FileField(upload_to=individual_profile_image_upload_path, blank=True)
    photo_url = models.URLField(max_length=255, blank=True, null=True, help_text="URL of the profile photo if uploaded via URL or third-party service(Google SSO).")
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.user)
    
    def get_profile_photo(self):
        return self.photo.url if self.photo else self.photo_url


class ServiceProvider(ModelUtilsMixin):
    user = models.OneToOneField(
        user, on_delete=models.CASCADE, related_name='serviceproviders_profile')
    bio = models.TextField(blank=True, null=True)
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(unique=True)
    business_tel = models.CharField(max_length=25, blank=False)
    business_type = models.CharField(max_length=100)
    logo = models.FileField(upload_to=sp_profile_image_upload_path, blank=True)
    description = models.TextField()
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    address_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.business_name)
    
    def get_logo(self):
        return self.logo.url if self.logo else None
class Review(models.Model):
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} rated {self.service_provider} with {self.rating}"


class SaveUserProfile(ModelUtilsMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    saved_user = models.ManyToManyField(CustomUser, related_name='saved_users')
    # fullname, vocation, university, profile_photo

    class Meta:
        ordering = ["-created", "-updated"]

    def __str__(self):
        return f"{self.user.username}'s saved users"
    
    def save_user(self, user):
        self.saved_user.add(user)
    
    def remove_user(self, user):
        self.saved_user.remove(user)

    def get_saved_users(self):
        return self.saved_user.all()

    def clear_saved_users(self):
        self.saved_user.clear()
    
    def is_user_saved(self, user):
        return self.saved_user.filter(id=user.id).exists()
    
    def get_user_saved_users(self):
        return self.saved_user.filter(saved_items__user=self.user)

    def get_saved_user_count(self):
        return int(self.saved_user.count())

    def get_saved_user_details(self):
        saved_users = []
        for user in self.saved_user.all():
            if hasattr(user, "user_profile"):
                saved_users.append(user.user_profile())
            else:
                saved_users.append({
                    "id": user.id,
                    "name": user.first_name + " " + user.last_name,
                    "university": user.university,
                    "service": user.serviceproviders_profile.business_type if hasattr(user, 'serviceproviders_profile') else "Student",
                })
        return saved_users
    
    def get_saved_user_by_id(self, user_id):
        return self.user.filter(id=user_id).first().user_profile() if self.user.filter(id=user_id).exists() else None