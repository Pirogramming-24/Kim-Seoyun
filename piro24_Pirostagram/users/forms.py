from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',) # 필요한 필드만 남기세요 (예: email 추가 가능)

    # 비밀번호 규칙(유효성 검사)을 아예 수행하지 않도록 비웁니다.
    def clean_password1(self):
        return self.cleaned_data.get("password1")
