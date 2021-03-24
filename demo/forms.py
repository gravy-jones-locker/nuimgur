from django.forms import ModelForm
from django import forms
from demo.models import ImageFile
from demo import config

class UploadFile(ModelForm):

    class Meta:
        model = ImageFile
        fields = ['in_file', 'gain', 'binned']