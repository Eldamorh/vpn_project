from django.forms import ModelForm
from vpn_app.models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('location', 'company')