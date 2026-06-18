from django import forms
from django.contrib.auth.models import Group, Permission, User
from django.core.validators import MaxLengthValidator
from django.forms import modelformset_factory
from .models import Destination, Inquiry, ItineraryItem

ALLOWED_INTERESTS=['Game Drive','Nature Walk','Photography','Culture','MICE','Birding','Cuisine','Camping','Beach','Adventure','Team Building','Conference','Wildlife Conservation','Hot Air Balloon','Hiking','Wellness','Honeymoon','Family Friendly','Historical Sites','Shopping','Nightlife','Water Sports','Volunteering','Luxury Lodges']

class InquiryForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(choices=[(i,i) for i in ALLOWED_INTERESTS], widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Inquiry
        fields = ['full_name','email','phone_number','travel_type','destination','duration_days','travel_style','group_size','interests','additional_interests']

    def clean_destination(self):
        d = self.cleaned_data['destination']
        if not Destination.objects.filter(id=d.id).exists():
            raise forms.ValidationError('Unsupported destination')
        return d

    def clean(self):
        data = super().clean()
        if data.get('travel_type') == 'Safari' and data.get('duration_days') and not (3 <= data['duration_days'] <= 5):
            self.add_error('duration_days', 'Safari core trips must be between 3 and 5 days.')
        return data

    def clean_additional_interests(self):
        value = self.cleaned_data.get('additional_interests', '')
        parts = [part.strip() for part in value.split(',') if part.strip()]
        return ', '.join(parts)


    def clean_additional_interests(self):
        value = self.cleaned_data.get('additional_interests', '')
        parts = [part.strip() for part in value.split(',') if part.strip()]
        return ', '.join(parts)


class ProposalForm(forms.Form):
    final_cost = forms.DecimalField(required=False, min_value=0, max_digits=10, decimal_places=2)
    proposal_notes = forms.CharField(required=False, validators=[MaxLengthValidator(5000)], widget=forms.Textarea)


class ItineraryItemEditForm(forms.ModelForm):
    class Meta:
        model = ItineraryItem
        fields = ['day_number', 'time_slot', 'title', 'notes']
        widgets = {
            'day_number': forms.NumberInput(attrs={'min': 1}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


ItineraryItemFormSet = modelformset_factory(
    ItineraryItem,
    form=ItineraryItemEditForm,
    extra=0,
    can_delete=False,
)


class StaffRoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']


class StaffUserForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.order_by('name'), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_staff'].initial = True
        if self.instance and self.instance.pk:
            self.fields['password'].help_text = 'Leave blank to keep the current password.'
        else:
            self.fields['password'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user
