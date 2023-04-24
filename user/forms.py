from django import forms
from .models import *


class CaseCreationForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ["case_number","domain","link"]
        def clean(self):
            cleaned_data=super().clean()
            
            case_number = cleaned_data.get('case_number')
            domain = cleaned_data.get('domain')
            link = cleaned_data.get('link')
    
            if len(case_number) == 0:
                 raise forms.ValidationError("Enter valid Data")

            if len(domain) == 0:
                 raise forms.ValidationError("Enter valid Domain")

            if len(link) == 0 :
                 raise forms.ValidationError("Enter valid Link")

            if Case.objects.filter(case_number=case_number).exists():
                 raise forms.ValidationError("Case Number Already Exists")
            print("cretaipon endyfbujerbghkv:")
            return cleaned_data

class CaseSearchForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ["case_number"]
        def clean(self):
            cleaned_data = super().clean()
            
            case_number = cleaned_data.get('case_number')
        
            if len(case_number) == 0:
                 raise forms.ValidationError("Enter valid Data")

            if not Case.objects.filter(case_number=case_number).exists():
                 raise forms.ValidationError("Case Number Does Not Exists")
            print("searcg endyfbujerbghkv:")

            return cleaned_data
'''

class CaseCreationForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ["case_number","domain","link"]

class CaseSearchForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ["case_number"]
        '''


class MalwareUploadForm(forms.Form):
    # class Meta:
    #     model = Case
    #     fields = ["case_number","malware_file"]
    case_number = forms.CharField(max_length=5)
    malware_file = forms.FileField()

class ImageUploadForm(forms.Form):
    image_file = forms.ImageField()
