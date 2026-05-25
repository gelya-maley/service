from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Client
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label='ФИО', required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(max_length=20, label='Телефон', required=True, help_text='Формат: +375 (29) 123-45-67')
    address = forms.CharField(widget=forms.Textarea, label='Адрес', required=True)
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.SelectDateWidget(years=range(1950, 2009)),
        help_text='Вы должны быть старше 18 лет'
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone', 'address', 'birth_date', 'password1', 'password2')
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        pattern = r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError('Телефон должен быть в формате: +375 (29) 123-45-67')
        return phone
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise forms.ValidationError('Вам должно быть 18 лет или старше для регистрации.')
        return birth_date
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['full_name'].split()[0] if self.cleaned_data['full_name'].split() else ''
        user.last_name = self.cleaned_data['full_name'].split()[-1] if len(self.cleaned_data['full_name'].split()) > 1 else ''
        
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                birth_date=self.cleaned_data['birth_date']
            )
        return user