from django import forms
from django.core.validators import validate_email
from django.utils.html import strip_tags

from .models import Destination, Inquiry

ALLOWED_INTERESTS = [
    'Game Drive', 'Nature Walk', 'Photography', 'Culture', 'MICE', 'Birding',
    'Cuisine', 'Camping', 'Beach', 'Adventure', 'Team Building', 'Conference'
]

MAX_NAME_LEN = 120
MAX_PHONE_LEN = 25


class InquiryForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=[(i, i) for i in ALLOWED_INTERESTS],
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Inquiry
        fields = [
            'full_name', 'email', 'phone_number', 'travel_type', 'destination',
            'duration_days', 'travel_style', 'group_size', 'interests'
        ]

    def clean_full_name(self):
        full_name = strip_tags((self.cleaned_data.get('full_name') or '').strip())
        if not full_name or len(full_name) > MAX_NAME_LEN:
            raise forms.ValidationError('Full name is required and must be at most 120 characters.')
        return full_name

    def clean_email(self):
        email = strip_tags((self.cleaned_data.get('email') or '').strip().lower())
        validate_email(email)
        return email

    def clean_phone_number(self):
        phone = strip_tags((self.cleaned_data.get('phone_number') or '').strip())
        if len(phone) > MAX_PHONE_LEN:
            raise forms.ValidationError('Phone number must be at most 25 characters.')
        return phone

    def clean_destination(self):
        d = self.cleaned_data['destination']
        if not Destination.objects.filter(id=d.id).exists():
            raise forms.ValidationError('Unsupported destination')
        return d

    def clean_interests(self):
        interests = self.cleaned_data.get('interests') or []
        if len(interests) > len(ALLOWED_INTERESTS):
            raise forms.ValidationError('Malformed interests payload.')
        invalid = [i for i in interests if i not in ALLOWED_INTERESTS]
        if invalid:
            raise forms.ValidationError('Unsupported interests provided.')
        return interests

    def clean(self):
        data = super().clean()
        if data.get('travel_type') == 'Safari' and data.get('duration_days') and not (3 <= data['duration_days'] <= 5):
            self.add_error('duration_days', 'Safari core trips must be between 3 and 5 days.')
        return data
