from django import forms
from .models import Requirement, Project


class RequirementForm(forms.Form):
    project_name = forms.CharField(
        max_length=200,
        label='Proje Adı',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Örn: E-Ticaret Platformu',
        }),
    )
    raw_text = forms.CharField(
        label='Yazılım Fikri / Gereksinim',
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 6,
            'placeholder': (
                'Örn: Kullanıcılar sisteme e-posta ve şifre ile giriş yapabilmeli, '
                'hatalı girişlerde hesap belirli süre kilitlenebilmeli...'
            ),
        }),
    )

    def clean_raw_text(self):
        text = self.cleaned_data.get('raw_text', '').strip()
        if len(text) < 10:
            raise forms.ValidationError(
                'Gereksinim metni en az 10 karakter olmalıdır. '
                'Lütfen daha ayrıntılı bir açıklama giriniz.'
            )
        return text

    def clean_project_name(self):
        name = self.cleaned_data.get('project_name', '').strip()
        if not name:
            raise forms.ValidationError('Proje adı boş bırakılamaz.')
        return name
