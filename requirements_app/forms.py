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
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Boş bırakılırsa Ayarlar menüsündeki anahtar kullanılır',
                'autocomplete': 'off',
            },
        ),
    )
    model_type = forms.ChoiceField(
        choices=[
            ('gemini', 'Gemini 2.5 Flash'),
            ('claude', 'Claude 3.5 Sonnet'),
            ('openai', 'GPT-4o'),
        ],
        initial='gemini',
        widget=forms.HiddenInput(),
        required=False,
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
        if key:
            return key
        raise forms.ValidationError(
            'API anahtarı zorunludur. Forma girin veya ⚙️ Ayarlar menüsünden kaydedin.'
        )

    def clean_model_type(self):
        mt = (self.cleaned_data.get('model_type') or 'gemini').strip().lower()
        if mt not in {'gemini', 'claude', 'openai'}:
            return 'gemini'
        return mt
