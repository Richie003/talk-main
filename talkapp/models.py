from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from utils.models import ModelUtilsMixin
from utils.custom_enums import Level, UserRole, AvailabilityStatus
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
def profile_image_upload_path(instance, filename):
    return f"imgs/{instance.user.talk_id}/{slugify(instance.user.talk-id)}-{filename}"

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
    talk_id = models.CharField(max_length=10, unique=True, blank=True)
    email = models.EmailField(unique=True, blank=True)
    gender = models.CharField(max_length=10, default="male", choices=[("male", "Male"), ("female", "Female")])
    university = models.CharField(max_length=100, blank=True)
    level = models.CharField(default=Level.LEVEL_100, max_length=100, blank=False, choices=Level.choices())
    # registration_number = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    user_role = models.CharField(max_length=255, default=UserRole.NONE, choices=UserRole.choices())
    policy = models.BooleanField(default=False, blank=True)
    availability = models.CharField(max_length=255, choices=AvailabilityStatus.choices(), default=AvailabilityStatus.AVAILABLE)
    email_verified = models.BooleanField(default=False, blank=True)
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

    def generate_talk_id(self):
        first_initial = self.first_name[0].upper()
        last_initial = self.last_name[0].upper()
        return first_initial + last_initial + ''.join(random.choices(string.digits, k=5))

    def clean(self):
        if self.talk_id:
            if not re.match(r"^[A-Z]{2}\d{5}$", self.talk_id):
                raise ValidationError("talk_id must be 2 uppercase letters followed by 5 digits (e.g., AB12345)")

    def save(self, *args, **kwargs):
        if not self.talk_id and self.first_name and self.last_name:
            for _ in range(10):
                try:
                    self.talk_id = self.generate_talk_id()
                    with transaction.atomic():
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    continue
            raise Exception(
                "Failed to generate a unique talk_id after multiple attempts."
            )
        else:
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
    photo = models.FileField(upload_to=f"individual/{profile_image_upload_path}", blank=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.user)
    
    def get_profile_photo(self):
        return self.photo.url if self.photo else None


class ServiceProvider(ModelUtilsMixin):
    user = models.OneToOneField(
        user, on_delete=models.CASCADE, related_name='serviceproviders_profile')
    bio = models.TextField(blank=True, null=True)
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(unique=True)
    business_tel = models.CharField(max_length=25, blank=False)
    business_type = models.CharField(max_length=100)
    logo = models.FileField(upload_to=f"service_provider/{profile_image_upload_path}", blank=True)
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


