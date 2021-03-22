from django.forms import forms, ModelForm
from demo.models import ImageFile

class UploadFile(ModelForm):

    class Meta:
        model = ImageFile
        fields = ['in_file', 'fname']