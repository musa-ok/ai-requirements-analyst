from django import forms


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
    api_key = forms.CharField(
        label='Gemini API anahtarı',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Google AI Studio anahtarı (sunucuda saklanmaz)',
                'autocomplete': 'off',
            },
        ),
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

    def clean_api_key(self):
        key = self.cleaned_data.get('api_key', '').strip()
        if not key:
            raise forms.ValidationError('Gemini API anahtarı zorunludur.')
        return key
