from django import forms
from django.core.mail import EmailMessage
from .models import CarsharUserModel

class CarsharUserCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwd):
        super(CarsharUserCreateForm, self).__init__(*args, **kwd)
        self.fields["gender"].required = False
    class Meta:
        model = CarsharUserModel
        fields = ['id', 'name', 'gender', 'age', 'birthday', 'zip01', 'pref01', 'addr01', 'addr02']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control'}),
            'zip01': forms.TextInput(attrs={'onKeyUp' : "AjaxZip3.zip2addr(this,'','pref01','addr01')"}),
        }
        labels={
           'name': '名前',
           'gender': '性別',
           'age': '年齢',
           'birthday': '生年月日',
           'zip01': '郵便番号',
           'pref01': '都道府県名',
           'addr01': '市町村',
           'addr02': 'それ以降の住所',
        }