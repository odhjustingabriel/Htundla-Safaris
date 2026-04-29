from django import forms
from .models import Inquiry, Destination

ALLOWED_INTERESTS=['Game Drive','Nature Walk','Photography','Culture','MICE','Birding','Cuisine','Camping','Beach','Adventure']

class InquiryForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(choices=[(i,i) for i in ALLOWED_INTERESTS], widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Inquiry
        fields = ['full_name','email','phone_number','travel_type','destination','duration_days','travel_style','group_size','interests']

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
