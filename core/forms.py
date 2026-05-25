from django import forms
from .models import Order, Client, DeviceType

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['device', 'client_problem', 'status']
        widgets = {
            'client_problem': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Опишите подробно проблему...'
            }),
            'device': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_client_problem(self):
        problem = self.cleaned_data.get('client_problem')
        if len(problem) < 10:
            raise forms.ValidationError('Описание проблемы должно быть не менее 10 символов')
        if len(problem) > 500:
            raise forms.ValidationError('Описание проблемы не должно превышать 500 символов')
        return problem
    
    def save(self, commit=True):
        order = super().save(commit=False)
        if self.user and hasattr(self.user, 'client_profile'):
            order.client = self.user.client_profile
        if commit:
            order.save()
        return order