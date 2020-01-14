from django.contrib.auth.forms import UserCreationForm

from insta_app.models import InstaUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = InstaUser
        fields = ['username', 'email', 'profile_pic']
