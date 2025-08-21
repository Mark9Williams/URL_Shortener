# shortener/forms.py
import re
from django import forms
from django.utils import timezone
from .models import ShortURL


class URLForm(forms.ModelForm):
    class Meta:
        model = ShortURL
        fields = ['original_url', 'custom_code', 'expires_at']
        help_texts = {
            'custom_code': 'Optional. Use letters, numbers, hyphen (-) or underscore (_).',
        }


    def clean_custom_code(self):
        code = self.cleaned_data.get('custom_code')
        if code and not re.fullmatch(r'[-a-zA-Z0-9_]+', code):
            raise forms.ValidationError('Use only letters, numbers, hyphen (-) or underscore (_).')
        return code


    def clean_expires_at(self):
        dt = self.cleaned_data.get('expires_at')
        if dt and dt <= timezone.now():
            raise forms.ValidationError('Expiration must be in the future.')
        return dt
