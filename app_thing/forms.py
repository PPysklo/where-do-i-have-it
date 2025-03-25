from django.forms import ModelForm  # ModelChoiceField
from django import forms

from .models import Thing, Location, Image


class ThingForm(ModelForm):
    city = forms.CharField(max_length=100, required=False)
    street = forms.CharField(max_length=255, required=False)
    street_address = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Thing
        fields = ["name", "city", "street", "street_address", "description"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ThingForm, self).__init__(*args, **kwargs)
        self.fields['existing_location'] = forms.ModelChoiceField(
            queryset=Location.objects.filter(owner=self.user),
            required=False,
            empty_label="Select existing location"
        )

        self.fields['description'].widget.attrs['class'] = 'form-control'


class ImageForm(forms.ModelForm):
    image = forms.FileField(widget=forms.TextInput(attrs={
            "name": "images",
            "type": "file",
            "class": "form-control",
            "multiple": "true",
            "accept": "image/jpeg, image/png",
        }), label="", required=False)

    class Meta:
        model = Image
        fields = ("image", )
