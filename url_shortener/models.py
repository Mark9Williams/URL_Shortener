# shortener/models.py
import secrets
import string
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError


User = get_user_model()


ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int = 7) -> str:
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))


class ShortURL(models.Model):
    user = models.ForeignKey(
    User, null=True, blank=True, on_delete=models.SET_NULL, related_name='short_urls'
    )
    original_url = models.URLField()
    short_code = models.SlugField(max_length=20, unique=True, editable=False)
    custom_code = models.SlugField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)


    class Meta:
        indexes = [
        models.Index(fields=['short_code']),
        models.Index(fields=['custom_code']),
        ]


    def clean(self):
        # Ensure a custom code never collides with any existing short or custom code
        if self.custom_code:
            conflict = ShortURL.objects.exclude(pk=self.pk).filter(
            models.Q(short_code=self.custom_code) | models.Q(custom_code=self.custom_code)
            )
            if conflict.exists():
                raise ValidationError({'custom_code': 'This code is already in use.'})
        return super().clean()


    def save(self, *args, **kwargs):
        if not self.short_code:
            code = generate_code()
            # Ensure new random code is globally unique across both fields
            while ShortURL.objects.filter(
                models.Q(short_code=code) | models.Q(custom_code=code)
            ).exists():
                code = generate_code()
            self.short_code = code
        super().save(*args, **kwargs)


    @property
    def code(self) -> str:
        return self.custom_code or self.short_code


    def is_expired(self) -> bool:
        return bool(self.expires_at and timezone.now() > self.expires_at)


    def get_absolute_short_url(self, request) -> str:
        return request.build_absolute_uri(f'/{self.code}')


    def __str__(self):
        return f"{self.code} -> {self.original_url}"

