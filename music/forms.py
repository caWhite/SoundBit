from django import forms
from django.contrib.auth.models import User
from models import UserModel


class UserForm(forms.ModelForm):
	class Meta:
		model = User

class UserForm(forms.ModelForm):
	class Meta:
		model = UserProfile